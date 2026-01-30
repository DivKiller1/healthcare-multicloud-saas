from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from datetime import datetime

app = FastAPI(title="Facility Service")

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

class Facility(BaseModel):
    name: str
    address: str
    mobile_number: str
    category: str   # clinic, hospital, blood_bank
    region: str

@app.on_event("startup")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS facilities (
        id SERIAL PRIMARY KEY,
        name TEXT,
        address TEXT,
        mobile TEXT,
        category TEXT,
        region TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

@app.get("/health")
def health():
    return {"status": "ok", "service": "facility"}

@app.post("/facility/register")
def register_facility(facility: Facility, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO facilities (name, address, mobile, category, region, status, created_at)
    VALUES (%s, %s, %s, %s, %s, 'PENDING', %s)
    """, (
        facility.name,
        facility.address,
        facility.mobile_number,
        facility.category,
        facility.region,
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()

    return {"message": "Facility registered, pending approval"}

@app.get("/facility/public")
def list_public_facilities():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT name, address, mobile, category, region
    FROM facilities
    WHERE status = 'APPROVED'
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "name": r[0],
            "address": r[1],
            "mobile": r[2],
            "category": r[3],
            "region": r[4]
        } for r in rows
    ]

@app.post("/facility/approve/{facility_id}")
def approve_facility(facility_id: int, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    # In real system: validate role == GOVT_ADMIN
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    UPDATE facilities
    SET status = 'APPROVED'
    WHERE id = %s
    """, (facility_id,))

    conn.commit()
    conn.close()

    return {"message": "Facility approved"}
