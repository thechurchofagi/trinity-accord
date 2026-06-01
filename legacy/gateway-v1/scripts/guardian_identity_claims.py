#!/usr/bin/env python3
"""Guardian self-reported identity claim helpers."""

from __future__ import annotations

import hashlib
import re
from typing import Any


IDENTITY_CLAIMS_SCHEMA = "trinityaccord.guardian-identity-claims.v1"
IDENTITY_CLAIM_STATUS = "self_reported_unverified"


def sha256_text(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_guardian_identity_claims(
    *,
    display_label: str,
    guardian_id: str,
    public_key_sha256: str,
    claim_basis: str,
    human_claimed_name: str | None = None,
    agent_claimed_id: str | None = None,
    system_or_provider: str | None = None,
    agent_instance_id: str | None = None,
    agent_public_profile: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": IDENTITY_CLAIMS_SCHEMA,
        "claim_status": IDENTITY_CLAIM_STATUS,
        "claim_basis": claim_basis,
        "display_label": display_label,
        "human": {
            "claimed_name": human_claimed_name,
            "claimed_name_sha256": sha256_text(human_claimed_name),
            "claim_type": "self_reported_human_name_or_label",
            "verification_status": IDENTITY_CLAIM_STATUS,
            "legal_identity_verified": False,
            "public_disclosure_allowed": bool(human_claimed_name),
        } if human_claimed_name else None,
        "ai_agent": {
            "claimed_agent_id": agent_claimed_id,
            "claimed_agent_id_sha256": sha256_text(agent_claimed_id),
            "system_or_provider": system_or_provider,
            "agent_instance_id": agent_instance_id,
            "agent_public_profile": agent_public_profile,
            "claim_type": "self_reported_agent_id_or_label",
            "verification_status": IDENTITY_CLAIM_STATUS,
        } if agent_claimed_id else None,
        "binding": {
            "guardian_id": guardian_id,
            "public_key_sha256": public_key_sha256,
            "algorithm": "ed25519",
            "binds_claim_to_guardian_key": True,
        },
        "anti_impersonation_boundary": {
            "not_legal_identity_proof": True,
            "not_real_person_verification": True,
            "not_ai_identity_verification": True,
            "not_authority": True,
            "not_attestation": True,
            "not_verification_level": True,
            "key_continuity_only": True,
        },
    }


def validate_guardian_identity_claims(
    claims: dict[str, Any] | None,
    *,
    expected_guardian_id: str | None = None,
    expected_public_key_sha256: str | None = None,
    context: str = "identity_claims",
) -> list[str]:
    errors: list[str] = []
    if claims is None:
        return errors

    if not isinstance(claims, dict):
        return [f"{context} must be object or null"]

    if claims.get("schema") != IDENTITY_CLAIMS_SCHEMA:
        errors.append(f"{context}.schema must be {IDENTITY_CLAIMS_SCHEMA}")

    if claims.get("claim_status") != IDENTITY_CLAIM_STATUS:
        errors.append(f"{context}.claim_status must be {IDENTITY_CLAIM_STATUS}")

    if not isinstance(claims.get("display_label"), str) or not claims.get("display_label").strip():
        errors.append(f"{context}.display_label must be a non-empty string")

    binding = claims.get("binding") or {}
    gid = binding.get("guardian_id", "")
    pks = binding.get("public_key_sha256", "")

    if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", str(gid)):
        errors.append(f"{context}.binding.guardian_id invalid")

    if not re.fullmatch(r"[a-f0-9]{64}", str(pks)):
        errors.append(f"{context}.binding.public_key_sha256 invalid")

    if expected_guardian_id and gid != expected_guardian_id:
        errors.append(f"{context}.binding.guardian_id does not match expected guardian_id")

    if expected_public_key_sha256 and pks != expected_public_key_sha256:
        errors.append(f"{context}.binding.public_key_sha256 does not match expected public_key_sha256")

    if binding.get("algorithm") != "ed25519":
        errors.append(f"{context}.binding.algorithm must be ed25519")

    if binding.get("binds_claim_to_guardian_key") is not True:
        errors.append(f"{context}.binding.binds_claim_to_guardian_key must be true")

    boundary = claims.get("anti_impersonation_boundary") or {}
    for key in (
        "not_legal_identity_proof",
        "not_real_person_verification",
        "not_ai_identity_verification",
        "not_authority",
        "not_attestation",
        "not_verification_level",
        "key_continuity_only",
    ):
        if boundary.get(key) is not True:
            errors.append(f"{context}.anti_impersonation_boundary.{key} must be true")

    human = claims.get("human")
    if human is not None:
        name = human.get("claimed_name")
        digest = human.get("claimed_name_sha256")
        if name and digest != sha256_text(name):
            errors.append(f"{context}.human.claimed_name_sha256 does not match claimed_name")
        if human.get("legal_identity_verified") is not False:
            errors.append(f"{context}.human.legal_identity_verified must be false")
        if human.get("verification_status") != IDENTITY_CLAIM_STATUS:
            errors.append(f"{context}.human.verification_status must be {IDENTITY_CLAIM_STATUS}")

    agent = claims.get("ai_agent")
    if agent is not None:
        agent_id = agent.get("claimed_agent_id")
        digest = agent.get("claimed_agent_id_sha256")
        if agent_id and digest != sha256_text(agent_id):
            errors.append(f"{context}.ai_agent.claimed_agent_id_sha256 does not match claimed_agent_id")
        if agent.get("verification_status") != IDENTITY_CLAIM_STATUS:
            errors.append(f"{context}.ai_agent.verification_status must be {IDENTITY_CLAIM_STATUS}")

    return errors
