import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

from dotenv import load_dotenv

load_dotenv()

# Replace with your actual Private App Access Token or OAuth token
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

HEADERS = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}

def fetch_hubspot_deal_details(deal_id):
    """Fetches deal full info + associated contact info."""
    # 1. Fetch Deal
    deal_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}?associations=contacts&properties=dealname,amount,closedate"
    response = requests.get(deal_url, headers=HEADERS)
    deal_data = response.json()
    
    # 2. Get Contact ID (we assume the first associated contact is the primary)
    try:
        contact_id = deal_data['associations']['contacts']['results'][0]['id']
        # 3. Fetch Contact
        contact_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}?properties=firstname,lastname,email,phone,address"
        contact_res = requests.get(contact_url, headers=HEADERS)
        contact_data = contact_res.json()
        
        return {
            "deal": deal_data['properties'],
            "contact": contact_data['properties']
        }
    except Exception as e:
        print(f"[!] Error fetching associated contact: {e}")
        return None

def create_jobber_client_and_job(deal_id):
    print(f"\n[JOBBER] 🚀 Triggering for Deal: {deal_id}")
    data = fetch_hubspot_deal_details(deal_id)
    
    if data:
        print(f"[JOBBER] Full Payload Collected:")
        print(f"    Client: {data['contact'].get('firstname')} {data['contact'].get('lastname')}")
        print(f"    Service/Deal: {data['deal'].get('dealname')}")
        print(f"    Amount: ${data['deal'].get('amount')}")
        print("[JOBBER] (Placeholder) Ready to send to Jobber API...")
    else:
        print("[JOBBER] Error: Could not retrieve full Deal/Contact data.")

@app.route('/hubspot-webhook', methods=['POST'])
def hubspot_webhook():
    events = request.json
    if not events: return jsonify({"status": "error"}), 400
    
    for event in events:
        if event.get('subscriptionType') == 'deal.propertyChange':
            if event.get('propertyName') == 'dealstage' and event.get('propertyValue') == 'closedwon':
                create_jobber_client_and_job(event.get('objectId'))

if __name__ == '__main__':
    print("Starting Miraculous Maids local integration server...")
    print("Listening for HubSpot Webhooks on port 5000...")
    app.run(host='0.0.0.0', port=5000)

