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

def add_visit(job_id, title, start_date, start_time, end_date, end_time, timezone="America/Belize"):
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'X-JOBBER-GRAPHQL-VERSION': '2025-04-16',
        'Content-Type': 'application/json'
    }

    mutation = """
    mutation AddScheduledVisit($jobId: ID!, $input: VisitCreateInput!) {
        visitCreate(jobId: $jobId, input: $input) {
            createdVisits {
                id
                title
            }
            job {
                id
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
        "jobId": job_id,
        "input": {
            "visits": [
                {
                    "title": title,
                    "schedule": {
                        "startAt": {
                            "date": start_date,
                            "time": start_time,
                            "timezone": timezone
                        },
                        "endAt": {
                            "date": end_date,
                            "time": end_time,
                            "timezone": timezone
                        }
                    }
                }
            ]
        }
    }

    try:
        response = requests.post(URL, headers=headers, json={"query": mutation, "variables": variables})
        response.raise_for_status()
        data = response.json()
        
        errors = data.get("data", {}).get("visitCreate", {}).get("userErrors", [])
        if errors:
            print(f"GraphQL User Error: {errors}", file=sys.stderr)
            return None

        return data.get("data", {}).get("visitCreate", {})

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Schedule a Visit for a Job.")
    parser.add_argument("--job_id", required=True, help="The Jobber Job ID")
    parser.add_argument("--title", required=True, help="Visit title")
    parser.add_argument("--start_date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--start_time", required=True, help="HH:MM:SS")
    parser.add_argument("--end_date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end_time", required=True, help="HH:MM:SS")
    parser.add_argument("--tz", required=False, default="America/Belize", help="Timezone")
    
    args = parser.parse_args()

    result = add_visit(args.job_id, args.title, args.start_date, args.start_time, args.end_date, args.end_time, args.tz)
    
    if result and result.get('createdVisits'):
        visit_id = result['createdVisits'][0]['id']
        job_status = result['job']['jobStatus']
        print(json.dumps({"status": "success", "visit_id": visit_id, "job_status": job_status}))
    else:
        print(json.dumps({"status": "failed"}), file=sys.stderr)
        sys.exit(1)