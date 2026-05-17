import token_manager
import argparse
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def get_headers_via_manager():
    token = token_manager.get_valid_token()
    return {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

def execute_graphql(query, variables=None):
    headers = get_headers_via_manager()
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

def find_client(search_term):
    query = """
    query FindClient($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    name
                    properties {
                        id
                    }
                }
            }
        }
    }
    """
    data = execute_graphql(query, {"searchTerm": search_term})
    if not data: return None
    
    edges = data.get("data", {}).get("clients", {}).get("edges", [])
    if edges:
        client = edges[0]["node"]
        # Add a convenience field for the server to find the property
        props = client.get("properties", [])
        client["firstPropertyId"] = props[0]["id"] if props else None
        return client
    return None

def create_request(client_id, property_id, title, description):
    # Step 1: Create the Request
    request_mutation = """
    mutation CreateRequest($input: RequestCreateInput!) {
        requestCreate(input: $input) {
            request { id title requestStatus }
            userErrors { message path }
        }
    }
    """
    request_variables = {
        "input": {
            "clientId": client_id,
            "propertyId": property_id,
            "title": title
        }
    }
    
    data = execute_graphql(request_mutation, request_variables)
    if not data: return None
    
    errors = data.get("data", {}).get("requestCreate", {}).get("userErrors", [])
    if errors:
        print(f"RequestCreate Error: {errors}", file=sys.stderr)
        return None
        
    request = data["data"]["requestCreate"]["request"]
    request_id = request["id"]

    # Step 2: Add the description as a Note
    if description:
        note_mutation = """
        mutation CreateRequestNote($requestId: EncodedId!, $input: RequestCreateNoteInput!) {
            requestCreateNote(requestId: $requestId, input: $input) {
                note { id }
                userErrors { message }
            }
        }
        """
        note_variables = {
            "requestId": request_id,
            "input": {
                "message": description
            }
        }
        note_data = execute_graphql(note_mutation, note_variables)
        if note_data:
            note_errors = note_data.get("data", {}).get("requestCreateNote", {}).get("userErrors", [])
            if note_errors:
                print(f"Note Error: {note_errors}", file=sys.stderr)
    
    return request

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert an existing Jobber client back into a Lead by creating a Request.")
    parser.add_argument("--search", required=True, help="Name, email, or phone of the client")
    parser.add_argument("--title", required=True, help="Short title for the new request")
    parser.add_argument("--description", required=True, help="Details for the request")
    
    args = parser.parse_args()

    # Step 1: Find the Client
    client_node = find_client(args.search)
    if not client_node:
        print(json.dumps({"status": "error", "message": f"Client matching '{args.search}' not found."}))
        sys.exit(1)
        
    client_id = client_node["id"]
    
    # Step 2: Ensure they have a property (Requests require properties)
    property_id = client_node.get("firstPropertyId")
    if not property_id:
        print(json.dumps({"status": "error", "message": f"Client found, but has no properties. Cannot create request."}))
        sys.exit(1)
    
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
