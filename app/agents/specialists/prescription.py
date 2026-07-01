"""Prescription explanation agent."""

from __future__ import annotations

from ...db import repository as repo
from ...safety import guardrails as g
from ..base import AgentContext, AgentResult, BaseAgent


class PrescriptionAgent(BaseAgent):
    name = "prescription_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        rx = repo.get_prescription()
        med_lines = [
            f"- {m['name']}: {m['frequency']}, {m['timing']}, for {m['duration']}"
            for m in rx["medicines"]
        ]
        facts = (
            "Using the patient's sample prescription:\n"
            + "\n".join(med_lines)
            + "\n- Do not change dose or duration without the doctor."
        )
        fallback = (
            "Here is your medicine schedule (sample prescription):\n"
            + "\n".join(
                f"• {m['name']} — {m['frequency']}, {m['timing']} ({m['duration']})"
                for m in rx["medicines"]
            )
            + "\n\nTake them exactly as listed."
        )
        reply, used = self.phrase(ctx, facts, fallback,
                                  extra_rules="- Never suggest stopping or changing a dose.\n")
        disclaimer = g.MEDICAL_DISCLAIMER + " " + g.MEDICATION_SAFETY_NOTE
        return AgentResult(reply=reply, agent=self.name,
                           data={"prescription": rx},
                           quick_actions=["Set medicine reminder", "Talk to a nurse"],
                           disclaimer=disclaimer, llm_used=used)
