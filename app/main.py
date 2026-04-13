import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.db import get_connection, init_db, insert_lead
from app.services.qualification import get_next_question, process_conversation_step

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(title="Travel Lead Qualification MVP")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

telegram_sessions = {}
last_update_id = None
processed_update_ids = set()


class LeadCreate(BaseModel):
    phone: str
    destination_country: str
    destination_city: str
    travel_period_text: str
    travelers_count: int
    trip_type: str
    budget_range: str
    decision_timing: str
    priority_focus: str


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
        "message": "Travel Lead Qualification MVP is running",
        "status": "ready",
        "environment": APP_ENV
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page_title": "Travel Lead Qualification Dashboard"
        }
    )


@app.get("/api/telegram/test")
def test_telegram():
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not configured")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not response.ok or not data.get("ok"):
        raise HTTPException(status_code=500, detail="Failed to validate Telegram bot token")

    return {
        "message": "Telegram bot connected successfully",
        "bot": data["result"]
    }


@app.get("/api/metrics")
def get_metrics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM leads")
    total_leads = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM leads WHERE lead_temperature = 'hot'")
    hot_leads = cur.fetchone()["total"]

    cur.execute("""
        SELECT destination_country, COUNT(*) AS count
        FROM leads
        GROUP BY destination_country
        ORDER BY count DESC
    """)
    by_destination = [
        {"destination_country": row["destination_country"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT budget_range, COUNT(*) AS count
        FROM leads
        GROUP BY budget_range
        ORDER BY count DESC
    """)
    by_budget = [
        {"budget_range": row["budget_range"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT lead_source, COUNT(*) AS count
        FROM leads
        GROUP BY lead_source
        ORDER BY count DESC
    """)
    by_source = [
        {"lead_source": row["lead_source"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT decision_timing, COUNT(*) AS count
        FROM leads
        GROUP BY decision_timing
        ORDER BY count DESC
    """)
    by_decision_timing = [
        {"decision_timing": row["decision_timing"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT trip_type, COUNT(*) AS count
        FROM leads
        GROUP BY trip_type
        ORDER BY count DESC
    """)
    by_trip_type = [
        {"trip_type": row["trip_type"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT priority_focus, COUNT(*) AS count
        FROM leads
        GROUP BY priority_focus
        ORDER BY count DESC
    """)
    by_priority_focus = [
        {"priority_focus": row["priority_focus"], "count": row["count"]}
        for row in cur.fetchall()
    ]

    cur.execute("""
        SELECT destination_country
        FROM leads
        GROUP BY destination_country
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    top_destination_row = cur.fetchone()
    top_destination = top_destination_row["destination_country"] if top_destination_row else "-"

    conn.close()

    qualification_rate = round((hot_leads / total_leads) * 100, 1) if total_leads else 0

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "qualification_rate": qualification_rate,
        "top_destination": top_destination,
        "by_destination": by_destination,
        "by_budget": by_budget,
        "by_source": by_source,
        "by_decision_timing": by_decision_timing,
        "by_trip_type": by_trip_type,
        "by_priority_focus": by_priority_focus
    }


@app.post("/api/leads")
def create_lead(lead: LeadCreate):
    lead_data = {
        "phone": lead.phone,
        "destination_country": lead.destination_country,
        "destination_city": lead.destination_city,
        "travel_period_text": lead.travel_period_text,
        "travelers_count": lead.travelers_count,
        "trip_type": lead.trip_type,
        "budget_range": lead.budget_range,
        "decision_timing": lead.decision_timing,
        "priority_focus": lead.priority_focus,
        "lead_source": "manual",
        "has_passport": "unknown",
        "has_visa": "unknown",
        "main_intent": "package_quote",
        "lead_temperature": "warm",
        "status": "new",
        "notes_summary": (
            f"Destino: {lead.destination_country}; "
            f"Roteiro/Cidade: {lead.destination_city}; "
            f"Período: {lead.travel_period_text}; "
            f"Viajantes: {lead.travelers_count}; "
            f"Perfil: {lead.trip_type}; "
            f"Orçamento: {lead.budget_range}; "
            f"Decisão: {lead.decision_timing}; "
            f"Prioridade: {lead.priority_focus}"
        )
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
            "destination_country": lead["destination_country"],
            "destination_city": lead["destination_city"],
            "travel_period_text": lead["travel_period_text"],
            "travelers_count": lead["travelers_count"],
            "trip_type": lead["trip_type"],
            "budget_range": lead["budget_range"],
            "decision_timing": lead["decision_timing"],
            "priority_focus": lead["priority_focus"],
            "lead_source": "simulate",
            "has_passport": "unknown",
            "has_visa": "unknown",
            "main_intent": "package_quote",
            "lead_temperature": lead["lead_temperature"],
            "status": "qualified",
            "notes_summary": lead["notes_summary"]
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


@app.get("/api/telegram/updates")
def telegram_updates():
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not configured")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url, timeout=15)
    data = response.json()

    if not response.ok or not data.get("ok"):
        raise HTTPException(status_code=500, detail="Failed to fetch Telegram updates")

    return data


@app.get("/api/telegram/send-test")
def telegram_send_test():
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not configured")

    if not TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=500, detail="TELEGRAM_CHAT_ID not configured")

    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "Test message from FastAPI: Telegram integration is working."
    }

    send_response = requests.post(send_url, json=payload, timeout=15)
    send_data = send_response.json()

    if not send_response.ok or not send_data.get("ok"):
        raise HTTPException(status_code=500, detail="Failed to send Telegram message")

    return {
        "message": "Telegram test message sent successfully",
        "chat_id": TELEGRAM_CHAT_ID
    }


@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not configured")

    update = await request.json()
    message = update.get("message")

    if not message:
        return {"message": "No valid message found"}

    chat_id = str(message["chat"]["id"])
    text = message.get("text", "").strip()

    if not text:
        return {"message": "Empty message ignored"}

    phone = f"tg_{chat_id}"

    if text.lower() == "/start":
        telegram_sessions[chat_id] = {
            "state": "start",
            "lead": {}
        }
        reply = get_next_question("start")
    else:
        session = telegram_sessions.get(chat_id, {
            "state": "start",
            "lead": {}
        })

        result = process_conversation_step(session, text)

        telegram_sessions[chat_id] = {
            "state": result["state"],
            "lead": result["lead"]
        }

        reply = result["reply"]

        if result["completed"]:
            lead = result["lead"]

            lead_data = {
                "phone": phone,
                "destination_country": lead["destination_country"],
                "destination_city": lead["destination_city"],
                "travel_period_text": lead["travel_period_text"],
                "travelers_count": lead["travelers_count"],
                "trip_type": lead["trip_type"],
                "budget_range": lead["budget_range"],
                "decision_timing": lead["decision_timing"],
                "priority_focus": lead["priority_focus"],
                "lead_source": "telegram",
                "has_passport": "unknown",
                "has_visa": "unknown",
                "main_intent": "package_quote",
                "lead_temperature": lead["lead_temperature"],
                "status": "qualified",
                "notes_summary": lead["notes_summary"]
            }

            insert_lead(lead_data)

            telegram_sessions[chat_id] = {
                "state": "done",
                "lead": {}
            }

    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": reply
    }

    send_response = requests.post(send_url, json=payload, timeout=15)
    send_data = send_response.json()

    if not send_response.ok or not send_data.get("ok"):
        raise HTTPException(status_code=500, detail="Failed to send Telegram message")

    return {
        "message": "Telegram update processed successfully",
        "chat_id": chat_id,
        "reply": reply
    }