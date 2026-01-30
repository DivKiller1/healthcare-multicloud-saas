from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="Auth Service")

class LoginRequest(BaseModel):
    mobile_number: str

class VerifyRequest(BaseModel):
    mobile_number: str
    otp: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/auth/login")
def login(req: LoginRequest):
    return {
        "message": "OTP sent (mock)",
        "request_id": str(uuid.uuid4())
    }

@app.post("/auth/verify-otp")
def verify(req: VerifyRequest):
    token = str(uuid.uuid4())
    return {
        "message": "Login successful",
        "token": token,
        "role": "citizen"
    }
