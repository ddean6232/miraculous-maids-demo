import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from dotenv import load_dotenv
import token_manager
import jobber_create_client
import jobber_create_quote
import jobber_create_job
import jobber_schedule_visit
import jobber_get_client_details

load_dotenv()

API_SERVER_TOKEN = os.getenv("API_SERVER_SECRET")
API_PORT = int(os.getenv("API_PORT", 8989))
API_HOST = os.getenv("API_HOST", "0.0.0.0")

app = FastAPI(title="Jobber Microservices API")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_SERVER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API Token")
    return credentials.credentials

# Models
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
    startDate: str
    startTime: str
    endDate: str
    endTime: str

# Endpoints
@app.get("/api/jobber/check_status")
def check():
    try:
        token_manager.get_valid_token()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Jobber Auth failed")

@app.get("/api/jobber/client_details", dependencies=[Depends(verify_token)])
def get_details(searchTerm: str):
    res = jobber_get_client_details.get_client_details(searchTerm)
    if not res: raise HTTPException(status_code=404, detail="Client not found")
    return {"status": "success", "clients": res}

@app.post("/api/jobber/create_client", dependencies=[Depends(verify_token)])
def create_c(p: ClientRequest):
    res = jobber_create_client.create_client(p.firstName, p.lastName, p.email, p.company, p.phone)
    if not res: raise HTTPException(status_code=400, detail="Failed")
    return {"status": "success", "clientId": res["id"], "name": res["name"]}

@app.post("/api/jobber/create_quote", dependencies=[Depends(verify_token)])
def create_q(p: QuoteRequest):
    client, prop_id = jobber_create_quote.find_client_and_property(p.clientSearch)
    if not client or not prop_id: raise HTTPException(status_code=404, detail="Client/Prop not found")
    items = [{"name": s.name, "price": s.price, "quantity": s.quantity} for s in p.services]
    quote = jobber_create_quote.create_quote(client["id"], prop_id, p.quoteTitle, items)
    if not quote: raise HTTPException(status_code=400, detail="Quote failed")
    return {"status": "success", "quoteId": quote["id"], "quoteLink": quote.get("clientHubUri")}

@app.post("/api/jobber/create_job", dependencies=[Depends(verify_token)])
def create_j(p: JobRequest):
    client, prop_id = jobber_create_quote.find_client_and_property(p.clientSearch)
    if not client or not prop_id: raise HTTPException(status_code=404, detail="Client/Prop not found")
    job = jobber_create_job.create_job(prop_id, p.jobTitle, p.serviceName, p.price)
    if not job: raise HTTPException(status_code=400, detail="Job creation failed")
    return {"status": "success", "jobId": job["id"], "jobNumber": job["jobNumber"]}

@app.post("/api/jobber/schedule_visit", dependencies=[Depends(verify_token)])
def schedule(p: ScheduleRequest):
    res = jobber_schedule_visit.add_visit(p.jobId, p.visitTitle, p.startDate, p.startTime, p.endDate, p.endTime)
    if not res: raise HTTPException(status_code=400, detail="Schedule failed")
    return {"status": "success", "visitId": res["createdVisits"][0]["id"]}

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
