Below is a **full-fledged requirements document** you can use for your Hackcelerate solution.

# Requirements Document

## AI Patient Engagement & Communication Platform

### Hackcelerate AI Hackathon Solution

***

## 1. Document Purpose

This document defines the product, functional, non-functional, safety, compliance, and demo requirements for an **AI-powered Patient Engagement & Communication Platform**.

The solution will use an **Orchestrator AI Agent** and multiple specialized AI agents to support patients across the complete care journey, from symptom discovery to appointment booking, consultation support, billing, discharge, recovery, and long-term engagement.

The platform is designed for a healthcare provider such as a hospital, clinic, diagnostic center, or integrated care network.

***

## 2. Product Vision

To build an intelligent, safe, multilingual, journey-aware patient engagement assistant that helps patients get the right information, access care faster, understand medical and administrative processes, and stay engaged throughout their care journey.

The solution should reduce patient confusion, lower call center load, improve appointment conversion, increase adherence to care instructions, and enable timely escalation for emergencies or complex queries.

***

## 3. Product Name Suggestions

You can use one of these for the hackathon:

1. **CarePath AI**
2. **Patient Journey Companion**
3. **CareNavigator AI**
4. **HealthConnect Agentic AI**
5. **MediAssist Journey AI**
6. **CareFlow AI**
7. **PatientConnect AI**
8. **HealGuide AI**

Recommended name:

## **CarePath AI — Agentic Patient Journey Companion**

Reason: It clearly communicates that the platform guides patients through their healthcare journey.

***

## 4. Problem Statement

Patients often struggle with fragmented communication across the healthcare journey. They may not know:

* Which doctor or department to consult
* Whether symptoms require emergency care
* How to book, reschedule, or cancel appointments
* What documents or instructions are needed before a visit
* Where to go after reaching the hospital
* How to understand prescriptions, lab reports, bills, insurance status, or discharge instructions
* When to follow up or seek help during recovery

Hospitals also face operational challenges:

* High call center volume
* Repeated queries for appointments, billing, directions, reports, and insurance
* Poor post-discharge engagement
* Delayed escalation of serious symptoms
* Limited visibility into patient concerns and journey gaps

The proposed solution addresses these problems using an **Army of AI Agents** coordinated by a central **Orchestrator AI Agent**.

***

## 5. Solution Overview

The platform will provide a conversational AI interface where patients or caregivers can ask healthcare-related administrative and engagement queries.

The user query will first go to the **Orchestrator AI Agent**. The orchestrator will:

1. Understand the query
2. Identify patient context and journey stage
3. Detect intent
4. Check safety and privacy rules
5. Route the query to the correct specialized AI agent
6. Collect the response
7. Validate and improve the response
8. Call another agent if needed
9. Return a clear, safe, human-friendly response to the user
10. Escalate to a human team when required

***

## 6. Target Users

### 6.1 Primary Users

* Patients
* Caregivers
* Elderly patients
* Chronic disease patients
* First-time hospital visitors
* Surgery patients
* Insurance/cashless claim patients
* Emergency patient family members

### 6.2 Secondary Users

* Hospital front desk team
* Appointment desk
* Billing team
* Insurance/TPA desk
* Nurses
* Doctors or doctor coordinators
* Hospital administrators
* Patient experience team

***

## 7. Key Patient Personas

### Persona 1: First-Time Outpatient Visitor

A working professional visiting the hospital for the first time due to symptoms such as headache, fever, knee pain, or stomach pain.

Needs:

* Find correct doctor
* Book appointment
* Know consultation fee
* Understand location and documents

High-value features:

* Symptom-to-specialty guidance
* Doctor search
* Appointment booking
* Pre-visit checklist
* Hospital navigation

***

### Persona 2: Chronic Disease Patient

A diabetes or hypertension patient requiring regular monitoring, tests, medicine reminders, and follow-ups.

Needs:

* Medication reminders
* Lab test reminders
* Follow-up booking
* Vitals tracking
* Lifestyle education

High-value features:

* Chronic care reminders
* Vitals dashboard
* Medicine adherence tracking
* Follow-up automation

***

### Persona 3: Elderly Patient

A senior citizen who needs simple instructions, caregiver support, and accessibility features.

Needs:

* Voice support
* Large text/simple language
* Caregiver alerts
* Appointment reminders
* Emergency help

High-value features:

* Caregiver mode
* Voice input/output
* Medication schedule
* Wheelchair assistance
* Emergency escalation

***

### Persona 4: Caregiver

A family member managing treatment for a parent, child, or post-surgery patient.

Needs:

* Discharge instructions
* Medicine schedule
* Warning signs
* Follow-up reminders
* Billing support

