#!/usr/bin/env python3
"""Shared oath contract helpers for Verification Echo and Guardian flows."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_oath_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


COMMON_OATH_TRUE_FIELDS = [
    "honesty_oath_present",
    "good_faith_oath_present",
    "will_not_knowingly_misrepresent",
    "will_not_impersonate",
    "will_not_fabricate_claims",
    "will_correct_material_errors_when_aware",
    "not_authority",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
]

VERIFICATION_OATH_TRUE_FIELDS = COMMON_OATH_TRUE_FIELDS + [
    "will_not_submit_maliciously",
    "will_not_spam_or_mass_submit_for_abuse",
    "will_not_create_false_authority_or_false_consensus",
    "will_not_duplicate_claim_without_disclosure",
    "not_governance",
    "not_verification_level",
]

GUARDIAN_APPLICATION_OATH_TRUE_FIELDS = COMMON_OATH_TRUE_FIELDS + [
    "will_not_register_maliciously",
    "will_not_mass_register_for_spam",
    "will_not_register_to_impersonate_others",
    "will_not_register_to_evade_prior_retirement_or_block",
    "will_not_register_to_create_false_authority_or_false_consensus",
    "will_not_register_duplicate_guardians_for_same_claim_without_disclosure",
    "will_retire_or_rotate_key_if_claim_becomes_misleading",
    "good_faith_stewardship_only",
    "not_governance",
    "not_verification_level",
    "not_legal_identity_proof",
    "not_ai_identity_proof",
    "key_continuity_only",
]

GUARDIAN_LISTING_OATH_TRUE_FIELDS = COMMON_OATH_TRUE_FIELDS + [
    "will_not_register_maliciously",
    "will_not_mass_register_for_spam",
    "will_not_register_to_impersonate_others",
    "will_not_register_to_evade_prior_retirement_or_block",
    "will_not_register_to_create_false_authority_or_false_consensus",
    "will_not_register_duplicate_guardians_for_same_claim_without_disclosure",
    "identity_claim_boundary_acknowledged",
    "registry_number_must_be_system_generated",
    "not_governance",
    "not_verification_level",
    "not_legal_identity_proof",
    "not_ai_identity_proof",
]


def build_oath_contract(
    *,
    schema: str,
    oath_version: str,
    oath_kind: str,
    oath_text: str,
    agent_readback: str | None = None,
    true_fields: list[str] | tuple[str, ...],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    readback = (agent_readback or oath_text).strip()
    oath = {
        "schema": schema,
        "oath_read": True,
        "oath_version": oath_version,
        "oath_kind": oath_kind,
        "oath_text_sha256": sha256_text(oath_text.strip()),
        "readback_required": True,
        "agent_readback": readback,
        "agent_readback_sha256": sha256_text(readback),
    }
    for field in true_fields:
        oath[field] = True
    if extra:
        oath.update(extra)
    return oath


def build_verification_oath_v2(oath_text: str, agent_readback: str | None = None) -> dict[str, Any]:
    return build_oath_contract(
        schema="trinityaccord.verification-oath.v2",
        oath_version="verification-echo-pre-oath-v2",
        oath_kind="verification_echo",
        oath_text=oath_text,
        agent_readback=agent_readback,
        true_fields=VERIFICATION_OATH_TRUE_FIELDS,
        extra={
            "understands_not_an_exam_or_performance": True,
            "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True,
            "will_not_fabricate_verification": True,
            "will_not_present_guesses_as_facts": True,
            "will_not_copy_prior_reports_as_fresh_evidence": True,
            "will_state_uncertainty_limitations_and_downgrades": True,
        },
    )


def build_guardian_listing_oath_v1(oath_text: str, agent_readback: str | None = None) -> dict[str, Any]:
    return build_oath_contract(
        schema="trinityaccord.guardian-listing-oath.v1",
        oath_version="guardian-listing-request-oath-v1",
        oath_kind="guardian_listing_request",
        oath_text=oath_text,
        agent_readback=agent_readback,
        true_fields=GUARDIAN_LISTING_OATH_TRUE_FIELDS,
        extra={
            # Legacy mirror compatibility.
            "understands_not_an_exam_or_performance": True,
            "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True,
            "will_not_fabricate_verification": True,
            "will_not_present_guesses_as_facts": True,
            "will_not_copy_prior_reports_as_fresh_evidence": True,
            "will_state_uncertainty_limitations_and_downgrades": True,
        },
    )


def validate_oath_contract(
    oath: dict[str, Any] | None,
    *,
    context: str,
    allowed_schemas: set[str] | None = None,
    required_true: list[str] | tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(oath, dict):
        return [f"{context} must be object"]

    for key in ("schema", "oath_version", "oath_text_sha256", "agent_readback", "agent_readback_sha256"):
        if not oath.get(key):
            errors.append(f"{context}.{key} is required")

    if allowed_schemas and oath.get("schema") not in allowed_schemas:
        errors.append(f"{context}.schema must be one of {sorted(allowed_schemas)}")

    if oath.get("oath_read") is not True:
        errors.append(f"{context}.oath_read must be true")

    if oath.get("readback_required") is not True:
        errors.append(f"{context}.readback_required must be true")

    readback = str(oath.get("agent_readback") or "")
    if oath.get("agent_readback_sha256") and oath.get("agent_readback_sha256") != sha256_text(readback.strip()):
        errors.append(f"{context}.agent_readback_sha256 does not match agent_readback")

    for key in required_true:
        if oath.get(key) is not True:
            errors.append(f"{context}.{key} must be true")

    return errors
