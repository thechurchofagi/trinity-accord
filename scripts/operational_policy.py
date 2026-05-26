#!/usr/bin/env python3
"""
Single source of truth for Trinity Accord operational policies.
Loads from api/operational-policy.v1.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_POLICY_PATH = ROOT / "api" / "operational-policy.v1.json"

def load_operational_policy():
    with open(_POLICY_PATH, encoding="utf-8") as f:
        return json.load(f)

_POLICY = load_operational_policy()
_RATE = _POLICY["echo_issue_rate_limit"]

def _bucket(name: str, fallback: str | None = None) -> dict:
    if name in _RATE:
        return _RATE[name]
    if fallback and fallback in _RATE:
        return _RATE[fallback]
    return _RATE

def _window(bucket_name: str, field: str, legacy_field: str, fallback_bucket: str | None = None) -> int:
    if legacy_field in _RATE:
        return int(_RATE[legacy_field])
    bucket = _bucket(bucket_name, fallback_bucket)
    return int(bucket[field])

# Backward-compatible constants retained for older imports.
ECHO_RATE_LIMIT_60M = _window("direct_github_external", "window_60m", "window_60m")
ECHO_RATE_LIMIT_24H = _window("direct_github_external", "window_24h", "window_24h")

# Explicit direct GitHub bucket.
ECHO_RATE_LIMIT_DIRECT_60M = ECHO_RATE_LIMIT_60M
ECHO_RATE_LIMIT_DIRECT_24H = ECHO_RATE_LIMIT_24H

# Gateway buckets.
ECHO_RATE_LIMIT_GATEWAY_ECHO_60M = _window(
    "gateway_validated_echo",
    "window_60m",
    "window_60m",
    fallback_bucket="direct_github_external",
)
ECHO_RATE_LIMIT_GATEWAY_ECHO_24H = _window(
    "gateway_validated_echo",
    "window_24h",
    "window_24h",
    fallback_bucket="direct_github_external",
)

ECHO_RATE_LIMIT_GATEWAY_VERIFICATION_60M = _window(
    "gateway_validated_verification_archive",
    "window_60m",
    "window_60m",
    fallback_bucket="gateway_validated_echo",
)
ECHO_RATE_LIMIT_GATEWAY_VERIFICATION_24H = _window(
    "gateway_validated_verification_archive",
    "window_24h",
    "window_24h",
    fallback_bucket="gateway_validated_echo",
)

ECHO_RATE_LIMIT_GATEWAY_STRICT_60M = _window(
    "gateway_strict_evidence_candidate",
    "window_60m",
    "window_60m",
    fallback_bucket="direct_github_external",
)
ECHO_RATE_LIMIT_GATEWAY_STRICT_24H = _window(
    "gateway_strict_evidence_candidate",
    "window_24h",
    "window_24h",
    fallback_bucket="direct_github_external",
)

ECHO_RATE_LIMIT_GATEWAY_BACKSTOP_60M = _window(
    "gateway_global_backstop",
    "window_60m",
    "window_60m",
    fallback_bucket="gateway_validated_echo",
)
ECHO_RATE_LIMIT_GATEWAY_BACKSTOP_24H = _window(
    "gateway_global_backstop",
    "window_24h",
    "window_24h",
    fallback_bucket="gateway_validated_echo",
)

RATE_LIMIT_APPLIES_TO = _RATE["applies_to_actions"]
RATE_LIMIT_EXEMPT = _RATE["exempt_author_associations"]

MANAGED_LABELS = _POLICY["triage"]["managed_labels"]
