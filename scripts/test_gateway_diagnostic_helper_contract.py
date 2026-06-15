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

    print(
        f"PASS: gateway diagnostic helper contract ({len(active_codes)} active codes)"
    )


if __name__ == "__main__":
    main()
