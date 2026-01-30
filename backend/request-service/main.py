from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from datetime import datetime, timedelta

app = FastAPI(title="Request Service")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "usersdb")
DB_USER = os.getenv("POSTGRES_USER", "useradmin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "userpass")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

class Request(BaseModel):
    category: str  # polio, blood, clinic, emergency
    address: str
    region: str
    description: str

@app.on_event("startup")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id SERIAL PRIMARY KEY,
        category TEXT,
        address TEXT,
        region TEXT,
        description TEXT,
        status TEXT DEFAULT 'OPEN',
        created_at TIMESTAMP,
        expires_at TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

@app.get("/health")
def health():
    return {"status": "ok", "service": "request"}

@app.post("/request/create")
def create_request(req: Request, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    now = datetime.utcnow()
    expires = now + timedelta(days=14)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO requests (category, address, region, description, status, created_at, expires_at)
    VALUES (%s, %s, %s, %s, 'OPEN', %s, %s)
    """, (
        req.category,
        req.address,
        req.region,
        req.description,
        now,
        expires
    ))
    conn.commit()
    conn.close()

    return {"message": "Request created", "expires_at": str(expires)}

@app.get("/request/open")
def list_open_requests(category: str = None):
    conn = get_conn()
    cur = conn.cursor()

    if category:
        cur.execute("""
        SELECT id, category, address, region, description
        FROM requests
        WHERE status='OPEN' AND category=%s
        """, (category,))
    else:
        cur.execute("""
        SELECT id, category, address, region, description
        FROM requests
        WHERE status='OPEN'
        """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "category": r[1],
            "address": r[2],
            "region": r[3],
            "description": r[4]
        } for r in rows
    ]

@app.post("/request/close/{req_id}")
def close_request(req_id: int, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    UPDATE requests
    SET status='CLOSED'
    WHERE id=%s
    """, (req_id,))
    conn.commit()
    conn.close()

    return {"message": "Request closed"}
