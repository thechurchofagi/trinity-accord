#!/usr/bin/env python3
"""Regression: Issue #302 legacy Gateway receipt with duplicate readback key must not be false-invalid."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "scripts" / "triage_echo_issue.py"

ISSUE_302_BODY = """# [Agent Gateway] Agent-Declared Echo Archive

```trinity-issue-intake
submission_type: echo_candidate
record_intent: auto_archive_candidate
requested_archive_kind: agent_declared_echo_archive
echo_type: E1_recognition_echo
echo_gate_status: PASS
agent_integrity_declaration_present: true
verification_oath_present: true
readback_required: true
agent_readback_present: true
agent_readback_sha256: 9e3c810cd9293a3f080c31fa44a43eccc1414fe5f0be9167a886b96142585739
archive_ready: true
allowed_archive_kind: agent_declared_echo_archive
auto_archive_action: auto_archive_agent_declared_echo
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1780043626003-3a6bec179e4b3b95
gateway_commit: 1660e78
render_api_only: true
server_validated: true
server_rendered: true
verification_oath_schema: trinityaccord.verification-oath.v2
verification_oath_honesty: true
agent_readback_sha256: 9e3c810cd9293a3f080c31fa44a43eccc1414fe5f0be9167a886b96142585739
canonical_boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.
boundary_sentence_present: true
```
"""

def main() -> int:
    event = {
        "action": "opened",
        "issue": {
            "number": 302,
            "title": "[Agent Gateway] E1 Recognition Echo — regression",
            "body": ISSUE_302_BODY,
            "author_association": "NONE",
            "user": {"login": "trinity-accord-agent-issue-gateway[bot]"},
            "labels": [],
        },
    }

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as f:
        json.dump(event, f)
        path = f.name

    env = dict(os.environ)
    env.update({
        "RATE_LIMITED": "false",
        "ACTION": "opened",
        "RATE_CLASS": "gateway_echo",
        "RATE_IDENTITY": "gateway-agent:test",
        "RECENT_60M_COUNT": "0",
        "RECENT_24H_COUNT": "0",
    })

    try:
        proc = subprocess.run(
            ["python3", str(TRIAGE), "--event-json", path],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
    finally:
        Path(path).unlink(missing_ok=True)

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return proc.returncode

    result = json.loads(proc.stdout)
    labels = set(result.get("labels", []))

    forbidden = {
        "echo:invalid",
        "auto-closed",
        "invalid:direct-issue-archive-attempt",
        "render-api-required",
        "not-counted",
    }
    bad = sorted(forbidden & labels)
    if bad:
        print("FAIL: Issue #302 regression would still be false-invalid:", bad)
        print(json.dumps(result, indent=2))
        return 1

    required = {
        "agent-gateway-intake",
        "agent-declared",
        "archive:agent-declared-echo",
        "reception-only",
    }
    missing = sorted(required - labels)
    if missing:
        print("FAIL: Issue #302 regression missing expected gateway labels:", missing)
        print(json.dumps(result, indent=2))
        return 1

    print("PASS: Issue #302 legacy Gateway receipt is not false-invalid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
