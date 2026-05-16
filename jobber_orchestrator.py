import argparse
import requests
import json
import sys
import os

URL = "https://api.getjobber.com/api/graphql"

def get_headers():
    try:
        with open("jobber_tokens.json", "r") as f:
            token = json.load(f).get("access_token")
            return {
                'Authorization': f'Bearer {token}',
                'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
                'Content-Type': 'application/json'
            }
    except FileNotFoundError:
        print("Error: jobber_tokens.json not found.", file=sys.stderr)
        sys.exit(1)

def execute_graphql(query, variables=None):
    headers = get_headers()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    # Check for basic GraphQL execution errors
    if "errors" in data:
        print(f"GraphQL Execution Error: {data['errors']}", file=sys.stderr)
        sys.exit(1)
        
    return data

def search_client(search_term):
    query = """
    query CheckExistingClient($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                }
            }
        }
    }
    """
    data = execute_graphql(query, {"searchTerm": search_term})
    edges = data.get("data", {}).get("clients", {}).get("edges", [])
    if edges:
        return edges[0]["node"]["id"]
    return None

def create_client(first_name, last_name, email=None):
    mutation = """
    mutation CreateNewClient($input: ClientCreateInput!) {
        clientCreate(input: $input) {
            client { id }
            userErrors { message path }
        }
    }
    """
    input_data = {"firstName": first_name, "lastName": last_name}
    if email:
        input_data["emails"] = [{"address": email, "description": "MAIN", "primary": True}]

    data = execute_graphql(mutation, {"input": input_data})
    errors = data.get("data", {}).get("clientCreate", {}).get("userErrors", [])
    if errors:
        print(f"ClientCreate Error: {errors}", file=sys.stderr)
        return None
    return data["data"]["clientCreate"]["client"]["id"]

def create_property(client_id, street, city, province=None, zip_code=None):
    mutation = """
    mutation CreatePropertyForClient($clientId: ID!, $input: PropertyCreateInput!) {
        propertyCreate(clientId: $clientId, input: $input) {
            properties { id }
            userErrors { message path }
        }
    }
    """
    address_input = {"street1": street, "city": city}
    if province: address_input["province"] = province
    if zip_code: address_input["postalCode"] = zip_code

    variables = {
        "clientId": client_id,
        "input": {
            "properties": [{"address": address_input}]
        }
    }
    
    data = execute_graphql(mutation, variables)
    errors = data.get("data", {}).get("propertyCreate", {}).get("userErrors", [])
    if errors:
        print(f"PropertyCreate Error: {errors}", file=sys.stderr)
        return None
    return data["data"]["propertyCreate"]["properties"][0]["id"]

def create_job(property_id, title, service_name, price):
    mutation = """
    mutation CreateValidTestJob($input: JobCreateInput!) {
        jobCreate(input: $input) {
            job { id jobNumber }
            userErrors { message path }
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
    errors = data.get("data", {}).get("jobCreate", {}).get("userErrors", [])
    if errors:
        print(f"JobCreate Error: {errors}", file=sys.stderr)
        return None
    return data["data"]["jobCreate"]["job"]["id"]

def schedule_visit(job_id, title, date, start_time, end_time, tz="America/New_York"):
    mutation = """
    mutation AddScheduledVisit($jobId: ID!, $input: VisitCreateInput!) {
        visitCreate(jobId: $jobId, input: $input) {
            createdVisits { id }
            userErrors { message path }
        }
    }
    """
    variables = {
        "jobId": job_id,
        "input": {
            "visits": [
                {
                    "title": title,
                    "schedule": {
                        "startAt": {"date": date, "time": start_time, "timezone": tz},
                        "endAt": {"date": date, "time": end_time, "timezone": tz}
                    }
                }
            ]
        }
    }
    
    data = execute_graphql(mutation, variables)
    errors = data.get("data", {}).get("visitCreate", {}).get("userErrors", [])
    if errors:
        print(f"ScheduleVisit Error: {errors}", file=sys.stderr)
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Full Jobber Automation Lifecycle")
    parser.add_argument("--firstname", required=True)
    parser.add_argument("--lastname", required=True)
    parser.add_argument("--email", required=False)
    parser.add_argument("--street", required=True)
    parser.add_argument("--city", required=True)
    parser.add_argument("--province", required=False)
    parser.add_argument("--zip", required=False)
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--price", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--start", required=True, help="HH:MM:SS")
    parser.add_argument("--end", required=True, help="HH:MM:SS")
    parser.add_argument("--tz", default="America/New_York")
    
    args = parser.parse_args()

    # Orchestration Logic
    search_query = f"{args.firstname} {args.lastname}"
    
    client_id = search_client(search_query)
    if not client_id:
        client_id = create_client(args.firstname, args.lastname, args.email)
    
    if not client_id:
        print(json.dumps({"status": "error", "message": "Failed to resolve Client."}))
        sys.exit(1)
        
    property_id = create_property(client_id, args.street, args.city, args.province, args.zip)
    if not property_id:
        print(json.dumps({"status": "error", "message": "Failed to create Property."}))
        sys.exit(1)
        
    job_id = create_job(property_id, args.job_title, args.service, args.price)
    if not job_id:
        print(json.dumps({"status": "error", "message": "Failed to create Job."}))
        sys.exit(1)
        
    scheduled = schedule_visit(job_id, args.service, args.date, args.start, args.end, args.tz)
    
    if scheduled:
        print(json.dumps({
            "status": "success",
            "client_id": client_id,
            "property_id": property_id,
            "job_id": job_id,
            "message": "Full Jobber lifecycle complete."
        }))
    else:
        print(json.dumps({"status": "error", "message": "Job created but scheduling failed."}))
        sys.exit(1)