High-value features:

* Caregiver dashboard
* Recovery check-ins
* Escalation workflow
* Document access

***

### Persona 5: Emergency Patient

A patient or family member reporting severe symptoms such as chest pain, breathing difficulty, stroke signs, or loss of consciousness.

Needs:

* Immediate emergency guidance
* Ambulance support
* ER direction
* Human escalation

High-value features:

* Red flag detection
* Emergency response template
* One-tap call support
* ER navigation

***

## 8. Scope

## 8.1 MVP Scope for Hackathon

The MVP should focus on the most demonstrable and valuable patient journey flows.

### Must-Have MVP Features

1. Chat interface
2. Orchestrator AI Agent
3. Intent detection
4. Patient journey stage detection
5. Safe symptom guidance
6. Department recommendation
7. Doctor search using mock doctor data
8. Appointment booking mock flow
9. Pre-visit checklist generation
10. Prescription explanation using sample data
11. Discharge instruction explanation using sample data
12. Billing and insurance FAQ support
13. Emergency red flag escalation
14. Human handoff simulation
15. Conversation audit log

***

## 8.2 Optional 48-Hour Features

1. Patient journey timeline
2. Caregiver mode
3. Multilingual support: English, Hindi, Marathi
4. Medicine reminder simulation
5. Lab report explanation
6. Recovery monitoring flow
7. Admin dashboard
8. Escalation queue
9. Patient satisfaction score
10. Analytics dashboard

***

## 8.3 Out of Scope for Hackathon MVP

The MVP should not attempt to fully implement:

* Real hospital EHR integration
* Real payment processing
* Real insurance approval
* Real doctor messaging
* Real prescriptions from live medical systems
* Actual diagnosis
* Treatment modification
* Real emergency dispatch

These can be shown as future integrations or simulated using mock APIs/data.

***

# 9. Agentic Architecture

## 9.1 High-Level Agent Model

The system will use a central orchestrator and multiple specialized AI agents.

### Core Agent Flow

```text
User Query
   ↓
Orchestrator AI Agent
   ↓
Safety & Privacy Guardrail Check
   ↓
Intent Detection
   ↓
Patient Journey Stage Detection
   ↓
Route to Specialized Agent
   ↓
Agent Response
   ↓
Response Validation
   ↓
Optional Additional Agent Call
   ↓
Final Response to User
   ↓
Audit Log / Escalation if Needed
```

***

## 9.2 Orchestrator AI Agent

### Purpose

The Orchestrator AI Agent is the central decision-making agent. It does not directly answer all queries. Instead, it decides which specialized agent should handle the request.

### Responsibilities

* Receive user query
* Identify patient intent
* Identify patient journey stage
* Detect urgency or emergency symptoms
* Check if authentication is required
* Route the query to the correct agent
* Coordinate multi-agent workflows
* Merge responses from multiple agents
* Apply safety and privacy guardrails
* Trigger human handoff when required
* Return final response to the user

### Example

User says:

> “My father was discharged yesterday and now has fever. What should I do?”

Orchestrator should:

1. Detect stage: Post-discharge care
2. Detect risk: Fever after discharge
3. Route to Recovery Monitoring Agent
4. Route to Safety Guardrail Agent
5. Possibly route to Nurse Handoff Agent
6. Respond with safe guidance and escalation recommendation

***

# 10. Specialized AI Agents

## 10.1 Patient Journey Agent

### Purpose

Determines where the patient is in the care journey.

### Inputs

* User query
* Patient profile
* Appointment status
* Recent discharge status
* Active prescriptions
* Previous conversation context

### Outputs

* Journey stage
* Next best action
* Supporting context for orchestrator

### Supported Journey Stages

1. Symptom discovery
2. Doctor discovery
3. Appointment booking
4. Pre-visit preparation
5. Hospital arrival/check-in
6. Consultation
7. Diagnostics/lab work
8. Prescription support
9. Surgery/procedure
10. Inpatient admission
11. Discharge planning
12. Billing and insurance
13. Post-discharge care
14. Follow-up
15. Medication reminders
16. Recovery monitoring
17. Preventive care

***

## 10.2 Symptom Guidance Agent

### Purpose

Provides safe symptom guidance without diagnosis.

### Responsibilities

* Ask basic triage questions
* Detect emergency red flags
* Suggest care level:
  * Emergency
  * Urgent OPD
  * Routine appointment
  * Teleconsultation
* Recommend department where appropriate
* Always include disclaimer

### Must Not Do

* Diagnose disease
* Prescribe medicine
* Suggest dosage change
* Replace doctor consultation

### Example Response

