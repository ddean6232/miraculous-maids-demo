import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def get_client_details(search_term):
    """
    Search for a client and return their basic info and all properties.
    """
    try:
        token = token_manager.get_valid_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
            'Content-Type': 'application/json'
        }
        
        query = """
        query GetClientDetails($searchTerm: String!) {
            clients(first: 5, searchTerm: $searchTerm) {
                edges {
                    node {
                        id
                        firstName
                        lastName
                        name
                        email
                        phone
                        properties {
                            id
                            address {
                                street
                                city
                                province
                                postalCode
                            }
                        }
                    }
                }
            }
        }
        """
        
        response = requests.post(URL, headers=headers, json={"query": query, "variables": {"searchTerm": search_term}})
        response.raise_for_status()
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            print(f"GraphQL Errors: {data['errors']}", file=sys.stderr)
            return None

        edges = data.get("data", {}).get("clients", {}).get("edges", [])
        if not edges:
            return None
            
        clients = []
        for edge in edges:
            node = edge["node"]
            properties = []
            for prop in node.get("properties", []):
                properties.append({
                    "id": prop["id"],
                    "address": prop.get("address", {})
                })
            
            clients.append({
                "id": node["id"],
                "firstName": node["firstName"],
                "lastName": node["lastName"],
                "name": node["name"],
                "email": node["email"],
                "phone": node["phone"],
                "properties": properties
            })
            
        return clients
        
    except Exception as e:
        print(f"Error fetching client details: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python jobber_get_client_details.py <search_term>")
        sys.exit(1)
        
    search_term = sys.argv[1]
    details = get_client_details(search_term)
    if details:
        print(json.dumps(details, indent=2))
    else:
        print("No client found.")
