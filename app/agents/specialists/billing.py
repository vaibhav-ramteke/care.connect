"""Billing & insurance agent."""

from __future__ import annotations

from ...db import repository as repo
from ..base import AgentContext, AgentResult, BaseAgent


class BillingInsuranceAgent(BaseAgent):
    name = "billing_insurance_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        if ctx.intent == "insurance_claim_query":
            return self._insurance(ctx)
        return self._billing(ctx)

    def _billing(self, ctx: AgentContext) -> AgentResult:
        bill = repo.get_bill()
        item_lines = [f"- {i['label']}: Rs.{i['amount']}" for i in bill["items"]]
        facts = (
            "Sample bill breakup (demo, would require login in production):\n"
            + "\n".join(item_lines)
            + f"\n- Total: Rs.{bill['total']}\n"
            f"- Insurance approved: Rs.{bill['insurance_approved']}\n"
            f"- Patient payable: Rs.{bill['patient_payable']}"
        )
        fallback = (
            "Here's your bill summary (demo data):\n"
            + "\n".join(f"• {i['label']}: Rs.{i['amount']}" for i in bill["items"])
            + f"\n\nTotal: Rs.{bill['total']} | Insurance: Rs.{bill['insurance_approved']} "
            f"| You pay: Rs.{bill['patient_payable']}."
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply, agent=self.name, data={"bill": bill},
            quick_actions=["Pay now", "Talk to billing team"],
            needs_handoff=False, llm_used=used,
        )

    def _insurance(self, ctx: AgentContext) -> AgentResult:
        ins = repo.get_insurance()
        facts = (
            f"Sample insurance claim (demo, login required in production):\n"
            f"- Policy: {ins['policy']}\n"
            f"- Claim {ins['claim_id']} status: {ins['status']}\n"
            f"- Approved amount: Rs.{ins['approved_amount']}\n"
            f"- Pending documents: {', '.join(ins['pending_documents'])}\n"
            f"- Note: {ins['uncovered_note']}"
        )
        fallback = (
            f"Your claim {ins['claim_id']} is currently '{ins['status']}'. "
            f"Approved so far: Rs.{ins['approved_amount']}.\n"
            f"Still needed: {', '.join(ins['pending_documents'])}.\n"
            f"{ins['uncovered_note']}"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply, agent=self.name, data={"insurance": ins},
            quick_actions=["Upload documents", "Talk to insurance desk"],
            llm_used=used,
        )
