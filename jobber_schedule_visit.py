import token_manager
import requests
import json
import sys

URL = "https://api.getjobber.com/api/graphql"

def add_visit(job_id, title, start_date, start_time, end_date, end_time, timezone="America/Belize"):
    try:
        token = token_manager.get_valid_token()
        headers = {'Authorization': f'Bearer {token}', 'X-JOBBER-GRAPHQL-VERSION': '2025-04-16', 'Content-Type': 'application/json'}
        mutation = """
        mutation AddScheduledVisit($jobId: ID!, $input: VisitCreateInput!) {
            visitCreate(jobId: $jobId, input: $input) {
                createdVisits { id title }
                job { id jobStatus }
                userErrors { message path }
            }
        }
        """
        variables = {"jobId": job_id, "input": {"visits": [{
            "title": title,
            "schedule": {
                "startAt": {"date": start_date, "time": start_time, "timezone": timezone},
                "endAt": {"date": end_date, "time": end_time, "timezone": timezone}
            }
        }]}}
        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": variables})
        data = response.json()
        errors = data.get("data", {}).get("visitCreate", {}).get("userErrors", [])
        if errors:
            print(f"Visit Error: {errors}", file=sys.stderr)
            return None
        return data["data"]["visitCreate"]
    except Exception as e:
        print(f"Error scheduling visit: {e}")
        return None

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--start_date", required=True)
    parser.add_argument("--start_time", required=True)
    parser.add_argument("--end_date", required=True)
    parser.add_argument("--end_time", required=True)
    args = parser.parse_args()
    res = add_visit(args.job_id, args.title, args.start_date, args.start_time, args.end_date, args.end_time)
    if res: print(json.dumps({"status": "success", "visit_id": res["createdVisits"][0]["id"]}))
    else: sys.exit(1)
