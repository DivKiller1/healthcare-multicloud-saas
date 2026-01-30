from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime

SECRET = "supersecretkey"
ALGORITHM = "HS256"

app = FastAPI(title="Auth Service")

class LoginRequest(BaseModel):
    mobile_number: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/auth/login")
def login(req: LoginRequest):
    payload = {
        "mobile": req.mobile_number,
        "role": "citizen",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return {
        "message": "Login successful",
        "token": token
    }

@app.post("/auth/verify")
def verify(token: str):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return decoded
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
