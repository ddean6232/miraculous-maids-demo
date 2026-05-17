import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def introspect_form():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query {
      __type(name: "FormInput") {
        inputFields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    introspect_form()
