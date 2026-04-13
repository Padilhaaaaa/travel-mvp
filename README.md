# Travel Lead Qualification MVP

Simple Python FastAPI project built as an MVP for travel lead qualification, dashboard monitoring, and Telegram-first customer conversation flows.

## Overview

This project was originally conceived around a WhatsApp-style lead qualification idea, but the current MVP is now centered on a Telegram-first flow with a FastAPI backend, SQLite persistence, API-based metrics, and a dashboard for operational visibility.

The app is designed to capture travel leads through conversation, structure the most relevant qualification data, persist it in a database, and expose metrics for commercial follow-up.

## Stack

- Python
- FastAPI
- SQLite
- Jinja2
- Chart.js
- Telegram Bot API

## Current scope

The MVP currently covers the essential lead qualification cycle:

- Conversational lead intake
- Structured lead qualification
- SQLite persistence
- Metrics aggregation through API
- Dashboard visualization for operational monitoring

## Features

- Travel lead qualification flow
- KPI dashboard with lead metrics
- Destination, budget, and source-based chart visualization
- Manual lead creation endpoint
- Conversation simulator for testing qualification logic
- SQLite persistence for qualified leads
- Telegram bot token validation endpoint
- JSON metrics endpoint for dashboard consumption

## What's new

Compared to the earlier project version, the MVP now emphasizes:

- Telegram as the primary messaging channel instead of a WhatsApp-oriented concept
- A clearer lead qualification narrative, not just chatbot interaction
- Dashboard consumption through `/api/metrics`
- Better separation between data capture, persistence, metrics, and visualization
- Expanded dashboard use as an operational monitoring layer

## Run locally

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DB_PATH=travel_mvp.db
APP_ENV=development
```

## Routes

### GET /
Returns the app health status.

### GET /dashboard
Renders the lead qualification dashboard.

### GET /api/metrics
Returns aggregated lead metrics in JSON format for dashboard consumption.

### GET /api/telegram/test
Validates the Telegram bot token using the Telegram Bot API.

### POST /api/leads
Creates a lead manually.

### POST /api/simulate
Simulates a customer conversation using the qualification flow.

## Example response

```json
{
  "reply": "Perfect. I qualified this opportunity as warm lead for Cancun (Mexico).",
  "session": {
    "state": "done",
    "lead": {
      "destination_city": "Cancun",
      "destination_region": "Mexico",
      "travel_period_text": "July",
      "travelers_count": 2,
      "budget_range": "20k",
      "trip_type": "couple",
      "lead_temperature": "warm"
    }
  },
  "completed": true
}
```

## Product flow

1. A lead enters through a conversational flow.
2. The system structures the qualification data.
3. The lead is persisted in SQLite.
4. Metrics are aggregated through `/api/metrics`.
5. The dashboard displays operational indicators for monitoring.

## Notes

This project originally started with a WhatsApp-oriented idea, but the current MVP is being positioned around Telegram-first lead intake and dashboard-based operational monitoring.

At this stage, the focus is on documenting and presenting the essential product flow rather than expanding the feature set.