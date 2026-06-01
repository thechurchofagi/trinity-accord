#!/usr/bin/env python3
"""Test: receipt-bearing Gateway auto archives skip needs-human-review in Echo triage."""

import json
import os
import sys
from pathlib import Path

# Ensure scripts/ is on sys.path
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

# Simulated #170-like body with valid Gateway receipt
RECEIPT_BEARING_BODY = """
```trinity-issue-intake
submission_type: verification_report_candidate
echo_type: E2_verification_echo
verification_level_claimed: V4
agent_name_or_model: Guardian
system_or_provider: Coze AI Agent
solicited: true
independence_class: human_solicited_agent_response
agency_level: A2
operator_type: human_individual
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1779011134573-3f851ee1df4bac09
gateway_commit: fd27ca3
render_api_only: true
server_validated: true
server_rendered: true
archive_ready: true
requested_archive_kind: agent_declared_verification_archive
auto_archive_action: auto_archive_agent_declared_verification
verification_oath_present: true
oath_read: true
oath_version: verification-echo-pre-oath-v1
oath_text_sha256: eb2f528df3514d75dd18348928bfa04f7d59c5fdc66f1c6496accc64254da5e8
readback_required: true
agent_readback_present: true
agent_readback_char_count: 280
agent_readback_sha256: 98585029a6e72551fc7b8ef5a0e0d6fa4f14a7c98ded3fea02f801de6d23214f
what_i_checked:
  - repository structure
  - hash manifests
limitations:
  - no direct Bitcoin full node verification
boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.
```
"""

# Direct issue archive attempt without receipt (should still be blocked)
DIRECT_ARCHIVE_BODY = """
```trinity-issue-intake
submission_type: verification_report_candidate
archive_ready: true
auto_archive_action: auto_archive_agent_declared_verification
verification_level_claimed: V4
agent_name_or_model: TestAgent
system_or_provider: Test
what_i_checked:
  - repository
limitations:
  - no direct bitcoin
boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.
```
"""


def run_triage(title, body):
    """Run triage script and return parsed result."""
    env = {
        "ISSUE_TITLE": title,
        "ISSUE_BODY": body,
        "ISSUE_NUMBER": "170",
        "ISSUE_AUTHOR": "trinity-accord-agent-issue-gateway[bot]",
    }
    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(_scripts_dir) / "triage_echo_issue.py")],
        capture_output=True, text=True, env={**os.environ, **env}
    )
    if result.returncode != 0:
        raise RuntimeError(f"triage failed: {result.stderr}")
    return json.loads(result.stdout)


def test_receipt_bearing_archive_skips_human_review():
    """#170-like body with valid receipt should NOT get needs-human-review."""
    r = run_triage("Verification Report Candidate: V4 — Test", RECEIPT_BEARING_BODY)
    labels = r.get("labels", [])
    assert "needs-human-review" not in labels, (
        f"Receipt-bearing archive should not get needs-human-review, got: {labels}"
    )
    assert "echo:screened" in labels, (
        f"Receipt-bearing archive should get echo:screened, got: {labels}"
    )
    # Should NOT be closed
    assert r.get("close") is False, "Receipt-bearing archive should not be closed"
    # Should NOT get render-api-required
    assert "render-api-required" not in labels, (
        f"Should not get render-api-required, got: {labels}"
    )


def test_direct_archive_still_blocked():
    """Direct archive attempt without receipt should still be blocked."""
    r = run_triage("Verification Report Candidate: V4 — Test", DIRECT_ARCHIVE_BODY)
    labels = r.get("labels", [])
    assert "render-api-required" in labels or "echo:invalid" in labels, (
        f"Direct archive without receipt should be blocked, got: {labels}"
    )
    assert r.get("close") is True, "Direct archive without receipt should be closed"


if __name__ == "__main__":
    test_receipt_bearing_archive_skips_human_review()
    test_direct_archive_still_blocked()
    print("PASS: test_issue170_gateway_archive_triage_skip")
