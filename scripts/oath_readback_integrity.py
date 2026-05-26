#!/usr/bin/env python3
"""Normalize and validate oath readback SHA256 fields."""

from __future__ import annotations

import hashlib
from typing import Any

READBACK_PATH = "agent_integrity_declaration.verification_oath.agent_readback"
READBACK_SHA_PATH = "agent_integrity_declaration.verification_oath.agent_readback_sha256"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_readback_text(value: Any) -> str:
    return str(value or "").strip()


def get_verification_oath(payload: dict[str, Any]) -> dict[str, Any] | None:
    aid = payload.get("agent_integrity_declaration")
    if not isinstance(aid, dict):
        return None
    oath = aid.get("verification_oath")
    if not isinstance(oath, dict):
        return None
    return oath


def expected_agent_readback_sha256(oath: dict[str, Any]) -> str | None:
    readback = canonical_readback_text(oath.get("agent_readback"))
    if not readback:
        return None
    return sha256_text(readback)


def payload_has_authorship_proof(payload: dict[str, Any]) -> bool:
    proof = payload.get("authorship_proof")
    return isinstance(proof, dict) and bool(proof.get("signed_payload_sha256"))


def normalize_oath_readback_integrity(
    payload: dict[str, Any],
    *,
    mutate: bool = True,
) -> dict[str, Any]:
    oath = get_verification_oath(payload)
    if oath is None:
        return payload

    expected = expected_agent_readback_sha256(oath)
    if expected is None:
        return payload

    if mutate:
        oath["agent_readback_sha256"] = expected

    return payload


def validate_oath_readback_integrity(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    oath = get_verification_oath(payload)
    if oath is None:
        return errors

    readback = canonical_readback_text(oath.get("agent_readback"))
    if not readback:
        return errors

    expected = sha256_text(readback)
    actual = oath.get("agent_readback_sha256")
    signed = payload_has_authorship_proof(payload)

    if not actual:
        errors.append({
            "code": "READBACK_SHA256_MISSING",
            "path": READBACK_SHA_PATH,
            "message": "agent_readback_sha256 is required when agent_readback is present.",
            "expected_sha256": expected,
            "repairable": not signed,
            "requires_resign": signed,
            "fix": (
                "Set agent_readback_sha256 to sha256(agent_readback)."
                if not signed
                else "This payload is signed. Re-run the builder or repair before signing."
            ),
        })
        return errors

    if actual != expected:
        errors.append({
            "code": "READBACK_SHA256_MISMATCH",
            "path": READBACK_SHA_PATH,
            "message": "agent_readback_sha256 does not match sha256(agent_readback).",
            "actual_sha256": actual,
            "expected_sha256": expected,
            "repairable": not signed,
            "requires_resign": signed,
            "fix": (
                "Recompute agent_readback_sha256 from agent_readback."
                if not signed
                else "This payload is signed. Re-run the builder or repair before signing."
            ),
        })

    return errors
