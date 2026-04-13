# Travel WhatsApp MVP
# Travel Lead Qualification MVP

Simple Python FastAPI project built as an MVP for travel lead qualification, dashboard monitoring, and Telegram-first customer conversation flows.

## Stack

- Python
- FastAPI
- SQLite
- Jinja2
- Chart.js
- Telegram Bot API

## Features

- Travel lead qualification flow
- KPI dashboard with lead metrics
- Region-based chart visualization
- Manual lead creation form
- Conversation simulator for testing the qualification flow
- SQLite persistence for qualified leads
- Telegram bot token validation endpoint

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
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
Returns lead metrics in JSON format.

### GET /api/telegram/test
Validates the Telegram bot token using the Bot API.

### POST /api/leads
Creates a lead manually from the dashboard form.

### POST /api/simulate
Simulates a customer conversation using the qualification flow.

## Response example

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

## Notes

This project originally started with a WhatsApp-oriented idea, but it is currently being adapted to use Telegram as the primary messaging channel.