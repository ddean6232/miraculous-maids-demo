import token_manager
# jobber_delete_tool.py

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

def delete_client(client_id):
    mutation = """
    mutation ClientDelete($id: ID!) {
        clientDelete(id: $id) {
            userErrors { message }
        }
    }
    """
    data = execute_graphql(mutation, {"id": client_id})
    return data and "clientDelete" in data.get("data", {})

def delete_job(job_id):
    mutation = """
    mutation JobDelete($id: ID!) {
        jobDelete(id: $id) {
            userErrors { message }
        }
    }
    """
    data = execute_graphql(mutation, {"id": job_id})
    return data and "jobDelete" in data.get("data", {})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tear-down utility for Jobber entities")
    subparsers = parser.add_subparsers(dest="action")
    
    del_client = subparsers.add_parser("client")
    del_client.add_argument("--id", required=True)
    
    del_job = subparsers.add_parser("job")
    del_job.add_argument("--id", required=True)
    
    args = parser.parse_args()
    
    if args.action == "client":
        success = delete_client(args.id)
        print(json.dumps({"status": "success" if success else "failed"}))
    elif args.action == "job":
        success = delete_job(args.id)
        print(json.dumps({"status": "success" if success else "failed"}))
