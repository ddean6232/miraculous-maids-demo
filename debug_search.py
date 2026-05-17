import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def debug_client_search(search_term):
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
                        name
                        properties {
                            id
                            address { street }
                        }
                        clientProperties {
                            nodes {
                                id
                                address { street }
                            }
                        }
                    }
                }
            }
        }
        """
        
        print(f"Searching for: {search_term}")
        response = requests.post(URL, headers=headers, json={"query": query, "variables": {"searchTerm": search_term}})
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print("Response Data:")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    term = sys.argv[1] if len(sys.argv) > 1 else "Darren Dean"
    debug_client_search(term)
