import argparse
import requests
import json
import sys
import os

URL = "https://api.getjobber.com/api/graphql"

def load_token():
    # Helper to load the persistent token we saved earlier
    try:
        with open("jobber_tokens.json", "r") as f:
            return json.load(f).get("access_token")
    except FileNotFoundError:
        print("Error: jobber_tokens.json not found. Run OAuth flow first.", file=sys.stderr)
        sys.exit(1)

def create_client(first_name, last_name, email, company_name=None, phone=None):
    """
    Executes the Jobber GraphQL mutation to create a new client.
    """
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

    # Constructing the GraphQL Mutation
    mutation = """
    mutation ClientCreate($input: ClientCreateInput!) {
        clientCreate(input: $input) {
            client {
                id
                name
                firstName
                lastName
                emails {
                    address
                    primary
                }
            }
            userErrors {
                message
                path
            }
        }
    }
    """

    # Building the input payload based on provided arguments
    input_data = {
        "firstName": first_name,
        "lastName": last_name,
    }
    
    if company_name:
        input_data["companyName"] = company_name

    if email:
        input_data["emails"] = [{"address": email, "primary": True}]
        
    if phone:
        input_data["phones"] = [{"number": phone, "primary": True}]

    # Removing properties from client creation as it is a separate step
    # input_data["properties"] = [{
    #    "address": {"street1": "123 Main St", "city": "Calgary", "province": "AB", "postalCode": "T2P 1J1"}
    # }]

    payload = {
        "query": mutation,
        "variables": {
            "input": input_data
        }
    }

    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Check for GraphQL user logic errors
        errors = data.get("data", {}).get("clientCreate", {}).get("userErrors", [])
        if errors:
            print(f"GraphQL User Error: {errors}", file=sys.stderr)
            return None

        # Extract the successfully created client
        new_client = data.get("data", {}).get("clientCreate", {}).get("client")
        if not new_client:
            print(f"Failed to extract new client. Raw response: {data}", file=sys.stderr)
            return None
        return new_client

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response Body: {e.response.text}", file=sys.stderr)
        return None

if __name__ == '__main__':
    # Setting up CLI argument parsing so the tool can be called dynamically
    parser = argparse.ArgumentParser(description="Create a Client in Jobber via GraphQL.")
    parser.add_argument("--firstname", required=True, help="Client's first name")
    parser.add_argument("--lastname", required=True, help="Client's last name")
    parser.add_argument("--email", required=False, help="Client's email address")
    parser.add_argument("--company", required=False, help="Company name (optional)")
    parser.add_argument("--phone", required=False, help="Phone number (optional)")
    
    args = parser.parse_args()

    client = create_client(
        first_name=args.firstname, 
        last_name=args.lastname, 
        email=args.email, 
        company_name=args.company,
        phone=args.phone
    )

    if client:
        # Output clean JSON for easy parsing by n8n or ElevenLabs
        print(json.dumps({
            "status": "success",
            "clientId": client['id'],
            "name": client['name']
        }))
    else:
        print(json.dumps({"status": "failed"}), file=sys.stderr)
        sys.exit(1)
