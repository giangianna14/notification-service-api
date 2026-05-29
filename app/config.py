"""
config.py — Centralized settings via pydantic-settings.
All values read from .env or environment variables.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_TITLE: str = "Notification Service API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    # WhatsApp — Twilio (leave blank to use mock mode)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Twilio sandbox default

    # Rate limiting (basic)
    MAX_RECIPIENTS_PER_REQUEST: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
