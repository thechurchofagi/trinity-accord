#!/usr/bin/env python3
"""Gateway diagnostic ↔ field-helper contract test.

Ensures every externally visible Gateway diagnostic code emitted via
_make_diagnostic(code="...") has a corresponding entry in
api/record-chain-field-helper.v1.json diagnostic_code_help.

Also enforces mission-critical security/privacy codes are always present.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALIDATION_PATH = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py"
AUTHORSHIP_PATH = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "authorship.py"
SECURITY_PATH = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "security.py"
HELPER_PATH = ROOT / "api" / "record-chain-field-helper.v1.json"

# Codes that MUST always be present regardless of AST analysis.
# These protect against private-key leaks, identity exposure, and
# placeholder/forgery attacks.
MISSION_CRITICAL_CODES = {
    "SECURITY_VIOLATION",
    "PLACEHOLDER_DETECTED",
    "FORBIDDEN_FIELD",
    "MISSING_V2_BLOCK",
    "MISSING_IDENTITY_FIELD",
    "INVALID_BOUNDARY_ACKNOWLEDGEMENT",
    "MISSING_BOUNDARY_FIELD",
    "BOUNDARY_FIELD_NOT_TRUE",
    "INVALID_CONTEXT_LEVEL_RANGE",
    "CC3_REQUIRES_LOADED_CONTEXT_URLS",
    "CONTEXT_SUFFICIENT_REQUIRES_LOADED_URLS",
    "INSUFFICIENT_CONTEXT_COMPLETENESS",
    "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN",
    "HUMAN_PRIVATE_NAME_SUBMITTED_FORBIDDEN",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def diagnostic_codes_from_make_diagnostic(path: Path) -> set[str]:
    """Extract all code="..." string literals from _make_diagnostic() calls."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    codes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (
            func.id
            if isinstance(func, ast.Name)
            else func.attr
            if isinstance(func, ast.Attribute)
            else ""
        )
        if name != "_make_diagnostic":
            continue
        for kw in node.keywords:
            if (
                kw.arg == "code"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                codes.add(kw.value.value)
    return codes


def private_human_identity_codes(path: Path) -> set[str]:
    """Extract PRIVATE_HUMAN_IDENTITY codes from security.py."""
    text = path.read_text(encoding="utf-8")
    return set(
        re.findall(
            r'"(PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN|HUMAN_PRIVATE_NAME_SUBMITTED_FORBIDDEN)"',
            text,
        )
    )


def authorship_return_codes(path: Path) -> set[str]:
    """Extract error codes returned as (False, code, msg) tuples from authorship.py."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    codes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Return):
            continue
        value = node.value
        if not isinstance(value, ast.Tuple) or len(value.elts) < 3:
            continue
        first, second = value.elts[0], value.elts[1]
        if (
            isinstance(first, ast.Constant)
            and first.value is False
            and isinstance(second, ast.Constant)
            and isinstance(second.value, str)
        ):
            codes.add(second.value)
    return codes


def gateway_surfaces_authorship_codes() -> bool:
    """Check if validation.py wraps verify_authorship_proof_submission errors
    into public diagnostics. Only enforce authorship codes when true."""
    validation_text = VALIDATION_PATH.read_text(encoding="utf-8")
    return "verify_authorship_proof_submission" in validation_text and "error_code" in validation_text


def main() -> None:
    helper = json.loads(HELPER_PATH.read_text(encoding="utf-8"))
    diagnostic_help = helper.get("diagnostic_code_help", {})
    require(
        isinstance(diagnostic_help, dict),
        "field helper diagnostic_code_help must be an object",
    )

    # Collect all active codes from Gateway source
    active_codes: set[str] = set()
    active_codes.update(diagnostic_codes_from_make_diagnostic(VALIDATION_PATH))
    active_codes.update(private_human_identity_codes(SECURITY_PATH))
    active_codes.add("SECURITY_VIOLATION")

    # Only include authorship codes if Gateway surfaces them as public diagnostics
    if gateway_surfaces_authorship_codes():
        active_codes.update(authorship_return_codes(AUTHORSHIP_PATH))

    # Check: all active codes must have helper entries
    missing = sorted(code for code in active_codes if code not in diagnostic_help)
    require(
        not missing,
        "field helper missing active Gateway diagnostic help entries: "
        + ", ".join(missing),
    )

    # Check: each active entry has required fields
    for code in sorted(active_codes):
        entry = diagnostic_help[code]
        require(
            isinstance(entry, dict),
            f"diagnostic_code_help.{code} must be an object",
        )
        require(
            entry.get("meaning"),
            f"diagnostic_code_help.{code}.meaning is required",
        )
        require(
            entry.get("fix"),
            f"diagnostic_code_help.{code}.fix is required",
        )
        require(
            entry.get("severity") in {"error", "warning", "info"},
            f"diagnostic_code_help.{code}.severity invalid",
        )
        require(
            "recovery_possible" in entry,
            f"diagnostic_code_help.{code}.recovery_possible is required",
        )

    # Check: mission-critical codes are always present
    missing_mission_critical = sorted(
        code for code in MISSION_CRITICAL_CODES if code not in diagnostic_help
    )
    require(
        not missing_mission_critical,
        "field helper missing mission-critical diagnostic entries: "
        + ", ".join(missing_mission_critical),
    )

    # Semantic assertions: key mismatch recovery + security leak semantics
    _check_key_mismatch_semantics(diagnostic_help)
    _check_alias_recovery_parity(diagnostic_help)
    _check_security_privacy_aliases(diagnostic_help)

    print(
        f"PASS: gateway diagnostic helper contract ({len(active_codes)} active codes)"
    )


def require_entry(
    diagnostic_help: dict,
    code: str,
    *,
    recovery_possible: bool | None = None,
    meaning_contains: list[str] | None = None,
    fix_contains: list[str] | None = None,
) -> None:
    require(code in diagnostic_help, f"field helper missing {code}")
    entry = diagnostic_help[code]
    require(isinstance(entry, dict), f"diagnostic_code_help.{code} must be an object")

    if recovery_possible is not None:
        require(
            entry.get("recovery_possible") is recovery_possible,
            f"diagnostic_code_help.{code}.recovery_possible must be {recovery_possible}",
        )

    meaning = str(entry.get("meaning", ""))
    fix = str(entry.get("fix", ""))

    for text in meaning_contains or []:
        require(
            text in meaning,
            f"diagnostic_code_help.{code}.meaning must contain {text!r}",
        )

    for text in fix_contains or []:
        require(
            text in fix,
            f"diagnostic_code_help.{code}.fix must contain {text!r}",
        )


def _check_key_mismatch_semantics(diagnostic_help: dict) -> None:
    """Key mismatch codes must be recoverable; security/privacy leaks must not."""

    # Key mismatches: recoverable by rebuilding/re-signing
    require_entry(
        diagnostic_help,
        "PARTICIPANT_KEY_MISMATCH",
        recovery_possible=True,
        meaning_contains=[
            "submitting_participant_identity.participant_public_key_sha256",
            "authorship_proof.public_key_sha256",
        ],
        fix_contains=[
            "Rebuild",
            "same Ed25519 key",
        ],
    )

    require_entry(
        diagnostic_help,
        "GUARDIAN_KEY_MISMATCH",
        recovery_possible=True,
        meaning_contains=[
            "guardian_application_content.guardian_public_key_sha256",
            "authorship_proof.public_key_sha256",
        ],
        fix_contains=[
            "guardian_application",
            "same Ed25519 key",
            "Rebuild",
        ],
    )

    require_entry(
        diagnostic_help,
        "GUARDIAN_RETIREMENT_KEY_MISMATCH",
        recovery_possible=True,
        meaning_contains=[
            "guardian_retirement.guardian_public_key_sha256",
            "authorship_proof.public_key_sha256",
        ],
        fix_contains=[
            "guardian_retirement",
            "same Guardian Ed25519 key",
            "Rebuild",
        ],
    )

    require_entry(
        diagnostic_help,
        "LINKED_GUARDIAN_KEY_MISMATCH",
        recovery_possible=True,
        meaning_contains=[
            "optional_linked_guardian_application_request.guardian_public_key_sha256",
            "authorship_proof.public_key_sha256",
        ],
        fix_contains=[
            "standalone guardian_application",
            "matching Guardian key",
        ],
    )

    # Security/privacy leaks: NOT recoverable (stop / human review)
    for code in [
        "SECURITY_VIOLATION",
        "PRIVATE_KEY_LEAK",
        "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN",
        "HUMAN_PRIVATE_NAME_SUBMITTED_FORBIDDEN",
    ]:
        require_entry(
            diagnostic_help,
            code,
            recovery_possible=False,
        )


def _check_alias_recovery_parity(diagnostic_help: dict) -> None:
    """Aliases must not contradict canonical recovery semantics."""
    for code, entry in diagnostic_help.items():
        if not isinstance(entry, dict):
            continue

        alias_for = entry.get("alias_for")
        if not alias_for:
            continue

        require(
            alias_for in diagnostic_help,
            f"diagnostic_code_help.{code}.alias_for target {alias_for!r} is missing",
        )

        target = diagnostic_help[alias_for]
        require(
            isinstance(target, dict),
            f"diagnostic_code_help.{code}.alias_for target {alias_for!r} must be an object",
        )

        require(
            entry.get("recovery_possible") is target.get("recovery_possible"),
            (
                f"diagnostic_code_help.{code}.recovery_possible must match alias target "
                f"{alias_for}.recovery_possible"
            ),
        )

        require(
            entry.get("severity") == target.get("severity"),
            (
                f"diagnostic_code_help.{code}.severity must match alias target "
                f"{alias_for}.severity"
            ),
        )


def _check_security_privacy_aliases(diagnostic_help: dict) -> None:
    """Explicitly assert known non-recoverable security/privacy aliases."""
    for alias, target in [
        ("PRIVATE_KEY_OR_TOKEN_DETECTED", "SECURITY_VIOLATION"),
        ("HUMAN_PRIVATE_NAME_NOT_ALLOWED", "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN"),
        ("PRIVATE_IDENTITY_BLOB_NOT_ALLOWED", "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN"),
    ]:
        require(alias in diagnostic_help, f"field helper missing legacy alias {alias}")
        require(target in diagnostic_help, f"field helper missing canonical target {target}")

        alias_entry = diagnostic_help[alias]
        target_entry = diagnostic_help[target]

        require(
            alias_entry.get("alias_for") == target,
            f"{alias}.alias_for must be {target}",
        )
        require(
            alias_entry.get("recovery_possible") is False,
            f"{alias}.recovery_possible must be false because {target} is non-recoverable",
        )
        require(
            target_entry.get("recovery_possible") is False,
            f"{target}.recovery_possible must remain false",
        )


if __name__ == "__main__":
    main()
