"""Rate limiting for the Record-Chain Intake Gateway.

Implements the trinityaccord.gateway-rate-limit-policy.v1:
- Per-participant: 10 submits/hour
- Global: 100 submits/hour
- Only applies to /record-chain/submit (not preflight)
- Uses in-memory sliding window counter
"""
from __future__ import annotations

import time
from typing import Any

# ---------------------------------------------------------------------------
# Configuration (matches api/gateway-rate-limit-policy.v1.json)
# ---------------------------------------------------------------------------
GLOBAL_LIMIT_PER_HOUR = 100
PARTICIPANT_LIMIT_PER_HOUR = 10
_WINDOW_SECONDS = 3600

# ---------------------------------------------------------------------------
# In-memory sliding window stores
# ---------------------------------------------------------------------------
# Each entry: list of timestamps (seconds since epoch)
_global_timestamps: list[float] = []
_participant_timestamps: dict[str, list[float]] = {}


def _extract_participant_key(submission: dict[str, Any]) -> str:
    """Extract participant key in priority order from the rate-limit policy.

    Priority:
    1. record_draft.submitting_participant_identity.public_key
    2. record_draft.submitting_participant_identity.label
    3. record_draft.actor_identity.label
    4. agent_label
    5. idempotency_key_prefix
    """
    draft = submission.get("record_draft") or submission.get("draft") or {}
    if isinstance(draft, dict):
        identity = draft.get("submitting_participant_identity")
        if isinstance(identity, dict):
            pub_key = identity.get("public_key") or identity.get("participant_public_key_sha256")
            if pub_key:
                return f"pk:{pub_key}"
            label = (
                identity.get("participant_public_display_label")
                or identity.get("label")
            )
            if label:
                return f"label:{label}"

        actor = draft.get("actor_identity")
        if isinstance(actor, dict):
            actor_label = actor.get("label")
            if actor_label:
                return f"actor:{actor_label}"

    agent_label = submission.get("agent_label")
    if agent_label:
        return f"agent:{agent_label}"

    idem = submission.get("idempotency_key_prefix")
    if idem:
        return f"idem:{idem}"

    return "anonymous"


def _prune_old(entries: list[float], now: float) -> list[float]:
    """Remove entries older than the window."""
    cutoff = now - _WINDOW_SECONDS
    while entries and entries[0] < cutoff:
        entries.pop(0)
    return entries


def check_rate_limit(submission: dict[str, Any]) -> dict[str, Any] | None:
    """Check rate limits for a submission.

    Returns None if allowed, or a rate-limit violation response dict if denied.
    """
    now = time.time()

    # Prune global window
    global _global_timestamps
    _global_timestamps = _prune_old(_global_timestamps, now)

    # Check global limit
    if len(_global_timestamps) >= GLOBAL_LIMIT_PER_HOUR:
        return _build_rate_limit_response(
            limit_type="global",
            limit=GLOBAL_LIMIT_PER_HOUR,
            retry_after_seconds=_compute_retry_after(_global_timestamps),
        )

    # Extract participant key
    participant_key = _extract_participant_key(submission)

    # Prune participant window
    if participant_key not in _participant_timestamps:
        _participant_timestamps[participant_key] = []
    _participant_timestamps[participant_key] = _prune_old(
        _participant_timestamps[participant_key], now
    )

    # Check participant limit
    if len(_participant_timestamps[participant_key]) >= PARTICIPANT_LIMIT_PER_HOUR:
        return _build_rate_limit_response(
            limit_type="participant",
            limit=PARTICIPANT_LIMIT_PER_HOUR,
            retry_after_seconds=_compute_retry_after(_participant_timestamps[participant_key]),
        )

    # Record this submission
    _global_timestamps.append(now)
    _participant_timestamps[participant_key].append(now)

    return None


def _compute_retry_after(entries: list[float]) -> int:
    """Compute seconds until the oldest entry expires from the window."""
    if not entries:
        return 0
    oldest = entries[0]
    remaining = int(oldest + _WINDOW_SECONDS - time.time())
    return max(remaining, 1)


def _build_rate_limit_response(
    limit_type: str,
    limit: int,
    retry_after_seconds: int,
) -> dict[str, Any]:
    """Build a rate-limit violation response matching the policy schema."""
    return {
        "accepted": False,
        "submitted": False,
        "diagnostic_code": "RATE_LIMIT_EXCEEDED",
        "diagnostics": [{
            "code": "RATE_LIMIT_EXCEEDED",
            "severity": "error",
            "field": "submit",
            "message": f"Rate limit exceeded: {limit_type} limit of {limit} submits per hour reached.",
            "meaning": f"The {limit_type} rate limit has been reached. Try again after the window expires.",
            "suggested_fix": f"Wait {retry_after_seconds} seconds before submitting again.",
            "help_url": "https://www.trinityaccord.org/api/gateway-rate-limit-policy.v1.json",
            "retry_allowed": True,
        }],
        "retry_after_seconds": retry_after_seconds,
        "rate_limit": {
            "limit_type": limit_type,
            "limit": limit,
            "window_seconds": _WINDOW_SECONDS,
        },
    }


def reset() -> None:
    """Reset all rate limit state (for testing)."""
    global _global_timestamps
    _global_timestamps = []
    _participant_timestamps.clear()
