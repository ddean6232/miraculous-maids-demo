import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def load_token():
    with open("jobber_tokens.json", "r") as f:
        return json.load(f).get("access_token")

def introspect(type_name):
    headers = {
        'Authorization': f'Bearer {load_token()}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

    query = """
    query IntrospectType($name: String!) {
        __type(name: $name) {
            name
            inputFields {
                name
                type {
                    name
                    kind
                    ofType { name }
                }
            }
            fields {
                name
                type {
                    name
                    kind
                    ofType { name }
                }
            }
        }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query, "variables": {"name": type_name}})
    if response.status_code == 200:
        data = response.json()
        obj_type = data.get("data", {}).get("__type")
        if obj_type:
            print(f"\n--- {type_name} ---")
            if obj_type.get("inputFields"):
                for f in obj_type["inputFields"]:
                    print(f"  Input: {f['name']} -> {f['type']}")
            if obj_type.get("fields"):
                for f in obj_type["fields"]:
                    print(f"  Field: {f['name']} -> {f['type']}")

introspect("QuoteCreateAttributes")
introspect("Quote")
