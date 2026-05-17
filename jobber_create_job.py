import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def create_job(property_id, title, service_name, price):
    try:
        token = token_manager.get_valid_token()
        headers = {'Authorization': f'Bearer {token}', 'X-JOBBER-GRAPHQL-VERSION': '2025-04-16', 'Content-Type': 'application/json'}
        mutation = """
        mutation CreateJob($input: JobCreateAttributes!) {
            jobCreate(input: $input) {
                job { id jobNumber jobStatus }
                userErrors { message path }
            }
        }
        """
        variables = {"input": {
            "propertyId": property_id, "title": title,
            "invoicing": {"invoicingType": "FIXED_PRICE", "invoicingSchedule": "ON_COMPLETION"},
            "lineItems": [{"name": service_name, "quantity": 1, "unitPrice": float(price)}]
        }}
        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": variables})
        data = response.json()
        if "errors" in data:
            error_msg = "; ".join([e.get("message", "Unknown GraphQL error") for e in data["errors"]])
            print(f"GraphQL Error: {error_msg}", file=sys.stderr)
            return {"status": "error", "message": error_msg}
            
        job_create = data.get("data", {}).get("jobCreate", {})
        errors = job_create.get("userErrors", [])
        if errors:
            error_msg = "; ".join([e.get("message", "Unknown error") for e in errors])
            print(f"Job User Error: {error_msg}", file=sys.stderr)
            return {"status": "error", "message": error_msg}
            
        return {"status": "success", "job": job_create.get("job")}
    except Exception as e:
        print(f"Error creating job: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--property_id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--item_name", required=True)
    parser.add_argument("--price", required=True)
    args = parser.parse_args()
    job = create_job(args.property_id, args.title, args.item_name, args.price)
    if job: print(json.dumps({"status": "success", "job_id": job['id'], "job_number": job['jobNumber']}))
    else: sys.exit(1)
