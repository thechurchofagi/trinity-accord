"""Rate limiting for the Record-Chain Intake Gateway.

Implements the trinityaccord.gateway-rate-limit-policy.v1:
- Per-participant: 10 submits/hour
- Global: 100 submits/hour
- Only applies to /record-chain/submit (not preflight)
- Uses in-memory sliding window counters with bounded key cardinality

Important: this limiter is process-local. It is not durable across restarts and
is not shared across multiple service instances. Public policy must not describe
it as multi-instance/durable enforcement unless replaced by a shared backend.
The durable secret-keyed acceptance cooldown remains the primary write boundary.
"""
from __future__ import annotations

import threading
import time
from typing import Any

# ---------------------------------------------------------------------------
# Configuration (matches api/gateway-rate-limit-policy.v1.json)
# ---------------------------------------------------------------------------
GLOBAL_LIMIT_PER_HOUR = 100
PARTICIPANT_LIMIT_PER_HOUR = 10
_WINDOW_SECONDS = 3600
PREFLIGHT_GLOBAL_LIMIT_PER_MINUTE = 600
PREFLIGHT_CLIENT_LIMIT_PER_MINUTE = 120
_PREFLIGHT_WINDOW_SECONDS = 60

# Process-memory safety bounds. These counters are defense in depth only and
# must not become an unbounded high-cardinality store during distributed abuse.
MAX_TRACKED_PARTICIPANTS = 10_000
MAX_TRACKED_PREFLIGHT_CLIENTS = 20_000

# ---------------------------------------------------------------------------
# In-memory sliding window stores
# ---------------------------------------------------------------------------
# Each entry: list of timestamps (seconds since epoch)
_global_timestamps: list[float] = []
_participant_timestamps: dict[str, list[float]] = {}
_preflight_global_timestamps: list[float] = []
_preflight_client_timestamps: dict[str, list[float]] = {}
_state_lock = threading.Lock()


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


def _prune_old(entries: list[float], now: float, *, window_seconds: int = _WINDOW_SECONDS) -> list[float]:
    """Remove entries older than the selected window."""
    cutoff = now - window_seconds
    while entries and entries[0] < cutoff:
        entries.pop(0)
    return entries


def _prune_mapping(mapping: dict[str, list[float]], cutoff: float) -> None:
    """Prune old timestamps and remove keys whose windows are now empty."""
    for key, entries in list(mapping.items()):
        while entries and entries[0] < cutoff:
            entries.pop(0)
        if not entries:
            mapping.pop(key, None)


def _make_room(mapping: dict[str, list[float]], limit: int) -> None:
    """Evict the least recently seen key before admitting a new key."""
    if len(mapping) < limit:
        return
    oldest_key = min(
        mapping,
        key=lambda key: mapping[key][-1] if mapping[key] else float("-inf"),
    )
    mapping.pop(oldest_key, None)


def check_rate_limit(submission: dict[str, Any]) -> dict[str, Any] | None:
    """Check rate limits for a submission.

    Returns None if allowed, or a rate-limit violation response dict if denied.
    """
    with _state_lock:
        return _check_rate_limit_locked(submission)


def _check_rate_limit_locked(submission: dict[str, Any]) -> dict[str, Any] | None:
    """Mutate process-local counters while ``_state_lock`` is held."""
    now = time.time()

    # Prune global and per-participant windows, including empty participant keys.
    global _global_timestamps
    _global_timestamps = _prune_old(_global_timestamps, now)
    _prune_mapping(_participant_timestamps, now - _WINDOW_SECONDS)

    # Check global limit.
    if len(_global_timestamps) >= GLOBAL_LIMIT_PER_HOUR:
        return _build_rate_limit_response(
            limit_type="global",
            limit=GLOBAL_LIMIT_PER_HOUR,
            retry_after_seconds=_compute_retry_after(_global_timestamps),
        )

    participant_key = _extract_participant_key(submission)
    if participant_key not in _participant_timestamps:
        _make_room(_participant_timestamps, MAX_TRACKED_PARTICIPANTS)
        _participant_timestamps[participant_key] = []

    entries = _participant_timestamps[participant_key]
    if len(entries) >= PARTICIPANT_LIMIT_PER_HOUR:
        return _build_rate_limit_response(
            limit_type="participant",
            limit=PARTICIPANT_LIMIT_PER_HOUR,
            retry_after_seconds=_compute_retry_after(entries),
        )

    _global_timestamps.append(now)
    entries.append(now)
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


def check_preflight_rate_limit(client_key: str) -> dict[str, Any] | None:
    """Protect the public preflight route and downstream GitHub lookups."""
    key = client_key.strip() or "unknown"
    now = time.time()
    cutoff = now - _PREFLIGHT_WINDOW_SECONDS
    with _state_lock:
        global _preflight_global_timestamps
        _preflight_global_timestamps = [t for t in _preflight_global_timestamps if t >= cutoff]
        _prune_mapping(_preflight_client_timestamps, cutoff)

        if key not in _preflight_client_timestamps:
            _make_room(_preflight_client_timestamps, MAX_TRACKED_PREFLIGHT_CLIENTS)
            _preflight_client_timestamps[key] = []
        client_entries = _preflight_client_timestamps[key]

        if len(_preflight_global_timestamps) >= PREFLIGHT_GLOBAL_LIMIT_PER_MINUTE:
            return _build_preflight_rate_limit_response(
                "global", PREFLIGHT_GLOBAL_LIMIT_PER_MINUTE, _preflight_global_timestamps, now
            )
        if len(client_entries) >= PREFLIGHT_CLIENT_LIMIT_PER_MINUTE:
            return _build_preflight_rate_limit_response(
                "client", PREFLIGHT_CLIENT_LIMIT_PER_MINUTE, client_entries, now
            )

        _preflight_global_timestamps.append(now)
        client_entries.append(now)
        return None


def _build_preflight_rate_limit_response(
    limit_type: str, limit: int, entries: list[float], now: float
) -> dict[str, Any]:
    retry_after = max(int(entries[0] + _PREFLIGHT_WINDOW_SECONDS - now), 1) if entries else 1
    return {
        "accepted": False,
        "preflight": True,
        "diagnostics": [{
            "code": "PREFLIGHT_RATE_LIMIT_EXCEEDED",
            "severity": "error",
            "field": "preflight",
            "message": f"Preflight {limit_type} limit of {limit} requests per minute reached.",
            "meaning": "The validation endpoint is temporarily rate limited to protect public availability and dependent repository lookups.",
            "suggested_fix": f"Wait {retry_after} seconds before retrying preflight.",
            "help_url": "https://www.trinityaccord.org/api/gateway-rate-limit-policy.v1.json",
            "retry_allowed": True,
        }],
        "retry_after_seconds": retry_after,
        "rate_limit": {
            "limit_type": f"preflight_{limit_type}",
            "limit": limit,
            "window_seconds": _PREFLIGHT_WINDOW_SECONDS,
        },
    }


def state_cardinality() -> dict[str, int]:
    """Expose bounded counter cardinality for diagnostics and regression tests."""
    with _state_lock:
        return {
            "participants": len(_participant_timestamps),
            "preflight_clients": len(_preflight_client_timestamps),
        }


def reset() -> None:
    """Reset all rate limit state (for testing)."""
    global _global_timestamps, _preflight_global_timestamps
    with _state_lock:
        _global_timestamps = []
        _participant_timestamps.clear()
        _preflight_global_timestamps = []
        _preflight_client_timestamps.clear()
