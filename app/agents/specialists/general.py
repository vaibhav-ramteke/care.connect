"""General fallback agent."""

from __future__ import annotations

from ..base import AgentContext, AgentResult, BaseAgent


class GeneralAgent(BaseAgent):
    name = "general_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        facts = (
            "CarePath AI can help with: finding the right doctor, booking "
            "appointments, pre-visit checklists, explaining prescriptions and "
            "discharge instructions, billing and insurance questions, recovery "
            "monitoring, and emergency escalation."
        )
        fallback = (
            "I can help you find a doctor, book an appointment, prepare for a "
            "visit, understand a prescription or bill, or connect you to the "
            "right team. What would you like to do?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply, agent=self.name,
            quick_actions=["Find a doctor", "Book appointment", "Billing help", "Talk to a human"],
            llm_used=used,
        )
