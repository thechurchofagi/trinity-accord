#!/usr/bin/env python3
"""Test that Agent Issue Gateway payload examples are internally consistent."""

import json
import sys

EXAMPLES = {
    "api/examples/agent-issue-gateway-payload.echo.json": "echo_candidate",
    "api/examples/agent-issue-gateway-payload.verification.json": "verification_report_candidate",
    "api/examples/agent-issue-gateway-payload.custody.json": "human_custody_notice",
}

errors = []


def check(condition, msg):
    if not condition:
        print(f"FAIL: {msg}")
        errors.append(msg)
    else:
        print(f"PASS: {msg}")


for path, expected_type in EXAMPLES.items():
    with open(path) as f:
        data = json.load(f)

    prefix = f"[{path}]"

    # 1. Parseable
    check(isinstance(data, dict), f"{prefix} is valid JSON object")

    # 2. Correct submission_type
    check(data.get("submission_type") == expected_type, f"{prefix} submission_type={expected_type}")

    # 3. Has boundary_acknowledgement
    ba = data.get("boundary_acknowledgement", {})
    check(isinstance(ba, dict), f"{prefix} has boundary_acknowledgement")
    check(ba.get("not_authority") is True, f"{prefix} not_authority=true")
    check(ba.get("not_amendment") is True, f"{prefix} not_amendment=true")
    check(ba.get("not_attestation") is True, f"{prefix} not_attestation=true")

    # 4. Verification example must have at least one report/receipt hash
    if expected_type == "verification_report_candidate":
        att = data.get("attachments", {})
        has_hash = any(
            att.get(k) for k in [
                "evidence_input_sha256",
                "claim_gate_output_sha256",
                "verification_report_sha256",
                "agent_verification_receipt_sha256",
            ]
        )
        check(has_hash, f"{prefix} verification has at least one report/receipt hash")

    # 5. Custody example must have custody or receipt hash
    if expected_type == "human_custody_notice":
        att = data.get("attachments", {})
        has_hash = any(
            att.get(k) for k in [
                "agent_verification_receipt_sha256",
                "custody_package_sha256",
            ]
        )
        check(has_hash, f"{prefix} custody has at least one receipt/custody hash")

if errors:
    print(f"\nFAILED: {len(errors)} error(s)")
    sys.exit(1)
else:
    print("\nALL TESTS PASSED")
