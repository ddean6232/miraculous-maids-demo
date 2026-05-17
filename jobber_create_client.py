import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def create_client(first_name, last_name, email, company_name=None, phone=None):
    """
    Executes the Jobber GraphQL mutation to create a new client.
    """
    try:
        token = token_manager.get_valid_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
            'Content-Type': 'application/json'
        }

        mutation = """
        mutation ClientCreate($input: ClientCreateInput!) {
            clientCreate(input: $input) {
                client { id name firstName lastName emails { address primary } }
                userErrors { message path }
            }
        }
        """

        input_data = {"firstName": first_name, "lastName": last_name}
        if company_name: input_data["companyName"] = company_name
        if email: input_data["emails"] = [{"address": email, "primary": True}]
        if phone: input_data["phones"] = [{"number": phone, "primary": True}]

        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": {"input": input_data}})
        response.raise_for_status()
        data = response.json()
        
        errors = data.get("data", {}).get("clientCreate", {}).get("userErrors", [])
        if errors:
            print(f"GraphQL User Error: {errors}", file=sys.stderr)
            return None

        return data.get("data", {}).get("clientCreate", {}).get("client")

    except Exception as e:
        print(f"Error in create_client: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--firstname", required=True)
    parser.add_argument("--lastname", required=True)
    parser.add_argument("--email")
    parser.add_argument("--company")
    parser.add_argument("--phone")
    args = parser.parse_args()

    client = create_client(args.firstname, args.lastname, args.email, args.company, args.phone)
    if client:
        print(json.dumps({"status": "success", "clientId": client['id'], "name": client['name']}))
    else:
        print(json.dumps({"status": "failed"}), file=sys.stderr)
        sys.exit(1)
