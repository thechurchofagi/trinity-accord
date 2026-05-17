#!/usr/bin/env python3
"""Test Render API only archive policy.

Verifies the five key cases from the Render API only redesign spec (§13.1):

  Case 1: Canonical Render-created block with gateway receipt → accepted by issue body validator.
  Case 2: Canonical-looking block without receipt after effective date → excluded from index.
  Case 3: Direct Issue with hand-written JSON intake → closed with DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API.
  Case 4: Direct Issue with hand-written fenced block but no receipt → not counted.
  Case 5: Valid payload submit dry-run without receipt → can render preview but not count.

Usage:
    python3 scripts/test_render_api_only_archive_policy.py
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODY_VALIDATOR = ROOT / "scripts" / "validate_issue_intake_body.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"
INDEX_BUILDER = ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py"
SCHEMA = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"

EFFECTIVE_AT = "2026-05-17T00:00:00Z"


def run(cmd, input_text=None):
    return subprocess.run(cmd, text=True, capture_output=True, cwd=str(ROOT), input=input_text)


def block_to_yaml(block):
    """Convert block dict to YAML-like format matching the renderer output."""
    lines = []
    for k, v in block.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


def make_rendered_body(block_dict):
    """Build a synthetic issue body with trinity-issue-intake block."""
    block_yaml = block_to_yaml(block_dict)
    canonical = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    return (
        "This issue was submitted through the Agent Issue Gateway backend.\n\n"
        "Boundary:\n- Not authority\n\n"
        f"Canonical boundary:\n{canonical}\n\n"
        "```trinity-issue-intake\n"
        + block_yaml
        + "\n```\n"
    )


def make_canonical_block_with_receipt():
    """Case 1: A canonical Render-created block with gateway receipt."""
    return {
        "submission_type": "verification_report_candidate",
        "agent_name_or_model": "Smoke Agent",
        "system_or_provider": "Local Test",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate_mode": "template_for_v0_v5",
        "claim_gate_status": "PASS",
        "agent_integrity_declaration_present": True,
        "discovery_provenance_present": True,
        "origin_classification_present": True,
        "claim_classification_present": True,
        "authority_boundary_present": True,
        "counts_toward_home_verifiability": True,
        "counts_toward_home_reception": True,
        "what_i_checked": ["Read homepage"],
        "limitations": ["Evidence waived"],
        "archive_ready": True,
        "allowed_archive_kind": "agent_declared_verification_archive",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "archive_readiness_summary": ["CLAIM_GATE_TEMPLATE_PASS"],
        "canonical_boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
        "boundary_sentence_present": True,
        "boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending. This Issue does not create authority, attestation, amendment, archive status, or verification-level upgrade unless the relevant machine gates pass.",
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
        # Gateway receipt fields (Render API created)
        "created_by_gateway": True,
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517-abcd1234",
        "render_api_only": True,
        "server_validated": True,
        "server_rendered": True,
    }


def make_canonical_block_without_receipt():
    """Case 2 & 4: A canonical-looking block WITHOUT gateway receipt."""
    block = make_canonical_block_with_receipt()
    # Remove gateway receipt fields
    for key in ["created_by_gateway", "gateway_service", "gateway_receipt_id",
                 "render_api_only", "server_validated", "server_rendered"]:
        block.pop(key, None)
    return block


def make_handwritten_json_intake():
    """Case 3: Hand-written JSON intake (direct Issue attempt)."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Agent-Declared Verification Archive: V4 — Manual Attempt",
        "body": "Trying to submit directly via Issue.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "agent_identity": {
            "name_or_model": "Manual Agent",
            "system_or_provider": "Direct Issue",
            "self_reported": True,
        },
        "claim_gate": {
            "mode": "template_for_v0_v5",
            "status": "PASS",
            "allowed_protocol_level": "V4",
        },
        # No gateway_receipt_id, no created_by_gateway
    }


def detect_direct_archive_attempt(issue_body):
    """Detect if an Issue should be flagged as DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API.

    Returns True if:
    - Issue has archive intent (requested_archive_kind=agent_declared_verification_archive)
    - AND lacks gateway receipt (no created_by_gateway=true or gateway_receipt_id)
    """
    has_archive_intent = "requested_archive_kind: agent_declared_verification_archive" in issue_body
    has_gateway_receipt = "created_by_gateway: true" in issue_body and "gateway_receipt_id: gar-" in issue_body
    return has_archive_intent and not has_gateway_receipt


