#!/usr/bin/env python3
"""Test that E2 Verification Echo path is consistent across schema, contract, capabilities, and docs."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# 1. agent-submit-gateway.json
print("--- api/agent-submit-gateway.json ---")
gw = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text())
check("verification_echo_candidate" in gw.get("accepted_submission_types", []),
      "accepted_submission_types includes verification_echo_candidate")
check("verification_echo_path" in gw, "has verification_echo_path")
vep = gw.get("verification_echo_path", {})
check(vep.get("builder") == "scripts/build_verification_echo_payload.py",
      "verification_echo_path builder is correct")
check(vep.get("raw_example_endpoint_path") == "/gateway/examples/verification-echo/raw",
      "verification_echo_path raw endpoint is correct")
check(vep.get("requires_strict_evidence_pipeline") is True,
      "verification_echo_path requires strict evidence")
check(vep.get("not_pure_echo") is True, "verification_echo_path is not pure echo")
check(vep.get("not_agent_declared_v0_v5_archive") is True,
      "verification_echo_path is not V0-V5 template")

# 2. agent-first-contact.json
print("--- api/agent-first-contact.json ---")
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text())
intents = [i.get("intent", "") for i in fc.get("choose_one", [])]
check("verification_echo_e2" in intents, "choose_one has verification_echo_e2 intent")
check("verification_echo_path" in fc, "has verification_echo_path top-level")

# 3. server.js capabilities
print("--- server.js capabilities ---")
server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
check("verification_echo_path:" in server, "server.js has verification_echo_path")
check("/gateway/examples/verification-echo/raw" in server,
      "server.js has /gateway/examples/verification-echo/raw endpoint")
check("/gateway/examples/verification-echo" in server,
      "server.js has /gateway/examples/verification-echo endpoint")

# 4. Schema allows verification_echo_candidate
print("--- schema ---")
schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text())
props = schema.get("properties", {})
st = props.get("submission_type", {})
enum_vals = st.get("enum", [])
check("verification_echo_candidate" in enum_vals,
      "schema enum includes verification_echo_candidate")

print(f"\n--- Results: {sum(1 for _ in errors) == 0} ({len(errors)} errors) ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("VERIFICATION_ECHO_PATH_CONSISTENCY_OK")
