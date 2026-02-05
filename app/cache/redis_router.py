"""
Redis Router
------------
This module handles Redis-based caching for
simple, repeatable, non-LLM responses.

Purpose:
- Bypass LLM for FAQ / static responses
- Reduce cost and latency
- Act as first lookup after intent detection
"""

# =========================
# IMPORTS
# =========================

import redis
import json
from typing import Optional

# =========================
# REDIS CONNECTION
# =========================

# In production, move these to ENV variables
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True  # return strings, not bytes
)

# =========================
# CACHE TTL (SECONDS)
# =========================

DEFAULT_TTL = 60 * 60 * 24  # 24 hours

# =========================
# CACHEABLE INTENTS
# (NO LLM REQUIRED)
# =========================

CACHEABLE_INTENTS = {
    "I7",   # Clinic Info
    "I6",   # Pricing
    "I8",   # Insurance
    "I9",   # EMI
}

# =========================
# CACHE KEY BUILDER
# =========================

def build_cache_key(intent: str, text: str) -> str:
    """
    Build a deterministic Redis key.

    Example:
    intent:I7:clinic_timing
    """
    normalized_text = text.lower().strip().replace(" ", "_")
    return f"intent:{intent}:{normalized_text[:50]}"

# =========================
# GET FROM CACHE
# =========================

def get_cached_response(intent: str, transcript: str) -> Optional[str]:
    """
    Try to fetch response from Redis.

    Returns:
        Cached response text OR None
    """

    # Only allow cache for safe intents
    if intent not in CACHEABLE_INTENTS:
        return None

    cache_key = build_cache_key(intent, transcript)

    cached_value = redis_client.get(cache_key)

    if cached_value:
        return cached_value

    return None

# =========================
# SAVE TO CACHE
# =========================

def save_response_to_cache(
    intent: str,
    transcript: str,
    response_text: str,
    ttl: int = DEFAULT_TTL
):
    """
    Save response in Redis for future reuse.
    """

    if intent not in CACHEABLE_INTENTS:
        return

    cache_key = build_cache_key(intent, transcript)

    redis_client.setex(
        cache_key,
        ttl,
        response_text
    )

