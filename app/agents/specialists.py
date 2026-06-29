"""Specialized agents the orchestrator routes to.

Each agent computes verified facts from mock data, builds a deterministic
fallback reply, then optionally lets the LLM rephrase those facts (hybrid).
"""

from __future__ import annotations

from ..data import mock_data as md
from ..safety import guardrails as g
from .base import AgentContext, AgentResult, BaseAgent


# --------------------------------------------------------------------------- #
# Symptom guidance (safe, non-diagnostic)
# --------------------------------------------------------------------------- #
class SymptomGuidanceAgent(BaseAgent):
    name = "symptom_guidance_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        dept = md.match_department(ctx.message)
        if dept:
            facts = (
                f"- We cannot diagnose, only suggest the next step.\n"
                f"- Based on the described symptoms, the relevant department is "
                f"usually {dept}.\n"
                f"- The patient can book a routine appointment, or choose "
                f"teleconsultation if available.\n"
                f"- If symptoms become severe or sudden, emergency care is advised."
            )
            fallback = (
                f"I can't diagnose the cause, but symptoms like these are usually "
                f"handled by the {dept} department. You can book an appointment, "
                f"or seek emergency care if things suddenly get worse."
            )
            data = {"recommended_department": dept, "doctors": md.doctors_in(dept)}
            actions = ["Find a doctor", "Book appointment", "Talk to a nurse"]
        else:
            facts = (
                "- We could not confidently map the symptom to a department.\n"
                "- Suggest General Medicine as a safe first step, or talking to "
                "a nurse.\n"
                "- We cannot diagnose."
            )
            fallback = (
                "I can't diagnose this, but a General Medicine consultation is a "
                "safe first step. Would you like me to find a doctor or connect "
                "you to a nurse?"
            )
            data = {"recommended_department": "General Medicine",
                    "doctors": md.doctors_in("General Medicine")}
            actions = ["Find a doctor", "Book appointment", "Talk to a nurse"]

        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply,
            agent=self.name,
            data=data,
            quick_actions=actions,
            disclaimer=g.MEDICAL_DISCLAIMER,
            llm_used=used,
        )


# --------------------------------------------------------------------------- #
# Doctor & department finder
# --------------------------------------------------------------------------- #
class DoctorFinderAgent(BaseAgent):
    name = "doctor_finder_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        dept = md.match_department(ctx.message)
        doctors = md.doctors_in(dept) if dept else md.DOCTORS

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


# --------------------------------------------------------------------------- #
# Appointment booking / reschedule / cancel
# --------------------------------------------------------------------------- #
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
        doctor = md.find_doctor_by_name(ctx.message)
        if not doctor:
            dept = md.match_department(ctx.message)
            candidates = md.doctors_in(dept) if dept else []
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
        ctx.session["appointments"].append(appointment)

        checklist = md.previsit_checklist(doctor["department"])
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
        doctor = next((d for d in md.DOCTORS if d["name"] == appt["doctor"]), None)
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
        facts = f"Appointment {appt['appointment_id']} with {appt['doctor']} is now cancelled."
        fallback = (
            f"Done — appointment {appt['appointment_id']} with {appt['doctor']} "
            f"has been cancelled. Would you like to book a new one?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"appointment": appt},
                           quick_actions=["Book appointment"], llm_used=used)


# --------------------------------------------------------------------------- #
# Pre-visit preparation
# --------------------------------------------------------------------------- #
class PreVisitAgent(BaseAgent):
    name = "previsit_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        appts = ctx.session.get("appointments", [])
        dept = appts[-1]["department"] if appts else md.match_department(ctx.message)
        checklist = md.previsit_checklist(dept)
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


# --------------------------------------------------------------------------- #
# Prescription explanation
# --------------------------------------------------------------------------- #
class PrescriptionAgent(BaseAgent):
    name = "prescription_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        rx = md.SAMPLE_PRESCRIPTION
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


# --------------------------------------------------------------------------- #
# Discharge assistant
# --------------------------------------------------------------------------- #
class DischargeAgent(BaseAgent):
    name = "discharge_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        ds = md.SAMPLE_DISCHARGE_SUMMARY
        facts = (
            f"Discharge summary (sample):\n"
            f"- Reason: {ds['reason']}; {ds['condition']}.\n"
            f"- Medicines for {ds['medicines_days']} days.\n"
            f"- Wound care: {ds['wound_care']}.\n"
            f"- Activity: {ds['activity']}.\n"
            f"- {ds['follow_up']}.\n"
            f"- Warning signs to call the hospital: {', '.join(ds['warning_signs'])}."
        )
        fallback = (
            "Here's your home-care plan after discharge:\n"
            f"• Medicines for {ds['medicines_days']} days\n"
            f"• {ds['wound_care']}\n"
            f"• {ds['activity']}\n"
            f"• {ds['follow_up']}\n"
            f"• Call us immediately if you notice: {', '.join(ds['warning_signs'])}.\n\n"
            "Would you like daily recovery check-ins?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"discharge_summary": ds},
                           quick_actions=["Start recovery check-ins", "Book follow-up"],
                           disclaimer=g.MEDICAL_DISCLAIMER, llm_used=used)


# --------------------------------------------------------------------------- #
# Billing & insurance
# --------------------------------------------------------------------------- #
class BillingInsuranceAgent(BaseAgent):
    name = "billing_insurance_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        if ctx.intent == "insurance_claim_query":
            return self._insurance(ctx)
        return self._billing(ctx)

    def _billing(self, ctx: AgentContext) -> AgentResult:
        bill = md.SAMPLE_BILL
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
        ins = md.SAMPLE_INSURANCE
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


# --------------------------------------------------------------------------- #
# General fallback agent
# --------------------------------------------------------------------------- #
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
