"""Base agent contracts and shared helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..llm import LLMClient

LANG_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi"}


@dataclass
class AgentContext:
    message: str
    session: dict
    patient_id: str | None = None
    language: str = "en"
    intent: str = "general"
    journey_stage: str = "symptom_discovery"


@dataclass
class AgentResult:
    reply: str
    agent: str
    data: dict[str, Any] = field(default_factory=dict)
    quick_actions: list[str] = field(default_factory=list)
    needs_handoff: bool = False
    handoff_team: str | None = None
    handoff_reason: str | None = None
    handoff_priority: str = "normal"
    disclaimer: str | None = None
    llm_used: bool = False


class BaseAgent:
    """All specialized agents inherit this.

    The :meth:`phrase` helper is the heart of the hybrid design: an agent first
    computes verified facts deterministically, then optionally asks the LLM to
    turn those facts into a warm, simple reply. The LLM is constrained to the
    supplied facts and never invents doctors, prices, or diagnoses. If the LLM
    is unavailable, the deterministic fallback text is used unchanged.
    """

    name = "base"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def handle(self, ctx: AgentContext) -> AgentResult:  # pragma: no cover
        raise NotImplementedError

    # ------------------------------------------------------------------
    def phrase(
        self,
        ctx: AgentContext,
        facts: str,
        fallback: str,
        *,
        extra_rules: str = "",
    ) -> tuple[str, bool]:
        language = LANG_NAMES.get(ctx.language, "English")
        system = (
            "You are CarePath AI, a safe, friendly hospital patient-engagement "
            "assistant. Rephrase the verified facts into a clear, warm, concise "
            "reply for a patient or caregiver.\n"
            "Rules:\n"
            "- Use ONLY the verified facts provided. Never invent doctors, "
            "slots, fees, diagnoses, lab values, bills, or policy details.\n"
            "- Do NOT give a medical diagnosis or change any medication.\n"
            "- Use simple, non-technical language. Keep it short.\n"
            f"- Write the reply in {language}.\n"
            f"{extra_rules}"
        )
        prompt = (
            f'Patient message: "{ctx.message}"\n\n'
            f"Verified facts to use:\n{facts}\n\n"
            "Write the reply now (do not add a disclaimer — that is added "
            "separately)."
        )
        out = self.llm.complete(system, prompt, max_tokens=700)
        if out:
            return out, True
        return fallback, False
