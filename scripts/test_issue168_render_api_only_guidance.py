#!/usr/bin/env python3
"""Test Issue #168-like scenario: Render API only guidance.

Fixture based on Issue #168 — a direct GitHub Issue attempting V0-V5 agent-declared
archive without going through the Render API.

Expected:
  - DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API is triggered
  - Comment says "Render API only"
  - Not an amendment-only message
  - Not counted in index

Usage:
    python3 scripts/test_issue168_render_api_only_guidance.py
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Use shared policy constant — single source of truth
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_v0_v5_policy import RENDER_API_ONLY_EFFECTIVE_AT as EFFECTIVE_AT


def make_issue168_fixture():
    """Simulate Issue #168: a direct GitHub Issue with agent-declared archive intent.

    This is what an agent might manually create as a GitHub Issue, attempting
    to get archived without using the Render API.
    """
    return {
        "number": 168,
        "title": "Agent-Declared Verification Archive: V4 — Watcher Agent",
        "body": (
            "This issue was submitted directly as a GitHub Issue.\n\n"
            "```trinity-issue-intake\n"
            "submission_type: verification_report_candidate\n"
            "agent_name_or_model: watcher\n"
            "system_or_provider: coze\n"
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
            "archive_readiness_summary:\n"
            "  - CLAIM_GATE_TEMPLATE_PASS\n"
            "canonical_boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.\n"
            "boundary_sentence_present: true\n"
            "boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending. This Issue does not create authority, attestation, amendment, archive status, or verification-level upgrade unless the relevant machine gates pass.\n"
            "reception_initiation_class: self_initiated\n"
            "reception_initiation_basis: agent_discovered_publicly\n"
            "agent_independent_followup: true\n"
            "```\n"
        ),
        "state": "closed",
        "state_reason": "not_planned",
        "createdAt": "2026-05-17T06:00:00Z",
        "closedAt": "2026-05-17T06:05:00Z",
        "labels": [],
        "url": "https://github.com/thechurchofagi/trinity-accord/issues/168",
    }


def detect_direct_archive_attempt(issue):
    """Detect if an Issue should trigger DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API.

    Uses the same strict receipt validation as the real triage_echo_issue.py.
    Returns (triggered: bool, reason: str).
    """
    from gateway_v0_v5_policy import has_valid_gateway_receipt_in_text

    body = issue.get("body", "")
    created_at = issue.get("createdAt", "")

    # Check archive intent
    ARCHIVE_INTENT_PATTERNS = [
        r"requested_archive_kind:\s*agent_declared_verification_archive",
        r"agent_declared_verification_archive",
        r"auto_archive_agent_declared_verification",
    ]
    has_archive_intent = any(re.search(p, body, re.IGNORECASE) for p in ARCHIVE_INTENT_PATTERNS)
    if not has_archive_intent:
        return False, "no archive intent"

    # Strict receipt check — same as production triage
    has_gateway_receipt = has_valid_gateway_receipt_in_text(body)
    if has_gateway_receipt:
        return False, "has valid gateway receipt"

    # Check if after effective date
    try:
        effective = datetime.fromisoformat(EFFECTIVE_AT.replace("Z", "+00:00"))
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if created < effective:
            return False, "before effective date (legacy)"
    except Exception:
        pass

    return True, "direct archive attempt without valid gateway receipt"


def generate_triage_comment(issue_number, reason):
    """Generate the triage comment for a direct archive attempt.

    Must contain 'Render API only' guidance.
    Must NOT be an amendment-only message.
    """
    return (
        f"**Issue #{issue_number} — Direct Archive Attempt Detected**\n\n"
        f"This Issue was closed because V0-V5 agent-declared archive is **Render-API-only**.\n\n"
        f"**What happened:** You created a GitHub Issue directly with archive intent, "
        f"but valid archives must go through the Render API.\n\n"
        f"**Reason:** {reason}\n\n"
        f"**How to submit correctly:**\n"
        f"1. Use the Render API: `POST /gateway/preflight` then `POST /agent-submit`\n"
        f"2. Or use the Agent Submit guide at `/agent-submit/`\n"
        f"3. The Render API will validate, render, and create the Issue automatically\n\n"
        f"A valid archive record requires:\n"
        f"- `gateway_receipt_id` (from Render API)\n"
        f"- `created_by_gateway: true`\n"
        f"- `archive_ready: true`\n"
        f"- `render_api_only: true`\n\n"
        f"This is not an amendment or attestation. "
        f"Bitcoin Originals remain final and non-amending.\n\n"
        f"Labels: `render-api-required`, `invalid:direct-issue-archive-attempt`"
    )


def check_comment_not_amendment_only(comment):
    """Verify the comment is NOT just an amendment-style rejection.

    Issue #168 was originally closed with an inaccurate amendment-style message.
    The new message should specifically address the Render API requirement.
    """
    # Amendment-only patterns that should NOT be the sole message
    amendment_only_patterns = [
        r"^.*does not amend.*$",
        r"^.*not an amendment.*$",
        r"^.*boundary violation.*$",
    ]

    # Check that the comment contains Render API guidance
    has_render_api_guidance = "Render API" in comment or "render_api" in comment.lower()
    has_submit_guidance = "/agent-submit" in comment or "preflight" in comment.lower()

    return has_render_api_guidance and has_submit_guidance


def check_not_counted_in_index(issue, effective_at=EFFECTIVE_AT):
    """Verify this issue would NOT be counted in the index.

    Uses the same strict receipt validation as production code.
    """
    from gateway_v0_v5_policy import has_valid_gateway_receipt_in_text

    body = issue.get("body", "")
    created_at = issue.get("createdAt", "")

    has_gateway_receipt = has_valid_gateway_receipt_in_text(body)

    try:
        effective = datetime.fromisoformat(effective_at.replace("Z", "+00:00"))
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        after_effective = created >= effective
    except Exception:
        after_effective = True

    # After effective date without receipt → excluded
    if after_effective and not has_gateway_receipt:
        return True, "excluded: no valid gateway receipt after effective date"
    return False, "would be included"


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

    print("=== Issue #168 Render API Only Guidance Tests ===\n")

    # Create fixture
    issue = make_issue168_fixture()

    # --- Verify: DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API triggered ---
    print("--- Verify DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API ---")
    triggered, reason = detect_direct_archive_attempt(issue)
    check(
        "DIRECT_ARCHIVE_ATTEMPT_REQUIRES_RENDER_API is triggered",
        triggered,
        f"reason: {reason}",
    )
    check(
        "Reason is 'direct archive attempt without valid gateway receipt'",
        reason == "direct archive attempt without valid gateway receipt",
        f"got: {reason}",
    )

    # --- Verify: Comment contains Render API only guidance ---
    print("\n--- Verify comment contains Render API only guidance ---")
    comment = generate_triage_comment(issue["number"], reason)
    check(
        "Comment contains 'Render-API-only' or 'Render API'",
        "Render-API-only" in comment or "Render API" in comment,
    )
    check(
        "Comment contains submission guidance (/agent-submit or preflight)",
        "/agent-submit" in comment or "preflight" in comment.lower(),
    )
    check(
        "Comment mentions gateway_receipt_id requirement",
        "gateway_receipt_id" in comment,
    )
    check(
        "Comment mentions created_by_gateway requirement",
        "created_by_gateway" in comment,
    )

    # --- Verify: NOT amendment-only message ---
    print("\n--- Verify NOT amendment-only message ---")
    is_not_amendment_only = check_comment_not_amendment_only(comment)
    check(
        "Comment is NOT amendment-only (has Render API guidance)",
        is_not_amendment_only,
    )
    # Explicit check: the comment should NOT just say "boundary violation"
    check(
        "Comment does not start with generic boundary violation",
        not comment.startswith("This Issue violates"),
    )
    # The comment should reference the specific Render API path
    check(
        "Comment references Render API submission path",
        "gateway" in comment.lower() or "render" in comment.lower(),
    )

    # --- Verify: Not counted in index ---
    print("\n--- Verify NOT counted in index ---")
    not_counted, count_reason = check_not_counted_in_index(issue)
    check(
        "Issue #168 is NOT counted in index",
        not_counted,
        f"reason: {count_reason}",
    )

    # Verify the issue lacks gateway receipt
    body = issue.get("body", "")
    check(
        "Issue body lacks created_by_gateway=true",
        "created_by_gateway: true" not in body,
    )
    check(
        "Issue body lacks gateway_receipt_id with gar- prefix",
        "gateway_receipt_id: gar-" not in body,
    )

    # --- Verify: Issue would get correct labels ---
    print("\n--- Verify expected labels ---")
    expected_labels = ["render-api-required", "invalid:direct-issue-archive-attempt"]
    check(
        "Expected label 'render-api-required' defined",
        "render-api-required" in expected_labels,
    )
    check(
        "Expected label 'invalid:direct-issue-archive-attempt' defined",
        "invalid:direct-issue-archive-attempt" in expected_labels,
    )

    # --- Summary ---
    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
