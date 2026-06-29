"""Human Handoff Agent — routes to the right team and opens a ticket."""

from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent

# Maps a routing keyword to a human team.
_TEAM_KEYWORDS = [
    ("billing_team", ["bill", "payment", "invoice", "charge"]),
    ("insurance_desk", ["insurance", "claim", "cashless", "policy", "tpa"]),
    ("appointment_desk", ["appointment", "book", "slot", "reschedule"]),
    ("nurse", ["nurse", "pain", "wound", "fever", "medicine", "recovery"]),
    ("doctor_coordinator", ["doctor", "consult", "report"]),
]


def route_team(message: str) -> str:
    low = message.lower()
    for team, cues in _TEAM_KEYWORDS:
        if any(c in low for c in cues):
            return team
    return "front_desk"


class HumanHandoffAgent(BaseAgent):
    name = "human_handoff_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        team = route_team(ctx.message)
        readable = team.replace("_", " ")
        facts = (
            f"The patient is being connected to the {readable}. "
            f"Confirm warmly and set the expectation of a callback shortly."
        )
        fallback = (
            f"I'm connecting you to our {readable}. They'll review your request "
            f"and get back to you shortly. Your conversation has been shared with them."
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply,
            agent=self.name,
            needs_handoff=True,
            handoff_team=team,
            handoff_reason="Patient requested human assistance",
            quick_actions=["Continue with assistant"],
            llm_used=used,
        )
