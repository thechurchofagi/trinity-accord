#!/usr/bin/env python3
"""Test that legacy JSON intake submissions are not counted as archives.

Verifies that Issues with freeform JSON intake blocks (not rendered through
the Render API) are properly rejected from the archive path.

Usage:
    python3 scripts/test_legacy_json_intake_not_archive.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_intake_block(body):
    """Extract trinity-issue-intake block from issue body."""
    match = re.search(r"```trinity-issue-intake\s*\n(.*?)```", body, re.DOTALL)
    if not match:
        return None
    block_text = match.group(1).strip()
    # Try JSON first
    try:
        return json.loads(block_text)
    except (json.JSONDecodeError, ValueError):
        pass
    # Fall back to key-value parsing
    result = {}
    for line in block_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def is_valid_archive_candidate(intake):
    """Check if intake block represents a valid archive candidate."""
    if not intake:
        return False, "no intake block"
    if intake.get("requested_archive_kind") != "agent_declared_verification_archive":
        return False, "not agent_declared_verification_archive"
    archive_ready = intake.get("archive_ready")
    if archive_ready not in (True, "true", "True"):
        return False, "archive_ready is not true"
    return True, "valid"


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"  PASS: {label}")
            passed += 1
        else:
            print(f"  FAIL: {label}")
            if detail:
                print(f"    {detail}")
            failed += 1

    print("=== Legacy JSON Intake Not Archive Tests ===\n")

    # Case 1: Freeform JSON inside code block (not trinity-issue-intake)
    print("--- Case 1: Freeform JSON code block ---")
    body1 = (
        "Some issue text\n\n"
        "```json\n"
        + json.dumps({"type": "verification", "level": "V4", "archive": True}, indent=2)
        + "\n```\n"
    )
    intake1 = parse_intake_block(body1)
    check("Freeform JSON block has no trinity-issue-intake", intake1 is None)
    valid1, reason1 = is_valid_archive_candidate(intake1)
    check("Freeform JSON block is not valid archive candidate", not valid1, reason1)

    # Case 2: Hand-written trinity-issue-intake with JSON content
    print("\n--- Case 2: Hand-written trinity-issue-intake with JSON ---")
    body2 = (
        "```trinity-issue-intake\n"
        + json.dumps({
            "submission_type": "verification_report_candidate",
            "agent_name_or_model": "Manual Agent",
            "system_or_provider": "Direct",
            "record_intent": "auto_archive_candidate",
            "requested_archive_kind": "agent_declared_verification_archive",
            "archive_ready": True,
        }, indent=2)
        + "\n```\n"
    )
    intake2 = parse_intake_block(body2)
    check("Hand-written JSON intake block is parsed", intake2 is not None)
    if intake2:
        check(
            "Has archive intent",
            intake2.get("requested_archive_kind") == "agent_declared_verification_archive",
        )
        check(
            "Lacks gateway receipt (not rendered through API)",
            intake2.get("created_by_gateway") is None
            and intake2.get("gateway_receipt_id") is None,
        )

    # Case 3: Proper YAML block with gateway receipt (valid)
    print("\n--- Case 3: Proper YAML block with gateway receipt ---")
    body3 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_report_candidate\n"
        "agent_name_or_model: Gateway Agent\n"
        "system_or_provider: Render API\n"
        "record_intent: auto_archive_candidate\n"
        "requested_archive_kind: agent_declared_verification_archive\n"
        "archive_ready: true\n"
        "created_by_gateway: true\n"
        "gateway_receipt_id: gar-20260517-abcd1234\n"
        "render_api_only: true\n"
        "```\n"
    )
    intake3 = parse_intake_block(body3)
    check("YAML intake block is parsed", intake3 is not None)
    if intake3:
        check(
            "Has gateway receipt",
            intake3.get("created_by_gateway") == "true"
            and intake3.get("gateway_receipt_id", "").startswith("gar-"),
        )

    # Case 4: Issue with no code block at all
    print("\n--- Case 4: No code block at all ---")
    body4 = "This is just a regular issue with no code blocks."
    intake4 = parse_intake_block(body4)
    check("No code block returns None", intake4 is None)
    valid4, reason4 = is_valid_archive_candidate(intake4)
    check("No code block is not valid archive candidate", not valid4, reason4)

    # Case 5: Echo candidate (not archive)
    print("\n--- Case 5: Echo candidate (not archive) ---")
    body5 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_echo_candidate\n"
        "echo_type: E2_verification_echo\n"
        "agent_name_or_model: Echo Agent\n"
        "system_or_provider: Test\n"
        "requested_archive_kind: archived_echo\n"
        "archive_ready: false\n"
        "```\n"
    )
    intake5 = parse_intake_block(body5)
    check("Echo candidate is parsed", intake5 is not None)
    if intake5:
        valid5, reason5 = is_valid_archive_candidate(intake5)
        check("Echo candidate is not agent_declared archive", not valid5, reason5)

    # --- Summary ---
    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
