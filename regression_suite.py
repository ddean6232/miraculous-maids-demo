import requests
import json
import sys

# --- Setup ---
BASE_URL = "http://localhost:8989"
SECRET = "a-very-long-and-secure-base64-string"
HEADERS = {"Authorization": f"Bearer {SECRET}", "Content-Type": "application/json"}
JOB_DELETE_TOOL = "/Users/darren_dean/projects/miraculous-maids-demo/jobber_delete_tool.py"

def call_api(endpoint, data):
    return requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, json=data).json()

def run_suite():
    results = {"created": [], "errors": []}
    
    print("--- Starting Regression Suite ---")
    
    # 1. Create Client
    client = call_api("/api/jobber/create_client", {"firstName": "Test", "lastName": "Runner", "email": "test@dtreeind.com"})
    if client.get("status") == "success":
        results["created"].append({"type": "client", "id": client["clientId"]})
        print(f"PASS: Client created ({client['clientId']})")
    else:
        results["errors"].append(f"Client creation failed: {client}")
        print("FAIL: Client creation")

    # 2. Create Quote
    quote = call_api("/api/jobber/create_quote", {
        "clientSearch": "Test Runner",
        "quoteTitle": "Automated Test Quote",
        "services": [{"name": "Standard Labor", "price": 50.0, "quantity": 1}]
    })
    
    if quote.get("status") == "success":
        results["created"].append({"type": "quote", "id": quote["quoteId"]})
        print(f"PASS: Quote created ({quote['quoteId']})")
    else:
        results["errors"].append(f"Quote creation failed: {quote}")
        print("FAIL: Quote creation")
        
    # --- TEARDOWN ---
    print("\n--- Starting Teardown ---")
    import subprocess
    
    # Delete Clients/Jobs created
    for item in results["created"]:
        if item["type"] == "client":
            subprocess.run(["python3", JOB_DELETE_TOOL, "client", "--id", item["id"]])
            print(f"Cleaned up Client: {item['id']}")
            
    print("\n--- TEST SUMMARY ---")
    if not results["errors"]:
        print("ALL TESTS PASSED & CLEANED.")
    else:
        print(f"TESTS FINISHED WITH ERRORS: {results['errors']}")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
