#!/usr/bin/env python3
"""Test that Builder rejects inconsistent provenance combinations."""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def run_builder(args):
    return subprocess.run(
        ["node", str(BUILDER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def main():
    with tempfile.TemporaryDirectory() as td:
        body = Path(td) / "echo.md"
        body.write_text("Provenance guard smoke test.", encoding="utf-8")

        common = [
            "echo",
            "--actor-label", "Provenance Guard Test Agent",
            "--provider", "Test Runtime",
            "--title", "Provenance Guard Smoke Test",
            "--body-file", str(body),
            "--context-level", "CC-3",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/agent-start/",
            "--readback", "dummy",
            "--key-dir", str(Path(td) / "keys"),
            "--out", str(Path(td) / "submission.json"),
        ]

        # Test 1: submission-executor self + human_operator_involved true must fail
        bad_execution = run_builder([
            *common,
            "--discovery-mode", "user_task_context",
            "--requesting-party-type", "human",
            "--record-decision", "human",
            "--submission-executor", "self",
            "--human-operator-involved", "true",
        ])
        combined = bad_execution.stdout + bad_execution.stderr
        require(bad_execution.returncode != 0, "builder must reject self + human_operator_involved true")
        require("human" in combined.lower() and "operator" in combined.lower(), combined)

        # Test 2: self_discovered + human introducer must fail
        bad_discovery = run_builder([
            *common,
            "--discovery-mode", "self_discovered",
            "--introducing-party-type", "human",
            "--requesting-party-type", "none",
            "--record-decision", "self",
            "--submission-executor", "self",
            "--human-operator-involved", "false",
        ])
        combined = bad_discovery.stdout + bad_discovery.stderr
        require(bad_discovery.returncode != 0, "builder must reject self_discovered + human introducer")
        require("self_discovered" in combined or "introducing" in combined.lower(), combined)

        # Test 3: record_decision self + human requester must fail
        bad_decision = run_builder([
            *common,
            "--discovery-mode", "user_task_context",
            "--introducing-party-type", "human",
            "--requesting-party-type", "human",
            "--record-decision", "self",
            "--submission-executor", "self",
            "--human-operator-involved", "false",
        ])
        combined = bad_decision.stdout + bad_decision.stderr
        require(bad_decision.returncode != 0, "builder must reject record_decision self + human requester")
        require("record-decision" in combined or "requesting" in combined.lower(), combined)

    print("PASS: builder provenance consistency guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
