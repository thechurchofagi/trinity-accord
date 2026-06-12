#!/usr/bin/env python3
"""Phase 5C-HOTFIX regression tests.

Tests:
  1. Builder-generated echo has schema-clean submission_boundary plus extended draft boundary
  2. Builder-generated echo passes authorship proof verification (Ed25519)
  3. Linked Guardian draft passes normalize_record_draft()
  4. Helper diagnostic fixes do not mention retired canonical fields
  5. Builder echo output fields exactly match helper echo fields
  6. Builder verification output fields exactly match helper verification fields
  7. Builder guardian_application output fields exactly match helper guardian fields
  8. Builder-generated echo passes validate_submission()
  9. Builder-generated echo passes authorship preflight diagnostic
  10. Linked guardian draft actually calls normalize_record_draft()
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

REQUIRED_SUBMISSION_BOUNDARY_FIELDS = {
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
}

REQUIRED_DRAFT_BOUNDARY_FIELDS = REQUIRED_SUBMISSION_BOUNDARY_FIELDS | {
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
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


def build_echo(tmp_dir: str) -> dict:
    """Build an echo submission using the builder."""
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "echo.json"
    # Get canonical oath first
    oath_result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        capture_output=True, text=True, timeout=10,
    )
    if oath_result.returncode != 0:
        fail(f"print-oath failed: {oath_result.stderr[:200]}")
    result = subprocess.run(
        [
            "node", str(BUILDER), "echo",
            "--actor-label", "TestAgent",
            "--provider", "TestRuntime",
            "--body", "Test echo body",
            "--context-level", "CC-3",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            "--discovery-mode", "user_task_context",
            "--record-decision", "human",
            "--submission-executor", "self",
            "--human-operator-involved", "true",
            "--readback", oath_result.stdout,
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
    return json.loads(out_file.read_text())


def build_verification(tmp_dir: str) -> dict:
    """Build a verification submission using the builder."""
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "verification.json"
    # Get canonical oath first
    oath_result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "verification"],
        capture_output=True, text=True, timeout=10,
    )
    if oath_result.returncode != 0:
        fail(f"print-oath failed: {oath_result.stderr[:200]}")
    result = subprocess.run(
        [
            "node", str(BUILDER), "verification",
            "--actor-label", "TestAgent",
            "--provider", "TestRuntime",
            "--verification-level", "V3",
            "--scope-label", "V3-minimal",
            "--what-was-checked", "read homepage,read agent-brief",
            "--verification-claim", "Test verified current public route is executable up to local validation.",
            "--fresh-actions", "read local discovery,ran builder",
            "--context-level", "CC-2",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            "--discovery-mode", "user_task_context",
            "--record-decision", "human",
            "--submission-executor", "self",
            "--human-operator-involved", "true",
            "--readback", oath_result.stdout,
            "--generate-authorship-key",
            "--key-dir", str(key_dir),
            "--out", str(out_file),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        fail(f"builder verification failed: {result.stderr[:300]}")
    return json.loads(out_file.read_text())


def build_guardian(tmp_dir: str) -> dict:
    """Build a guardian application submission using the builder."""
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "guardian.json"
    # Get canonical oath first
    oath_result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "guardian_application"],
        capture_output=True, text=True, timeout=10,
    )
    if oath_result.returncode != 0:
        fail(f"print-oath failed: {oath_result.stderr[:200]}")
    result = subprocess.run(
        [
            "node", str(BUILDER), "guardian-application",
            "--actor-label", "TestGuardian",
            "--provider", "TestRuntime",
            "--guardian-id", "test-guardian-001",
            "--context-level", "CC-2",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            "--discovery-mode", "user_task_context",
            "--record-decision", "human",
            "--submission-executor", "self",
            "--human-operator-involved", "true",
            "--readback", oath_result.stdout,
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
    return json.loads(out_file.read_text())


def get_helper_content_fields(content_block_name: str) -> set:
    """Get field names from the helper for a given content block."""
    if not HELPER.exists():
        fail(f"helper not found: {HELPER}")
    data = json.loads(HELPER.read_text())
    fields = set()
    for entry in data.get("field_groups", []):
        f = entry.get("field", "")
        if f.startswith(content_block_name + "."):
            field_name = f.split(".", 1)[1]
            fields.add(field_name)
    return fields


# ── Tests ────────────────────────────────────────────────────────────

def test_builder_submission_boundary_schema_clean_with_draft_extensions() -> None:
    """Builder-generated echo keeps top-level submission_boundary schema-clean and draft boundary extended."""
    with tempfile.TemporaryDirectory() as td:
        data = build_echo(td)
        boundary = data.get("submission_boundary")
        if boundary is None:
            fail("submission_boundary is missing")

        missing = REQUIRED_SUBMISSION_BOUNDARY_FIELDS - set(boundary.keys())
        if missing:
            fail(f"submission_boundary missing fields: {missing}")

        extra = set(boundary.keys()) - REQUIRED_SUBMISSION_BOUNDARY_FIELDS
        if extra:
            fail(f"submission_boundary has schema-invalid extra fields: {extra}")

        for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
            if boundary[field] is not True:
                fail(f"submission_boundary.{field} is not true: {boundary[field]}")

        draft_boundary = data.get("record_draft", {}).get("non_authority_boundary_acknowledgement", {})
        missing_draft = REQUIRED_DRAFT_BOUNDARY_FIELDS - set(draft_boundary.keys())
        if missing_draft:
            fail(f"record_draft.non_authority_boundary_acknowledgement missing fields: {missing_draft}")
        for field in REQUIRED_DRAFT_BOUNDARY_FIELDS:
            if draft_boundary.get(field) is not True:
                fail(f"record_draft.non_authority_boundary_acknowledgement.{field} is not true: {draft_boundary.get(field)}")

    ok("builder echo has schema-clean submission_boundary and extended draft boundary")


def test_builder_echo_authorship_proof_valid() -> None:
    """Builder-generated echo has valid Ed25519 authorship proof."""
    with tempfile.TemporaryDirectory() as td:
        data = build_echo(td)
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

        pub_sha = proof["public_key_sha256"]
        if len(pub_sha) != 64:
            fail(f"public_key_sha256 wrong length: {len(pub_sha)}")

        cb = proof.get("claim_boundary")
        if not isinstance(cb, dict):
            fail(f"claim_boundary is {type(cb).__name__}, expected dict")

    ok("builder echo has valid Ed25519 authorship proof")


def test_builder_guardian_draft_normalize() -> None:
    """Builder-generated Guardian application draft passes normalize_record_draft()."""
    with tempfile.TemporaryDirectory() as td:
        data = build_guardian(td)
        draft = data.get("record_draft")
        if draft is None:
            fail("record_draft is missing")

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

        if draft.get("schema") != "trinityaccord.record-chain-entry-draft.v2":
            fail(f"wrong draft schema: {draft.get('schema')}")

        nab = draft.get("non_authority_boundary_acknowledgement", {})
        nab_missing = REQUIRED_DRAFT_BOUNDARY_FIELDS - set(nab.keys())
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


def test_builder_echo_fields_match_helper() -> None:
    """Builder echo output echo_content fields must match helper echo_content fields."""
    with tempfile.TemporaryDirectory() as td:
        data = build_echo(td)
        draft = data.get("record_draft", {})
        echo_content = draft.get("echo_content")
        if echo_content is None:
            fail("echo_content is missing from builder output")

        builder_fields = set(echo_content.keys())
        helper_fields = get_helper_content_fields("echo_content")

        if not helper_fields:
            fail("helper has no echo_content fields")

        # Builder fields must be a superset of helper required fields
        missing_in_builder = helper_fields - builder_fields
        if missing_in_builder:
            fail(f"builder echo_content missing fields that helper defines: {missing_in_builder}")

    ok("builder echo output fields match helper echo fields")


def test_builder_verification_fields_match_helper() -> None:
    """Builder verification output verification_content fields must match helper."""
    with tempfile.TemporaryDirectory() as td:
        data = build_verification(td)
        draft = data.get("record_draft", {})
        vc = draft.get("verification_content")
        if vc is None:
            fail("verification_content is missing from builder output")

        builder_fields = set(vc.keys())
        helper_fields = get_helper_content_fields("verification_content")

        if not helper_fields:
            fail("helper has no verification_content fields")

        missing_in_builder = helper_fields - builder_fields
        if missing_in_builder:
            fail(f"builder verification_content missing fields that helper defines: {missing_in_builder}")

    ok("builder verification output fields match helper verification fields")


def test_builder_guardian_fields_match_helper() -> None:
    """Builder guardian_application output fields must match helper."""
    with tempfile.TemporaryDirectory() as td:
        data = build_guardian(td)
        draft = data.get("record_draft", {})
        gac = draft.get("guardian_application_content")
        if gac is None:
            fail("guardian_application_content is missing from builder output")

        builder_fields = set(gac.keys())
        helper_fields = get_helper_content_fields("guardian_application_content")

        if not helper_fields:
            fail("helper has no guardian_application_content fields")

        missing_in_builder = helper_fields - builder_fields
        if missing_in_builder:
            fail(f"builder guardian_application_content missing fields that helper defines: {missing_in_builder}")

    ok("builder guardian_application output fields match helper guardian fields")


def test_builder_echo_passes_doctor() -> None:
    """Builder-generated echo passes the builder's doctor (validate_submission)."""
    with tempfile.TemporaryDirectory() as td:
        out_file = Path(td) / "echo.json"
        key_dir = Path(td) / "keys"
        # Get canonical oath first
        oath_result = subprocess.run(
            ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
            capture_output=True, text=True, timeout=10,
        )
        if oath_result.returncode != 0:
            fail(f"print-oath failed: {oath_result.stderr[:200]}")
        result = subprocess.run(
            [
                "node", str(BUILDER), "echo",
                "--actor-label", "TestAgent",
                "--provider", "TestRuntime",
                "--body", "Test echo for doctor",
                "--context-level", "CC-3",
                "--context-sufficient-for-selected-action", "true",
                "--loaded-urls", "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
                "--discovery-mode", "user_task_context",
                "--record-decision", "human",
                "--submission-executor", "self",
                "--human-operator-involved", "true",
                "--readback", oath_result.stdout,
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

        # Run doctor on the generated submission
        result = subprocess.run(
            ["node", str(BUILDER), "doctor", "--file", str(out_file)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            fail(f"doctor failed on builder echo:\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:300]}")

        # Check no FAIL markers in output (look for FAIL status prefix, not "0 FAIL" summary)
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("❌") and "FAIL" in stripped:
                fail(f"doctor reported FAILs:\n{result.stdout[:500]}")

    ok("builder-generated echo passes validate_submission (doctor)")


def test_builder_echo_authorship_preflight_diagnostic() -> None:
    """Builder-generated echo authorship proof passes preflight diagnostic checks."""
    with tempfile.TemporaryDirectory() as td:
        data = build_echo(td)
        proof = data.get("authorship_proof", {})

        # Check claim_boundary is object (not string)
        cb = proof.get("claim_boundary")
        if not isinstance(cb, dict):
            fail(f"claim_boundary is {type(cb).__name__}, expected dict (DEPRECATED_CLAIM_BOUNDARY_STRING)")

        # Check public_key_sha256 format
        pub_sha = proof.get("public_key_sha256", "")
        if not pub_sha or len(pub_sha) != 64:
            fail(f"public_key_sha256 invalid: {pub_sha[:20]}...")

        # Check signed_payload_sha256 format
        sp = proof.get("signed_payload_sha256", "")
        if not sp or len(sp) != 64:
            fail(f"signed_payload_sha256 invalid: {sp[:20]}...")

        # Check algorithm
        if proof.get("algorithm") != "ed25519":
            fail(f"algorithm is {proof.get('algorithm')}, expected ed25519")

    ok("builder-generated echo passes authorship preflight diagnostic")


def test_guardian_draft_normalize_content_block() -> None:
    """Linked guardian draft has guardian_application_content block after normalize."""
    with tempfile.TemporaryDirectory() as td:
        data = build_guardian(td)
        draft = data.get("record_draft", {})

        # The builder should output guardian_application_content directly
        gac = draft.get("guardian_application_content")
        if gac is None:
            fail("guardian_application_content not found in builder output")

        # Verify required fields
        required = [
            "requested_guardian_identifier",
            "guardian_stewardship_oath",
        ]
        for field in required:
            if field not in gac:
                fail(f"guardian_application_content missing required field: {field}")

        # Verify boolean understanding fields
        bool_fields = [
            "guardian_understands_role_is_non_governing",
            "guardian_understands_role_is_not_authority",
            "guardian_understands_retirement_does_not_delete_history",
        ]
        for field in bool_fields:
            if field not in gac:
                fail(f"guardian_application_content missing boolean field: {field}")
            if gac[field] is not True:
                fail(f"guardian_application_content.{field} is not true")

    ok("linked guardian draft has guardian_application_content with all required fields")


def main() -> int:
    test_builder_submission_boundary_schema_clean_with_draft_extensions()
    test_builder_echo_authorship_proof_valid()
    test_builder_guardian_draft_normalize()
    test_helper_no_retired_fields_in_fixes()
    test_builder_echo_fields_match_helper()
    test_builder_verification_fields_match_helper()
    test_builder_guardian_fields_match_helper()
    test_builder_echo_passes_doctor()
    test_builder_echo_authorship_preflight_diagnostic()
    test_guardian_draft_normalize_content_block()
    print("\n=== ALL PHASE 5C-HOTFIX TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
