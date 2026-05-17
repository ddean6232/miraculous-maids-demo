import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def check_note_mutation():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query {
      __type(name: "Mutation") {
        fields {
          name
          args {
            name
            type {
              name
              kind
              ofType { name kind }
            }
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    data = response.json()
    fields = data.get("data", {}).get("__type", {}).get("fields", [])
    for f in fields:
        if f['name'] == 'requestCreateNote':
            print(json.dumps(f, indent=2))

if __name__ == '__main__':
    check_note_mutation()
