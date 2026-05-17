import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:6767/api/jobber"
TOKEN = os.getenv("API_SERVER_SECRET")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def test_endpoint(name, method, endpoint, payload=None):
    print(f"Testing {name} ({method} {endpoint})...")
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=payload)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, json=payload)
        
        # We expect 200 OK for ALL scenarios due to our new design
        if response.status_code == 200:
            print(f"  [PASS] Got 200 OK: {response.json()}")
        else:
            print(f"  [FAIL] Got {response.status_code}: {response.text}")
    except Exception as e:
        print(f"  [FAIL] Connection error: {e}")

if __name__ == "__main__":
    # 1. Health Check
    test_endpoint("Check Status", "GET", "/check_status")

    # 2. Client Details (requires a search param)
    test_endpoint("Client Details", "GET", "/client_details", {"searchTerm": "Darren"})

    # 3. Create Client
    test_endpoint("Create Client", "POST", "/create_client", {
        "firstName": "Test", "lastName": "User", "email": "test@example.com"
    })

    # 4. Reactivate Lead
    test_endpoint("Reactivate Lead", "POST", "/reactivate_lead", {
        "search": "test@example.com", "title": "Test Lead", "description": "Auto-test lead"
    })

    print("\nAPI Integration Tests Complete.")
