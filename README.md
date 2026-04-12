# Travel WhatsApp MVP

Simple Python FastAPI project built as the first step in my fullstack and AI-enabled customer experience learning path.

## Stack

- Python
- FastAPI
- SQLite
- Jinja2
- WhatsApp Cloud API

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

### GET /dashboard
Renders the KPI dashboard.

### GET /api/metrics
Returns lead and conversation metrics in JSON.

### GET /webhook/whatsapp
Validates the WhatsApp webhook challenge.

### POST /webhook/whatsapp
Receives incoming WhatsApp messages, qualifies travel leads, stores data in SQLite, and sends a reply.

### POST /api/simulate
Simulates a customer conversation without using the real webhook.

## Response example

```json
{
  "reply": "Perfeito. Qual faixa de orçamento vocês imaginam para essa viagem?",
  "lead_temperature": "warm"
}
```