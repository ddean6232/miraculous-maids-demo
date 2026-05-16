import json
import traceback
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uvicorn

# Import the logic from our standalone tools
import jobber_create_client
import jobber_create_quote
import jobber_create_job
import jobber_schedule_visit

app = FastAPI(title="Jobber Microservices API", description="Exposes Jobber automation tools for n8n and ElevenLabs.")

# --- Pydantic Models for strict API Validation ---

class ClientRequest(BaseModel):
    firstName: str
    lastName: str
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None

class QuoteServiceItem(BaseModel):
    name: str
    price: float
    quantity: int = 1

class QuoteRequest(BaseModel):
    clientSearch: str
    quoteTitle: str
    services: List[QuoteServiceItem]

class JobRequest(BaseModel):
    clientSearch: str
    jobTitle: str
    serviceName: str
    price: float

class ScheduleRequest(BaseModel):
    jobId: str
    visitTitle: str
    startDate: str  # YYYY-MM-DD
    startTime: str  # HH:MM:SS
    endDate: str    # YYYY-MM-DD
    endTime: str    # HH:MM:SS
    timezone: str = "America/New_York"

# --- API Endpoints ---

@app.post("/api/jobber/create_client")
def api_create_client(payload: ClientRequest):
    try:
        client_node = jobber_create_client.create_client(
            first_name=payload.firstName,
            last_name=payload.lastName,
            email=payload.email,
            company_name=payload.company,
            phone=payload.phone
        )
        if not client_node:
            raise HTTPException(status_code=400, detail="Failed to create client in Jobber.")
            
        return {
            "status": "success",
            "clientId": client_node["id"],
            "name": client_node["name"]
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobber/create_quote")
def api_create_quote(payload: QuoteRequest):
    try:
        # 1. Resolve Client & Property
        client, property_id = jobber_create_quote.find_client_and_property(payload.clientSearch)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client '{payload.clientSearch}' not found.")
        if not property_id:
            raise HTTPException(status_code=400, detail=f"Client found, but has no Property to attach Quote to.")

        # 2. Map Payload to array format our script expects
        items = [{"name": s.name, "price": s.price, "quantity": s.quantity} for s in payload.services]
        
        # 3. Create Quote
        quote = jobber_create_quote.create_quote(client["id"], property_id, payload.quoteTitle, items)
        if not quote:
            raise HTTPException(status_code=400, detail="Jobber failed to generate Quote.")

        return {
            "status": "success",
            "client": f"{client['firstName']} {client['lastName']}",
            "quoteId": quote["id"],
            "quoteNumber": quote.get("quoteNumber"),
            "totalAmount": quote.get("amounts", {}).get("total"),
            "statusLabel": quote.get("quoteStatus"),
            "quoteLink": quote.get("clientHubUri")
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobber/create_job")
def api_create_job(payload: JobRequest):
    try:
        # 1. Resolve Client & Property
        client, property_id = jobber_create_quote.find_client_and_property(payload.clientSearch)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client '{payload.clientSearch}' not found.")
        if not property_id:
            raise HTTPException(status_code=400, detail="Client has no default Property.")

        # 2. Create Job
        job = jobber_create_job.create_job(property_id, payload.jobTitle, payload.serviceName, payload.price)
        if not job:
            raise HTTPException(status_code=400, detail="Failed to create Job.")

        return {
            "status": "success",
            "jobId": job["id"],
            "jobNumber": job.get("jobNumber"),
            "jobStatus": job.get("jobStatus")
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobber/schedule_visit")
def api_schedule_visit(payload: ScheduleRequest):
    try:
        result = jobber_schedule_visit.add_visit(
            job_id=payload.jobId,
            title=payload.visitTitle,
            start_date=payload.startDate,
            start_time=payload.startTime,
            end_date=payload.endDate,
            end_time=payload.endTime,
            timezone=payload.timezone
        )
        if not result or not result.get("createdVisits"):
            raise HTTPException(status_code=400, detail="Failed to schedule visit. Ensure Job ID is valid.")
            
        visit_id = result['createdVisits'][0]['id']
        job_status = result['job']['jobStatus']
        
        return {
            "status": "success",
            "visitId": visit_id,
            "jobStatus": job_status
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("======================================================")
    print("Starting FastAPI Microservices Server on port 8000...")
    print("You can expose this via Tailscale Funnel by running:")
    print("  tailscale funnel 8000")
    print("======================================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)
