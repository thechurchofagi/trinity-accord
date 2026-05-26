#!/usr/bin/env python3
"""Test: server-generated field error policy in server.js and agent-submit-gateway.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "examples" / "github-app-backend" / "server.js"
GATEWAY_SPEC = ROOT / "api" / "agent-submit-gateway.json"

PASS = 0
FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")


def main():
    global PASS, FAIL
    src = SERVER.read_text()
    spec = json.loads(GATEWAY_SPEC.read_text())

    print("=== Server-Generated Field Error Policy Tests ===\n")

    # 1. gatewayError function
    check("function gatewayError" in src,
          "server.js has gatewayError function")

    # 2. SERVER_GENERATED_FIELDS array with 7 fields
    check("SERVER_GENERATED_FIELDS" in src,
          "server.js has SERVER_GENERATED_FIELDS")
    # Count the fields in the array
    match = re.search(r'const SERVER_GENERATED_FIELDS\s*=\s*\[([^\]]+)\]', src)
    if match:
        fields = [f.strip().strip('"').strip("'") for f in match.group(1).split(",") if f.strip().strip('"').strip("'")]
        check(len(fields) == 7,
              f"SERVER_GENERATED_FIELDS has 7 fields (found {len(fields)})",
              f"fields: {fields}")
    else:
        check(False, "SERVER_GENERATED_FIELDS array found")

    # 3. mentionsServerGeneratedField function
    check("function mentionsServerGeneratedField" in src,
          "server.js has mentionsServerGeneratedField function")

    # 4. agent-submit-gateway.json has server_generated_field_error_policy
    check("server_generated_field_error_policy" in spec,
          "agent-submit-gateway.json has server_generated_field_error_policy")

    # 5. Error responses include validation_stage and agent_action
    # Check that gatewayError calls include both fields
    check("validation_stage" in src and "agent_action" in src,
          "Error responses include validation_stage and agent_action")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


import re

if __name__ == "__main__":
    sys.exit(main())
