from mcp.server.fastmcp import FastMCP
import jobber_get_client_details
import jobber_reactivate_lead
import jobber_create_client
import jobber_create_quote
import jobber_create_job
import jobber_schedule_visit
import jobber_delete_tool

# Initialize the MCP server
mcp = FastMCP("Jobber-Automation")

@mcp.tool()
def search_client(search_term: str):
    """Search for a client in Jobber by name, email, or phone."""
    clients = jobber_get_client_details.get_client_details(search_term)
    if not clients:
        return {"status": "error", "message": "No clients found"}
    return {"status": "success", "clients": clients}

@mcp.tool()
def reactivate_lead(search: str, title: str, description: str, days_threshold: int = 90):
    """Reactivate an archived past customer by creating a new Request."""
    client = jobber_reactivate_lead.find_client(search)
    if not client:
        return {"status": "error", "message": "Client not found"}
    
    is_eligible, reason = jobber_reactivate_lead.validate_eligibility(client, days_threshold=days_threshold)
    if not is_eligible:
        return {"status": "ineligible", "reason": reason}
    
    prop_id = client.get("firstPropertyId")
    if not prop_id:
        return {"status": "error", "message": "Client has no property"}
        
    req = jobber_reactivate_lead.create_request(client["id"], prop_id, title, description)
    if not req:
        return {"status": "error", "message": "Failed to create request"}
    
    return {"status": "success", "requestId": req["id"]}

@mcp.tool()
def create_job(property_id: str, job_title: str, service_name: str, price: float):
    """Convert a property into a new service job."""
    res = jobber_create_job.create_job(property_id, job_title, service_name, price)
    if res.get("status") == "error":
        return res
    job = res.get("job")
    return {"status": "success", "jobId": job["id"], "jobNumber": job["jobNumber"]}

@mcp.tool()
def create_quote(client_id: str, property_id: str, quote_title: str, services: list):
    """Generate a quote for a client property. Services should be a list of dicts with 'name' and 'price'."""
    quote = jobber_create_quote.create_quote(client_id, property_id, quote_title, services)
    if not quote:
        return {"status": "error", "message": "Failed to create quote"}
    return {"status": "success", "quoteId": quote["id"], "quoteLink": quote.get("clientHubUri")}

if __name__ == "__main__":
    mcp.run(transport='stdio')
