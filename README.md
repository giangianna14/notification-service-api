# Notification Service API

[![Railway](https://img.shields.io/badge/Deploy-Railway-6c47ff?logo=railway)](https://railway.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Portfolio Project 2** — Production-inspired notification microservice reconstructed from enterprise experience at PT ASDP Indonesia Ferry.  
> Live demo: **https://notification-api-xxx.railway.app/docs** *(replace after deploy)*

---

## Business Context

At PT ASDP Indonesia Ferry, the Passenger System & Digital Ticketing team needed a reliable multi-channel notification service to:

- Confirm ferry bookings via **email** to customers
- Send operational alerts via **WhatsApp Business** to field operators
- Provide a single unified API endpoint for all notification channels
- Decouple notification logic from the core booking system (microservice pattern)

This repository is a **public demo reconstruction** — same architecture, sanitized of proprietary data.

---

## Features

| Capability | Detail |
|---|---|
| `POST /notify` | Send email or WhatsApp with single request |
| Email channel | Gmail SMTP (TLS) with HTML template |
| WhatsApp channel | Twilio WABA; falls back to **mock mode** if not configured |
| Mock mode | API fully functional without real credentials — safe for demo |
| Schema validation | Pydantic v2 — validates email format, E.164 phone, non-empty fields |
| Auto docs | Swagger UI at `/docs`, ReDoc at `/redoc` |
| Health check | `GET /health` — reports env + channel configuration status |
| Docker ready | Multi-stage slim image, non-root user |
| Railway deploy | One-click via `railway.toml` |

---

## Architecture

```
Client
  │
  ▼
POST /notify
  │
  ├─ channel=email ──► EmailService (smtplib → Gmail SMTP → TLS)
  │
  └─ channel=whatsapp ─► WhatsAppService (Twilio REST API / mock)
```

```
notification-service-api/
├── app/
│   ├── main.py              ← FastAPI app, CORS, health check
│   ├── config.py            ← Settings (pydantic-settings, .env)
│   ├── routes/
│   │   └── notifications.py ← POST /notify
│   ├── models/
│   │   └── notification.py  ← Pydantic schemas (request + response)
│   └── services/
│       ├── email_service.py
│       └── whatsapp_service.py
├── tests/
│   └── test_notifications.py
├── Dockerfile               ← multi-stage, python:3.11-slim
├── railway.toml
├── requirements.txt
└── .env.example
```

---

## Quick Start — Local

```bash
# 1. Clone
git clone https://github.com/giangianna14/notification-service-api.git
cd notification-service-api

# 2. Create venv
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Configure (optional — service works in mock mode without this)
cp .env.example .env
# edit .env → fill SMTP_USER, SMTP_PASS

# 5. Run
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

---

## API Reference

### `POST /notify`

Send a notification to one recipient.

**Request body:**

```json
{
  "channel": "email",
  "recipient": "user@example.com",
  "message": "Your ferry booking #TKT-2024-001 is confirmed.",
  "subject": "Booking Confirmation — ASDP"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `channel` | `"email"` \| `"whatsapp"` | ✅ | |
| `recipient` | string | ✅ | Email or E.164 phone (`+628…`) |
| `message` | string | ✅ | Plain text body |
| `subject` | string | – | Default: `"Notification"` |
| `html_body` | string | – | Optional HTML override for email |

**Response:**

```json
{
  "job_id": "f3a8c2d1-...",
  "status": "sent",
  "channel": "email",
  "recipient": "user@example.com",
  "message": "Email delivered to user@example.com"
}
```

`status` values: `sent` · `mock` · `failed`

---

### `GET /health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "email_configured": true,
  "whatsapp_configured": false
}
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` / `production` |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS) |
| `SMTP_USER` | *(empty)* | Gmail address — enables real email |
| `SMTP_PASS` | *(empty)* | Gmail App Password |
| `TWILIO_ACCOUNT_SID` | *(empty)* | Twilio SID — enables real WhatsApp |
| `TWILIO_AUTH_TOKEN` | *(empty)* | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` | Twilio sandbox number |

> All variables are **optional**. Without them the API returns `status=mock` — perfect for demos.

---

## Deploy to Railway

```bash
# 1. Push to GitHub
git init && git add . && git commit -m "feat: initial notification service API"
git remote add origin https://github.com/giangianna14/notification-service-api.git
git push -u origin main

# 2. Go to https://railway.app → New Project → Deploy from GitHub
# 3. Select this repo → Railway detects Dockerfile automatically
# 4. Add environment variables in Railway dashboard (Settings → Variables)
# 5. Copy the generated URL → paste below
```

**Live URL:** `https://notification-api-xxx.railway.app/docs`

---

## Run Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_notifications.py::test_health_ok                    PASSED
tests/test_notifications.py::test_root                         PASSED
tests/test_notifications.py::test_notify_email_mock            PASSED
tests/test_notifications.py::test_notify_whatsapp_mock         PASSED
...
11 passed in 0.xx s
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.111 |
| Schema validation | Pydantic v2 |
| Email | smtplib (stdlib) + Gmail SMTP |
| WhatsApp | Twilio REST API / mock |
| Server | Uvicorn (ASGI) |
| Container | Docker (multi-stage, python:3.11-slim) |
| Deploy | Railway |
| Testing | pytest + httpx + FastAPI TestClient |

---

## Author

**Gian Gianna** — Backend & Data Engineer  
[github.com/giangianna14](https://github.com/giangianna14)  

> *See also: [Telecom Monitoring Automation](https://github.com/giangianna14/telecom-monitoring-automation) — Portfolio Project 1*
