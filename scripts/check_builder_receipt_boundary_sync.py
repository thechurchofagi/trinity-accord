#!/usr/bin/env python3
"""Verify Builder receipt-boundary fields stay synchronized across CI surfaces.

This check intentionally fails with a clear message instead of editing files in CI.
It protects the Builder, generated submissions, submission schema, Phase 5C
regression allowlist, and builder bundle manifest from drifting out of sync after
receipt-boundary changes.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

RECEIPT_BOUNDARY_FIELDS = [
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
]

BASE_BOUNDARY_FIELDS = [
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
]

REQUIRED_SUBMISSION_BOUNDARY_FIELDS = BASE_BOUNDARY_FIELDS + RECEIPT_BOUNDARY_FIELDS
REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET = set(REQUIRED_SUBMISSION_BOUNDARY_FIELDS)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(command: list[str], *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        fail(f"required command not found while running {command[0]!r}: {exc}")
    except subprocess.TimeoutExpired as exc:
        fail(f"command timed out after {timeout}s: {' '.join(command)}; stderr={exc.stderr!r}")


def assert_exact_true_object(obj: Any, *, label: str) -> None:
    if not isinstance(obj, dict):
        fail(f"{label} is missing or not an object")

    keys = set(obj)
    missing = sorted(REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET - keys)
    extra = sorted(keys - REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET)
    if missing:
        fail(f"{label} missing fields: {missing}")
    if extra:
        fail(f"{label} has extra fields: {extra}")

    for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
        if obj.get(field) is not True:
            fail(f"{label}.{field} must be true, got {obj.get(field)!r}")


def check_submission_schema() -> None:
    schema = load_json("api/record-chain-submission-schema.v1.json")
    boundary = schema.get("properties", {}).get("submission_boundary")
    if not isinstance(boundary, dict):
        fail("schema properties.submission_boundary is missing or not an object")

    required = boundary.get("required")
    if required != REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
        fail(f"submission_boundary.required drifted: {required!r}")

    properties = boundary.get("properties", {})
    for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
        if properties.get(field) != {"const": True}:
            fail(f"submission_boundary.properties.{field} must be {{'const': True}}")

    extra = sorted(set(properties) - REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET)
    if extra:
        fail(f"submission_boundary has schema-invalid extra properties: {extra}")

    if boundary.get("additionalProperties") is not False:
        fail("submission_boundary.additionalProperties must be false")


def check_builder_generated_submission() -> None:
    if not BUILDER.exists():
        fail(f"missing {BUILDER.relative_to(ROOT)}")

    oath_result = run_command(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        timeout=10,
    )
    if oath_result.returncode != 0:
        fail(f"builder print-oath failed: {oath_result.stderr[:500]}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out_file = tmp_path / "echo.json"
        key_dir = tmp_path / "keys"
        build_result = run_command(
            [
                "node",
                str(BUILDER),
                "echo",
                "--actor-label",
                "ReceiptBoundaryGuard",
                "--provider",
                "CI",
                "--body",
                "Receipt boundary guard echo",
                "--context-level",
                "CC-3",
                "--context-sufficient-for-selected-action",
                "true",
                "--loaded-urls",
                "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
                "--discovery-mode",
                "user_task_context",
                "--record-decision",
                "human",
                "--submission-executor",
                "self",
                "--human-operator-involved",
                "true",
                "--readback",
                oath_result.stdout,
                "--generate-authorship-key",
                "--key-dir",
                str(key_dir),
                "--out",
                str(out_file),
            ],
            timeout=20,
        )
        if build_result.returncode != 0:
            fail(f"builder echo failed: {build_result.stderr[:1000]}")
        if not out_file.exists():
            fail("builder echo did not write the expected output file")

        submission = json.loads(out_file.read_text(encoding="utf-8"))
        assert_exact_true_object(
            submission.get("submission_boundary"),
            label="generated submission_boundary",
        )
        assert_exact_true_object(
            submission.get("record_draft", {}).get("non_authority_boundary_acknowledgement"),
            label="generated record_draft.non_authority_boundary_acknowledgement",
        )

        doctor_result = run_command(
            ["node", str(BUILDER), "doctor", "--file", str(out_file)],
            timeout=20,
        )
        if doctor_result.returncode != 0:
            fail(f"builder doctor failed for generated submission: {doctor_result.stderr[:1000]}")


def literal_assignment_value(path: Path, assignment_name: str) -> Any:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        fail(f"could not parse {path.relative_to(ROOT)}: {exc}")

    matches: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == assignment_name:
                    matches.append(node.value)
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id == assignment_name and node.value is not None:
                matches.append(node.value)

    if len(matches) != 1:
        fail(f"expected exactly one {assignment_name} assignment in {path.relative_to(ROOT)}, found {len(matches)}")

    try:
        return ast.literal_eval(matches[0])
    except (ValueError, SyntaxError) as exc:
        fail(f"{assignment_name} in {path.relative_to(ROOT)} must be a literal collection: {exc}")


def check_phase5_allowlist() -> None:
    path = ROOT / "scripts" / "test_phase_5c_hotfix.py"
    if not path.exists():
        fail("missing scripts/test_phase_5c_hotfix.py")

    value = literal_assignment_value(path, "REQUIRED_SUBMISSION_BOUNDARY_FIELDS")
    if not isinstance(value, (set, list, tuple)) or not all(isinstance(item, str) for item in value):
        fail("scripts/test_phase_5c_hotfix.py REQUIRED_SUBMISSION_BOUNDARY_FIELDS must be a literal string collection")

    actual = set(value)
    missing = sorted(REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET - actual)
    extra = sorted(actual - REQUIRED_SUBMISSION_BOUNDARY_FIELD_SET)
    if missing or extra:
        fail(
            "scripts/test_phase_5c_hotfix.py REQUIRED_SUBMISSION_BOUNDARY_FIELDS drifted; "
            f"missing={missing}, extra={extra}"
        )


def check_builder_manifest_hash() -> None:
    builder_path = ROOT / "downloads/record-chain-builder.mjs"
    manifest = load_json("api/record-chain-builder-bundles.v1.json")
    canonical_builder = manifest.get("canonical_builder", {})
    builder_bytes = builder_path.read_bytes()
    expected_sha = hashlib.sha256(builder_bytes).hexdigest()
    expected_size = len(builder_bytes)
    if canonical_builder.get("sha256") != expected_sha:
        fail("api/record-chain-builder-bundles.v1.json canonical_builder.sha256 is stale")
    if canonical_builder.get("size_bytes") != expected_size:
        fail("api/record-chain-builder-bundles.v1.json canonical_builder.size_bytes is stale")


def main() -> int:
    check_submission_schema()
    check_builder_generated_submission()
    check_phase5_allowlist()
    check_builder_manifest_hash()
    print("PASS: Builder receipt-boundary fields are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