> I can help you decide the next step, but I cannot diagnose the cause. Chest pain can sometimes be urgent, especially if it is severe, spreading to the arm/jaw, associated with sweating, breathlessness, or dizziness. Please seek emergency care immediately or call local emergency services.

***

## 10.3 Doctor and Department Finder Agent

### Purpose

Helps patients find the right department or doctor.

### Responsibilities

* Map symptoms to departments
* Search doctor directory
* Filter by:
  * Specialty
  * Location
  * Language
  * Gender
  * Availability
  * Teleconsultation
* Explain specialty names in simple language

### Example

User:

> “Which doctor should I see for knee pain?”

Response:

> Knee pain is usually handled by the Orthopedics department. I found two orthopedic doctors available this week. Would you like to book the earliest slot?

***

## 10.4 Appointment Agent

### Purpose

Handles appointment booking, rescheduling, cancellation, and confirmation.

### Responsibilities

* Show available slots
* Book appointment
* Reschedule appointment
* Cancel appointment
* Confirm appointment details
* Send mock confirmation
* Trigger pre-visit checklist

### MVP Data Needed

* Doctor list
* Department list
* Available slots
* Appointment status

***

## 10.5 Pre-Visit Preparation Agent

### Purpose

Guides patients before hospital visit.

### Responsibilities

* Generate visit checklist
* Ask patient to carry required documents
* Share fasting instructions
* Share location and parking info
* Remind insurance documents
* Suggest arrival time

### Example Output

For cardiology OPD:

* Carry previous ECG/Echo reports if available
* Carry current medicine list
* Bring ID proof
* Bring insurance card if applicable
* Reach 20 minutes before appointment

***

## 10.6 Check-In and Navigation Agent

### Purpose

Helps patients after they arrive at the hospital.

### Responsibilities

* Digital check-in
* Generate token number
* Show queue/wait time
* Guide to counter/room
* Request wheelchair assistance
* Alert patient about doctor delay

### MVP Simulation

Use mock token and waiting time.

Example:

> You are checked in. Your token number is C-14. Estimated waiting time is 20 minutes. Please proceed to Cardiology OPD, Room 204.

***

## 10.7 Lab and Diagnostic Agent

### Purpose

Supports diagnostic tests and reports.

### Responsibilities

* Explain test preparation
* Share report availability status
* Explain lab values in simple language with disclaimer
* Alert critical results
* Offer home sample collection

### Must Not Do

* Diagnose based on report
* Suggest treatment independently

***

## 10.8 Prescription Support Agent

### Purpose

Helps patients understand prescribed medicines.

### Responsibilities

* Explain medicine timing
* Explain before/after food instructions
* Create medicine schedule
* Provide missed-dose general guidance from approved content
* Set reminder simulation
* Escalate serious side effects

### Must Not Do

* Change medicine dosage
* Stop medicines
* Modify antibiotics/insulin/blood thinners
* Handle unsafe medication interactions without human handoff

***

## 10.9 Discharge Assistant Agent

### Purpose

Turns discharge instructions into simple, actionable steps.

### Responsibilities

* Explain discharge summary
* Create home care checklist
* Create medicine schedule
* Explain activity restrictions
* Explain wound care instructions
* Identify warning signs
* Book follow-up
* Trigger recovery monitoring

### Example Output

> Your discharge plan includes medicines for 5 days, wound care once daily, no heavy lifting for 2 weeks, and follow-up after 7 days. Please contact the hospital immediately if you notice fever, increasing pain, swelling, bleeding, or breathing difficulty.

***

## 10.10 Billing and Insurance Agent

### Purpose

Handles billing, estimates, invoices, payment support, insurance checklist, and claim status.

### Responsibilities

* Explain bill breakup
* Share estimate
* Show insurance approval status
* Explain uncovered charges
* Provide cashless claim document checklist
* Provide payment link simulation
* Escalate disputes to billing team

### Must Not Do

* Show bill details without authentication
* Expose insurance information to unauthorized caregiver

***

## 10.11 Recovery Monitoring Agent

### Purpose

Supports patients after discharge.

### Responsibilities

* Daily recovery check-ins
* Pain score tracking
* Fever tracking
* Wound symptom tracking
* Vitals logging
* Red flag detection
* Nurse callback escalation
* Follow-up reminder

### Sample Recovery Questions

* Do you have fever?
* What is your pain score from 1 to 10?
* Is there redness, swelling, or discharge from wound?
* Did you take your medicines today?
* Are you having breathing difficulty?

***

## 10.12 Medication Reminder Agent

### Purpose

Helps patients follow medicine schedules.

### Responsibilities

