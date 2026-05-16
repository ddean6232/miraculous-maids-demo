import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def load_token():
    with open("jobber_tokens.json", "r") as f:
        return json.load(f).get("access_token")

def introspect_quote():
    token = load_token()
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
                        ofType { name }
                    }
                }
                type {
                    name
                }
            }
        }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    if response.status_code == 200:
        data = response.json()
        fields = data.get("data", {}).get("__type", {}).get("fields", [])
        
        # Find the quoteCreate mutation
        for f in fields:
            if f["name"] == "quoteCreate":
                print("--- quoteCreate Arguments ---")
                for arg in f["args"]:
                    print(f'{arg["name"]}: {arg["type"]}')
                print(f"Returns: {f['type']['name']}")
                
        # Find the ClientHub type to see if it has URLs
        print("\n--- Introspecting QuoteCreatePayload ---")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == '__main__':
    introspect_quote()
