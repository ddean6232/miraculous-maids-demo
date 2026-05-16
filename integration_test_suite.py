import requests
import json
import time

# --- Setup ---
BASE_URL = "http://localhost:8989"
SECRET = "a-very-long-and-secure-base64-string" # Must match .env
HEADERS = {"Authorization": f"Bearer {SECRET}", "Content-Type": "application/json"}

def run_test(name, task_fn):
    print(f"\n>>> Running Test: {name}")
    result = task_fn()
    print(json.dumps(result, indent=2))
    return result

# --- Workflow Tests ---
def test_workflow():
    # 1. Create Client
    client = run_test("Create Client", lambda: requests.post(f"{BASE_URL}/api/jobber/create_client", headers=HEADERS, json={
        "firstName": "Integration", "lastName": "Tester", "email": "tester@dtreeind.com"
    }).json())
    
    if client.get("status") != "success": return
    client_id = client["clientId"]

    # 2. Create Quote
    quote = run_test("Create Quote", lambda: requests.post(f"{BASE_URL}/api/jobber/create_quote", headers=HEADERS, json={
        "clientSearch": "Integration Tester",
        "quoteTitle": "Regression Test Quote",
        "services": [{"name": "Standard Labor", "price": 100.0, "quantity": 1}]
    }).json())
    
    if quote.get("status") != "success": return
    quote_id = quote["quoteId"]

    # 3. Create Job
    job = run_test("Create Job", lambda: requests.post(f"{BASE_URL}/api/jobber/create_job", headers=HEADERS, json={
        "clientSearch": "Integration Tester",
        "jobTitle": "Regression Job",
        "serviceName": "Standard Labor",
        "price": 100.0
    }).json())
    
    if job.get("status") != "success": return
    job_id = job["jobId"]

    # 4. Schedule Visit
    visit = run_test("Schedule Visit", lambda: requests.post(f"{BASE_URL}/api/jobber/schedule_visit", headers=HEADERS, json={
        "jobId": job_id,
        "visitTitle": "System Test Visit",
        "startDate": "2026-06-01", "startTime": "09:00:00",
        "endDate": "2026-06-01", "endTime": "10:00:00"
    }).json())

    # 5. Tear Down / Delete (Add these endpoints to your server if needed)
    print("\n>>> TEAR DOWN: Run manually when ready.")

if __name__ == "__main__":
    test_workflow()
