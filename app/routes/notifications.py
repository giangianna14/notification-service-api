"""
notifications.py — Router for /notify endpoints.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.notification import (
    Channel,
    NotificationRequest,
    NotificationResponse,
    NotificationStatus,
)
from app.services.email_service import send_email
from app.services.whatsapp_service import send_whatsapp

log = logging.getLogger(__name__)

router = APIRouter(prefix="/notify", tags=["Notifications"])


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification via email or WhatsApp",
    description=(
        "Send a notification to a single recipient through the specified channel.\n\n"
        "- **channel=email** → recipient must be a valid email address\n"
        "- **channel=whatsapp** → recipient must be E.164 format (e.g. `+628123456789`)\n\n"
        "If backend credentials are not configured the service returns `status=mock` "
        "so you can test the API without real SMTP/Twilio keys."
    ),
)
async def send_notification(req: NotificationRequest) -> NotificationResponse:
    log.info("[notify] channel=%s recipient=%s", req.channel, req.recipient)

    if req.channel == Channel.email:
        result = send_email(
            recipient=req.recipient,
            subject=req.subject,
            message=req.message,
            html_body=req.html_body,
        )
    elif req.channel == Channel.whatsapp:
        result = send_whatsapp(
            recipient=req.recipient,
            message=req.message,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported channel: {req.channel}",
        )

    raw_status = result.get("status", "failed")
    try:
        notif_status = NotificationStatus(raw_status)
    except ValueError:
        notif_status = NotificationStatus.failed

    return NotificationResponse.make(
        status=notif_status,
        channel=req.channel,
        recipient=req.recipient,
        message=result.get("detail", req.message),
    )
