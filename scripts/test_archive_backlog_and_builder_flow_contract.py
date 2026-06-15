#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def assert_template(record_type: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "template.json"
        result = run([
            "node",
            "downloads/record-chain-builder.mjs",
            "template",
            "--record-type",
            record_type,
            "--out",
            str(out),
        ])
        if result.returncode != 0:
            fail(f"template failed for {record_type}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        require(out.exists(), f"template did not write output for {record_type}")
        data = json.loads(out.read_text(encoding="utf-8"))
        require(isinstance(data, dict), f"template output not JSON object for {record_type}")
        return data


def assert_guardian_template(record_type: str, expected_type: str, expected_scope: str) -> None:
    data = assert_template(record_type)

    require(
        data.get("record_type") == expected_type,
        f"{record_type} template record_type mismatch: {data.get('record_type')!r}",
    )

    optional = data.get("optional_linked_guardian_application_request")
    require(
        isinstance(optional, dict),
        f"{record_type} template missing optional_linked_guardian_application_request",
    )
    require(
        optional.get("does_participant_request_guardian_application_with_this_record") is False,
        f"{record_type} template optional linked guardian request must default false",
    )

    auth = data.get("authorization_context") or {}
    require(
        auth.get("authorization_scope") == expected_scope,
        f"{record_type} template authorization_scope mismatch: {auth.get('authorization_scope')!r}",
    )


def assert_builder_command_fails(args: list[str], expected_text: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "submission.json"
        result = run([
            "node",
            "downloads/record-chain-builder.mjs",
            *args,
            "--actor-label",
            "Test Agent",
            "--provider",
            "Test Runtime",
            "--context-level",
            "CC-3",
            "--context-sufficient-for-selected-action",
            "true",
            "--loaded-urls",
            "https://www.trinityaccord.org/agent-start/",
            "--discovery-mode",
            "user_task_context",
            "--requesting-party-type",
            "human",
            "--record-decision",
            "human",
            "--submission-executor",
            "self",
            "--human-operator-involved",
            "false",
            "--readback",
            "not-used-because-validation-should-fail-before-oath",
            "--key-dir",
            str(Path(tmp) / "keys"),
            "--out",
            str(out),
        ])
        require(
            result.returncode != 0,
            f"builder command unexpectedly passed: {' '.join(args)}",
        )
        combined = result.stdout + "\n" + result.stderr
        require(
            expected_text in combined,
            f"builder failure did not mention {expected_text!r}; got:\n{combined}",
        )


def assert_doctor_fails_for_draft(record_type: str, draft: dict, expected_code: str, expected_scope: str) -> None:
    submission = {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "record_type": record_type,
        "record_draft": {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": record_type,
            "context_readiness": {
                "declared_context_level": "CC-3",
                "minimum_required_for_action": "CC-3",
                "context_sufficient_for_selected_action": True,
                "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
            },
            "authorization_context": {
                "authorization_scope": expected_scope,
            },
            **draft,
        },
    }

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad-submission.json"
        path.write_text(json.dumps(submission, indent=2), encoding="utf-8")
        result = run(["node", "downloads/record-chain-builder.mjs", "doctor", "--file", str(path)])
        require(
            result.returncode != 0,
            f"builder doctor unexpectedly passed invalid {record_type}",
        )
        combined = result.stdout + "\n" + result.stderr
        require(
            expected_code in combined,
            f"doctor failure did not mention {expected_code}; got:\n{combined}",
        )


def assert_bad_classification_doctor_fails() -> None:
    bad = {
        "submission_type": "record_chain_entry",
        "schema": "trinityaccord.record-chain-submission.v1",
        "record_type": "classification_update",
        "record_draft": {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": "classification_update",
            "classification_update_content": {
                "target_record_id": "",
                "target_record_sha256": "bad",
                "previous_classification": "",
                "new_classification": "",
                "classification_reason": "",
                "evidence_or_review_basis": "",
            },
            "context_readiness": {
                "declared_context_level": "CC-2",
                "minimum_required_for_action": "CC-2",
                "context_sufficient_for_selected_action": True,
                "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
                "context_readiness_notes": "test",
            },
        },
    }

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad-classification.json"
        path.write_text(json.dumps(bad, indent=2), encoding="utf-8")
        result = run(["node", "downloads/record-chain-builder.mjs", "doctor", "--file", str(path)])
        require(
            result.returncode != 0,
            "builder doctor unexpectedly passed invalid classification_update_content",
        )
        combined = result.stdout + "\n" + result.stderr
        require(
            "MISSING_CLASSIFICATION_UPDATE_CONTENT" in combined
            or "INVALID_CLASSIFICATION_TARGET_SHA" in combined,
            "doctor failure did not mention classification_update content diagnostics",
        )


def main() -> None:
    workflow = read(".github/workflows/archive-backlog-repair.yml")
    builder_text = read("downloads/record-chain-builder.mjs")
    manifest = json.loads(read("api/record-chain-builder-bundles.v1.json"))
    builder_bytes = (ROOT / "downloads" / "record-chain-builder.mjs").read_bytes()

    require(
        "record-chain/arweave-archives/" in workflow,
        "archive-backlog-repair.yml must git add record-chain/arweave-archives/",
    )
    require(
        "api/record-chain-arweave-index.json" in workflow,
        "archive-backlog-repair.yml must git add api/record-chain-arweave-index.json",
    )
    require(
        "Failed to push archive backlog repair metadata after retries" in workflow,
        "archive-backlog-repair.yml must use push retry/rebase for repaired metadata",
    )

    require(
        "const rt = normalizeRecordType(recordType)" in builder_text,
        "generateTemplate must normalize recordType internally",
    )
    require(
        'draft.record_type === "classification_update"' in builder_text,
        "builder doctor must check classification_update records",
    )
    require("MISSING_CLASSIFICATION_UPDATE_CONTENT" in builder_text, "missing classification content diagnostic")
    require("INVALID_CLASSIFICATION_TARGET_SHA" in builder_text, "missing classification sha diagnostic")

    for record_type in [
        "classification-update",
        "classification_update",
        "guardian-application",
        "guardian_application",
        "guardian-retirement",
        "guardian_retirement",
        "context-insufficient",
        "context_insufficient_notice",
    ]:
        assert_template(record_type)

    # Guardian semantic template assertions (hyphen and underscore forms)
    assert_guardian_template(
        "guardian-application",
        "guardian_application",
        "create_guardian_application_record",
    )
    assert_guardian_template(
        "guardian_application",
        "guardian_application",
        "create_guardian_application_record",
    )
    assert_guardian_template(
        "guardian-retirement",
        "guardian_retirement",
        "create_guardian_retirement_record",
    )
    assert_guardian_template(
        "guardian_retirement",
        "guardian_retirement",
        "create_guardian_retirement_record",
    )

    assert_bad_classification_doctor_fails()

    # Patch 5: Negative tests for Builder build fail-fast
    assert_builder_command_fails(["guardian-application"], "--guardian-id is required")
    assert_builder_command_fails(
        ["guardian-application", "--guardian-id", "guardian-test"],
        "--guardian-key-sha is required",
    )
    assert_builder_command_fails(
        ["guardian-application", "--guardian-id", "guardian-test", "--guardian-key-sha", "bad", "--oath", "test oath"],
        "--guardian-key-sha must be a 64-character lowercase hex SHA-256",
    )
    assert_builder_command_fails(["guardian-retirement"], "--guardian-id is required")
    assert_builder_command_fails(
        ["guardian-retirement", "--guardian-id", "guardian-test", "--guardian-key-sha", "bad", "--body", "test reason"],
        "--guardian-key-sha must be a 64-character lowercase hex SHA-256",
    )
    assert_builder_command_fails(["propagation"], "--body is required")
    assert_builder_command_fails(["correction"], "--body is required")

    # Patch 6: Negative tests for Builder doctor content validation
    assert_doctor_fails_for_draft(
        "guardian_retirement",
        {
            "guardian_id": "",
            "guardian_public_key_sha256": "",
            "reason": "",
            "optional_linked_guardian_application_request": {
                "does_participant_request_guardian_application_with_this_record": False,
            },
        },
        "MISSING_GUARDIAN_RETIREMENT_FIELD",
        "create_guardian_retirement_record",
    )
    assert_doctor_fails_for_draft(
        "propagation",
        {"title": "Propagation Record", "body": ""},
        "MISSING_RECORD_CONTENT",
        "create_propagation_record",
    )
    assert_doctor_fails_for_draft(
        "correction",
        {"title": "Correction", "body": ""},
        "MISSING_RECORD_CONTENT",
        "create_correction_record",
    )
    assert_doctor_fails_for_draft(
        "context_insufficient_notice",
        {"reason": ""},
        "MISSING_CONTEXT_INSUFFICIENT_REASON",
        "create_context_insufficient_notice_record",
    )

    canonical = manifest["canonical_builder"]
    require(
        canonical["sha256"] == hashlib.sha256(builder_bytes).hexdigest(),
        "record-chain-builder-bundles.v1.json canonical_builder.sha256 is stale",
    )
    require(
        canonical["size_bytes"] == len(builder_bytes),
        "record-chain-builder-bundles.v1.json canonical_builder.size_bytes is stale",
    )
    require(
        "classification_update" in canonical.get("supports", []),
        "canonical builder manifest must declare classification_update support",
    )

    print("PASS: archive backlog and builder flow contract")


if __name__ == "__main__":
    main()
