"""Appointment agent — book / reschedule / cancel."""

from __future__ import annotations

from ...data import mock_data as md
from ...db import repository as repo
from ..base import AgentContext, AgentResult, BaseAgent


class AppointmentAgent(BaseAgent):
    name = "appointment_agent"

    def __init__(self, llm, store) -> None:
        super().__init__(llm)
        self.store = store

    def handle(self, ctx: AgentContext) -> AgentResult:
        if ctx.intent == "appointment_cancellation":
            return self._cancel(ctx)
        if ctx.intent == "appointment_reschedule":
            return self._reschedule(ctx)
        return self._book(ctx)

    # -- book ----------------------------------------------------------
    def _book(self, ctx: AgentContext) -> AgentResult:
        doctor = repo.find_doctor_by_name(ctx.message)
        if not doctor:
            dept = md.match_department(ctx.message)
            candidates = repo.doctors_in(dept) if dept else []
            if len(candidates) == 1:
                doctor = candidates[0]
            elif candidates:
                # Ask the patient to pick.
                facts = (
                    f"Multiple doctors are available in {dept}. Ask the patient "
                    f"to choose one:\n"
                    + "\n".join(
                        f"- {d['name']}: {d['slots'][0]} (Rs.{d['fee']})"
                        for d in candidates
                    )
                )
                fallback = (
                    f"Several {dept} doctors are available:\n"
                    + "\n".join(
                        f"• {d['name']} — {d['slots'][0]} (Rs.{d['fee']})"
                        for d in candidates
                    )
                    + "\n\nWhich doctor would you like to book?"
                )
                reply, used = self.phrase(ctx, facts, fallback)
                return AgentResult(
                    reply=reply, agent=self.name,
                    data={"department": dept, "doctors": candidates},
                    quick_actions=[d["name"] for d in candidates],
                    llm_used=used,
                )

        if not doctor:
            facts = (
                "We need to know the symptom, department, or doctor to book.\n"
                "Offer to help find the right doctor first."
            )
            fallback = (
                "I can book that for you — which doctor or department would you "
                "like? Or tell me your symptom and I'll suggest the right one."
            )
            reply, used = self.phrase(ctx, facts, fallback)
            return AgentResult(
                reply=reply, agent=self.name,
                quick_actions=["Find a doctor"], llm_used=used,
            )

        # We have a doctor — confirm the booking against the first open slot.
        slot = doctor["slots"][0]
        apt_id = self.store.next_appointment_id()
        appointment = {
            "appointment_id": apt_id,
            "doctor": doctor["name"],
            "department": doctor["department"],
            "time": slot,
            "fee": doctor["fee"],
            "location": "OPD Block, Room 204",
            "status": "Confirmed",
        }
        self.store.add_appointment(ctx.session, appointment)

        checklist = repo.previsit_checklist(doctor["department"])
        facts = (
            f"Appointment confirmed:\n"
            f"- ID: {apt_id}\n"
            f"- Doctor: {doctor['name']} ({doctor['department']})\n"
            f"- Time: {slot}\n"
            f"- Location: OPD Block, Room 204\n"
            f"- Fee: Rs.{doctor['fee']}\n"
            f"Pre-visit checklist: {'; '.join(checklist)}"
        )
        fallback = (
            f"Your appointment is confirmed.\n"
            f"• ID: {apt_id}\n"
            f"• {doctor['name']} ({doctor['department']})\n"
            f"• {slot} — OPD Block, Room 204\n"
            f"• Fee: Rs.{doctor['fee']}\n\n"
            f"Please carry: {', '.join(checklist[:3])}."
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply, agent=self.name,
            data={"appointment": appointment, "checklist": checklist},
            quick_actions=["Reschedule", "Cancel", "Pre-visit checklist"],
            llm_used=used,
        )

    # -- reschedule ----------------------------------------------------
    def _reschedule(self, ctx: AgentContext) -> AgentResult:
        appts = ctx.session.get("appointments", [])
        if not appts:
            fallback = "I couldn't find an existing appointment to reschedule. Would you like to book a new one?"
            return AgentResult(reply=fallback, agent=self.name,
                               quick_actions=["Book appointment"])
        appt = appts[-1]
        doctor = next((d for d in repo.all_doctors() if d["name"] == appt["doctor"]), None)
        options = doctor["slots"][1:] if doctor else ["Tomorrow 10:00 AM"]
        facts = (
            f"Existing appointment {appt['appointment_id']} with {appt['doctor']} "
            f"is at {appt['time']}. Other available slots: {', '.join(options)}."
        )
        fallback = (
            f"Your appointment {appt['appointment_id']} with {appt['doctor']} is "
            f"currently {appt['time']}. Available alternatives: "
            f"{', '.join(options)}. Which one should I move it to?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"appointment": appt, "options": options},
                           quick_actions=options, llm_used=used)

    # -- cancel --------------------------------------------------------
    def _cancel(self, ctx: AgentContext) -> AgentResult:
        appts = ctx.session.get("appointments", [])
        if not appts:
            return AgentResult(
                reply="I couldn't find an appointment to cancel. Is there anything else I can help with?",
                agent=self.name,
            )
        appt = appts[-1]
        appt["status"] = "Cancelled"
        self.store.update_appointment_status(appt["appointment_id"], "Cancelled")
        facts = f"Appointment {appt['appointment_id']} with {appt['doctor']} is now cancelled."
        fallback = (
            f"Done — appointment {appt['appointment_id']} with {appt['doctor']} "
            f"has been cancelled. Would you like to book a new one?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"appointment": appt},
                           quick_actions=["Book appointment"], llm_used=used)