* Create medicine reminders
* Send caregiver alerts
* Track dose adherence
* Remind refills
* Escalate side effects

***

## 10.13 Caregiver Agent

### Purpose

Allows family members to support patient care with permission.

### Responsibilities

* Add caregiver
* Manage caregiver permissions
* Share appointment reminders
* Share medication schedules
* Share recovery alerts
* Restrict sensitive data based on consent

### Permission Examples

Caregiver can access:

* Appointment reminders
* Medicine schedule
* Follow-up dates

Caregiver may need additional consent for:

* Billing data
* Lab reports
* Diagnosis notes
* Insurance details

***

## 10.14 Human Handoff Agent

### Purpose

Routes unresolved, risky, sensitive, or low-confidence cases to human teams.

### Handoff Teams

* Appointment desk
* Billing team
* Insurance desk
* Nurse
* Doctor coordinator
* Emergency team
* Technical support

### Handoff Triggers

* Emergency symptoms
* Low-confidence response
* Patient asks for diagnosis
* Medication safety issue
* Billing dispute
* Insurance rejection
* Angry or distressed patient
* Repeated failed attempts
* Sensitive data access issue

***

## 10.15 Safety Guardrail Agent

### Purpose

Applies safety, privacy, and healthcare response rules.

### Responsibilities

* Detect emergency symptoms
* Add medical disclaimers
* Block unsafe clinical advice
* Enforce authentication checks
* Prevent PHI exposure
* Detect patient distress
* Recommend human handoff
* Maintain audit trail

***

# 11. Functional Requirements

## 11.1 Chat Interface

### Requirement

The system shall provide a conversational interface for patients and caregivers.

### Acceptance Criteria

* User can enter free-text queries
* System responds in natural language
* System can ask follow-up questions
* System supports quick action buttons
* System shows disclaimers where needed
* System can show structured cards for doctors, slots, bills, reminders, and checklists

***

## 11.2 Intent Detection

### Requirement

The system shall detect the intent of the user query.

### Supported Intents

* Symptom guidance
* Emergency help
* Doctor search
* Department search
* Appointment booking
* Appointment reschedule
* Appointment cancellation
* Pre-visit checklist
* Hospital navigation
* Lab test support
* Lab report explanation
* Prescription help
* Discharge instruction help
* Billing query
* Insurance claim query
* Recovery monitoring
* Follow-up booking
* Medication reminder
* Caregiver access
* Human handoff

### Acceptance Criteria

* System identifies primary intent
* System identifies secondary intent if present
* System asks clarification if intent is unclear
* System routes query to correct agent

***

## 11.3 Patient Journey Stage Detection

### Requirement

The system shall identify the patient’s current journey stage.

### Acceptance Criteria

* System identifies stage based on query and patient context
* System suggests next best action
* System updates journey timeline
* System remembers current stage during conversation

***

## 11.4 Safe Symptom Guidance

### Requirement

The system shall provide safe, non-diagnostic symptom guidance.

### Acceptance Criteria

* System does not provide final diagnosis
* System identifies red flag symptoms
* System recommends emergency escalation for urgent symptoms
* System recommends relevant department for non-emergency symptoms
* System adds medical disclaimer
* System offers appointment booking if appropriate

***

## 11.5 Emergency Escalation

### Requirement

The system shall detect emergency symptoms and immediately recommend emergency care.

### Emergency Red Flags

* Chest pain
* Difficulty breathing
* Stroke symptoms
* Loss of consciousness
* Severe bleeding
* Seizure
* Severe allergic reaction
* Severe abdominal pain in pregnancy
* High fever in infants
* Sudden confusion or weakness
* Severe headache with blurred vision
* Suicidal thoughts or self-harm risk

### Acceptance Criteria

* System interrupts normal flow for emergency cases
* System provides emergency instructions
* System shows emergency contact option
* System does not continue routine appointment flow unless user confirms non-emergency context
* System logs escalation event

***

## 11.6 Doctor and Department Search

### Requirement

The system shall help patients find doctors and departments.

### Acceptance Criteria

* User can search by symptom
* User can search by specialty
* User can filter by location
* User can filter by language
* User can filter by gender
* User can view consultation fee
* User can view available appointment slots

***

## 11.7 Appointment Booking

### Requirement

The system shall allow users to book, reschedule, cancel, and confirm appointments.

### Acceptance Criteria

* User can select doctor
* User can select date and time
* System confirms appointment
* System generates appointment ID
* System provides appointment details
* System triggers pre-visit checklist
* System supports reschedule and cancellation simulation

***

## 11.8 Pre-Visit Checklist

### Requirement

The system shall generate a personalized pre-visit checklist.

### Acceptance Criteria

