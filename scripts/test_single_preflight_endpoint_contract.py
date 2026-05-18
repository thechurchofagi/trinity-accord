#!/usr/bin/env python3
"""Single Preflight Endpoint Contract Test.
Checks that all docs/API JSON use the same preflight endpoint for V0-V5
and that /gateway/archive-preflight is not exposed as a normal endpoint.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = F = T = 0
def check(c, l):
    global P, F, T; T += 1
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l}")
def rf(r):
    return (ROOT / r).read_text("utf-8")

def test():
    EP = "/gateway/preflight"

    print("\n--- Docs ---")
    for f in ["agent-submit.md","external-agent-quickstart.md","llms.txt"]:
        check(EP in rf(f), f"{f} uses {EP}")

    print("\n--- API JSON ---")
    for f in ["api/agent-first-contact.json","api/agent-submission-guide.json","api/agent-submit-gateway.json"]:
        check(EP in rf(f), f"{f} references {EP}")

    print("\n--- server.js ---")
    server = rf("examples/github-app-backend/server.js")
    check(EP in server, f"server.js uses {EP}")

    # archive-preflight must NOT be a plain string endpoint
    check('archive_preflight: "/gateway/archive-preflight"' not in server,
          "archive-preflight not exposed as plain string endpoint")

    # If present, must be legacy alias
    if "archive_preflight" in server:
        check("legacy_alias" in server, "archive_preflight marked as legacy_alias")
        check('canonical: "/gateway/preflight"' in server, "archive_preflight canonical is /gateway/preflight")
        check("do_not_use_for_new_v0_v5_submissions" in server, "archive_preflight has do_not_use flag")

    # Docs must NOT reference archive-preflight
    print("\n--- Docs must not reference archive-preflight ---")
    for f in ["agent-submit.md","external-agent-quickstart.md","llms.txt",
              "api/agent-first-contact.json","api/agent-submission-guide.json","api/agent-submit-gateway.json"]:
        check("/gateway/archive-preflight" not in rf(f), f"{f} does not reference archive-preflight")

if __name__ == "__main__":
    test()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
