#!/usr/bin/env python3
"""Regression tests for canonical Builder oath readback handling."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

RECEIPT_BOUNDARY_FIELDS = {
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def run_builder(args: list[str], *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(BUILDER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def print_echo_oath() -> str:
    result = run_builder(["print-oath", "--record-type", "echo"], timeout=10)
    if result.returncode != 0:
        fail(f"print-oath failed: {result.stderr[:300]}")
    if "=== Common Submission Integrity (common_submission_integrity_v1) ===" not in result.stdout:
        fail("print-oath output is missing the common module header")
    if "=== Echo Integrity (echo_integrity_v1) ===" not in result.stdout:
        fail("print-oath output is missing the echo module header")
    return result.stdout


def build_echo(readback: str, tmp_dir: Path) -> subprocess.CompletedProcess[str]:
    return run_builder(
        [
            "echo",
            "--actor-label",
            "CanonicalReadbackTest",
            "--provider",
            "CI",
            "--body",
            "Canonical oath readback test echo",
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
            "--submission-executor", "self",
            "--human-operator-involved", "false",
            "--readback",
            readback,
            "--generate-authorship-key",
            "--key-dir",
            str(tmp_dir / "keys"),
            "--out",
            str(tmp_dir / "echo.json"),
        ],
        timeout=20,
    )


def without_module_headers(oath: str) -> str:
    return "\n".join(line for line in oath.splitlines() if not line.startswith("==="))


def require_receipt_boundary_fields(submission: dict[str, Any]) -> None:
    boundary = submission.get("submission_boundary")
    if not isinstance(boundary, dict):
        fail("Builder-generated submission_boundary is missing or not an object")
    missing = sorted(RECEIPT_BOUNDARY_FIELDS - set(boundary))
    if missing:
        fail(f"Builder-generated submission_boundary missing receipt fields: {missing}")
    for field in sorted(RECEIPT_BOUNDARY_FIELDS):
        if boundary.get(field) is not True:
            fail(f"Builder-generated submission_boundary.{field} is not true")


def test_complete_print_oath_stdout_is_accepted() -> None:
    oath = print_echo_oath()
    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        result = build_echo(oath, tmp_dir)
        if result.returncode != 0:
            fail(f"Builder rejected unchanged print-oath stdout: {result.stderr[:500]}")
        submission = json.loads((tmp_dir / "echo.json").read_text(encoding="utf-8"))
        require_receipt_boundary_fields(submission)
    ok("unchanged print-oath stdout with module headers is accepted")


def test_removed_module_headers_fail_closed() -> None:
    oath = print_echo_oath()
    stripped_oath = without_module_headers(oath)
    if stripped_oath == oath:
        fail("test setup did not remove module headers")
    with tempfile.TemporaryDirectory() as td:
        result = build_echo(stripped_oath, Path(td))
        if result.returncode == 0:
            fail("Builder accepted readback after module headers were removed")
        combined = f"{result.stdout}\n{result.stderr}"
        if "does not match canonical oath text" not in combined:
            fail(f"Builder failed for the wrong reason: {combined[:500]}")
    ok("removing module headers fails closed")


def main() -> int:
    test_complete_print_oath_stdout_is_accepted()
    test_removed_module_headers_fail_closed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