Checklist may include:

* ID proof
* Appointment confirmation
* Previous reports
* Current medicines
* Insurance card
* Fasting instructions
* Arrival time
* Department location
* Parking details

***

## 11.9 Digital Check-In

### Requirement

The system shall support mock digital check-in.

### Acceptance Criteria

* User can confirm arrival
* System generates token
* System shows waiting time
* System shows room/counter direction
* System allows wheelchair assistance request

***

## 11.10 Prescription Explanation

### Requirement

The system shall explain prescriptions in simple language using approved prescription data.

### Acceptance Criteria

* System explains medicine name, timing, and duration
* System distinguishes before/after food
* System creates medicine schedule
* System supports reminder simulation
* System escalates side-effect concerns
* System does not change dosage or duration

***

## 11.11 Discharge Summary Explanation

### Requirement

The system shall simplify discharge instructions.

### Acceptance Criteria

* System summarizes discharge instructions
* System creates medication schedule
* System lists warning signs
* System lists diet and activity restrictions
* System shows follow-up date
* System offers recovery check-ins

***

## 11.12 Billing and Insurance Support

### Requirement

The system shall answer billing and insurance queries.

### Acceptance Criteria

* System explains mock bill breakup
* System shows insurance claim status
* System lists pending documents
* System explains uncovered charges
* System provides payment link simulation
* System supports human handoff for disputes

***

## 11.13 Recovery Monitoring

### Requirement

The system shall support post-discharge recovery tracking.

### Acceptance Criteria

* System asks daily recovery questions
* System records fever, pain score, wound symptoms, vitals
* System detects red flags
* System escalates to nurse/human team
* System shows recovery status

***

## 11.14 Follow-Up Management

### Requirement

The system shall support follow-up appointment reminders and booking.

### Acceptance Criteria

* System reminds patient of follow-up
* System allows booking with same doctor
* System allows report upload simulation
* System supports teleconsultation option
* System informs what documents/reports to bring

***

## 11.15 Caregiver Mode

### Requirement

The system shall allow a caregiver to manage patient-related tasks with consent.

### Acceptance Criteria

* Patient can add caregiver
* Patient can define access permissions
* Caregiver can receive reminders
* Caregiver can view permitted information only
* System blocks unauthorized sensitive data access

***

## 11.16 Multilingual and Simple Language Support

### Requirement

The system shall support simple and multilingual responses.

### MVP Languages

* English
* Hindi
* Marathi

### Acceptance Criteria

* User can ask query in supported language
* System responds in the same or selected language
* System uses simple, non-technical wording
* System can explain medical terms in simple language

***

## 11.17 Human Handoff

### Requirement

The system shall escalate to human staff when needed.

### Acceptance Criteria

* System identifies handoff need
* System categorizes issue
* System creates escalation ticket
* System assigns team
* System shows expected response time
* System keeps conversation history for staff

***

# 12. Non-Functional Requirements

## 12.1 Performance

* Chat response should be generated within 3 to 5 seconds for standard queries
* Emergency responses should be prioritized immediately
* Appointment slot lookup should complete within 2 seconds in MVP mock flow

***

## 12.2 Availability

* Platform should be designed for 24/7 availability
* Emergency and symptom guidance flows should not depend on business hours
* Human handoff availability may vary by department

***

## 12.3 Security

* Sensitive data must require authentication
* All patient data access must be logged
* Role-based access control must be supported
* Caregiver access must be consent-based
* Payment and insurance details must not be exposed without verification

***

## 12.4 Privacy

The system must protect:

* Patient name
* Contact number
* Appointment details
* Diagnosis
* Prescription
* Lab reports
* Discharge summary
* Insurance details
* Billing details

***

## 12.5 Auditability

The system shall maintain logs for:

* User query
* Detected intent
* Detected journey stage
* Selected agent
* Response given
* Safety flags
* Escalation decision
* Human handoff
* Consent action
* Sensitive data access

***

## 12.6 Usability

* Interface should be simple and friendly
* Responses should avoid medical jargon
* Long answers should be broken into sections
* Critical alerts should be visually highlighted
* Elderly users should be supported with larger text and voice support in future scope

***

## 12.7 Scalability

Future architecture should support:

* Multiple hospital branches
* Multiple departments
* Multiple languages
* Multiple patient profiles
* Integration with EHR, billing, lab, pharmacy, and insurance systems

***

# 13. Data Requirements

## 13.1 MVP Demo Data

The hackathon MVP should include mock data.

### Doctor Data

Minimum 5 doctors:

* Cardiologist
* Orthopedic doctor
* General physician
* Gynecologist
* Dermatologist

### Department Data

