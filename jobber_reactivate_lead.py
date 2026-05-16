import argparse
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def get_headers():
    try:
        with open("jobber_tokens.json", "r") as f:
            token = json.load(f).get("access_token")
            return {
                'Authorization': f'Bearer {token}',
                'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
                'Content-Type': 'application/json'
            }
    except FileNotFoundError:
        print("Error: jobber_tokens.json not found.", file=sys.stderr)
        sys.exit(1)

def execute_graphql(query, variables=None):
    headers = get_headers()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    if "errors" in data:
        print(f"GraphQL Execution Error: {data['errors']}", file=sys.stderr)
        return None
        
    return data

def find_client(name):
    query = """
    query FindClient($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    defaultProperty {
                        id
                    }
                }
            }
        }
    }
    """
    data = execute_graphql(query, {"searchTerm": name})
    if not data: return None
    
    edges = data.get("data", {}).get("clients", {}).get("edges", [])
    if edges:
        return edges[0]["node"]
    return None

def create_request(client_id, property_id, title, description):
    mutation = """
    mutation CreateRequest($input: RequestCreateInput!) {
        requestCreate(input: $input) {
            request {
                id
                title
                requestStatus
            }
            userErrors {
                message
                path
            }
        }
    }
    """
    variables = {
        "input": {
            "clientId": client_id,
            "propertyId": property_id,
            "title": title,
            "description": description
        }
    }
    
    data = execute_graphql(mutation, variables)
    if not data: return None
    
    errors = data.get("data", {}).get("requestCreate", {}).get("userErrors", [])
    if errors:
        print(f"RequestCreate Error: {errors}", file=sys.stderr)
        return None
        
    return data["data"]["requestCreate"]["request"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert an existing Jobber client back into a Lead by creating a Request.")
    parser.add_argument("--client_name", required=True, help="Full name of the client to search for")
    parser.add_argument("--title", required=True, help="Short title for the new request (e.g., 'Spring Cleaning Inquiry')")
    parser.add_argument("--description", required=True, help="Details captured by the Voice Agent")
    
    args = parser.parse_args()

    # Step 1: Find the Client
    client_node = find_client(args.client_name)
    if not client_node:
        print(json.dumps({"status": "error", "message": f"Client '{args.client_name}' not found."}))
        sys.exit(1)
        
    client_id = client_node["id"]
    
    # Step 2: Ensure they have a property (Requests require properties)
    default_prop = client_node.get("defaultProperty")
    if not default_prop:
        # Note: robust implementation would create a property here if missing
        print(json.dumps({"status": "error", "message": f"Client found, but has no default property. Cannot create request."}))
        sys.exit(1)
        
    property_id = default_prop["id"]
    
    # Step 3: Create the Request
    request_data = create_request(client_id, property_id, args.title, args.description)
    
    if request_data:
        print(json.dumps({
            "status": "success",
            "client_id": client_id,
            "request_id": request_data["id"],
            "request_status": request_data["requestStatus"],
            "message": "Lead reactivated via new Request."
        }))
    else:
        print(json.dumps({"status": "error", "message": "Failed to create Request."}))
        sys.exit(1)
