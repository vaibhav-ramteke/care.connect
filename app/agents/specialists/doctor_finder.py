"""Doctor & department finder agent."""

from __future__ import annotations

from ...data import mock_data as md
from ...db import repository as repo
from ..base import AgentContext, AgentResult, BaseAgent


class DoctorFinderAgent(BaseAgent):
    name = "doctor_finder_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        dept = md.match_department(ctx.message)
        doctors = repo.doctors_in(dept) if dept else repo.all_doctors()

        lines = [
            f"- {d['name']} ({d['department']}) — fee Rs.{d['fee']}, "
            f"languages: {', '.join(d['languages'])}, "
            f"next slot: {d['slots'][0]}"
            f"{', teleconsult available' if d['teleconsult'] else ''}"
            for d in doctors
        ]
        dept_text = f"for {dept}" if dept else "across departments"
        facts = f"Available doctors {dept_text}:\n" + "\n".join(lines)
        fallback = (
            f"Here are doctors {dept_text}:\n"
            + "\n".join(
                f"• {d['name']} — Rs.{d['fee']}, next slot {d['slots'][0]}"
                for d in doctors
            )
            + "\n\nWould you like me to book the earliest slot?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply,
            agent=self.name,
            data={"department": dept, "doctors": doctors},
            quick_actions=["Book earliest slot", "Pre-visit checklist"],
            llm_used=used,
        )
