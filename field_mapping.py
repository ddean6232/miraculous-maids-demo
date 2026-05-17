import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def get_mapping():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query IntrospectRequest {
      # Input fields for creating a Request
      creationInput: __type(name: "RequestCreateInput") {
        inputFields {
          name
          description
          type {
            name
            kind
            ofType { name kind }
          }
        }
      }
      # Resulting fields on a Request object
      objectFields: __type(name: "Request") {
        fields {
          name
          description
          type {
            name
            kind
            ofType { name kind }
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    data = response.json().get("data", {})
    
    print("### 1. RequestCreateInput (Used for POST /api/jobber/reactivate_lead)")
    print("| Field Name | Type | Required? | Description |")
    print("| :--- | :--- | :--- | :--- |")
    for f in data.get("creationInput", {}).get("inputFields", []):
        is_required = "YES" if f["type"]["kind"] == "NON_NULL" else "no"
        type_name = f["type"]["name"] or f["type"]["ofType"]["name"]
        print(f"| {f['name']} | {type_name} | {is_required} | {f['description']} |")

    print("\n### 2. Request Object (Resulting Data)")
    print("| Field Name | Type | Description |")
    print("| :--- | :--- | :--- |")
    for f in data.get("objectFields", {}).get("fields", []):
        type_name = f["type"]["name"] or (f["type"]["ofType"]["name"] if f["type"]["ofType"] else "N/A")
        print(f"| {f['name']} | {type_name} | {f['description']} |")

if __name__ == '__main__':
    get_mapping()
