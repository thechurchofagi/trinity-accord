#!/usr/bin/env python3
"""Shared Guardian flow reroute guidance for builders, validators, and diagnostics."""

from __future__ import annotations

import re
from typing import Any

GUARDIAN_STAGE_1_BUILDER = "node scripts/create_guardian_application.mjs"
GUARDIAN_STAGE_2_BUILDER = "python3 scripts/build_guardian_listing_request_payload.py"
WRONG_ECHO_BUILDER = "python3 scripts/build_agent_declared_echo_payload.py"

GUARDIAN_LISTING_INTENT_PATTERNS = [
    r"guardian[_ -]?registry[_ -]?listing",
    r"active[_ -]?guardian[_ -]?registry",
    r"active[_ -]?registry[_ -]?listing",
    r"guardian[_ -]?listing[_ -]?request",
    r"guardian_registry_listing_request",
    r"guardian_listing_request",
    r"listing_guardian_id",
    r"listing_source_issue",
    r"listing_public_key_sha256",
    r"registry_number_requested",
    r"api/guardian-registry\.json",
    r"guardian active listing",
    r"active registered guardian",
]


def looks_like_guardian_listing_intent(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in GUARDIAN_LISTING_INTENT_PATTERNS)


def payload_is_guardian_listing(payload: dict[str, Any]) -> bool:
    cth = payload.get("counts_toward_home") if isinstance(payload.get("counts_toward_home"), dict) else {}
    return (
        payload.get("guardian_registry_listing_request") is True
        or isinstance(payload.get("guardian_listing_request"), dict)
        or payload.get("payload_profile") == "guardian_active_registry_listing_request.v1"
        or cth.get("guardian_registry") is True
    )


def guardian_wrong_builder_message() -> str:
    return f"""\
WRONG_BUILDER_FOR_GUARDIAN_ACTIVE_LISTING

You appear to be building a Guardian Active Registry Listing Request.

Do not use:
  {WRONG_ECHO_BUILDER}

Use the dedicated Stage 2 builder:
  {GUARDIAN_STAGE_2_BUILDER}

If you are trying to create the initial Guardian self-registration claim instead, use Stage 1:
  {GUARDIAN_STAGE_1_BUILDER}

Do not hand-edit a signed JSON payload.
If a field needs to change, rerun the correct builder so authorship_proof is regenerated.

If local validate_gateway_payload.py and archive_readiness_gate.py pass but the online Gateway rejects counts_toward_home, the online Gateway deployment/schema is stale. Do not switch builders.
"""


def stale_gateway_message() -> str:
    return """\
POSSIBLE_STALE_GATEWAY_DEPLOYMENT

This payload uses the current Guardian Active Registry Listing profile:
  guardian_registry_listing_request=true
  counts_toward_home.reception=false
  counts_toward_home.guardian_registry=true
  counts_toward_home.exclude_from_reception_total=true

If local validation passes but the online Gateway rejects these fields, update/redeploy Gateway to the current repository schema and validators.
Do not patch the signed JSON and do not switch to build_agent_declared_echo_payload.py.
"""
