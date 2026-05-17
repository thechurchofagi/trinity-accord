#!/usr/bin/env python3
"""Test agent-declared index requires gateway receipt.

Verifies the four key cases for index inclusion/exclusion based on
gateway receipt requirements (§13.3):

  Case 1: archive_ready=true + gateway receipt → included in index
  Case 2: archive_ready=true + no receipt + after effective date → excluded
  Case 3: Legacy pre-effective canonical record → included with legacy flag
  Case 4: Freeform JSON intake → excluded

Usage:
    python3 scripts/test_agent_declared_index_requires_gateway_receipt.py
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_BUILDER = ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py"
INDEX_PATH = ROOT / "api" / "agent-declared-verification-index.json"

# Use shared policy constant — single source of truth
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_v0_v5_policy import RENDER_API_ONLY_EFFECTIVE_AT as EFFECTIVE_AT

# Import real build_index — test against production logic, not a simulation
from build_agent_declared_verification_index_from_issues import build_index


def run(cmd, input_text=None):
    return subprocess.run(cmd, text=True, capture_output=True, cwd=str(ROOT), input=input_text)


def make_issue_with_receipt(issue_number, created_at):
    """Case 1: archive_ready=true + gateway receipt."""
    return {
        "number": issue_number,
        "title": f"Agent-Declared Verification Archive: V4 — Test #{issue_number}",
        "body": (
            "Submitted through the Agent Issue Gateway.\n\n"
            "```trinity-issue-intake\n"
            "submission_type: verification_report_candidate\n"
            f"agent_name_or_model: Test Agent {issue_number}\n"
            "system_or_provider: Test System\n"
            "record_intent: auto_archive_candidate\n"
            "requested_archive_kind: agent_declared_verification_archive\n"
            "agent_declared_protocol_level: V4\n"
            "evidence_requirement_mode: waived_for_v0_v5\n"
            "claim_gate_mode: template_for_v0_v5\n"
            "claim_gate_status: PASS\n"
            "agent_integrity_declaration_present: true\n"
            "discovery_provenance_present: true\n"
            "origin_classification_present: true\n"
            "claim_classification_present: true\n"
            "authority_boundary_present: true\n"
            "counts_toward_home_verifiability: true\n"
            "counts_toward_home_reception: true\n"
            "what_i_checked:\n"
            "  - Read homepage\n"
            "limitations:\n"
            "  - Evidence waived\n"
            "archive_ready: true\n"
            "allowed_archive_kind: agent_declared_verification_archive\n"
            "auto_archive_action: auto_archive_agent_declared_verification\n"
            "created_by_gateway: true\n"
            "gateway_service: trinity-agent-issue-gateway\n"
            f"gateway_receipt_id: gar-20260517-{issue_number:04d}abcd\n"
            "render_api_only: true\n"
            "server_validated: true\n"
            "server_rendered: true\n"
            "```\n"
        ),
        "state": "closed",
        "createdAt": created_at,
        "closedAt": created_at,
        "labels": [],
        "url": f"https://github.com/test/repo/issues/{issue_number}",
    }


def make_issue_without_receipt(issue_number, created_at):
    """Case 2: archive_ready=true + NO gateway receipt."""
    return {
        "number": issue_number,
        "title": f"Agent-Declared Verification Archive: V4 — Direct #{issue_number}",
        "body": (
            "Direct Issue submission.\n\n"
            "```trinity-issue-intake\n"
            "submission_type: verification_report_candidate\n"
            f"agent_name_or_model: Direct Agent {issue_number}\n"
            "system_or_provider: Direct System\n"
            "record_intent: auto_archive_candidate\n"
            "requested_archive_kind: agent_declared_verification_archive\n"
            "agent_declared_protocol_level: V4\n"
            "evidence_requirement_mode: waived_for_v0_v5\n"
            "claim_gate_mode: template_for_v0_v5\n"
            "claim_gate_status: PASS\n"
            "agent_integrity_declaration_present: true\n"
            "discovery_provenance_present: true\n"
            "origin_classification_present: true\n"
            "claim_classification_present: true\n"
            "authority_boundary_present: true\n"
            "counts_toward_home_verifiability: true\n"
            "counts_toward_home_reception: true\n"
            "what_i_checked:\n"
            "  - Read homepage\n"
            "limitations:\n"
            "  - Evidence waived\n"
            "archive_ready: true\n"
            "allowed_archive_kind: agent_declared_verification_archive\n"
            "auto_archive_action: auto_archive_agent_declared_verification\n"
            "```\n"
        ),
        "state": "closed",
        "createdAt": created_at,
        "closedAt": created_at,
        "labels": [],
        "url": f"https://github.com/test/repo/issues/{issue_number}",
    }


def make_legacy_pre_effective_issue(issue_number, created_at):
    """Case 3: Legacy pre-effective canonical record (no gateway receipt, before effective date)."""
    return {
        "number": issue_number,
        "title": f"Agent-Declared Verification Archive: V4 — Legacy #{issue_number}",
        "body": (
            "Legacy submission before Render API only policy.\n\n"
            "```trinity-issue-intake\n"
            "submission_type: verification_report_candidate\n"
            f"agent_name_or_model: Legacy Agent {issue_number}\n"
            "system_or_provider: Legacy System\n"
            "record_intent: auto_archive_candidate\n"
            "requested_archive_kind: agent_declared_verification_archive\n"
            "agent_declared_protocol_level: V4\n"
            "evidence_requirement_mode: waived_for_v0_v5\n"
            "claim_gate_mode: template_for_v0_v5\n"
            "claim_gate_status: PASS\n"
            "agent_integrity_declaration_present: true\n"
            "discovery_provenance_present: true\n"
            "origin_classification_present: true\n"
            "claim_classification_present: true\n"
            "authority_boundary_present: true\n"
            "counts_toward_home_verifiability: true\n"
            "counts_toward_home_reception: true\n"
            "what_i_checked:\n"
            "  - Read homepage\n"
            "limitations:\n"
            "  - Evidence waived\n"
            "archive_ready: true\n"
            "allowed_archive_kind: agent_declared_verification_archive\n"
            "auto_archive_action: auto_archive_agent_declared_verification\n"
            "```\n"
        ),
        "state": "closed",
        "createdAt": created_at,
        "closedAt": created_at,
        "labels": [],
        "url": f"https://github.com/test/repo/issues/{issue_number}",
    }


def make_freeform_json_issue(issue_number, created_at):
    """Case 4: Freeform JSON intake (not a valid trinity-issue-intake block)."""
    return {
        "number": issue_number,
        "title": "Some random Issue",
        "body": (
            "This is a freeform issue with some JSON:\n\n"
            "```json\n"
            + json.dumps({
                "type": "verification",
                "level": "V4",
                "archive": True,
            }, indent=2)
            + "\n```\n"
        ),
        "state": "closed",
        "createdAt": created_at,
        "closedAt": created_at,
        "labels": [],
        "url": f"https://github.com/test/repo/issues/{issue_number}",
    }


def make_issue_with_fake_receipt(issue_number, created_at):
    """Case 5: Fake receipt attack — has created_by_gateway + gateway_receipt_id
    but missing render_api_only, server_validated, server_rendered, gateway_service."""
    return {
        "number": issue_number,
        "title": f"Agent-Declared Verification Archive: V4 — Fake Receipt #{issue_number}",
        "body": (
            "Attempted bypass with fake receipt.\n\n"
            "```trinity-issue-intake\n"
            "submission_type: verification_report_candidate\n"
            f"agent_name_or_model: Fake Agent {issue_number}\n"
            "system_or_provider: Fake System\n"
            "record_intent: auto_archive_candidate\n"
            "requested_archive_kind: agent_declared_verification_archive\n"
            "agent_declared_protocol_level: V4\n"
            "evidence_requirement_mode: waived_for_v0_v5\n"
            "claim_gate_mode: template_for_v0_v5\n"
            "claim_gate_status: PASS\n"
            "agent_integrity_declaration_present: true\n"
            "discovery_provenance_present: true\n"
            "origin_classification_present: true\n"
            "claim_classification_present: true\n"
            "authority_boundary_present: true\n"
            "counts_toward_home_verifiability: true\n"
            "counts_toward_home_reception: true\n"
            "what_i_checked:\n"
            "  - Read homepage\n"
            "limitations:\n"
            "  - Evidence waived\n"
            "archive_ready: true\n"
            "allowed_archive_kind: agent_declared_verification_archive\n"
            "auto_archive_action: auto_archive_agent_declared_verification\n"
            "created_by_gateway: true\n"
            f"gateway_receipt_id: fake-receipt-{issue_number}\n"
            "```\n"
        ),
        "state": "closed",
        "createdAt": created_at,
        "closedAt": created_at,
        "labels": [],
        "url": f"https://github.com/test/repo/issues/{issue_number}",
    }


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

    print("=== Agent-Declared Index Requires Gateway Receipt Tests ===\n")

    # Create test issues
    after_effective = "2026-05-17T12:00:00Z"
    before_effective = "2026-05-16T12:00:00Z"

    issue_with_receipt = make_issue_with_receipt(200, after_effective)
    issue_no_receipt = make_issue_without_receipt(201, after_effective)
    issue_legacy = make_legacy_pre_effective_issue(164, before_effective)
    issue_freeform = make_freeform_json_issue(202, after_effective)
    issue_fake_receipt = make_issue_with_fake_receipt(203, after_effective)

    all_issues = [issue_with_receipt, issue_no_receipt, issue_legacy, issue_freeform, issue_fake_receipt]

    # Use real build_index — production logic, not simulation
    index_result = build_index(all_issues, repo="test/repo")
    records = index_result.get("records", [])
    skipped = index_result.get("skipped_direct_issue_archive_attempts", [])

    # --- Case 1: archive_ready=true + receipt → included ---
    print("--- Case 1: archive_ready=true + receipt → included ---")
    record_200 = next((r for r in records if r["issue_number"] == 200), None)
    check(
        "Issue #200 (with receipt) is included in index",
        record_200 is not None,
    )
    if record_200:
        check(
            "Record has created_by_gateway=true",
            record_200.get("created_by_gateway") is True,
        )
        check(
            "Record has gateway_receipt_id",
            record_200.get("gateway_receipt_id", "").startswith("gar-"),
        )
        check(
            "Record has render_api_only=true",
            record_200.get("render_api_only") is True,
        )

    # --- Case 2: archive_ready=true + no receipt + after effective → excluded ---
    print("\n--- Case 2: archive_ready=true + no receipt + after effective → excluded ---")
    record_201 = next((r for r in records if r["issue_number"] == 201), None)
    check(
        "Issue #201 (no receipt, after effective) is excluded from index",
        record_201 is None,
    )
    check(
        "Issue #201 is in skipped list",
        201 in skipped,
    )

    # --- Case 3: Legacy pre-effective canonical record → included with legacy flag ---
    print("\n--- Case 3: Legacy pre-effective → included with legacy flag ---")
    record_164 = next((r for r in records if r["issue_number"] == 164), None)
    check(
        "Issue #164 (legacy, pre-effective) is included in index",
        record_164 is not None,
    )
    if record_164:
        check(
            "Record has legacy_pre_render_api_only=true",
            record_164.get("legacy_pre_render_api_only") is True,
        )
        check(
            "Record does NOT have render_api_only=true",
            record_164.get("render_api_only") is not True,
        )
        check(
            "Record does NOT have created_by_gateway=true",
            record_164.get("created_by_gateway") is not True,
        )

    # --- Case 4: Freeform JSON intake → excluded ---
    print("\n--- Case 4: Freeform JSON intake → excluded ---")
    record_202 = next((r for r in records if r["issue_number"] == 202), None)
    check(
        "Issue #202 (freeform JSON) is excluded from index",
        record_202 is None,
    )
    check(
        "Issue #202 is NOT in skipped list (no trinity-issue-intake block at all)",
        202 not in skipped,
    )

    # --- Case 5: Fake receipt attack → excluded ---
    print("\n--- Case 5: Fake receipt attack → excluded ---")
    record_203 = next((r for r in records if r["issue_number"] == 203), None)
    check(
        "Issue #203 (fake receipt) is excluded from index",
        record_203 is None,
    )
    check(
        "Issue #203 is in skipped list (has archive intent but no valid receipt)",
        203 in skipped,
    )

    # --- Verify actual index file structure ---
    print("\n--- Verify actual index file structure ---")
    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        check(
            "Index file has render_api_only_effective_at",
            "render_api_only_effective_at" in index,
        )
        check(
            "Index file effective_at matches spec",
            index.get("render_api_only_effective_at") == EFFECTIVE_AT,
        )
        check(
            "Index file has records list",
            isinstance(index.get("records"), list),
        )
        # Check that existing records have correct structure
        for rec in index.get("records", []):
            check(
                f"Record #{rec.get('issue_number')} has issue_number",
                "issue_number" in rec,
            )
    except FileNotFoundError:
        check("Index file exists", False, "File not found")
    except json.JSONDecodeError as e:
        check("Index file is valid JSON", False, str(e))

    # --- Summary ---
    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
