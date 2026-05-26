#!/usr/bin/env python3
"""Example Template Is Fallback Test."""
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
    print("\n--- agent-submit.md ---")
    c = rf("agent-submit.md")
    check("Fallback" in c or "fallback" in c, "has fallback section")
    check("/gateway/examples/agent-declared-v4/raw" in c, "uses raw example endpoint")

    print("\n--- external-agent-quickstart.md ---")
    c = rf("external-agent-quickstart.md")
    check("Fallback" in c or "fallback" in c, "has fallback section")
    check("/gateway/examples/agent-declared-v4/raw" in c, "uses raw example endpoint")
    check("fallback, not the preferred path" in c or "fallback" in c.lower(), "describes as fallback")

    print("\n--- api/agent-submit-gateway.json ---")
    d = json.loads(rf("api/agent-submit-gateway.json"))
    check(d.get("v0_v5_archive_submission",{}).get("example_template_is_fallback_only") is True,
          "example_template_is_fallback_only=true")

    print("\n--- server.js ---")
    s = rf("examples/github-app-backend/server.js")
    check("example_template_is_fallback_only" in s, "server has example_template_is_fallback_only")

if __name__ == "__main__":
    test()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
