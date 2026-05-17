# Jobber Microservices API - Integration Guide

This API provides a unified, secure gateway to your Jobber account. It abstracts GraphQL life-cycles into simple REST endpoints, making it perfect for your automation stack (n8n and Voice Agents).

## 1. Prerequisites
- **Configuration:** Ensure your `.env` file is populated with your Jobber tokens, `API_SERVER_SECRET`, and optionally `API_PORT` (defaults to 8989).
- **Server:** Run the API server locally:
  `uv run jobber_api_server_secure.py`
- **Expose:** Expose the configured port to the internet (e.g., if using 8989):
  `tailscale funnel 8989`

## 2. API Endpoints
Endpoints require an `Authorization: Bearer <API_SERVER_SECRET>` header.

### A. Check Client Details
- **Endpoint:** `GET /api/jobber/client_details?searchTerm=...`
- **Purpose:** Returns a list of matching clients and their property information.

### B. Create a New Client
- **Endpoint:** `POST /api/jobber/create_client`
- **Body:** `{"firstName": "...", "lastName": "...", "email": "..."}`

### C. Generate a Quote
- **Endpoint:** `POST /api/jobber/create_quote`
- **Body:** `{"clientSearch": "Name", "quoteTitle": "...", "services": [{"name": "Labor", "price": 100.0}]}`

### D. Spawn a Direct Job
- **Endpoint:** `POST /api/jobber/create_job`
- **Body:** `{"clientSearch": "Name", "jobTitle": "...", "serviceName": "...", "price": 100.0}`

### E. Schedule Visit
- **Endpoint:** `POST /api/jobber/schedule_visit`
- **Body:** `{"jobId": "...", "visitTitle": "...", "startDate": "YYYY-MM-DD", ...}`

### F. Health Check
- **Endpoint:** `GET /api/jobber/check_status`
- **Purpose:** Diagnostic. Verifies if the server is up and if the Jobber OAuth tokens are still valid.

---

## 3. Automated Regression Testing

We have built a dedicated test suite to ensure the system is operational. It runs through the full creation lifecycle (Client -> Quote -> Job) and then executes a **self-cleaning tear-down**.

1. **Run the test suite:**
   ```bash
   uv run integration_test_suite.py
   ```
2. **Result Monitoring:** The script initializes the process, lists PASS/FAIL for each step, performs a cleanup using `jobber_delete_tool.py`, and prints a final summary report. 

This is the standard for your "Sanity Check" before pushing any changes to GitHub.
