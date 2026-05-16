import argparse
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def load_token():
    try:
        with open("jobber_tokens.json", "r") as f:
            return json.load(f).get("access_token")
    except FileNotFoundError:
        print("Error: jobber_tokens.json not found.", file=sys.stderr)
        sys.exit(1)

def create_job(property_id, title, line_item_name, unit_price):
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

    mutation = """
    mutation CreateJob($input: JobCreateInput!) {
        jobCreate(input: $input) {
            job {
                id
                jobNumber
                jobStatus
            }
            userErrors {
                message
                path
            }
        }
    }
    """

    variables = {
        "input": {
            "propertyId": property_id,
            "title": title,
            "invoicing": {
                "invoicingType": "FIXED_PRICE",
                "invoicingSchedule": "ON_COMPLETION"
            },
            "lineItems": [
                {
                    "name": line_item_name,
                    "quantity": 1,
                    "unitPrice": float(unit_price),
                    "saveToProductsAndServices": False
                }
            ]
        }
    }

    try:
        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": variables})
        response.raise_for_status()
        data = response.json()
        
        errors = data.get("data", {}).get("jobCreate", {}).get("userErrors", [])
        if errors:
            print(f"GraphQL User Error: {errors}", file=sys.stderr)
            return None

        return data.get("data", {}).get("jobCreate", {}).get("job")

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a Job in Jobber.")
    parser.add_argument("--property_id", required=True, help="The Jobber Property ID (e.g. Z2lkOi...)")
    parser.add_argument("--title", required=True, help="Job title / Deal Name")
    parser.add_argument("--item_name", required=True, help="Line item service description")
    parser.add_argument("--price", required=True, help="Unit price/amount")
    
    args = parser.parse_args()

    job = create_job(args.property_id, args.title, args.item_name, args.price)
    
    if job:
        print(json.dumps({"status": "success", "job_id": job['id'], "job_number": job['jobNumber']}))
    else:
        print(json.dumps({"status": "failed"}), file=sys.stderr)
        sys.exit(1)