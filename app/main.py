"""
main.py — FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload

Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.notification import HealthResponse
from app.routes.notifications import router as notify_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

cfg = get_settings()

app = FastAPI(
    title=cfg.APP_TITLE,
    version=cfg.APP_VERSION,
    description=(
        "**Portfolio demo** — production-inspired notification microservice.\n\n"
        "Supports **email** (SMTP/Gmail) and **WhatsApp** (Twilio WABA/sandbox).\n"
        "Service runs in **mock mode** when credentials are not configured — "
        "safe for public demos.\n\n"
        "> Built by **Gian Gianna** · [GitHub](https://github.com/giangianna14) · PT Swamedia Informatika"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Gian Gianna",
        "url": "https://github.com/giangianna14",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(notify_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Service health check",
)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=cfg.APP_VERSION,
        environment=cfg.APP_ENV,
        email_configured=bool(cfg.SMTP_USER and cfg.SMTP_PASS),
        whatsapp_configured=bool(cfg.TWILIO_ACCOUNT_SID and cfg.TWILIO_AUTH_TOKEN),
    )


@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    return {
        "service": cfg.APP_TITLE,
        "version": cfg.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
