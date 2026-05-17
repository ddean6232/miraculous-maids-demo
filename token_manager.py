import os
import requests
import sys
import json
from dotenv import load_dotenv, set_key

# Load credentials from .env
ENV_PATH = "/Users/darren_dean/projects/miraculous-maids-demo/.env"
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv("JOBBER_CLIENT_ID")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET")
# We store the CURRENT valid access token and refresh token in .env
ACCESS_TOKEN = os.getenv("JOBBER_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("JOBBER_REFRESH_TOKEN")

def refresh_tokens():
    """Exchanges the refresh token for a brand new pair and updates .env"""
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    url = "https://api.getjobber.com/api/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        data = response.json()
        new_access = data.get("access_token")
        new_refresh = data.get("refresh_token")
        
        # Update current session
        ACCESS_TOKEN = new_access
        REFRESH_TOKEN = new_refresh
        
        # PERSIST to .env file programmatically
        set_key(ENV_PATH, "JOBBER_ACCESS_TOKEN", new_access)
        set_key(ENV_PATH, "JOBBER_REFRESH_TOKEN", new_refresh)
        
        return new_access
    else:
        print(f"Refresh failed: {response.text}", file=sys.stderr)
        return None

def get_valid_token():
    """Validates the existing access token; refreshes if expired."""
    if not ACCESS_TOKEN:
        return refresh_tokens()

    # Fast validation: Hit the Jobber 'me' or simpler endpoint to check token health
    url = "https://api.getjobber.com/api/graphql"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }
    payload = {"query": "{ apiEventHistory(first: 1) { nodes { id } } }"}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        # If we get a 401, the token is expired - trigger refresh
        if response.status_code == 401:
            print("Access token expired. Refreshing...", file=sys.stderr)
            return refresh_tokens()
        
        response.raise_for_status()
        return ACCESS_TOKEN
    except Exception:
        return refresh_tokens()
