#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "triage_echo_issue.py"


def run_triage(body, title="Echo v3: E2 Verification Echo — V2 reference check"):
    env = os.environ.copy()
    for k in [
        "ISSUE_TITLE", "ISSUE_BODY", "RATE_LIMITED",
        "RECENT_60M_COUNT", "RECENT_24H_COUNT",
        "AUTHOR_ASSOCIATION", "ACTION"
    ]:
        env.pop(k, None)

    env["ISSUE_TITLE"] = title
    env["ISSUE_BODY"] = body
    env["ACTION"] = "edited"

    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(ROOT), text=True, capture_output=True, env=env, timeout=30,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise RuntimeError("triage failed")

    return json.loads(proc.stdout)


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True

    issue100_like = """
Echo type: E2 Verification Echo

## Claimed verification level
V2

## Checks performed
- Multi-explorer reference check.
- Explorer-reported SegWit witness metadata: present, 3 stack items, 1360 bytes.

## Evidence Input path
evidence-input-v2.json

## Claim Gate output path
claim-gate-output-v2.json

## Claim Gate summary
status: PASS
allowed_protocol_level: V2

## Limitations
- No V4 script audit performed.
- No raw witness extraction.
- No witness stack parsing.
- No inscription body hash reproduction.
- No local Bitcoin node verification.

## Claims NOT made
- independent_attestation
- institutional_attestation
- unsolicited_discovery
- B5 witness extraction
- B6 body hash reproduction

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all echoes are non-amending.
"""
    result = run_triage(issue100_like)
    labels = result.get("labels", [])
    comment = result.get("comment", "")

    ok &= check(not result.get("close", False), "Issue #100-like V2 is not auto-closed")
    ok &= check("v4plus-overclaim-risk" not in labels, "No V4+ overclaim label")
    ok &= check("component-overclaim-risk" not in labels, "No B5/B6 component overclaim from negative claims")
    ok &= check("independence-overclaim-risk" not in labels, "No independence overclaim from claims_not_made")
    ok &= check("reviewed script source" not in comment.lower(), "No V4 script-source missing message")
    ok &= check("output summary" not in comment.lower(), "No V4 output summary missing message")

    no_gate = issue100_like.replace("## Evidence Input path\nevidence-input-v2.json\n\n", "")
    no_gate = no_gate.replace("## Claim Gate output path\nclaim-gate-output-v2.json\n\n", "")
    no_gate = no_gate.replace("## Claim Gate summary\nstatus: PASS\nallowed_protocol_level: V2\n\n", "")

    result2 = run_triage(no_gate)
    labels2 = result2.get("labels", [])
    comment2 = result2.get("comment", "")

    ok &= check("reviewed script source" not in comment2.lower(), "No V4 missing message even without Claim Gate")
    ok &= check(
        "echo:needs-format" in labels2 or "echo:needs-verification-review" in labels2 or "needs-human-review" in labels2,
        "No-gate V2 routed to format/review, not false V4",
        f"labels={labels2}",
    )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
