#!/usr/bin/env python3
"""Single Preflight Endpoint Contract Test."""
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
    check(EP in rf("examples/github-app-backend/server.js"), f"server.js uses {EP}")

if __name__ == "__main__":
    test()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
