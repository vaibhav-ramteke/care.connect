"""Application settings, loaded from environment / .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CarePath AI"
    app_tagline: str = "Agentic Patient Journey Companion"

    # LLM configuration. When anthropic_api_key is empty the backend runs
    # entirely on deterministic rule-based logic (the "hybrid" fallback).
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-8"

    # Demo hospital details.
    emergency_number: str = "112"
    hospital_name: str = "CarePath General Hospital"


settings = Settings()
