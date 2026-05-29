"""
whatsapp_service.py — Send WhatsApp messages via Twilio API.
Falls back to mock mode when Twilio credentials are not configured.
"""
from __future__ import annotations

import logging

from app.config import get_settings

log = logging.getLogger(__name__)


def send_whatsapp(recipient: str, message: str) -> dict:
    """
    Send a WhatsApp message.

    Parameters
    ----------
    recipient : str  E.164 phone number, e.g. "+628123456789"
    message   : str  plain text message body

    Returns
    -------
    dict  with keys: status ("sent" | "mock" | "failed"), detail, sid
    """
    cfg = get_settings()

    if not cfg.TWILIO_ACCOUNT_SID or not cfg.TWILIO_AUTH_TOKEN:
        log.warning("[whatsapp_service] Twilio not configured → mock mode")
        return {
            "status": "mock",
            "detail": f"[MOCK] WhatsApp to {recipient}: {message[:80]}",
            "sid": "MOCK_SID_00000000",
        }

    try:
        from twilio.rest import Client  # optional dep — only needed in prod

        client = Client(cfg.TWILIO_ACCOUNT_SID, cfg.TWILIO_AUTH_TOKEN)
        wa_to = f"whatsapp:{recipient}" if not recipient.startswith("whatsapp:") else recipient

        msg = client.messages.create(
            from_=cfg.TWILIO_WHATSAPP_FROM,
            to=wa_to,
            body=message,
        )
        log.info("[whatsapp_service] Sent to %s SID=%s", recipient, msg.sid)
        return {
            "status": "sent",
            "detail": f"WhatsApp delivered to {recipient}",
            "sid": msg.sid,
        }

    except ImportError:
        log.warning("[whatsapp_service] twilio package not installed → mock mode")
        return {
            "status": "mock",
            "detail": "[MOCK] twilio not installed — install with: pip install twilio",
            "sid": "MOCK_SID_NO_TWILIO",
        }
    except Exception as exc:
        log.exception("[whatsapp_service] Unexpected error")
        return {"status": "failed", "detail": str(exc), "sid": None}
