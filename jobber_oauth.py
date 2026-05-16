import os
import requests
import json
from flask import Flask, request, redirect

app = Flask(__name__)

# Jobber OAuth 2.0 Endpoints
AUTH_URL = "https://api.getjobber.com/api/oauth/authorize"
TOKEN_URL = "https://api.getjobber.com/api/oauth/token"

# These need to come from your Jobber Developer Dashboard
CLIENT_ID = os.getenv("JOBBER_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
# This must match EXACTLY what you put in the Jobber Developer Dashboard
REDIRECT_URI = "http://localhost:5000/callback" 

TOKEN_FILE = "jobber_tokens.json"

@app.route("/")
def home():
    # Step 1: Redirect user to Jobber to approve the app
    # Adding necessary Jobber scopes and restoring the explicit redirect_uri to prevent Access Denied errors
    scopes = "read_clients write_clients read_jobs write_jobs read_quotes write_quotes"
    auth_uri = f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scopes}"
    return f'''
        <h1>Jobber OAuth Setup</h1>
        <p><a href="{auth_uri}">Click here to Authorize with Jobber</a></p>
    '''

@app.route("/callback")
def callback():
    # Step 2: Jobber redirects back here with an authorization code
    code = request.args.get("code")
    if not code:
        return "Error: No code provided by Jobber.", 400

    # Step 3: Exchange the authorization code for access & refresh tokens
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        tokens = response.json()
        
        # Save tokens securely to a local file
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=4)
            
        return f'''
            <h1>Success!</h1>
            <p>Tokens successfully retrieved and saved to <code>{TOKEN_FILE}</code>.</p>
            <p>You can close this window and return to your terminal.</p>
        '''
    except requests.exceptions.RequestException as e:
        error_details = "Check the console for details."
        return f"<h1>Failed to get tokens</h1><p>{e}</p><p>{error_details}</p>", 400

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("Starting Jobber OAuth Server...")
    print("Go to http://localhost:5000 in your browser to begin.")
    print("--------------------------------------------------")
    app.run(host="localhost", port=5000)