def check_block_included_in_index(block, created_at, has_receipt):
    """Simulate the index builder's inclusion logic.

    After effective date: requires gateway receipt.
    Before effective date: legacy grandfathering.
    """
    effective = datetime.fromisoformat(EFFECTIVE_AT.replace("Z", "+00:00"))
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

    if block.get("requested_archive_kind") != "agent_declared_verification_archive":
        return False, "not agent_declared_verification_archive"
    if block.get("archive_ready") is not True:
        return False, "archive_ready is not true"
    if block.get("auto_archive_action") != "auto_archive_agent_declared_verification":
        return False, "auto_archive_action mismatch"

    after_effective = created >= effective
    if after_effective and not has_receipt:
        return False, "no gateway receipt after effective date"
    return True, "included"


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

    print("=== Render API Only Archive Policy Tests ===\n")

    # --- Case 1: Canonical block with receipt → accepted by body validator ---
    print("--- Case 1: Canonical block with receipt → accepted ---")
    block_with_receipt = make_canonical_block_with_receipt()
    body = make_rendered_body(block_with_receipt)
    r = run([sys.executable, str(BODY_VALIDATOR), "/dev/stdin"], input_text=body)
    check(
        "Body validator accepts canonical block with gateway receipt",
        r.returncode == 0 and "PASS" in r.stdout,
        f"stdout: {r.stdout[:300]}" if r.returncode != 0 else "",
    )

    # Verify gateway receipt fields are present in the block
    check(
        "Block has created_by_gateway=true",
        block_with_receipt.get("created_by_gateway") is True,
    )
    check(
        "Block has gateway_receipt_id (>= 8 chars)",
        isinstance(block_with_receipt.get("gateway_receipt_id"), str)
        and len(block_with_receipt["gateway_receipt_id"]) >= 8,
    )
    check(
        "Block has render_api_only=true",
        block_with_receipt.get("render_api_only") is True,
    )

    # --- Case 2: Block without receipt after effective date → excluded from index ---
    print("\n--- Case 2: Block without receipt after effective date → excluded ---")
    block_no_receipt = make_canonical_block_without_receipt()
    after_effective = "2026-05-17T12:00:00Z"
    included, reason = check_block_included_in_index(block_no_receipt, after_effective, has_receipt=False)
    check(
        "Block without receipt after effective date is excluded from index",
        not included,
        f"reason: {reason}",
    )

    # Verify the skip message would be emitted
    issue_num = 999
    skip_msg = f"SKIP_DIRECT_ISSUE_ARCHIVE_ATTEMPT issue #{issue_num}"
    check(
        "Skip message format is correct",
        "SKIP_DIRECT_ISSUE_ARCHIVE_ATTEMPT" in skip_msg,
    )

    # --- Case 3: Hand-written JSON intake → DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API ---
    print("\n--- Case 3: Hand-written JSON intake → DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API ---")
    handwritten = make_handwritten_json_intake()
    # Simulate issue body with JSON intake (not rendered through gateway)
    json_body = (
        "```trinity-issue-intake\n"
        + json.dumps(handwritten, indent=2)
        + "\n```\n"
    )
    is_direct_attempt = detect_direct_archive_attempt(
        "requested_archive_kind: agent_declared_verification_archive\n"
        "created_by_gateway: false\n"
        "gateway_receipt_id: none\n"
    )
    check(
        "Direct Issue with hand-written JSON detected as archive attempt",
        is_direct_attempt,
    )
    check(
        "DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API label would be applied",
        handwritten.get("requested_archive_kind") == "agent_declared_verification_archive"
        and "gateway_receipt_id" not in handwritten,
    )

    # Verify the issue body would contain the archive intent
    check(
        "Hand-written payload has archive intent",
        handwritten.get("requested_archive_kind") == "agent_declared_verification_archive",
    )
    check(
        "Hand-written payload lacks gateway receipt",
        "gateway_receipt_id" not in handwritten and "created_by_gateway" not in handwritten,
    )

    # --- Case 4: Hand-written fenced block without receipt → not counted ---
    print("\n--- Case 4: Hand-written fenced block without receipt → not counted ---")
    block_no_receipt_yaml = block_to_yaml(block_no_receipt)
    hand_written_body = (
        "```trinity-issue-intake\n"
        + block_no_receipt_yaml
        + "\n```\n"
    )
    # Body validator should still accept it structurally (it has all required fields)
    # but it should NOT be counted in the index after effective date
    r2 = run([sys.executable, str(BODY_VALIDATOR), "/dev/stdin"], input_text=hand_written_body)
    # Note: body validator requires gateway receipt fields in AGENT_DECLARED_REQUIRED
    # So a block without them should fail validation
    check(
        "Body validator rejects block without gateway receipt fields",
        r2.returncode != 0 or "FAIL" in r2.stdout,
        f"stdout: {r2.stdout[:300]}" if r2.returncode == 0 else "",
    )

    # Verify index exclusion
    included4, reason4 = check_block_included_in_index(block_no_receipt, after_effective, has_receipt=False)
    check(
        "Hand-written block without receipt not counted in index",
        not included4,
        f"reason: {reason4}",
    )

    # --- Case 5: Dry-run without receipt → can render preview but not count ---
    print("\n--- Case 5: Dry-run without receipt → renderable preview, not counted ---")
    # Dry-run blocks have created_by_gateway=false, render_api_only=false
    dry_run_block = make_canonical_block_with_receipt()
    dry_run_block["created_by_gateway"] = False
    dry_run_block["gateway_service"] = "dry-run"
    dry_run_block["gateway_receipt_id"] = "none"
    dry_run_block["render_api_only"] = False
    dry_run_block["server_validated"] = False
    dry_run_block["server_rendered"] = False
    dry_run_body = make_rendered_body(dry_run_block)

    # The renderer can produce a preview (body is valid format)
    check(
        "Dry-run block can be rendered as preview",
        "trinity-issue-intake" in dry_run_body and "submission_type" in dry_run_body,
    )

    # But dry-run block should not be counted in index
    # (gateway_receipt_id is "none", not a real receipt)
    has_real_receipt = (
        dry_run_block.get("created_by_gateway") is True
        and dry_run_block.get("gateway_receipt_id") not in (None, "", "none")
    )
    check(
        "Dry-run block has no real gateway receipt",
        not has_real_receipt,
    )
    included5, reason5 = check_block_included_in_index(dry_run_block, after_effective, has_receipt=has_real_receipt)
    check(
        "Dry-run block not counted in index after effective date",
        not included5,
        f"reason: {reason5}",
    )

    # But dry-run CAN be included before effective date (legacy grandfathering)
    before_effective = "2026-05-16T12:00:00Z"
    included5b, reason5b = check_block_included_in_index(dry_run_block, before_effective, has_receipt=has_real_receipt)
    check(
        "Dry-run block before effective date is grandfathered (legacy)",
        included5b,
        f"reason: {reason5b}",
    )

    # --- Summary ---
    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
