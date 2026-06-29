"""Mock hospital data for the hackathon MVP.

Everything here is demo data — no real EHR / billing / insurance integration.
Mirrors the sample data described in the requirements document (section 14).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Departments
# --------------------------------------------------------------------------- #
DEPARTMENTS: list[dict] = [
    {"name": "Cardiology", "description": "Heart and blood-vessel conditions"},
    {"name": "Orthopedics", "description": "Bones, joints, muscles and spine"},
    {"name": "General Medicine", "description": "Fever, infections, general adult care"},
    {"name": "Gynecology", "description": "Women's health and pregnancy care"},
    {"name": "Dermatology", "description": "Skin, hair and nail conditions"},
]

# --------------------------------------------------------------------------- #
# Doctor directory (>= 3 slots each)
# --------------------------------------------------------------------------- #
DOCTORS: list[dict] = [
    {
        "id": "doc-mehta",
        "name": "Dr. Mehta",
        "department": "Cardiology",
        "languages": ["English", "Hindi"],
        "gender": "M",
        "fee": 1200,
        "teleconsult": True,
        "slots": ["Today 5:00 PM", "Tomorrow 10:00 AM", "Tomorrow 4:30 PM"],
    },
    {
        "id": "doc-kulkarni",
        "name": "Dr. Kulkarni",
        "department": "Orthopedics",
        "languages": ["English", "Marathi"],
        "gender": "M",
        "fee": 900,
        "teleconsult": False,
        "slots": ["Tomorrow 11:00 AM", "Tomorrow 3:00 PM", "Saturday 9:30 AM"],
    },
    {
        "id": "doc-shah",
        "name": "Dr. Shah",
        "department": "General Medicine",
        "languages": ["English", "Hindi"],
        "gender": "M",
        "fee": 700,
        "teleconsult": True,
        "slots": ["Today 3:00 PM", "Today 6:00 PM", "Tomorrow 9:00 AM"],
    },
    {
        "id": "doc-rao",
        "name": "Dr. Rao",
        "department": "Gynecology",
        "languages": ["English", "Hindi"],
        "gender": "F",
        "fee": 1000,
        "teleconsult": True,
        "slots": ["Saturday 10:00 AM", "Saturday 12:30 PM", "Monday 11:00 AM"],
    },
    {
        "id": "doc-iyer",
        "name": "Dr. Iyer",
        "department": "Dermatology",
        "languages": ["English", "Tamil", "Hindi"],
        "gender": "F",
        "fee": 800,
        "teleconsult": True,
        "slots": ["Friday 4:00 PM", "Friday 5:30 PM", "Saturday 2:00 PM"],
    },
]

# --------------------------------------------------------------------------- #
# Symptom -> department keyword mapping (non-emergency routing)
# --------------------------------------------------------------------------- #
SYMPTOM_DEPARTMENT_MAP: dict[str, list[str]] = {
    "Cardiology": [
        "heart", "cardiac", "palpitation", "bp", "blood pressure",
        "cholesterol", "chest",
    ],
    "Orthopedics": [
        "knee", "joint", "bone", "back pain", "fracture", "sprain",
        "shoulder", "hip", "arthritis", "leg pain", "ankle",
    ],
    "General Medicine": [
        "fever", "cold", "cough", "flu", "body pain", "headache", "weakness",
        "fatigue", "diabetes", "sugar", "infection", "stomach", "vomit",
        "loose motion", "acidity", "dizzy",
    ],
    "Dermatology": [
        "skin", "rash", "acne", "pimple", "hair", "itch", "itching",
        "eczema", "allergy", "nail",
    ],
    "Gynecology": [
        "pregnan", "period", "menstru", "gynec", "pcod", "pcos",
        "uterus", "ovary",
    ],
}

# Specialty names patients may type directly.
SPECIALTY_KEYWORDS: dict[str, list[str]] = {
    "Cardiology": ["cardiolog", "heart specialist"],
    "Orthopedics": ["orthopedic", "orthopaedic", "bone specialist"],
    "General Medicine": ["physician", "general medicine", "general doctor"],
    "Gynecology": ["gynec", "gynaec", "obstetric"],
    "Dermatology": ["dermatolog", "skin specialist"],
}


def match_department(text: str) -> str | None:
    """Best-effort symptom/specialty -> department mapping."""
    low = text.lower()
    for dept, keywords in SPECIALTY_KEYWORDS.items():
        if any(k in low for k in keywords):
            return dept
    for dept, keywords in SYMPTOM_DEPARTMENT_MAP.items():
        if any(k in low for k in keywords):
            return dept
    return None


def doctors_in(department: str) -> list[dict]:
    return [d for d in DOCTORS if d["department"] == department]


def find_doctor_by_name(text: str) -> dict | None:
    low = text.lower()
    for d in DOCTORS:
        # match on surname, e.g. "mehta" in "book dr mehta"
        surname = d["name"].split()[-1].lower()
        if surname in low:
            return d
    return None


# --------------------------------------------------------------------------- #
# Sample clinical / billing records (demo only)
# --------------------------------------------------------------------------- #
SAMPLE_PRESCRIPTION: dict = {
    "patient": "Demo Patient",
    "medicines": [
        {
            "name": "Paracetamol 500 mg",
            "timing": "After food",
            "frequency": "Twice daily",
            "duration": "3 days",
        },
        {
            "name": "Pantoprazole 40 mg",
            "timing": "Before breakfast",
            "frequency": "Once daily",
            "duration": "5 days",
        },
    ],
}

SAMPLE_DISCHARGE_SUMMARY: dict = {
    "patient": "Demo Patient",
    "reason": "Minor knee surgery",
    "condition": "Discharged in stable condition",
    "medicines_days": 5,
    "wound_care": "Dressing change required every alternate day",
    "activity": "Avoid heavy walking for 2 weeks",
    "follow_up": "Follow-up after 7 days",
    "warning_signs": ["fever", "severe pain", "swelling", "bleeding", "wound discharge"],
}

SAMPLE_BILL: dict = {
    "appointment_id": "APT-10245",
    "items": [
        {"label": "Consultation", "amount": 900},
        {"label": "Lab Tests", "amount": 1500},
        {"label": "Procedure Charges", "amount": 12000},
        {"label": "Room Charges", "amount": 5000},
        {"label": "Pharmacy", "amount": 2200},
    ],
    "total": 21600,
    "insurance_approved": 16000,
    "patient_payable": 5600,
}

SAMPLE_INSURANCE: dict = {
    "policy": "Corporate Mediclaim — HealthSecure",
    "claim_id": "CLM-55821",
    "status": "Partially approved",
    "approved_amount": 16000,
    "pending_documents": ["Discharge summary", "Final itemised bill", "ID proof copy"],
    "uncovered_note": "Room rent above eligible limit and pharmacy consumables are not covered.",
}

PREVISIT_CHECKLISTS: dict[str, list[str]] = {
    "Cardiology": [
        "Previous ECG / Echo reports if available",
        "Current medicine list",
        "Photo ID proof",
        "Insurance card (if applicable)",
        "Reach 20 minutes before the appointment",
    ],
    "Orthopedics": [
        "Previous X-rays / MRI reports",
        "Current medicine list",
        "Photo ID proof",
        "Comfortable clothing for examination",
        "Reach 15 minutes before the appointment",
    ],
    "_default": [
        "Photo ID proof",
        "Any previous reports or prescriptions",
        "Current medicine list",
        "Insurance card (if applicable)",
        "Reach 15 minutes before the appointment",
    ],
}


def previsit_checklist(department: str | None) -> list[str]:
    if department and department in PREVISIT_CHECKLISTS:
        return PREVISIT_CHECKLISTS[department]
    return PREVISIT_CHECKLISTS["_default"]
