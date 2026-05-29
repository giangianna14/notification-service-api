"""
notification.py — Pydantic request/response schemas.
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class Channel(str, Enum):
    email = "email"
    whatsapp = "whatsapp"


class NotificationStatus(str, Enum):
    sent = "sent"
    failed = "failed"
    mock = "mock"


class NotificationRequest(BaseModel):
    channel: Channel
    recipient: str
    message: str
    subject: str = "Notification"
    html_body: Optional[str] = None  # optional rich HTML for email

    @field_validator("recipient")
    @classmethod
    def recipient_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("recipient cannot be empty")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_email_recipient(self) -> "NotificationRequest":
        if self.channel == Channel.email and "@" not in self.recipient:
            raise ValueError("recipient must be a valid email address for channel=email")
        if self.channel == Channel.whatsapp and not self.recipient.startswith("+"):
            raise ValueError(
                "recipient for WhatsApp must be E.164 format (e.g. +628123456789)"
            )
        return self


class NotificationResponse(BaseModel):
    job_id: str
    status: NotificationStatus
    channel: Channel
    recipient: str
    message: str

    @classmethod
    def make(
        cls,
        *,
        status: NotificationStatus,
        channel: Channel,
        recipient: str,
        message: str,
    ) -> "NotificationResponse":
        return cls(
            job_id=str(uuid.uuid4()),
            status=status,
            channel=channel,
            recipient=recipient,
            message=message,
        )


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    email_configured: bool
    whatsapp_configured: bool
