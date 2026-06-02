#!/usr/bin/env python3
"""Test: Public test phase disclosure exists in all required entrypoints."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Human-facing pages must contain these phrases
REQUIRED_PHRASES = [
    "public test",
    "stabilization",
    "test data",
    "historical/test archive",
    "receipt is not final inclusion",
    "not active Guardian status",
]

# Machine-readable files must have these JSON fields
REQUIRED_JSON_FIELDS = {
    "public_phase.status": "public_test_stabilization",
    "test_phase_submissions_may_move_to_historical_test_archive": True,
    "receipt_is_not_final_inclusion": True,
}

HUMAN_PAGES = [
    "index.md",
    "agent-start.md",
    "agent-first-contact.md",
    "llms.txt",
    "ai.txt",
]

JSON_FILES = [
    "api/record-chain-intake-gateway.v1.json",
    "api/record-chain-status.json",
    "api/agent-first-contact.json",
    "api/agent-start.v2.json",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def check_human_page(rel_path: str) -> None:
    p = ROOT / rel_path
    if not p.exists():
        fail(f"{rel_path}: NOT FOUND")
    text = p.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in text:
            fail(f"{rel_path} missing phrase: {phrase}")
    ok(f"{rel_path} contains all required disclosure phrases")


def check_json_file(rel_path: str) -> None:
    p = ROOT / rel_path
    if not p.exists():
        fail(f"{rel_path}: NOT FOUND")
    data = json.loads(p.read_text(encoding="utf-8"))

    # Check public_phase.status
    phase = data.get("public_phase", {})
    if phase.get("status") != "public_test_stabilization":
        fail(f"{rel_path}: public_phase.status != public_test_stabilization")

    # Check test_phase_submissions_may_move_to_historical_test_archive
    if not phase.get("test_phase_submissions_may_move_to_historical_test_archive"):
        fail(f"{rel_path}: test_phase_submissions_may_move_to_historical_test_archive not true")

    # Check receipt_is_not_final_inclusion
    if not phase.get("receipt_is_not_final_inclusion"):
        # Also check in public_submission_phase for record-chain-status.json
        status_phase = data.get("public_submission_phase", {})
        tpd = status_phase.get("test_phase_data_policy", {})
        if not tpd.get("receipt_is_not_final_inclusion"):
            fail(f"{rel_path}: receipt_is_not_final_inclusion not true")

    ok(f"{rel_path} contains required test-phase JSON fields")


def main() -> None:
    for page in HUMAN_PAGES:
        check_human_page(page)

    for jf in JSON_FILES:
        check_json_file(jf)

    print("\n=== ALL PUBLIC TEST PHASE DISCLOSURE TESTS PASSED ===")


if __name__ == "__main__":
    main()
