import token_manager
import argparse
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def get_headers_via_manager():
    token = token_manager.get_valid_token()
    return {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

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

from datetime import datetime, timedelta

def find_client(search_term):
    query = """
    query FindClient($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    name
                    isArchived
                    isLead
                    properties {
                        id
                    }
                    invoices(first: 1, sortBy: issuedDate, sortOrder: desc) {
                        edges {
                            node {
                                issuedDate
                            }
                        }
                    }
                }
            }
        }
    }
    """
    data = execute_graphql(query, {"searchTerm": search_term})
    if not data: return None

    edges = data.get("data", {}).get("clients", {}).get("edges", [])
    if edges:
        client = edges[0]["node"]
        props = client.get("properties", [])
        client["firstPropertyId"] = props[0]["id"] if props else None

        # Extract last invoice date
        inv_edges = client.get("invoices", {}).get("edges", [])
        client["lastInvoiceDate"] = inv_edges[0]["node"]["issuedDate"] if inv_edges else None

        return client
    return None

def validate_eligibility(client, days_threshold=90):
    """
    Validates if a client is eligible for reactivation.
    Must be archived, NOT a lead, and no invoice in the last N days.
    """
    if not client.get("isArchived"):
        return False, "Client is not archived. Only archived past customers can be reactivated."

    if client.get("isLead"):
        return False, "Client is marked as a Lead. Reactivation is for past customers only."

    last_inv_str = client.get("lastInvoiceDate")
    if last_inv_str:
        # Jobber dates are ISO8601 like 2024-01-01T00:00:00Z
        # We handle potential variations by taking the first 10 chars (YYYY-MM-DD)
        last_inv_date = datetime.strptime(last_inv_str[:10], "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(days=days_threshold)

        if last_inv_date > cutoff_date:
            return False, f"Client had activity on {last_inv_str[:10]}, which is within the last {days_threshold} days."

    return True, "Eligible"

    return None

def create_request(client_id, property_id, title, description):
    # Construct the Request with structured Service Details
    mutation = """
    mutation CreateRequest($input: RequestCreateInput!) {
        requestCreate(input: $input) {
            request {
                id
                title
                requestStatus
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
            "clientId": client_id,
            "propertyId": property_id,
            "title": title,
            "requestDetails": {
                "form": {
                    "sections": [
                        {
                            "label": "Service Details",
                            "items": [
                                {
                                    "label": "Details",
                                    "answerText": description
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    data = execute_graphql(mutation, variables)
    if not data: return None
    
    errors = data.get("data", {}).get("requestCreate", {}).get("userErrors", [])
    if errors:
        print(f"RequestCreate Error: {errors}", file=sys.stderr)
        return None
        
    return data["data"]["requestCreate"]["request"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert an existing Jobber client back into a Lead by creating a Request.")
    parser.add_argument("--search", required=True, help="Name, email, or phone of the client")
    parser.add_argument("--title", required=True, help="Short title for the new request")
    parser.add_argument("--description", required=True, help="Details for the request")
    
    args = parser.parse_args()

    # Step 1: Find the Client
    client_node = find_client(args.search)
    if not client_node:
        print(json.dumps({"status": "error", "message": f"Client matching '{args.search}' not found."}))
        sys.exit(1)
        
    # Step 1.5: Validate Eligibility
    is_eligible, reason = validate_eligibility(client_node)
    if not is_eligible:
        print(json.dumps({"status": "error", "message": reason}))
        sys.exit(1)
        
    client_id = client_node["id"]
    
    # Step 2: Ensure they have a property (Requests require properties)
    property_id = client_node.get("firstPropertyId")
    if not property_id:
        print(json.dumps({"status": "error", "message": f"Client found, but has no properties. Cannot create request."}))
        sys.exit(1)
    
    # Step 3: Create the Request
    request_data = create_request(client_id, property_id, args.title, args.description)
    
    if request_data:
        print(json.dumps({
            "status": "success",
            "client_id": client_id,
            "request_id": request_data["id"],
            "request_status": request_data["requestStatus"],
            "message": "Lead reactivated via new Request."
        }))
    else:
        print(json.dumps({"status": "error", "message": "Failed to create Request."}))
        sys.exit(1)
