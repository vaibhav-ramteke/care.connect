"""Pre-visit preparation agent."""

from __future__ import annotations

from ...data import mock_data as md
from ...db import repository as repo
from ..base import AgentContext, AgentResult, BaseAgent


class PreVisitAgent(BaseAgent):
    name = "previsit_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        appts = ctx.session.get("appointments", [])
        dept = appts[-1]["department"] if appts else md.match_department(ctx.message)
        checklist = repo.previsit_checklist(dept)
        dept_text = f"your {dept} visit" if dept else "your visit"
        facts = f"Pre-visit checklist for {dept_text}:\n" + "\n".join(
            f"- {item}" for item in checklist
        )
        fallback = (
            f"Here's what to prepare for {dept_text}:\n"
            + "\n".join(f"• {item}" for item in checklist)
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"department": dept, "checklist": checklist},
                           quick_actions=["Book appointment", "Hospital directions"],
                           llm_used=used)
