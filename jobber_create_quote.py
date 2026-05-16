import argparse
import requests
import json
import sys

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
    
    if "errors" in data:
        print(f"GraphQL Execution Error: {data['errors']}", file=sys.stderr)
        return None
        
    return data

def find_client_and_property(name_or_email):
    query = """
    query FindClientProperty($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    properties {
                        id
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
        # In this API version, properties is a direct array (not paginated with nodes/edges)
        properties = client.get("properties", [])
        property_id = properties[0]["id"] if properties else None
        return client, property_id
    return None, None

# In jobber_create_quote.py
from jobber_create_client import create_client
from jobber_orchestrator import create_property

# We need to define this helper in jobber_create_quote.py since it's missing from jobber_create_client.py
def find_client_and_property(name_or_email):
    query = """
    query FindClientProperty($searchTerm: String!) {
        clients(first: 1, searchTerm: $searchTerm) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    properties {
                        id
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
        properties = client.get("properties", [])
        property_id = properties[0]["id"] if properties else None
        return client, property_id
    return None, None

def create_quote(client_id, property_id, title, items_list):
    """
    Creates a detailed Quote mapping to the property.
    items_list must be a list of dictionaries: [{"name": "Deep Clean", "price": 150.0}, ...]
    """
    mutation = """
    mutation CreateQuote($attributes: QuoteCreateAttributes!) {
        quoteCreate(attributes: $attributes) {
            quote {
                id
                quoteNumber
                quoteStatus
                clientHubUri
                amounts {
                    total
                }
            }
            userErrors {
                message
                path
            }
        }
    }
    """
    
    # Format line items for the GraphQL input
    line_items_input = []
    for item in items_list:
        line_items_input.append({
            "name": item.get("name"),
            "quantity": item.get("quantity", 1),
            "unitPrice": float(item.get("price")),
            "saveToProductsAndServices": False
        })
        
    variables = {
        "attributes": {
            "clientId": client_id,
            "propertyId": property_id,
            "title": title,
            "lineItems": line_items_input,
            "clientViewOptions": {
                "showLineItemQty": True,
                "showLineItemUnitCosts": True,
                "showLineItemTotalCosts": True,
                "showTotals": True
            }
        }
    }
    
    data = execute_graphql(mutation, variables)
    if not data: return None
    
    errors = data.get("data", {}).get("quoteCreate", {}).get("userErrors", [])
    if errors:
        print(f"QuoteCreate Error: {errors}", file=sys.stderr)
        return None
        
    return data["data"]["quoteCreate"]["quote"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a Quote for an existing Client.")
    parser.add_argument("--client_search", required=True, help="Name or email of the existing client")
    parser.add_argument("--quote_title", required=True, help="Title of the Quote (e.g. 'Spring Deep Clean Estimate')")
    parser.add_argument("--service1_name", required=True, help="Primary service name")
    parser.add_argument("--service1_price", required=True, help="Primary service cost")
    parser.add_argument("--service2_name", required=False, help="Secondary service name (optional addon)")
    parser.add_argument("--service2_price", required=False, help="Secondary service cost (optional addon)")
    
    args = parser.parse_args()

    # Step 1: Lookup Client and Property
    client, property_id = find_client_and_property(args.client_search)
    
    if not client:
        print(json.dumps({"status": "error", "message": f"Client matching '{args.client_search}' not found."}))
        sys.exit(1)
        
    # FIX: If property doesn't exist, create one dynamically for the quote
    if not property_id:
        print(f"No property found for client {client['id']}. Creating one now...")
        property_id = create_property(client['id'], "Default Address", "Calgary", "AB", "T2P 1J1")
        if not property_id:
             print(json.dumps({"status": "error", "message": "Failed to create Property."}))
             sys.exit(1)
        
    # Step 2: Build Line Items
    items = [{"name": args.service1_name, "price": args.service1_price}]
    if args.service2_name and args.service2_price:
        items.append({"name": args.service2_name, "price": args.service2_price})
        
    # Step 3: Spawn Quote
    quote = create_quote(client["id"], property_id, args.quote_title, items)
    
    if quote:
        print(json.dumps({
            "status": "success",
            "client": f"{client['firstName']} {client['lastName']}",
            "quote_id": quote["id"],
            "quote_number": quote.get("quoteNumber"),
            "total_amount": quote.get("amounts", {}).get("total"),
            "status_label": quote.get("quoteStatus"),
            "send_this_link_to_customer": quote.get("clientHubUri")
        }))
    else:
        print(json.dumps({"status": "error", "message": "Failed to generate Quote."}))
        sys.exit(1)
