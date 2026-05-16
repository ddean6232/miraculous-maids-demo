import requests
import time
import os

# Your tokens
HUBSPOT_PAT = "REDACTED_BY_SECURITY_PROTOCOL"
# Replace with your actual Jobber API token
JOBBER_API_TOKEN = os.getenv("JOBBER_API_TOKEN", "YOUR_JOBBER_TOKEN") 

def get_closed_won_deals():
    # Fetch deals where stage is 'closedwon'
    # Note: 'closedwon' is the default ID; please verify your stage ID in HS settings
    url = "https://api.hubapi.com/crm/v3/objects/deals?properties=dealstage,dealname,amount&filterGroups=%5B%7B%22filters%22%3A%5B%7B%22propertyName%22%3A%22dealstage%22%2C%22operator%22%3A%22EQ%22%2C%22value%22%3A%22closedwon%22%7D%5D%7D%5D"
    headers = {"Authorization": f"Bearer {HUBSPOT_PAT}"}
    response = requests.get(url, headers=headers)
    return response.json().get('results', [])

def process_sync():
    print("Checking for new Closed Won deals...")
    deals = get_closed_won_deals()
    for deal in deals:
        print(f"Found Deal: {deal['properties']['dealname']} - Triggering Jobber sync...")
        # IMPLEMENT JOBBER SYNC HERE
    time.sleep(60) # Poll every minute

if __name__ == "__main__":
    while True:
        process_sync()
