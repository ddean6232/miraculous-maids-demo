import requests
import json
import os

# Standard headers required by Jobber
JOBBER_TOKEN = os.getenv("JOBBER_CLIENT_ID")
URL = "https://api.getjobber.com/api/graphql"
HEADERS = {
    'Authorization': f'Bearer {JOBBER_TOKEN}',
    'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
    'Content-Type': 'application/json'
}

def search_client(search_term):
    """
    Query Jobber for a client by name or keyword.
    """
    payload = {
        "query": """
            query CheckExistingClient($searchTerm: String!) {
                clients(first: 20, searchTerm: $searchTerm) {
                    edges {
                        node {
                            id
                            firstName
                            lastName
                            billingAddress {
                                street1
                                city
                            }
                        }
                    }
                }
            }
        """,
        "variables": {
            "searchTerm": search_term
        }
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Safely parse the nested GraphQL edges structure
        edges = data.get('data', {}).get('clients', {}).get('edges', [])
        clients = [edge['node'] for edge in edges]
        
        return clients

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if response.text:
            print(f"Details: {response.text}")
        return None

if __name__ == '__main__':
    # Test the client search just like your cURL command
    term = "John Doe"
    print(f"Searching for Client: '{term}'...")
    results = search_client(term)
    
    if results:
        print(f"Found {len(results)} matches:")
        print(json.dumps(results, indent=2))
    else:
        print("No matches found or an error occurred.")