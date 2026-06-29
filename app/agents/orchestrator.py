"""Orchestrator AI Agent — the central decision-maker.

Implements the flow from the requirements (section 9):

    query -> safety/privacy check -> intent detection -> journey stage
    -> route to specialized agent -> validate/augment response
    -> human handoff if needed -> final response -> audit log

The orchestrator never answers domain queries itself; it coordinates the
specialized agents, applies safety guardrails, and escalates to humans.
"""

from __future__ import annotations

from ..config import settings
from ..llm import LLMClient
from ..safety import guardrails as g
from ..schemas import ChatRequest, ChatResponse, HandoffInfo
from ..store import Store
from .base import AgentContext, AgentResult
from .handoff import HumanHandoffAgent, route_team
from .intent import IntentDetector
from .journey import JourneyAgent
from .specialists import (
    AppointmentAgent,
    BillingInsuranceAgent,
    DischargeAgent,
    DoctorFinderAgent,
    GeneralAgent,
    PreVisitAgent,
    PrescriptionAgent,
    SymptomGuidanceAgent,
)


class Orchestrator:
    def __init__(self, llm: LLMClient, store: Store) -> None:
        self.llm = llm
        self.store = store

        self.intent_detector = IntentDetector(llm)
        self.journey_agent = JourneyAgent()
        self.handoff_agent = HumanHandoffAgent(llm)

        symptom = SymptomGuidanceAgent(llm)
        doctor = DoctorFinderAgent(llm)
        appointment = AppointmentAgent(llm, store)
        previsit = PreVisitAgent(llm)
        prescription = PrescriptionAgent(llm)
        discharge = DischargeAgent(llm)
        billing = BillingInsuranceAgent(llm)
        self.general = GeneralAgent(llm)

        # intent -> agent routing table (requirements 17.1)
        self.routes = {
            "symptom_guidance": symptom,
            "emergency_help": symptom,  # emergencies short-circuit earlier
            "doctor_search": doctor,
            "department_search": doctor,
            "appointment_booking": appointment,
            "appointment_reschedule": appointment,
            "appointment_cancellation": appointment,
            "previsit_checklist": previsit,
            "prescription_help": prescription,
            "discharge_help": discharge,
            "billing_query": billing,
            "insurance_claim_query": billing,
            "human_handoff": self.handoff_agent,
        }

    # ------------------------------------------------------------------
    def process(self, request: ChatRequest) -> ChatResponse:
        session = self.store.get_or_create_session(
            request.session_id, request.patient_id
        )
        self.store.add_message(session, "user", request.message)

        # 1) Safety first — emergencies bypass normal routing.
        red_flag = g.detect_emergency(request.message)
        if red_flag:
            return self._emergency_response(request, session, red_flag)

        # 2) Intent + journey stage.
        intent = self.intent_detector.detect(request.message)
        stage = self.journey_agent.detect(intent, session["journey_stage"])
        session["journey_stage"] = stage

        ctx = AgentContext(
            message=request.message,
            session=session,
            patient_id=request.patient_id,
            language=request.language,
            intent=intent,
            journey_stage=stage,
        )

        # 3) Route to the specialized agent (general fallback otherwise).
        agent = self.routes.get(intent, self.general)
        result = agent.handle(ctx)

        # 4) Distress detection can force a human handoff.
        if g.detect_distress(request.message) and not result.needs_handoff:
            result.needs_handoff = True
            result.handoff_team = route_team(request.message)
            result.handoff_reason = "Patient appears distressed/dissatisfied"
            result.handoff_priority = "high"

        # 5) Ensure clinical replies carry a medical disclaimer.
        if intent in g.CLINICAL_INTENTS and not result.disclaimer:
            result.disclaimer = g.MEDICAL_DISCLAIMER

        return self._finalize(request, session, ctx, result)

    # ------------------------------------------------------------------
    def _emergency_response(
        self, request: ChatRequest, session: dict, red_flag: str
    ) -> ChatResponse:
        stage = "symptom_discovery"
        session["journey_stage"] = stage

        reply = (
            f"{g.EMERGENCY_DISCLAIMER}\n\n"
            f"What you described ('{red_flag}') can be a medical emergency. "
            f"Please call {settings.emergency_number} now or go to the nearest "
            f"Emergency Department. If you are at {settings.hospital_name}, head "
            f"to the Emergency entrance — staff will be alerted."
        )

        ticket = self.store.create_handoff(
            session_id=session["id"],
            team="emergency_team",
            reason=f"Emergency red flag detected: {red_flag}",
            query=request.message,
            priority="critical",
            patient_id=request.patient_id,
        )

        self.store.add_message(session, "assistant", reply)
        self.store.log_audit(
            {
                "session_id": session["id"],
                "query": request.message,
                "intent": "emergency_help",
                "journey_stage": stage,
                "agent": "safety_guardrail_agent",
                "emergency": True,
                "red_flag": red_flag,
                "handoff_team": "emergency_team",
                "handoff_ticket": ticket["ticket_id"],
                "disclaimer_shown": True,
                "llm_used": False,
            }
        )

        return ChatResponse(
            session_id=session["id"],
            reply=reply,
            agent="safety_guardrail_agent",
            intent="emergency_help",
            journey_stage=stage,
            emergency=True,
            disclaimer=g.EMERGENCY_DISCLAIMER,
            handoff=HandoffInfo(
                triggered=True,
                team="emergency_team",
                ticket_id=ticket["ticket_id"],
                reason=ticket["reason"],
            ),
            quick_actions=[
                f"Call {settings.emergency_number}",
                "Emergency directions",
                "Talk to a nurse",
            ],
            data={"emergency_number": settings.emergency_number},
            llm_used=False,
        )

    # ------------------------------------------------------------------
    def _finalize(
        self,
        request: ChatRequest,
        session: dict,
        ctx: AgentContext,
        result: AgentResult,
    ) -> ChatResponse:
        handoff = HandoffInfo()
        if result.needs_handoff and result.handoff_team:
            ticket = self.store.create_handoff(
                session_id=session["id"],
                team=result.handoff_team,
                reason=result.handoff_reason or "Escalation requested",
                query=request.message,
                priority=result.handoff_priority,
                patient_id=request.patient_id,
            )
            handoff = HandoffInfo(
                triggered=True,
                team=result.handoff_team,
                ticket_id=ticket["ticket_id"],
                reason=ticket["reason"],
            )

        self.store.add_message(session, "assistant", result.reply)
        self.store.log_audit(
            {
                "session_id": session["id"],
                "query": request.message,
                "intent": ctx.intent,
                "journey_stage": ctx.journey_stage,
                "agent": result.agent,
                "emergency": False,
                "handoff_team": handoff.team,
                "handoff_ticket": handoff.ticket_id,
                "disclaimer_shown": bool(result.disclaimer),
                "llm_used": result.llm_used,
            }
        )

        return ChatResponse(
            session_id=session["id"],
            reply=result.reply,
            agent=result.agent,
            intent=ctx.intent,
            journey_stage=ctx.journey_stage,
            emergency=False,
            disclaimer=result.disclaimer,
            handoff=handoff,
            quick_actions=result.quick_actions,
            data=result.data,
            llm_used=result.llm_used,
        )
