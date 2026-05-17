import token_manager
import requests
import json

URL = "https://api.getjobber.com/api/graphql"

def find_details_field():
    token = token_manager.get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    
    query = """
    query {
      __schema {
        types {
          name
          kind
          fields {
            name
            description
          }
          inputFields {
            name
            description
          }
        }
      }
    }
    """
    
    response = requests.post(URL, headers=headers, json={"query": query})
    data = response.json()
    types = data.get("data", {}).get("__schema", {}).get("types", [])
    
    for t in types:
        if t['name'] in ["Request", "RequestCreateInput", "RequestDetailsInput", "AssessmentCreateInput"]:
            print(f"--- Type: {t['name']} ---")
            for f in t.get("fields") or []:
                if "detail" in f['name'].lower() or "service" in f['name'].lower() or (f['description'] and "detail" in f['description'].lower()):
                    print(f"  Field: {f['name']} - {f['description']}")
            for f in t.get("inputFields") or []:
                if "detail" in f['name'].lower() or "service" in f['name'].lower() or (f['description'] and "detail" in f['description'].lower()):
                    print(f"  Input: {f['name']} - {f['description']}")

if __name__ == '__main__':
    find_details_field()
