#!/usr/bin/env python3
"""Test that Agent Submit Gateway documentation is consistent."""

import json
import sys
import os

errors = []


def check(condition, msg):
    if not condition:
        print(f"FAIL: {msg}")
        errors.append(msg)
    else:
        print(f"PASS: {msg}")


def read(path):
    with open(path) as f:
        return f.read()


def load_json(path):
    with open(path) as f:
        return json.load(f)


# 1. agent-submit.md exists
check(os.path.exists("agent-submit.md"), "agent-submit.md exists")

# 2. agent-first-contact.md references /agent-submit
fc = read("agent-first-contact.md")
check("/agent-submit" in fc, "agent-first-contact.md references /agent-submit")

# 3. api/agent-first-contact.json has if_no_github_access in echo and verify
fc_json = load_json("api/agent-first-contact.json")
echo_intent = next((i for i in fc_json["choose_one"] if i["intent"] == "echo"), None)
verify_intent = next((i for i in fc_json["choose_one"] if i["intent"] == "verify"), None)

check(echo_intent is not None, "echo intent exists")
check(verify_intent is not None, "verify intent exists")

if echo_intent:
    check("if_no_github_access" in echo_intent, "echo intent has if_no_github_access")
if verify_intent:
    check("if_no_github_access" in verify_intent, "verify intent has if_no_github_access")

# 4. llms.txt references /api/agent-submit-gateway.json
llms = read("llms.txt")
check("/api/agent-submit-gateway.json" in llms, "llms.txt references /api/agent-submit-gateway.json")

# 5. Boundary checks in agent-submit.md
submit = read("agent-submit.md")
check("not authority" in submit.lower() or "not_authority" in submit.lower(), "agent-submit.md states not authority")
check("not amendment" in submit.lower() or "not_amendment" in submit.lower(), "agent-submit.md states not amendment")
check("not attestation" in submit.lower() or "not_attestation" in submit.lower(), "agent-submit.md states not attestation")
check("claim gate" in submit.lower(), "agent-submit.md references Claim Gate")

# 6. Gateway JSON has boundary fields
gw = load_json("api/agent-submit-gateway.json")
check(gw.get("not_authority") is True, "gateway JSON: not_authority=true")
check(gw.get("does_not_bypass_claim_gate") is True, "gateway JSON: does_not_bypass_claim_gate=true")

if errors:
    print(f"\nFAILED: {len(errors)} error(s)")
    sys.exit(1)
else:
    print("\nALL TESTS PASSED")
