import token_manager
import argparse
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def get_headers_via_manager():
    try:
        token = token_manager.get_valid_token()
            return {
                'Authorization': f'Bearer {token}',
                'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
                'Content-Type': 'application/json'
            }
    except FileNotFoundError:
        print("Error: jobber_tokens.json not found.", file=sys.stderr)
        sys.exit(1)

def execute_graphql(query, variables=None):
    headers = get_headers_via_manager()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    if "errors" in data:
        print(f"GraphQL Execution Error: {data['errors']}", file=sys.stderr)
        return None
        
    return data

def find_client_and_property(name_or_email):
    """
    Search for a client and cleanly extract their default property.
    We need the property ID to create the Job.
    """
    query = """
    query FindClientProperty($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    defaultProperty {
                        id
                        address {
                            street1
                            city
                        }
                    }
                }
            }
        }
    }
    """
    data = execute_graphql(query, {"searchTerm": name_or_email})
    if not data: return None, None
    
    edges = data.get("data", {}).get("clients", {}).get("edges", [])
    if edges:
        client = edges[0]["node"]
        property_id = client.get("defaultProperty", {}).get("id") if client.get("defaultProperty") else None
        return client, property_id
    return None, None

def create_job_for_property(property_id, title, service_name, price):
    """
    Creates a direct Job mapped to the provided Property.
    """
    mutation = """
    mutation CreateDirectJob($input: JobCreateInput!) {
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
                    "name": service_name,
                    "quantity": 1,
                    "unitPrice": float(price),
                    "saveToProductsAndServices": False
                }
            ]
        }
    }
    
    data = execute_graphql(mutation, variables)
    if not data: return None
    
    errors = data.get("data", {}).get("jobCreate", {}).get("userErrors", [])
    if errors:
        print(f"JobCreate Error: {errors}", file=sys.stderr)
        return None
        
    return data["data"]["jobCreate"]["job"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Spawn a Job instantly for an existing Client.")
    parser.add_argument("--client_search", required=True, help="Name or email of the existing client")
    parser.add_argument("--job_title", required=True, help="Title of the job (e.g. 'Monthly Clean')")
    parser.add_argument("--service", required=True, help="Line item description")
    parser.add_argument("--price", required=True, help="Price of the service")
    
    args = parser.parse_args()

    # Step 1: Lookup Client and Property
    client, property_id = find_client_and_property(args.client_search)
    
    if not client:
        print(json.dumps({"status": "error", "message": f"Client matching '{args.client_search}' not found."}))
        sys.exit(1)
        
    if not property_id:
        print(json.dumps({"status": "error", "message": f"Client {client['firstName']} found, but has no Property to attach a job to."}))
        sys.exit(1)
        
    # Step 2: Spawn Job
    job = create_job_for_property(property_id, args.job_title, args.service, args.price)
    
    if job:
        print(json.dumps({
            "status": "success",
            "client": f"{client['firstName']} {client['lastName']}",
            "property_id": property_id,
            "job_id": job["id"],
            "job_number": job["jobNumber"],
            "job_status": job["jobStatus"],
            "message": "Direct Job spawn successful."
        }))
    else:
        print(json.dumps({"status": "error", "message": "Failed to create Job structure."}))
        sys.exit(1)
