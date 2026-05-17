import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def dump_schema():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    # Full Introspection Query
    query = """
    query {
      __schema {
        types {
          name
          kind
          description
          fields {
            name
            description
            type { name kind ofType { name kind } }
          }
          inputFields {
            name
            description
            type { name kind ofType { name kind } }
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    with open("jobber_full_schema.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    print("Schema dumped to jobber_full_schema.json")

if __name__ == "__main__":
    dump_schema()
