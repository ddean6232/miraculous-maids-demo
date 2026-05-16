import requests

PAT = "REDACTED_BY_SECURITY_PROTOCOL"
HEADERS = {"Authorization": f"Bearer {PAT}"}

print("Fetching all deals to see what's in the account...")

url = "https://api.hubapi.com/crm/v3/objects/deals?properties=dealstage,dealname"
response = requests.get(url, headers=HEADERS)

if response.status_code == 200:
    deals = response.json().get('results', [])
    print(f"Found {len(deals)} deals in total:")
    for deal in deals:
        print(f"- {deal['properties']['dealname']} (Stage: {deal['properties']['dealstage']})")
else:
    print(f"Error {response.status_code}: {response.text}")
