# Multi-Service Webhook Integration System

A lean, production-ready FastAPI backend to receive, process, and forward webhooks, logging everything to a PostgreSQL database.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure your environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints

- `GET /health` — Health check

## Project Structure

```
webhook-system/
├── app/
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Environment variable configuration
│   ├── routes/
│   │   └── webhooks.py    # Webhook route handlers
│   ├── services/
│   │   ├── processor.py   # Webhook processing logic
│   │   └── integrations.py# External service integrations
│   ├── database/
│   │   ├── models.py      # SQLAlchemy models
│   │   └── db.py          # Database connection setup
│   └── schemas/
│       └── payload.py     # Pydantic schemas
├── .env.example
├── requirements.txt
└── README.md
```
