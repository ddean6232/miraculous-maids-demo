import json
import requests
import sys

TOKEN_FILE = "jobber_tokens.json"
# Note: In production, these should be environment variables.
CLIENT_ID = "REDACTED_BY_SECURITY_PROTOCOL"
CLIENT_SECRET = "REDACTED_BY_SECURITY_PROTOCOL"

def get_valid_token():
    """Reads refresh token and gets a fresh access token."""
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
            
        url = "https://api.getjobber.com/api/oauth/token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"]
        }
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        new_tokens = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_tokens, f, indent=4)
            
        return new_tokens["access_token"]
    except Exception as e:
        print(f"Token refresh failed: {e}", file=sys.stderr)
        raise Exception("Jobber authentication invalid.")
