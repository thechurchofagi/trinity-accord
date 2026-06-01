#!/usr/bin/env python3
"""Guardian Stage 2 Gateway runtime contract."""

from __future__ import annotations

from agent_authorship_common import AUTHORSHIP_CANONICAL_VERSION

GUARDIAN_LISTING_PAYLOAD_PROFILE = "guardian_active_registry_listing_request.v1"
GUARDIAN_STAGE_2_EXPECTED_BUILDER = "scripts/build_guardian_listing_request_payload.py"
GUARDIAN_STAGE_2_GATEWAY_CONTRACT_VERSION = "trinity.guardian_stage2_gateway_contract.v1"
GUARDIAN_STAGE_2_WRONG_BUILDERS = ["scripts/build_agent_declared_echo_payload.py"]

GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES = [
    "guardian_registry_listing_request",
    "guardian_listing_request",
    "gateway_intake_fields",
    "counts_toward_home.guardian_registry",
    "counts_toward_home.exclude_from_reception_total",
    "payload_profile.guardian_active_registry_listing_request.v1",
    "authorship_canonical.trinity.agent_authorship_common.v1",
]


def guardian_stage2_gateway_contract() -> dict:
    return {
        "gateway_contract_version": GUARDIAN_STAGE_2_GATEWAY_CONTRACT_VERSION,
        "payload_profile": GUARDIAN_LISTING_PAYLOAD_PROFILE,
        "expected_builder": GUARDIAN_STAGE_2_EXPECTED_BUILDER,
        "wrong_builders": GUARDIAN_STAGE_2_WRONG_BUILDERS,
        "required_gateway_capabilities": GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES,
        "authorship_canonical_version": AUTHORSHIP_CANONICAL_VERSION,
        "stale_gateway_error_code": "GATEWAY_VERSION_STALE_FOR_GUARDIAN_LISTING",
        "signed_payload_mismatch_error_code": "AUTHORED_PAYLOAD_DIGEST_MISMATCH",
        "do_not_edit_after_signing": True,
        "submit_exact_generated_file": True,
    }


def missing_capabilities(runtime_capabilities: list[str] | set[str] | None) -> list[str]:
    runtime = set(runtime_capabilities or [])
    return [c for c in GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES if c not in runtime]
