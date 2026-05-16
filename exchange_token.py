import requests
import json

CODE = "REDACTED_BY_SECURITY_PROTOCOL"
CLIENT_ID = "REDACTED_BY_SECURITY_PROTOCOL"
CLIENT_SECRET = "REDACTED_BY_SECURITY_PROTOCOL"
REDIRECT_URI = "https://n8nio.dtreeind.com/webhook-test/jobber-oauth-callback"

url = "https://api.getjobber.com/api/oauth/token"
payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(url, data=payload)
if response.status_code == 200:
    tokens = response.json()
    with open("jobber_tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)
    print("SUCCESS: Tokens refreshed with all scopes from Jobber Dashboard.")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)
