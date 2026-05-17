import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def exhaust_introspect(type_name):
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
            inputFields {
                name
                description
                type {
                    name
                    kind
                }
            }
        }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query, "variables": {"name": type_name}})
    data = response.json()
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    exhaust_introspect("RequestCreateInput")
