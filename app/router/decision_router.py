"""
Decision Router
---------------
Central brain that routes each call based on:
- Intent
- Confidence
- Redis cache
- Safety rules

This ensures:
- Minimal LLM usage
- Predictable behavior
- Safe escalation
"""

# =========================
# IMPORTS
# =========================

from typing import Dict

from app.intents.intent_detector import detect_intent
from app.cache.redis_router import (
    get_cached_response,
    save_response_to_cache
)

# =========================
# CONFIG
# =========================

LLM_CONFIDENCE_THRESHOLD = 0.6

# =========================
# MAIN ROUTER FUNCTION
# =========================

async def route_call(transcript: str) -> Dict:
    """
    Routes incoming transcript to the correct handling path.

    Returns a dict with:
    - action
    - intent
    - response (if available)
    """

    # -------------------------
    # 1. Detect intent
    # -------------------------
    intent, confidence = detect_intent(transcript)

    # -------------------------
    # 2. Emergency handling
    # -------------------------
    if intent == "I5":
        return {
            "action": "EMERGENCY_HANDOFF",
            "intent": intent,
            "confidence": confidence
        }

    # -------------------------
    # 3. Human request
    # -------------------------
    if intent == "I99":
        return {
            "action": "HUMAN_HANDOFF",
            "intent": intent,
            "confidence": confidence
        }

    # -------------------------
    # 4. Redis cache check
    # -------------------------
    if intent:
        cached_response = get_cached_response(intent, transcript)
        if cached_response:
            return {
                "action": "RESPOND_FROM_CACHE",
                "intent": intent,
                "confidence": confidence,
                "response": cached_response
            }

    # -------------------------
    # 5. Low confidence fallback
    # -------------------------
    if not intent or confidence < LLM_CONFIDENCE_THRESHOLD:
        return {
            "action": "CALL_LLM",
            "intent": intent,
            "confidence": confidence
        }

    # -------------------------
    # 6. Deterministic workflows
    # -------------------------
    if intent in {"I1", "I3", "I4"}:
        return {
            "action": "BOOKING_WORKFLOW",
            "intent": intent,
            "confidence": confidence
        }

    if intent in {"I6", "I7", "I8", "I9"}:
        return {
            "action": "STATIC_WORKFLOW",
            "intent": intent,
            "confidence": confidence
        }

    if intent in {"I10", "I11", "I13", "I15"}:
        return {
            "action": "TICKET_OR_LEAD",
            "intent": intent,
            "confidence": confidence
        }

    # -------------------------
    # 7. Default safe fallback
    # -------------------------
    return {
        "action": "CALL_LLM",
        "intent": intent,
        "confidence": confidence
    }
