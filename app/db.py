import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "travel_mvp.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            destination_country TEXT,
            destination_city TEXT,
            travel_period_text TEXT,
            travelers_count INTEGER,
            trip_type TEXT,
            budget_range TEXT,
            decision_timing TEXT,
            priority_focus TEXT,
            lead_source TEXT,
            has_passport TEXT,
            has_visa TEXT,
            main_intent TEXT,
            lead_temperature TEXT,
            status TEXT,
            notes_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_lead(lead_data: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (
            phone,
            destination_country,
            destination_city,
            travel_period_text,
            travelers_count,
            trip_type,
            budget_range,
            decision_timing,
            priority_focus,
            lead_source,
            has_passport,
            has_visa,
            main_intent,
            lead_temperature,
            status,
            notes_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_data.get("phone"),
        lead_data.get("destination_country"),
        lead_data.get("destination_city"),
        lead_data.get("travel_period_text"),
        lead_data.get("travelers_count"),
        lead_data.get("trip_type"),
        lead_data.get("budget_range"),
        lead_data.get("decision_timing"),
        lead_data.get("priority_focus"),
        lead_data.get("lead_source"),
        lead_data.get("has_passport"),
        lead_data.get("has_visa"),
        lead_data.get("main_intent"),
        lead_data.get("lead_temperature"),
        lead_data.get("status"),
        lead_data.get("notes_summary"),
    ))

    lead_id = cur.lastrowid
    conn.commit()
    conn.close()

    return lead_id