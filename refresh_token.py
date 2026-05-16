import requests
import json
import traceback

CLIENT_ID = "REDACTED_BY_SECURITY_PROTOCOL"
CLIENT_SECRET = "REDACTED_BY_SECURITY_PROTOCOL"

try:
    with open("jobber_tokens.json", "r") as f:
        tokens = json.load(f)
        refresh_token = tokens.get("refresh_token")
        
    url = "https://api.getjobber.com/api/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        with open("jobber_tokens.json", "w") as f:
            json.dump(new_tokens, f, indent=4)
        print("SUCCESS: Token refreshed!")
    else:
        print(f"FAILED to refresh: {response.status_code}")
        print(response.text)
except Exception as e:
    print("Error during refresh:", e)
    traceback.print_exc()
