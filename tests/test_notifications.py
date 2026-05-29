"""
test_notifications.py — pytest suite for Notification Service API.
Uses FastAPI TestClient (no real network calls — all services return mock).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "email_configured" in body
    assert "whatsapp_configured" in body


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "docs" in resp.json()


# ── Notify — Email ────────────────────────────────────────────────────────────

def test_notify_email_mock():
    """When SMTP creds are absent the service returns status=mock, not an error."""
    resp = client.post(
        "/notify",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "message": "Hello from pytest",
            "subject": "Test Suite",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("sent", "mock", "failed")
    assert body["channel"] == "email"
    assert body["recipient"] == "test@example.com"
    assert "job_id" in body


def test_notify_email_invalid_recipient():
    """Recipient without @ must fail validation for email channel."""
    resp = client.post(
        "/notify",
        json={
            "channel": "email",
            "recipient": "not-an-email",
            "message": "test",
        },
    )
    assert resp.status_code == 422


def test_notify_email_empty_message():
    """Empty message must fail validation."""
    resp = client.post(
        "/notify",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "message": "   ",
        },
    )
    assert resp.status_code == 422


# ── Notify — WhatsApp ─────────────────────────────────────────────────────────

def test_notify_whatsapp_mock():
    """When Twilio creds are absent the service returns status=mock."""
    resp = client.post(
        "/notify",
        json={
            "channel": "whatsapp",
            "recipient": "+628123456789",
            "message": "Test WA from pytest",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("sent", "mock", "failed")
    assert body["channel"] == "whatsapp"


def test_notify_whatsapp_invalid_recipient():
    """WhatsApp recipient must start with +."""
    resp = client.post(
        "/notify",
        json={
            "channel": "whatsapp",
            "recipient": "08123456789",  # no +
            "message": "test",
        },
    )
    assert resp.status_code == 422


# ── Schema edge cases ─────────────────────────────────────────────────────────

def test_notify_invalid_channel():
    resp = client.post(
        "/notify",
        json={
            "channel": "sms",  # not in enum
            "recipient": "+628123456789",
            "message": "test",
        },
    )
    assert resp.status_code == 422


def test_notify_missing_fields():
    resp = client.post("/notify", json={"channel": "email"})
    assert resp.status_code == 422


def test_notify_html_body_optional():
    """html_body is optional — omitting it must not cause errors."""
    resp = client.post(
        "/notify",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "message": "plain text only",
        },
    )
    assert resp.status_code == 200


def test_notify_with_html_body():
    resp = client.post(
        "/notify",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "message": "fallback",
            "html_body": "<b>Rich HTML</b>",
        },
    )
    assert resp.status_code == 200
