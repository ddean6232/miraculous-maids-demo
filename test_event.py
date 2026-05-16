import requests
import json

PAT = "REDACTED_BY_SECURITY_PROTOCOL"
HEADERS = {"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"}

print("Querying deals modified in the last 24 hours...")

# Use the search endpoint to find recently updated deals
url = "https://api.hubapi.com/crm/v3/objects/deals/search"
payload = {
    "filterGroups": [
        {
            "filters": [
                {
                    "propertyName": "hs_lastmodifieddate",
                    "operator": "GTE",
                    "value": "1747267200000" 
                }
            ]
        }
    ],
    "properties": ["dealstage", "dealname", "hs_lastmodifieddate"]
}

response = requests.post(url, headers=HEADERS, json=payload)
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data.get('results', []))} recently modified deals:")
    for deal in data.get('results', []):
        print(f"Deal: {deal['properties']['dealname']} | Stage: {deal['properties']['dealstage']} | Last Modified: {deal['properties']['hs_lastmodifieddate']}")
else:
    print(f"Error {response.status_code}: {response.text}")
