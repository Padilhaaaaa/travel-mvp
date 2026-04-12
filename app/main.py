from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.db import get_connection, init_db, insert_lead
from app.services.qualification import get_next_question, process_conversation_step

app = FastAPI(title="Travel WhatsApp MVP")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class LeadCreate(BaseModel):
    phone: str
    destination_region: str
    destination_city: str
    travel_period_text: str
    travelers_count: int
    trip_type: str
    budget_range: str


class SimulateRequest(BaseModel):
    phone: str
    message: str
    session: dict | None = None


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {
        "message": "Travel WhatsApp MVP is running",
        "status": "ready"
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page_title": "Travel WhatsApp MVP Dashboard"
        }
    )


@app.get("/api/metrics")
def get_metrics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM leads")
    total_leads = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM leads WHERE lead_temperature = 'hot'")
    hot_leads = cur.fetchone()["total"]

    cur.execute("""
        SELECT destination_region, COUNT(*) AS count
        FROM leads
        GROUP BY destination_region
        ORDER BY count DESC
    """)
    by_region = [
        {"region": row["destination_region"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT destination_region
        FROM leads
        GROUP BY destination_region
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    top_region_row = cur.fetchone()
    top_region = top_region_row["destination_region"] if top_region_row else "-"

    conn.close()

    qualification_rate = round((hot_leads / total_leads) * 100, 1) if total_leads else 0

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "qualification_rate": qualification_rate,
        "top_region": top_region,
        "by_region": by_region
    }


@app.post("/api/leads")
def create_lead(lead: LeadCreate):
    lead_data = {
        "phone": lead.phone,
        "destination_region": lead.destination_region,
        "destination_city": lead.destination_city,
        "travel_period_text": lead.travel_period_text,
        "travelers_count": lead.travelers_count,
        "trip_type": lead.trip_type,
        "budget_range": lead.budget_range,
        "has_passport": "unknown",
        "has_visa": "n/a" if lead.destination_region in ["LATAM", "Mexico"] else "unknown",
        "main_intent": "package_quote",
        "lead_temperature": "warm",
        "status": "new"
    }

    lead_id = insert_lead(lead_data)

    return {
        "message": "Lead created successfully",
        "lead_id": lead_id,
        "phone": lead.phone
    }


@app.post("/api/simulate")
def simulate_chat(payload: SimulateRequest):
    session = payload.session or {
        "state": "start",
        "lead": {}
    }

    if payload.message.strip().lower() == "start":
        return {
            "reply": get_next_question("start"),
            "session": {
                "state": "start",
                "lead": {}
            },
            "completed": False
        }

    result = process_conversation_step(session, payload.message)

    if result["completed"]:
        lead = result["lead"]

        lead_data = {
            "phone": payload.phone,
            "destination_region": lead["destination_region"],
            "destination_city": lead["destination_city"],
            "travel_period_text": lead["travel_period_text"],
            "travelers_count": lead["travelers_count"],
            "trip_type": lead["trip_type"],
            "budget_range": lead["budget_range"],
            "has_passport": "unknown",
            "has_visa": "n/a" if lead["destination_region"] in ["LATAM", "Mexico"] else "unknown",
            "main_intent": "package_quote",
            "lead_temperature": lead["lead_temperature"],
            "status": "qualified"
        }

        insert_lead(lead_data)

    return {
        "reply": result["reply"],
        "session": {
            "state": result["state"],
            "lead": result["lead"]
        },
        "completed": result["completed"]
    }