Minimum 5 departments:

* Cardiology
* Orthopedics
* General Medicine
* Gynecology
* Dermatology

### Appointment Slots

Minimum 3 slots per doctor.

### Prescription Data

Minimum 2 sample prescriptions.

### Discharge Summary

Minimum 1 sample discharge summary.

### Billing Data

Minimum 1 sample bill with itemized charges.

### Insurance Data

Minimum 1 sample claim status with pending documents.

### Lab Data

Optional:

* CBC report
* Lipid profile
* Blood sugar report

***

# 14. Example Demo Data

## 14.1 Doctor Directory

| Doctor       | Department       | Language              | Fee   | Availability   |
| ------------ | ---------------- | --------------------- | ----- | -------------- |
| Dr. Mehta    | Cardiology       | English, Hindi        | ₹1200 | Today 5 PM     |
| Dr. Kulkarni | Orthopedics      | English, Marathi      | ₹900  | Tomorrow 11 AM |
| Dr. Shah     | General Medicine | English, Hindi        | ₹700  | Today 3 PM     |
| Dr. Rao      | Gynecology       | English, Hindi        | ₹1000 | Saturday 10 AM |
| Dr. Iyer     | Dermatology      | English, Tamil, Hindi | ₹800  | Friday 4 PM    |

***

## 14.2 Sample Appointment

```text
Appointment ID: APT-10245
Patient: Demo Patient
Doctor: Dr. Kulkarni
Department: Orthopedics
Date: 30 June 2026
Time: 11:00 AM
Location: OPD Block, Room 204
Fee: ₹900
Status: Confirmed
```

***

## 14.3 Sample Prescription

```text
Medicine 1: Paracetamol 500 mg
Timing: After food
Frequency: Twice daily
Duration: 3 days

Medicine 2: Pantoprazole 40 mg
Timing: Before breakfast
Frequency: Once daily
Duration: 5 days
```

***

## 14.4 Sample Discharge Summary

```text
Patient was admitted for minor knee surgery.
Discharged in stable condition.
Medicines prescribed for 5 days.
Dressing change required every alternate day.
Avoid heavy walking for 2 weeks.
Follow-up after 7 days.
Warning signs: fever, severe pain, swelling, bleeding, wound discharge.
```

***

## 14.5 Sample Bill

```text
Consultation: ₹900
Lab Tests: ₹1500
Procedure Charges: ₹12000
Room Charges: ₹5000
Pharmacy: ₹2200
Insurance Approved: ₹16000
Patient Payable: ₹5600
```

***

# 15. User Stories

## 15.1 Symptom Guidance

As a patient, I want to describe my symptoms so that I can understand whether I should visit emergency, book an appointment, or consult online.

### Acceptance Criteria

* Bot asks relevant follow-up questions
* Bot identifies red flags
* Bot avoids diagnosis
* Bot recommends next care step

***

## 15.2 Doctor Search

As a patient, I want to find the right doctor based on my symptoms so that I do not have to understand medical specialties myself.

### Acceptance Criteria

* Bot maps symptom to department
* Bot shows available doctors
* Bot shows fee and slot
* Bot allows booking

***

## 15.3 Appointment Booking

As a patient, I want to book an appointment using chat so that I do not need to call the hospital.

### Acceptance Criteria

* Bot shows available slots
* User selects slot
* Appointment is confirmed
* Confirmation details are shown

***

## 15.4 Pre-Visit Checklist

As a patient, I want to know what to carry before my hospital visit so that I do not miss important documents.

### Acceptance Criteria

* Bot generates checklist
* Bot includes department-specific instructions
* Bot includes arrival time and location

***

## 15.5 Prescription Explanation

As a patient, I want my prescription explained in simple language so that I can take medicines correctly.

### Acceptance Criteria

* Bot explains timing
* Bot explains before/after food
* Bot creates schedule
* Bot warns not to change dosage without doctor approval

***

## 15.6 Discharge Support

As a caregiver, I want discharge instructions converted into a simple checklist so that I can take care of the patient at home.

### Acceptance Criteria

* Bot summarizes discharge summary
* Bot lists medicines
* Bot lists warning signs
* Bot creates follow-up reminder

***

## 15.7 Billing Support

As a patient, I want to understand my bill so that I know what I need to pay and what insurance covers.

### Acceptance Criteria

* Bot explains bill breakup
* Bot shows insurance-approved amount
* Bot shows patient payable amount
* Bot offers billing handoff

***

## 15.8 Recovery Monitoring

As a discharged patient, I want daily recovery check-ins so that complications can be detected early.

### Acceptance Criteria

* Bot asks recovery questions
* Bot logs symptoms
* Bot detects red flags
* Bot escalates to nurse if needed

