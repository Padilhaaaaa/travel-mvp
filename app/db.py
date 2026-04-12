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
            phone TEXT UNIQUE NOT NULL,
            destination_region TEXT,
            destination_city TEXT,
            travel_period_text TEXT,
            travelers_count INTEGER,
            trip_type TEXT,
            budget_range TEXT,
            has_passport TEXT,
            has_visa TEXT,
            main_intent TEXT,
            lead_temperature TEXT DEFAULT 'cold',
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("SELECT COUNT(*) as total FROM leads")
    total = cur.fetchone()["total"]

    if total == 0:
        sample_leads = [
            (
                "5511999991111", "Mexico", "Cancun", "july", 2,
                "couple", "20k", "yes", "n/a", "package_quote", "hot", "qualified"
            ),
            (
                "5511999992222", "USA", "Orlando", "december", 4,
                "family", "35k", "yes", "unknown", "package_quote", "warm", "new"
            ),
            (
                "5511999993333", "LATAM", "Bariloche", "august", 2,
                "leisure", "15k", "yes", "n/a", "hotel_only", "warm", "new"
            ),
            (
                "5511999994444", "Mexico", "Mexico City", "october", 1,
                "corporate", "10k", "yes", "n/a", "flight_only", "cold", "new"
            )
        ]

        cur.executemany("""
            INSERT INTO leads (
                phone, destination_region, destination_city, travel_period_text,
                travelers_count, trip_type, budget_range, has_passport, has_visa,
                main_intent, lead_temperature, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_leads)

    conn.commit()
    conn.close()


def insert_lead(lead_data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (
            phone,
            destination_region,
            destination_city,
            travel_period_text,
            travelers_count,
            trip_type,
            budget_range,
            has_passport,
            has_visa,
            main_intent,
            lead_temperature,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_data["phone"],
        lead_data["destination_region"],
        lead_data["destination_city"],
        lead_data["travel_period_text"],
        lead_data["travelers_count"],
        lead_data["trip_type"],
        lead_data["budget_range"],
        lead_data["has_passport"],
        lead_data["has_visa"],
        lead_data["main_intent"],
        lead_data["lead_temperature"],
        lead_data["status"]
    ))

    conn.commit()
    lead_id = cur.lastrowid
    conn.close()

    return lead_id