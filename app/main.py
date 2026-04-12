from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import get_connection, init_db

app = FastAPI(title="Travel WhatsApp MVP")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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