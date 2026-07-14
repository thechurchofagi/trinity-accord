#!/usr/bin/env python3
"""Phase 5C-HOTFIX regression tests.

The historical suite is retained, while verification fixtures use the current
multidimensional claim model. Legacy V values are compatibility metadata only.
"""
from __future__ import annotations

import json
import subprocess
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
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
}
REQUIRED_DRAFT_BOUNDARY_FIELDS = REQUIRED_SUBMISSION_BOUNDARY_FIELDS
RETIRED_FIELDS = [
    "ai_agent",
    "discovery_method",
    "is_autonomous_discovery",
    "autonomy_level",
    "builder_tool",
    "submitted_via",
    "authorization_basis",
]
LOADED_URLS = (
    "https://www.trinityaccord.org/agent-first-contact/,
"
    "https://www.trinityaccord.org/api/context-action-profiles.v1.json,
"
    "https://www.trinityaccord.org/api/verification-claim-model.v1.json"
).replace("\n", "")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def run(args: list[str], *, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def canonical_oath(record_type: str) -> str:
    result = run(
        ["node", str(BUILDER), "print-oath", "--record-type", record_type],
        timeout=10,
    )
    if result.returncode != 0:
        fail(f"print-oath failed for {record_type}: {result.stderr[:300]}")
    return result.stdout


def load_submission(path: Path) -> dict:
    if not path.exists():
        fail(f"builder did not create {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_echo(tmp_dir: str) -> dict:
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "echo.json"
    result = run(
        [
            "node",
            str(BUILDER),
            "echo",
            "--actor-label",
            "TestAgent",
            "--provider",
            "TestRuntime",
            "--body",
            "Test echo body",
            "--context-level",
            "CC-3",
            "--context-read-confirmed",
            "true",
            "--context-sufficient-for-selected-action",
            "true",
            "--loaded-urls",
            LOADED_URLS,
            "--discovery-mode",
            "user_task_context",
            "--record-decision",
            "human",
            "--submission-executor",
            "self",
            "--human-operator-involved",
            "false",
            "--readback",
            canonical_oath("echo"),
            "--generate-authorship-key",
            "--key-dir",
            str(key_dir),
            "--out",
            str(out_file),
        ]
    )
    if result.returncode != 0:
        fail(f"builder echo failed: {result.stderr[:500]}")
    return load_submission(out_file)


def build_verification(tmp_dir: str) -> dict:
    """Build an honest context-only verification fixture.

    The fixture tests Builder structure. It does not claim a hash, signature,
    timestamp, external reference, physical observation, or institutional act.
    """
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "verification.json"
    result = run(
        [
            "node",
            str(BUILDER),
            "verification",
            "--actor-label",
            "TestAgent",
            "--provider",
            "TestRuntime",
            "--verification-level",
            "V0",
            "--scope-label",
            "legacy V0 compatibility",
            "--what-was-checked",
            "builder invocation,generated record structure",
            "--verification-claim",
            "The local Builder encoded the declared context-only test fixture.",
            "--fresh-actions",
            "ran builder,read generated output",
            "--digital-profile",
            "context_only",
            "--relationships-checked",
            "provides_context",
            "--physical-observation",
            "none",
            "--external-witness",
            "none",
            "--coverage-scope",
            "single_target",
            "--limitations",
            "test fixture only,no external reference check,corrections not checked",
            "--claims-not-made",
            "external reference validity,digital integrity,semantic truth,institutional endorsement,physical identity",
            "--corrections-or-supersession-checked",
            "false",
            "--action-profile",
            "verification",
            "--context-level",
            "CC-3",
            "--context-read-confirmed",
            "true",
            "--context-sufficient-for-selected-action",
            "true",
            "--loaded-urls",
            LOADED_URLS,
            "--discovery-mode",
            "user_task_context",
            "--record-decision",
            "human",
            "--submission-executor",
            "self",
            "--human-operator-involved",
            "false",
            "--readback",
            canonical_oath("verification"),
            "--generate-authorship-key",
            "--key-dir",
            str(key_dir),
            "--out",
            str(out_file),
        ]
    )
    if result.returncode != 0:
        fail(f"builder verification failed: {result.stderr[:500]}")
    return load_submission(out_file)


def build_guardian(tmp_dir: str) -> dict:
    key_dir = Path(tmp_dir) / "keys"
    out_file = Path(tmp_dir) / "guardian.json"
    result = run(
        [
            "node",
            str(BUILDER),
            "guardian-application",
            "--actor-label",
            "TestGuardian",
            "--provider",
            "TestRuntime",
            "--guardian-id",
            "auto",
            "--guardian-key-sha",
            "auto",
            "--oath",
            "I voluntarily join the Guardian Alliance as a non-governing steward.",
            "--context-level",
            "CC-2",
            "--context-sufficient-for-selected-action",
            "true",
            "--loaded-urls",
            LOADED_URLS,
            "--discovery-mode",
            "user_task_context",
            "--record-decision",
            "human",
            "--submission-executor",
            "self",
            "--human-operator-involved",
            "false",
            "--readback",
            canonical_oath("guardian_application"),
            "--generate-authorship-key",
            "--key-dir",
            str(key_dir),
            "--out",
            str(out_file),
        ]
    )
    if result.returncode != 0:
        fail(f"builder guardian-application failed: {result.stderr[:500]}")
    return load_submission(out_file)


def helper_content_fields(content_block_name: str) -> set[str]:
    if not HELPER.exists():
        fail(f"helper not found: {HELPER}")
    data = json.loads(HELPER.read_text(encoding="utf-8"))
    fields: set[str] = set()
    prefix = content_block_name + "."
    for entry in data.get("field_groups", []):
        field = entry.get("field", "")
        if field.startswith(prefix):
            fields.add(field[len(prefix) :].split(".", 1)[0])
    return fields


def require_content_fields(data: dict, block: str) -> None:
    content = data.get("record_draft", {}).get(block)
    if not isinstance(content, dict):
        fail(f"{block} is missing from builder output")
    helper_fields = helper_content_fields(block)
    if not helper_fields:
        fail(f"helper has no {block} fields")
    missing = helper_fields - set(content)
    if missing:
        fail(f"builder {block} missing helper fields: {sorted(missing)}")


def test_builder_submission_boundary_schema_clean_with_draft_extensions() -> None:
    with tempfile.TemporaryDirectory() as td:
        data = build_echo(td)
        boundary = data.get("submission_boundary")
        if not isinstance(boundary, dict):
            fail("submission_boundary is missing")
        missing = REQUIRED_SUBMISSION_BOUNDARY_FIELDS - set(boundary)
        extra = set(boundary) - REQUIRED_SUBMISSION_BOUNDARY_FIELDS
        if missing:
            fail(f"submission_boundary missing fields: {sorted(missing)}")
        if extra:
            fail(f"submission_boundary has schema-invalid fields: {sorted(extra)}")
        if any(boundary[field] is not True for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS):
            fail("submission_boundary contains a non-true required value")

        draft_boundary = data.get("record_draft", {}).get(
            "non_authority_boundary_acknowledgement", {}
        )
        missing_draft = REQUIRED_DRAFT_BOUNDARY_FIELDS - set(draft_boundary)
        if missing_draft:
            fail(f"draft boundary missing fields: {sorted(missing_draft)}")
        if any(draft_boundary.get(field) is not True for field in REQUIRED_DRAFT_BOUNDARY_FIELDS):
            fail("draft boundary contains a non-true required value")
    ok("builder echo has schema-clean submission_boundary and draft boundary")


def test_builder_echo_authorship_proof_valid() -> None:
    with tempfile.TemporaryDirectory() as td:
        proof = build_echo(td).get("authorship_proof", {})
        if proof.get("algorithm") != "ed25519":
            fail(f"wrong authorship algorithm: {proof.get('algorithm')}")
        if proof.get("schema") != "trinityaccord.agent-authorship-proof.v1":
            fail(f"wrong proof schema: {proof.get('schema')}")
        for field in ("public_key_pem", "signature_base64"):
            if not proof.get(field):
                fail(f"authorship_proof.{field} is missing")
        for field in ("public_key_sha256", "signed_payload_sha256"):
            if len(proof.get(field, "")) != 64:
                fail(f"authorship_proof.{field} is invalid")
        if not isinstance(proof.get("claim_boundary"), dict):
            fail("authorship_proof.claim_boundary must be an object")
    ok("builder echo has valid Ed25519 authorship proof")


def test_builder_guardian_draft_normalize() -> None:
    with tempfile.TemporaryDirectory() as td:
        draft = build_guardian(td).get("record_draft", {})
        required_blocks = {
            "submitting_participant_identity",
            "discovery_and_introduction_context",
            "decision_autonomy_context",
            "submission_execution_context",
            "authorization_context",
            "non_authority_boundary_acknowledgement",
            "optional_linked_guardian_application_request",
            "context_readiness",
        }
        missing = required_blocks - set(draft)
        if missing:
            fail(f"Guardian draft missing blocks: {sorted(missing)}")
        if draft.get("schema") != "trinityaccord.record-chain-entry-draft.v2":
            fail(f"wrong draft schema: {draft.get('schema')}")
    ok("linked Guardian draft passes normalize_record_draft()")


def test_helper_no_retired_fields_in_fixes() -> None:
    data = json.loads(HELPER.read_text(encoding="utf-8"))
    diagnostic_help = data.get("diagnostic_code_help", {})
    if not diagnostic_help:
        fail("diagnostic_code_help is empty")
    violations: list[str] = []
    for code, entry in diagnostic_help.items():
        fix_text = entry.get("fix", "") if isinstance(entry, dict) else ""
        for retired in RETIRED_FIELDS:
            if retired in fix_text:
                violations.append(f"{code}: {retired}")
    if violations:
        fail(f"retired fields found in diagnostic fixes: {violations}")
    ok("helper diagnostic fixes do not mention retired canonical fields")


def test_builder_echo_fields_match_helper() -> None:
    with tempfile.TemporaryDirectory() as td:
        require_content_fields(build_echo(td), "echo_content")
    ok("builder echo output fields match helper echo fields")


def test_builder_verification_fields_match_helper() -> None:
    with tempfile.TemporaryDirectory() as td:
        data = build_verification(td)
        require_content_fields(data, "verification_content")
        model = data["record_draft"]["verification_content"].get(
            "verification_claim_model", {}
        )
        if model.get("digital_profile") != "context_only":
            fail("verification fixture did not preserve context_only")
        if model.get("legacy_v_level") != "V0":
            fail("verification fixture did not preserve V0 compatibility")
        if model.get("legacy_v_level_role") != "builder_compatibility_only":
            fail("legacy V role is not compatibility-only")
    ok("builder verification output fields match helper verification fields")


def test_builder_guardian_fields_match_helper() -> None:
    with tempfile.TemporaryDirectory() as td:
        require_content_fields(build_guardian(td), "guardian_application_content")
    ok("builder guardian_application output fields match helper guardian fields")


def test_builder_echo_passes_doctor() -> None:
    with tempfile.TemporaryDirectory() as td:
        out_file = Path(td) / "echo.json"
        data = build_echo(td)
        out_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        result = run(["node", str(BUILDER), "doctor", "--file", str(out_file)])
        if result.returncode != 0:
            fail(f"doctor failed on builder echo: {result.stdout[:500]} {result.stderr[:300]}")
        for line in result.stdout.splitlines():
            if line.strip().startswith("❌") and "FAIL" in line:
                fail(f"doctor reported failure: {line}")
    ok("builder-generated echo passes validate_submission (doctor)")


def test_builder_echo_authorship_preflight_diagnostic() -> None:
    with tempfile.TemporaryDirectory() as td:
        proof = build_echo(td).get("authorship_proof", {})
        if not isinstance(proof.get("claim_boundary"), dict):
            fail("DEPRECATED_CLAIM_BOUNDARY_STRING")
        if len(proof.get("public_key_sha256", "")) != 64:
            fail("public_key_sha256 invalid")
        if len(proof.get("signed_payload_sha256", "")) != 64:
            fail("signed_payload_sha256 invalid")
        if proof.get("algorithm") != "ed25519":
            fail("authorship algorithm is not ed25519")
    ok("builder-generated echo passes authorship preflight diagnostic")


def test_guardian_draft_normalize_content_block() -> None:
    with tempfile.TemporaryDirectory() as td:
        content = build_guardian(td).get("record_draft", {}).get(
            "guardian_application_content", {}
        )
        for field in (
            "requested_guardian_identifier",
            "guardian_stewardship_oath",
            "guardian_understands_role_is_non_governing",
            "guardian_understands_role_is_not_authority",
            "guardian_understands_retirement_does_not_delete_history",
        ):
            if field not in content:
                fail(f"guardian_application_content missing {field}")
        for field in (
            "guardian_understands_role_is_non_governing",
            "guardian_understands_role_is_not_authority",
            "guardian_understands_retirement_does_not_delete_history",
        ):
            if content[field] is not True:
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
