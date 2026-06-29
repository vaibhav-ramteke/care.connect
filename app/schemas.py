"""Pydantic request/response models for the public API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Free-text patient message")
    session_id: str | None = Field(None, description="Existing conversation id")
    patient_id: str | None = Field(None, description="Optional patient identifier")
    language: str = Field("en", description="Preferred reply language (en/hi/mr)")


class HandoffInfo(BaseModel):
    triggered: bool = False
    team: str | None = None
    ticket_id: str | None = None
    reason: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    agent: str
    intent: str
    journey_stage: str
    emergency: bool = False
    disclaimer: str | None = None
    handoff: HandoffInfo = HandoffInfo()
    quick_actions: list[str] = []
    data: dict[str, Any] = {}
    llm_used: bool = False
