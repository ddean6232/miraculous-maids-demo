import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def get_latest_request():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query {
      requests(first: 1) {
        edges {
          node {
            id
            title
            assessment {
              instructions
            }
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    get_latest_request()
