"""
Intent Detector
----------------
This module performs deterministic intent induction
before any LLM call.

Goals:
- Reduce LLM usage
- Detect emergencies & human requests early
- Provide confidence score for routing decisions
"""

# =========================
# IMPORTS
# =========================

from typing import Tuple, Optional

# =========================
# EMERGENCY & HUMAN OVERRIDES
# (Highest priority – checked first)
# =========================

EMERGENCY_KEYWORDS = [
    "pain",
    "severe pain",
    "bleeding",
    "swelling",
    "broken tooth",
    "accident",
    "injury",
    "can't sleep",
    "child crying",
    "emergency"
]

HUMAN_REQUEST_KEYWORDS = [
    "human",
    "real person",
    "receptionist",
    "staff",
    "agent",
    "talk to someone"
]

# =========================
# INTENT DEFINITIONS
# (Single Source of Truth)
# =========================

INTENT_DEFINITIONS = {
    "I1": {
        "name": "New Appointment",
        "keywords": [
            "book appointment",
            "new appointment",
            "first time",
            "checkup",
            "cleaning",
            "see dentist",
            "schedule visit"
        ]
    },
    "I3": {
        "name": "Reschedule Appointment",
        "keywords": [
            "reschedule",
            "change appointment",
            "move appointment",
            "different time",
            "postpone"
        ]
    },
    "I4": {
        "name": "Cancel Appointment",
        "keywords": [
            "cancel appointment",
            "won't come",
            "drop booking"
        ]
    },
    "I7": {
        "name": "Clinic Info",
        "keywords": [
            "timing",
            "opening time",
            "closing time",
            "address",
            "location",
            "parking",
            "directions"
        ]
    },
    "I8": {
        "name": "Insurance Inquiry",
        "keywords": [
            "insurance",
            "policy",
            "covered",
            "claim",
            "cashless"
        ]
    }
}

# =========================
# CONFIG
# =========================

CONFIDENCE_THRESHOLD = 0.6
MAX_KEYWORDS_PER_INTENT = 3  # used for confidence normalization

# =========================
# MAIN FUNCTION
# =========================

def detect_intent(transcript: str) -> Tuple[Optional[str], float]:
    """
    Detect intent from STT transcript using keyword + rules.

    Returns:
        (intent_code, confidence)
        intent_code: e.g. 'I1', 'I5', 'I99', or None
        confidence: float between 0.0 and 1.0
    """

    # -------------------------
    # 1. Normalize input text
    # -------------------------
    text = transcript.lower().strip()

    # -------------------------
    # 2. Emergency override
    # -------------------------
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text:
            return "I5", 1.0  # Emergency intent

    # -------------------------
    # 3. Human request override
    # -------------------------
    for keyword in HUMAN_REQUEST_KEYWORDS:
        if keyword in text:
            return "I99", 1.0  # Human handoff

    # -------------------------
    # 4. Intent scoring
    # -------------------------
    intent_scores = {}

    for intent_code, intent_data in INTENT_DEFINITIONS.items():
        score = 0
        for keyword in intent_data["keywords"]:
            if keyword in text:
                score += 1

        if score > 0:
            intent_scores[intent_code] = score

    # -------------------------
    # 5. No intent matched
    # -------------------------
    if not intent_scores:
        return None, 0.0

    # -------------------------
    # 6. Select best intent
    # -------------------------
    best_intent = max(intent_scores, key=intent_scores.get)
    best_score = intent_scores[best_intent]

    # -------------------------
    # 7. Confidence calculation
    # -------------------------
    confidence = min(
        best_score / MAX_KEYWORDS_PER_INTENT,
        1.0
    )

    return best_intent, confidence
