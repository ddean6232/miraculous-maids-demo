import requests
import json

with open("jobber_tokens.json", "r") as f:
    tokens = json.load(f)
    ACCESS_TOKEN = tokens.get("access_token")

URL = "https://api.getjobber.com/api/graphql"
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
    'Content-Type': 'application/json'
}

payload = {
    "query": """
        query CheckExistingClient {
            clients(first: 20, searchTerm: "John Doe") {
                edges {
                    node {
                        id
                        firstName
                        lastName
                    }
                }
            }
        }
    """
}

print("Testing Jobber GraphQL API...")
response = requests.post(URL, headers=HEADERS, json=payload)
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
