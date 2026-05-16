import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def load_token():
    with open("jobber_tokens.json", "r") as f:
        return json.load(f).get("access_token")

def introspect(type_name):
    token = load_token()
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

if __name__ == '__main__':
    introspect("Mutation")
    introspect("QuoteCreateInput")
