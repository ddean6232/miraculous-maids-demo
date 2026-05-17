import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def find_client_and_property(name_or_email):
    try:
        token = token_manager.get_valid_token()
        headers = {'Authorization': f'Bearer {token}', 'X-JOBBER-GRAPHQL-VERSION': '2025-04-16', 'Content-Type': 'application/json'}
        query = """
        query FindClientProperty($searchTerm: String!) {
            clients(first: 1, searchTerm: $searchTerm) {
                edges { node { id firstName lastName properties { id } } }
            }
        }
        """
        response = requests.post(URL, headers=headers, json={"query": query, "variables": {"searchTerm": name_or_email}})
        data = response.json()
        edges = data.get("data", {}).get("clients", {}).get("edges", [])
        if edges:
            client = edges[0]["node"]
            props = client.get("properties", [])
            prop_id = props[0]["id"] if props else None
            return client, prop_id
        return None, None
    except Exception as e:
        print(f"Error finding client: {e}", file=sys.stderr)
        return None, None

def create_quote(client_id, property_id, title, items_list):
    try:
        token = token_manager.get_valid_token()
        headers = {'Authorization': f'Bearer {token}', 'X-JOBBER-GRAPHQL-VERSION': '2025-04-16', 'Content-Type': 'application/json'}
        mutation = """
        mutation CreateQuote($attributes: QuoteCreateAttributes!) {
            quoteCreate(attributes: $attributes) {
                quote { id quoteNumber quoteStatus clientHubUri amounts { total } }
                userErrors { message path }
            }
        }
        """
        line_items = [{"name": i["name"], "quantity": i.get("quantity", 1), "unitPrice": float(i["price"]), "saveToProductsAndServices": False} for i in items_list]
        variables = {"attributes": {"clientId": client_id, "propertyId": property_id, "title": title, "lineItems": line_items, "clientViewOptions": {"showLineItemQty": True, "showLineItemUnitCosts": True, "showLineItemTotalCosts": True, "showTotals": True}}}
        
        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": variables})
        data = response.json()
        errors = data.get("data", {}).get("quoteCreate", {}).get("userErrors", [])
        if errors:
            print(f"Quote Error: {errors}", file=sys.stderr)
            return None
        return data["data"]["quoteCreate"]["quote"]
    except Exception as e:
        print(f"Error creating quote: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--client_search", required=True)
    parser.add_argument("--quote_title", required=True)
    parser.add_argument("--service1_name", required=True)
    parser.add_argument("--service1_price", required=True)
    args = parser.parse_args()
    
    client, prop_id = find_client_and_property(args.client_search)
    if not client or not prop_id:
        print(json.dumps({"status": "error", "message": "Client/Property not found"}))
        sys.exit(1)
    
    quote = create_quote(client["id"], prop_id, args.quote_title, [{"name": args.service1_name, "price": args.service1_price}])
    if quote:
        print(json.dumps({"status": "success", "quote_id": quote["id"], "quoteLink": quote.get("clientHubUri")}))
    else:
        print(json.dumps({"status": "failed"}))
        sys.exit(1)
