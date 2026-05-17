import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def introspect(type_name):
    try:
        token = token_manager.get_valid_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
            'Content-Type': 'application/json'
        }

        query = """
        query IntrospectType($name: String!) {
            __type(name: $name) {
                name
                fields {
                    name
                    type {
                        name
                        kind
                        ofType { name kind }
                    }
                }
                inputFields {
                    name
                    type {
                        name
                        kind
                        ofType { name kind }
                    }
                }
            }
        }
        """
        
        response = requests.post(URL, headers=headers, json={"query": query, "variables": {"name": type_name}})
        if response.status_code == 200:
            data = response.json()
            print(f"--- Introspection for {type_name} ---")
            obj_type = data.get("data", {}).get("__type")
            if not obj_type:
                 print(f"Type {type_name} not found in schema.")
                 return
                 
            if obj_type.get("inputFields"):
                 print("Input Fields:")
                 for f in obj_type["inputFields"]:
                      print(f"  - {f['name']}: {f['type']}")
            
            if obj_type.get("fields"):
                 print("Fields:")
                 for f in obj_type["fields"]:
                      print(f"  - {f['name']}: {f['type']}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Introspection failed: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        introspect(sys.argv[1])
    else:
        introspect("Mutation")
        introspect("QuoteCreateAttributes")
