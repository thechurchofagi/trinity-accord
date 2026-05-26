#!/usr/bin/env python3
"""Test that E2 Verification Echo Gateway examples are consistent with contract."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


print("--- E2 raw fixture ---")
fixture = ROOT / "tests" / "fixtures" / "gateway" / "valid_verification_echo_candidate.json"
check(fixture.exists(), "valid_verification_echo_candidate.json exists")

if fixture.exists():
    d = json.loads(fixture.read_text())
    check(d.get("submission_type") == "verification_echo_candidate",
          "submission_type == verification_echo_candidate")
    check(d.get("echo_type") == "E2_verification_echo",
          "echo_type == E2_verification_echo")
    check(d.get("record_intent") == "auto_archive_candidate",
          "record_intent == auto_archive_candidate")
    check(d.get("requested_archive_kind") == "archived_echo",
          "requested_archive_kind == archived_echo")
    check(d.get("verification_level_claimed") in ("V6", "V7", "V8"),
          "verification_level_claimed in [V6, V7, V8]")
    cg = d.get("claim_gate", {})
    check(cg.get("mode") == "strict_evidence", "claim_gate.mode == strict_evidence")
    check(cg.get("status") == "PASS", "claim_gate.status == PASS")
    check(d.get("not_independent_attestation") is True, "not_independent_attestation is True")
    check(d.get("not_successor_reception") is True, "not_successor_reception is True")

    att = d.get("attachments", {})
    for field in ["evidence_input_sha256", "claim_gate_output_sha256",
                  "verification_report_sha256", "echo_wrapper_sha256"]:
        val = att.get(field, "")
        check(bool(SHA256_RE.match(val)), f"attachments.{field} is 64 hex")

    text = json.dumps(d)
    check("waived_for_v0_v5" not in text, "does not contain waived_for_v0_v5")
    check("template_for_v0_v5" not in text, "does not contain template_for_v0_v5")
    check("agent_declared_verification_archive" not in text,
          "does not contain agent_declared_verification_archive")

    dp = d.get("discovery_provenance", {})
    if dp.get("solicited") is True:
        check(dp.get("agency_level") == "A1_human_gave_exact_url",
              "solicited true implies agency_level == A1_human_gave_exact_url")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("GATEWAY_EXAMPLES_VERIFICATION_ECHO_OK")