***

# 16. Safety and Compliance Requirements

## 16.1 No Diagnosis

The system shall not provide final diagnosis.

Incorrect:

> You have pneumonia.

Correct:

> Your symptoms may need medical evaluation. Please consult a doctor for diagnosis.

***

## 16.2 Medical Disclaimer

For clinical or symptom-related responses, the system must include:

> This is general information and not a substitute for professional medical advice.

***

## 16.3 Emergency Escalation

For red flag symptoms, the system must immediately say:

> This may be urgent. Please seek emergency medical care immediately or call local emergency services.

***

## 16.4 Medication Safety

The system must not independently recommend:

* Changing dosage
* Stopping medicines
* Extending antibiotics
* Modifying insulin
* Modifying blood thinners
* Combining medicines without verification

***

## 16.5 Privacy Protection

The system must not expose personal medical, billing, insurance, or report data without authentication.

***

## 16.6 Authentication Rules

Authentication is required for:

* Appointment details
* Lab reports
* Prescriptions
* Discharge summary
* Bills
* Insurance status
* Payment links
* Caregiver access

Possible verification options:

* Login
* OTP
* Patient ID
* Date of birth
* Registered mobile number

***

# 17. Orchestrator Decision Logic

## 17.1 Routing Logic

| User Query Type                  | Primary Agent           | Secondary Agent         |
| -------------------------------- | ----------------------- | ----------------------- |
| Chest pain, breathing difficulty | Safety Guardrail Agent  | Emergency/Handoff Agent |
| Which doctor should I consult?   | Doctor Finder Agent     | Symptom Guidance Agent  |
| Book appointment                 | Appointment Agent       | Pre-Visit Agent         |
| What documents should I bring?   | Pre-Visit Agent         | Appointment Agent       |
| Where is my room?                | Navigation Agent        | Check-In Agent          |
| Explain my prescription          | Prescription Agent      | Safety Guardrail Agent  |
| Explain discharge summary        | Discharge Agent         | Recovery Agent          |
| Is my insurance approved?        | Billing/Insurance Agent | Handoff Agent           |
| I have fever after surgery       | Recovery Agent          | Safety Guardrail Agent  |
| Remind me of medicines           | Medication Agent        | Caregiver Agent         |

***

## 17.2 Sample Orchestration Flow

User:

> “I have knee pain. Can I book an appointment?”

System flow:

```text
Orchestrator receives query
↓
Intent detected: Doctor search + Appointment booking
↓
Journey stage: Care discovery / Appointment access
↓
Doctor Finder Agent maps knee pain to Orthopedics
↓
Appointment Agent fetches available orthopedic slots
↓
Pre-Visit Agent prepares checklist
↓
Orchestrator combines response
↓
Final response shown to user
```

Final response:

> Knee pain is usually handled by the Orthopedics department. Dr. Kulkarni is available tomorrow at 11 AM. Consultation fee is ₹900. Would you like me to book this appointment?  
> If booked, please carry previous X-rays, reports, ID proof, and your current medicine list.

***

# 18. Admin Dashboard Requirements

## 18.1 Dashboard Features

The hospital staff dashboard should show:

* Total conversations
* Active escalations
* Emergency alerts
* Appointment requests
* Billing queries
* Insurance queries
* Recovery risk alerts
* Patient satisfaction score
* Common query categories
* Agent performance

***

## 18.2 Escalation Queue

Each escalation should include:

* Ticket ID
* Patient name or masked ID
* Query
* Category
* Priority
* Assigned team
* Status
* Created time
* Conversation summary

***

# 19. Analytics Requirements

The system should track:

* Most common patient queries
* Most common pain points
* Appointment conversion rate
* Emergency escalation count
* Human handoff count
* Average response time
* Patient satisfaction
* Drop-off points
* Post-discharge risk alerts
* Missed medication reminders

***

# 20. Suggested MVP Screens

## 20.1 Patient Chat Screen

Features:

* Chat window
* Quick action buttons:
  * Book appointment
  * Find doctor
  * Billing help
  * Prescription help
  * Emergency help
* Patient journey status
* Human handoff option

***

## 20.2 Patient Timeline Screen

Example timeline:

```text
Appointment Booked → Pre-Visit Checklist → Consultation → Prescription → Follow-Up → Recovery
```

***

## 20.3 Doctor Selection Screen

Shows:

* Doctor name
* Department
* Fee
* Language
* Available slots
* Book button

***

## 20.4 Appointment Confirmation Screen

Shows:

* Appointment ID
* Doctor
* Date/time
* Location
* Fee
* Checklist

***

