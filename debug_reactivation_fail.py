import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def debug_client(search_term):
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query FindClient($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    name
                    isArchived
                    isLead
                    properties {
                        id
                        address { street }
                    }
                    invoices(first: 10) {
                        edges {
                            node {
                                id
                                issuedDate
                                invoiceStatus
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query, "variables": {"searchTerm": search_term}})
    data = response.json()
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    debug_client("ddean@dtreeind.com")
