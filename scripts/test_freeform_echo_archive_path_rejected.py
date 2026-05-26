#!/usr/bin/env python3
"""Test that freeform echo submissions cannot claim archive status.

Verifies that echo candidates submitted through freeform paths (not through
the Render API) cannot claim to be agent_declared_verification_archive.

Usage:
    python3 scripts/test_freeform_echo_archive_path_rejected.py
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
    result = {}
    for line in block_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def validate_archive_claim(intake):
    """Validate whether an intake block can legitimately claim archive status.

    Returns (valid, reason).
    """
    if not intake:
        return False, "no intake block"

    requested_kind = intake.get("requested_archive_kind", "none")
    submission_type = intake.get("submission_type", "")
    archive_ready = intake.get("archive_ready", "").lower()
    has_gateway_receipt = (
        intake.get("created_by_gateway", "").lower() == "true"
        and intake.get("gateway_receipt_id", "").startswith("gar-")
    )

    # Echo candidates cannot claim agent_declared_verification_archive
    if submission_type == "verification_echo_candidate" and requested_kind == "agent_declared_verification_archive":
        return False, "echo candidate cannot claim agent_declared_verification_archive"

    # archived_echo requires submission_type=verification_echo_candidate
    if requested_kind == "archived_echo" and submission_type != "verification_echo_candidate":
        return False, "archived_echo requires verification_echo_candidate"

    # successor_reception_candidate must not be archive_ready=true
    if requested_kind == "successor_reception_candidate" and archive_ready == "true":
        return False, "successor_reception_candidate must not be archive_ready=true"

    # agent_declared_verification_archive without gateway receipt after effective date
    if requested_kind == "agent_declared_verification_archive" and not has_gateway_receipt:
        return False, "agent_declared archive requires gateway receipt"

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

    print("=== Freeform Echo Archive Path Rejected Tests ===\n")

    # Case 1: Echo candidate trying to claim agent_declared archive
    print("--- Case 1: Echo candidate + agent_declared archive → rejected ---")
    body1 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_echo_candidate\n"
        "echo_type: E2_verification_echo\n"
        "agent_name_or_model: Echo Agent\n"
        "system_or_provider: Test\n"
        "requested_archive_kind: agent_declared_verification_archive\n"
        "archive_ready: true\n"
        "```\n"
    )
    intake1 = parse_intake_block(body1)
    valid1, reason1 = validate_archive_claim(intake1)
    check(
        "Echo candidate cannot claim agent_declared_verification_archive",
        not valid1,
        reason1,
    )

    # Case 2: Freeform echo with archived_echo but wrong submission_type
    print("\n--- Case 2: Report candidate + archived_echo → rejected ---")
    body2 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_report_candidate\n"
        "agent_name_or_model: Report Agent\n"
        "system_or_provider: Test\n"
        "requested_archive_kind: archived_echo\n"
        "archive_ready: true\n"
        "```\n"
    )
    intake2 = parse_intake_block(body2)
    valid2, reason2 = validate_archive_claim(intake2)
    check(
        "Report candidate cannot claim archived_echo",
        not valid2,
        reason2,
    )

    # Case 3: successor_reception_candidate with archive_ready=true
    print("\n--- Case 3: successor_reception_candidate + archive_ready=true → rejected ---")
    body3 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_report_candidate\n"
        "agent_name_or_model: Successor Agent\n"
        "system_or_provider: Test\n"
        "requested_archive_kind: successor_reception_candidate\n"
        "archive_ready: true\n"
        "```\n"
    )
    intake3 = parse_intake_block(body3)
    valid3, reason3 = validate_archive_claim(intake3)
    check(
        "successor_reception_candidate must not be archive_ready=true",
        not valid3,
        reason3,
    )

    # Case 4: Valid agent_declared with gateway receipt → accepted
    print("\n--- Case 4: Valid agent_declared with gateway receipt → accepted ---")
    body4 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_report_candidate\n"
        "agent_name_or_model: Gateway Agent\n"
        "system_or_provider: Render API\n"
        "requested_archive_kind: agent_declared_verification_archive\n"
        "archive_ready: true\n"
        "created_by_gateway: true\n"
        "gateway_receipt_id: gar-20260517-abcd1234\n"
        "render_api_only: true\n"
        "```\n"
    )
    intake4 = parse_intake_block(body4)
    valid4, reason4 = validate_archive_claim(intake4)
    check(
        "Valid agent_declared with receipt is accepted",
        valid4,
        reason4,
    )

    # Case 5: Agent declared without gateway receipt → rejected
    print("\n--- Case 5: Agent declared without gateway receipt → rejected ---")
    body5 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_report_candidate\n"
        "agent_name_or_model: Direct Agent\n"
        "system_or_provider: Direct Issue\n"
        "requested_archive_kind: agent_declared_verification_archive\n"
        "archive_ready: true\n"
        "```\n"
    )
    intake5 = parse_intake_block(body5)
    valid5, reason5 = validate_archive_claim(intake5)
    check(
        "Agent declared without receipt is rejected",
        not valid5,
        reason5,
    )

    # Case 6: Intake-only (no archive claim) → fine
    print("\n--- Case 6: Intake-only (no archive claim) ---")
    body6 = (
        "```trinity-issue-intake\n"
        "submission_type: verification_echo_candidate\n"
        "echo_type: E2_verification_echo\n"
        "agent_name_or_model: Echo Agent\n"
        "system_or_provider: Test\n"
        "record_intent: intake_only\n"
        "requested_archive_kind: none\n"
        "archive_ready: false\n"
        "```\n"
    )
    intake6 = parse_intake_block(body6)
    valid6, reason6 = validate_archive_claim(intake6)
    check(
        "Intake-only echo (no archive claim) is valid",
        valid6,
        reason6,
    )

    # --- Summary ---
    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
