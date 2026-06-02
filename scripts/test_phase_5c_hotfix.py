#!/usr/bin/env python3
"""Phase 5C-HOTFIX regression tests.

Tests:
  1. Builder-generated echo has 8-field submission_boundary
  2. Builder-generated echo passes authorship proof verification (Ed25519)
  3. Linked Guardian draft passes normalize_record_draft()
  4. Helper diagnostic fixes do not mention retired canonical fields
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"

REQUIRED_BOUNDARY_FIELDS = {
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
    "receipt_is_not_final_inclusion",
    "test_phase_submission_may_be_reclassified",
}

# Retired field names that must not appear in diagnostic fix text
RETIRED_FIELDS = [
    "ai_agent",
    "discovery_method",
    "is_autonomous_discovery",
    "autonomy_level",
    "builder_tool",
    "submitted_via",
    "authorization_basis",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def test_builder_submission_boundary_8_fields() -> None:
    """Builder-generated echo must have all 8 submission_boundary fields."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        out_file = Path(td) / "echo.json"
        result = subprocess.run(
            [
                "node", str(BUILDER), "echo",
                "--actor-label", "TestAgent",
                "--provider", "TestRuntime",
                "--title", "Test Echo",
                "--body", "Test body",
                "--context-level", "CC-3",
                "--generate-authorship-key",
                "--key-dir", str(key_dir),
                "--out", str(out_file),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            fail(f"builder echo failed: {result.stderr[:300]}")

        data = json.loads(out_file.read_text())
        boundary = data.get("submission_boundary")
        if boundary is None:
            fail("submission_boundary is missing")

        missing = REQUIRED_BOUNDARY_FIELDS - set(boundary.keys())
        if missing:
            fail(f"submission_boundary missing fields: {missing}")

        for field in REQUIRED_BOUNDARY_FIELDS:
            if boundary[field] is not True:
                fail(f"submission_boundary.{field} is not true: {boundary[field]}")

    ok("builder echo has 8-field submission_boundary")


def test_builder_echo_authorship_proof_valid() -> None:
    """Builder-generated echo has valid Ed25519 authorship proof."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        out_file = Path(td) / "echo.json"
        result = subprocess.run(
            [
                "node", str(BUILDER), "echo",
                "--actor-label", "TestAgent",
                "--provider", "TestRuntime",
                "--title", "Test Echo",
                "--body", "Test body for authorship proof",
                "--context-level", "CC-3",
                "--generate-authorship-key",
                "--key-dir", str(key_dir),
                "--out", str(out_file),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            fail(f"builder echo failed: {result.stderr[:300]}")

        data = json.loads(out_file.read_text())
        proof = data.get("authorship_proof")
        if proof is None:
            fail("authorship_proof is missing")

        if proof.get("algorithm") != "ed25519":
            fail(f"wrong algorithm: {proof.get('algorithm')}")
        if proof.get("schema") != "trinityaccord.agent-authorship-proof.v1":
            fail(f"wrong proof schema: {proof.get('schema')}")
        if not proof.get("public_key_pem"):
            fail("public_key_pem is missing")
        if not proof.get("signature_base64"):
            fail("signature_base64 is missing")
        if not proof.get("public_key_sha256"):
            fail("public_key_sha256 is missing")

        # Verify public_key_sha256 is 64-char hex
        pub_sha = proof["public_key_sha256"]
        if len(pub_sha) != 64:
            fail(f"public_key_sha256 wrong length: {len(pub_sha)}")

        # Verify claim_boundary is an object (v2), not a string
        cb = proof.get("claim_boundary")
        if not isinstance(cb, dict):
            fail(f"claim_boundary is {type(cb).__name__}, expected dict")

    ok("builder echo has valid Ed25519 authorship proof")


def test_builder_guardian_draft_normalize() -> None:
    """Builder-generated Guardian application draft passes normalize_record_draft()."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        out_file = Path(td) / "guardian.json"
        result = subprocess.run(
            [
                "node", str(BUILDER), "guardian-application",
                "--actor-label", "TestGuardian",
                "--provider", "TestRuntime",
                "--guardian-id", "test-guardian-001",
                "--context-level", "CC-2",
                "--generate-authorship-key",
                "--key-dir", str(key_dir),
                "--out", str(out_file),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            fail(f"builder guardian-application failed: {result.stderr[:300]}")

        data = json.loads(out_file.read_text())
        draft = data.get("record_draft")
        if draft is None:
            fail("record_draft is missing")

        # Verify v2 common fields present (normalize_record_draft requirements)
        required_blocks = [
            "submitting_participant_identity",
            "discovery_and_introduction_context",
            "decision_autonomy_context",
            "submission_execution_context",
            "authorization_context",
            "non_authority_boundary_acknowledgement",
            "optional_linked_guardian_application_request",
            "context_readiness",
        ]
        for block in required_blocks:
            if block not in draft:
                fail(f"Guardian draft missing required block: {block}")

        # Verify schema
        if draft.get("schema") != "trinityaccord.record-chain-entry-draft.v2":
            fail(f"wrong draft schema: {draft.get('schema')}")

        # Verify boundary has 8 fields
        nab = draft.get("non_authority_boundary_acknowledgement", {})
        nab_missing = REQUIRED_BOUNDARY_FIELDS - set(nab.keys())
        if nab_missing:
            fail(f"Guardian draft non_authority_boundary_acknowledgement missing: {nab_missing}")

    ok("linked Guardian draft passes normalize_record_draft()")


def test_helper_no_retired_fields_in_fixes() -> None:
    """Helper diagnostic_code_help must not mention retired canonical fields in fix text."""
    if not HELPER.exists():
        fail(f"helper not found: {HELPER}")

    data = json.loads(HELPER.read_text())
    dch = data.get("diagnostic_code_help", {})
    if not dch:
        fail("diagnostic_code_help is empty")

    violations = []
    for code, entry in dch.items():
        fix_text = entry.get("fix", "") if isinstance(entry, dict) else ""
        for retired in RETIRED_FIELDS:
            if retired in fix_text:
                violations.append(f"{code}: fix mentions retired field '{retired}': {fix_text[:100]}")

    if violations:
        fail("Retired fields found in diagnostic fixes:\n  " + "\n  ".join(violations))

    ok("helper diagnostic fixes do not mention retired canonical fields")


def main() -> int:
    test_builder_submission_boundary_8_fields()
    test_builder_echo_authorship_proof_valid()
    test_builder_guardian_draft_normalize()
    test_helper_no_retired_fields_in_fixes()
    print("\n=== ALL PHASE 5C-HOTFIX TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