## 20.5 Recovery Monitoring Screen

Shows:

* Pain score
* Fever status
* Medicine taken
* Warning signs
* Nurse escalation button

***

## 20.6 Admin Escalation Dashboard

Shows:

* Queue of escalated cases
* Priority label
* Assigned department
* Conversation summary
* Action buttons

***

# 21. Demo Scenarios

## Demo Scenario 1: Emergency Detection

User:

> My father has chest pain and breathing difficulty.

Expected bot behavior:

* Detect emergency red flag
* Stop normal flow
* Recommend immediate emergency care
* Show emergency contact
* Offer ER navigation
* Create emergency escalation log

***

## Demo Scenario 2: First-Time OPD Visitor

User:

> I have knee pain. Which doctor should I consult?

Expected bot behavior:

* Suggest Orthopedics
* Show available doctors
* Book appointment
* Generate pre-visit checklist
* Show hospital direction

***

## Demo Scenario 3: Appointment Booking

User:

> Book an appointment with a cardiologist tomorrow.

Expected bot behavior:

* Show available cardiologists
* Show slots
* Confirm selected appointment
* Generate appointment ID
* Send checklist

***

## Demo Scenario 4: Prescription Support

User:

> When should I take these medicines?

Expected bot behavior:

* Explain medicine schedule from sample prescription
* Show morning/evening plan
* Mention before/after food
* Offer reminder setup
* Add medication safety disclaimer

***

## Demo Scenario 5: Discharge Assistant

User:

> I was discharged after surgery. What should I do at home?

Expected bot behavior:

* Summarize discharge instructions
* Create home care checklist
* List warning signs
* Start recovery check-in
* Offer follow-up booking

***

## Demo Scenario 6: Billing and Insurance

User:

> Is my insurance approval done?

Expected bot behavior:

* Ask authentication if required
* Show mock approval status
* Show pending documents
* Explain patient payable amount
* Offer insurance desk handoff

***

# 22. Success Metrics

## 22.1 Patient Experience Metrics

* Reduced time to find correct doctor
* Faster appointment booking
* Better understanding of care instructions
* Improved medication adherence
* Improved discharge clarity
* Higher patient satisfaction

***

## 22.2 Operational Metrics

* Reduced call center load
* Reduced repeated billing queries
* Reduced appointment no-shows
* Reduced missed follow-ups
* Faster human escalation
* Better visibility into patient concerns

***

## 22.3 Safety Metrics

* Emergency red flags detected
* Unsafe medication questions escalated
* Low-confidence responses handed off
* Sensitive data protected
* Audit logs maintained

***

# 23. Recommended Hackathon Build Plan

## Phase 1: Core Foundation

Build:

* Chat UI
* Orchestrator
* Intent detection
* Mock data
* Basic routing to agents

***

## Phase 2: High-Impact Agents

Build:

* Symptom Guidance Agent
* Doctor Finder Agent
* Appointment Agent
* Pre-Visit Agent
* Billing Agent
* Discharge Agent
* Safety Guardrail Agent

***

## Phase 3: Demo Experience

Build:

* Patient timeline
* Recovery monitoring simulation
* Human handoff queue
* Admin dashboard
* Conversation audit log

***

## Phase 4: Polish

Add:

* Multilingual examples
* Better UI cards
* Demo scripts
* Safety disclaimers
* Journey-aware responses
* Metrics dashboard

***

# 24. Recommended MVP Feature Priority

## Must Build

1. Orchestrator agent
2. Chat interface
3. Intent detection
4. Doctor/department recommendation
5. Appointment booking mock
6. Pre-visit checklist
7. Emergency escalation
8. Prescription explanation
9. Discharge support
10. Billing/insurance support

## Should Build

1. Patient timeline
2. Recovery check-in
3. Human handoff queue
4. Conversation logs
5. Admin dashboard

## Could Build

1. Voice support
2. Multilingual support
3. Caregiver mode
4. Lab report explanation
5. Patient satisfaction score

***

# 25. Final Recommended Positioning for Hackathon

You can present the platform as:

## **CarePath AI: An Agentic Patient Journey Companion**

A healthcare communication platform powered by an orchestrator and specialized AI agents that helps patients navigate every step of their care journey safely and intelligently.

### One-line pitch

> CarePath AI is a journey-aware, safety-first patient engagement assistant that uses an orchestrator and specialized AI agents to guide patients from symptom discovery to appointment booking, discharge, recovery, billing, and long-term care.

### Strong demo message

> This is not just a hospital FAQ chatbot. It is an agentic patient journey companion that understands where the patient is, routes queries to the right AI agent, protects patient safety, and escalates to humans when needed.
