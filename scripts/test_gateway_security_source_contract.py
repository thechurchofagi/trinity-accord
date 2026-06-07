#!/usr/bin/env python3
"""Source-level contract tests for PR #453 Gateway security hardening.

This intentionally does not start the Node Gateway. Current system tests must
remain stable and dependency-light. Runtime HTTP Gateway tests belong in a
separate opt-in integration workflow with explicit Node dependency installation.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_server_security_markers() -> None:
    text = read("examples/github-app-backend/server.js")

    required = [
        "function computePayloadIdempotencyDigest(payload)",
        "function computeIdempotencyKey(payload)",
        "computePayloadIdempotencyDigest(payload).slice(0, 48)",
        "function validateGuardianRetirementPayload(payload)",
        "MISSING_GUARDIAN_PRESENCE_PROOF",
        "retirement_requires_guardian_presence_proof",
        "function validateTitleSafety(title)",
        "function sanitizeIssueTitleFragment(title, maxChars = 180)",
        "FORBIDDEN_TRUTH_CLAIM",
        "FORBIDDEN_AMENDMENT_VERB_CLAIM",
    ]

    for marker in required:
        if marker not in text:
            fail(f"server.js missing required hardening marker: {marker}")

    forbidden = [
        "if (provided) return provided;",
        '`[Agent Gateway] ${String(payload.title || "").slice(0, 180)}`',
        "`| Signed by Guardian Key | ${payload.signed_by_guardian_key} |`",
    ]

    for marker in forbidden:
        if marker in text:
            fail(f"server.js still contains forbidden pre-hardening pattern: {marker}")

    ok("server.js hardening markers")


def test_schema_title_pattern() -> None:
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    title = schema["properties"]["title"]

    expected = r"^(?!\s*#)(?!.*<!--)[^\r\n\u0000-\u001f\u007f]+$"
    if title.get("pattern") != expected:
        fail(f"title pattern mismatch: expected {expected!r}, got {title.get('pattern')!r}")

    if "Single-line display title" not in title.get("description", ""):
        fail("title description should explain single-line safety")

    ok("schema title pattern")


def test_python_validator_contract() -> None:
    text = read("scripts/validate_gateway_payload.py")

    required = [
        "def validate_title(payload, errors):",
        "title must be a single line",
        "title must not contain HTML comments",
        "title must not start with a Markdown heading marker",
        "discovery_provenance.agent_performed_independent_followup must match top-level agent_independent_followup",
        "agency_level={agency_level} requires discovery_provenance.agent_performed_independent_followup=true",
        "validate_title(payload, errors)",
    ]

    for marker in required:
        if marker not in text:
            fail(f"validate_gateway_payload.py missing marker: {marker}")

    ok("python validator contract")


def test_renderer_title_contract() -> None:
    text = read("scripts/render_gateway_issue_body.py")

    if 'short_title = one_line_excerpt(title, 80) if title else ""' not in text:
        fail("render_gateway_issue_body.py should use one_line_excerpt for short title")

    ok("renderer title contract")


def test_fixture_provenance_contract() -> None:
    fixture = json.loads(read("tests/fixtures/gateway/valid_pure_echo.json"))
    prov = fixture.get("discovery_provenance") or {}

    if fixture.get("agent_independent_followup") is not True:
        fail("valid_pure_echo top-level agent_independent_followup must be true")

    if prov.get("agent_performed_independent_followup") is not True:
        fail("valid_pure_echo nested agent_performed_independent_followup must be true")

    if prov.get("agent_performed_independent_followup") != fixture.get("agent_independent_followup"):
        fail("valid_pure_echo top-level and nested independent followup fields must match")

    ok("fixture provenance contract")


def main() -> int:
    test_server_security_markers()
    test_schema_title_pattern()
    test_python_validator_contract()
    test_renderer_title_contract()
    test_fixture_provenance_contract()
    print("\n=== GATEWAY SECURITY SOURCE CONTRACT PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
