# Multi-Service Webhook Integration System (Architecture Demo)

A lightweight, high-throughput, production-style MVP designed to showcase asynchronous webhook ingestion, data normalization, database logging, and resilient third-party API integration.

> **Portfolio Project Notice:** This repository serves as a functional, production-pattern architectural demo (MVP) focused on clean code, background workers, and error resilience. It is intentionally scoped around a single "Order Intake to Slack" integration to demonstrate system design without unnecessary multi-tenant SaaS bloat.

---

## System Architecture

```
[Webhook Source] ──(HTTP POST)──> [FastAPI Ingestion] ──(Immediate 202)──> [Client Response]
                                         │
                                  (Background Task)
                                         ▼
[Slack / Third-Party API] <──(Retry Loop)── [Processor Layer] ──> [PostgreSQL Log]
```

**Flow Summary:**
1. An external service sends an order webhook payload via `POST /webhooks/event`.
2. The server validates the payload, persists a `WebhookEvent` record with status `pending`, and immediately returns `202 Accepted`.
3. A background task formats the data, sends it to Slack (with up to 3 retries on failure), logs the outbound attempt in `APIRequestLog`, and updates the event status to `success` or `failed`.

---

## Key Engineering Features

- **Low-Latency Ingestion:** Uses FastAPI's `BackgroundTasks` to offload third-party API latency, returning an immediate `202 Accepted` response to the caller with zero blocking.
- **Resilient Delivery:** Implements an asynchronous exponential backoff retry mechanism (up to 3 attempts: 1s, 2s, 4s) for external API communication to gracefully handle transient network errors and 5xx failures.
- **Full Observability Audit:** Double-table tracking logs raw incoming payloads (`WebhookEvent`) separately from outbound transaction states (`APIRequestLog`), enabling independent debugging of ingestion vs. delivery.
- **Data Validation:** Strict schema enforcement using Pydantic models with email validation, type coercion, and automatic 422 rejection for malformed payloads.
- **Live Monitoring Dashboard:** Server-rendered Jinja2 dashboard at `/dashboard` with color-coded status badges for real-time event inspection.

---

## Tech Stack & Rationale

| Technology | Purpose |
|---|---|
| **FastAPI** | Native async support, high performance (Starlette-based), automatic OpenAPI/Swagger docs generation |
| **SQLAlchemy** | Robust ORM with relationship mapping, eager loading, and PostgreSQL UUID support |
| **PostgreSQL 15** | Production-grade relational database for audit-critical webhook logging |
| **HTTPX** | Modern async HTTP client for outbound API calls with timeout control |
| **Tenacity** | Battle-tested retry library with exponential backoff and exception-based retry policies |
| **Docker Compose** | Streamlines local development by packaging the API and an isolated PostgreSQL instance |
| **Pydantic** | Runtime type validation with automatic serialization/deserialization |
| **Jinja2 + Tailwind** | Lightweight server-rendered UI without frontend build complexity |

---

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose installed
- (Optional) Python 3.11+ for running outside Docker

### 1. Clone the repository

```bash
git clone https://github.com/brook1717/api-webhook-integration-system.git
cd api-webhook-integration-system
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your Slack Webhook URL
```

### 3. Start services

```bash
docker-compose up --build
```

The API will be live at `http://localhost:8000`. PostgreSQL starts automatically and tables are created on first boot.

### 4. Run tests (without Docker)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
pytest tests/ -v
```

---

## API Verification & Testing

### Send a test webhook

```bash
curl -X POST http://localhost:8000/webhooks/event \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-78432",
    "customer_email": "jane.doe@example.com",
    "total_amount": 149.99,
    "items": [
      {"name": "Wireless Headphones", "qty": 1},
      {"name": "USB-C Cable", "qty": 3}
    ]
  }'
```

**Expected Response (202 Accepted):**
```json
{
  "message": "accepted",
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Interactive Documentation

| Endpoint | Description |
|---|---|
| `GET /docs` | Swagger UI - interactive API explorer |
| `GET /redoc` | ReDoc - alternative API documentation |
| `GET /dashboard` | Live monitoring dashboard with status badges |
| `GET /health` | Health check endpoint |

---

## Project Structure

```
webhook-system/
├── app/
│   ├── main.py              # Application entry point, route registration, dashboard
│   ├── config.py            # Environment variable configuration (Pydantic Settings)
│   ├── routes/
│   │   └── webhooks.py      # POST /webhooks/event endpoint
│   ├── services/
│   │   ├── processor.py     # Background task: format, send, log
│   │   └── integrations.py  # Slack API client with retry mechanism
│   ├── database/
│   │   ├── models.py        # WebhookEvent & APIRequestLog models
│   │   └── db.py            # Engine, session factory, Base
│   ├── schemas/
│   │   └── payload.py       # Pydantic request validation schemas
│   └── templates/
│       └── dashboard.html   # Jinja2 monitoring dashboard
├── tests/
│   ├── conftest.py          # SQLite test DB override
│   └── test_webhooks.py     # Endpoint unit tests
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## Future Enterprise Scalability Next Steps

- **Message Queue Integration:** Replace FastAPI `BackgroundTasks` with RabbitMQ or Celery workers for distributed, fault-tolerant job processing at scale.
- **API Key Authentication:** Add per-client API key validation middleware with rate limiting via Redis to secure webhook ingestion endpoints.
- **Horizontal Scaling:** Deploy behind a load balancer with stateless containers, using connection pooling (PgBouncer) for database efficiency under high concurrency.
- **Multi-Service Fan-Out:** Extend the processor layer to route events to multiple downstream services (email, CRM, analytics) based on configurable rules.

---

## Author

**Biruk Kasahun**

Software Engineer specializing in backend systems, security architecture, and cloud-native deployments.

Site: [https://birukkasahun.com/](https://birukkasahun.com/)
