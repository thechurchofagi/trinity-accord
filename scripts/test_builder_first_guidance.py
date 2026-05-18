#!/usr/bin/env python3
"""Builder-First Guidance Test."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = F = T = 0
def check(c, l):
    global P, F, T; T += 1
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l}")
def rf(r):
    p = ROOT / r
    return p.read_text("utf-8") if p.exists() else ""

def test():
    print("\n--- agent-submit.md ---")
    c = rf("agent-submit.md")
    check("scripts/build_agent_declared_archive_payload.py" in c, "mentions builder script")
    check("builder-first" in c.lower() or "canonical builder" in c.lower(), "builder-first language")
    check("Do not wrap" in c or "do not wrap" in c, "do not wrap payload")
    check("build-from-evidence" in c, "mentions build-from-evidence")
    check("Fallback" in c or "fallback" in c, "has fallback section")

    print("\n--- external-agent-quickstart.md ---")
    c = rf("external-agent-quickstart.md")
    check("scripts/build_agent_declared_archive_payload.py" in c, "mentions builder script")
    check("builder-first" in c.lower() or "canonical builder" in c.lower(), "builder-first language")
    check("Do not wrap" in c or "do not wrap" in c, "do not wrap payload")
    check("Fallback" in c or "fallback" in c, "has fallback section")

    print("\n--- api/agent-first-contact.json ---")
    d = json.loads(rf("api/agent-first-contact.json"))
    v = next((i for i in d.get("choose_one",[]) if i.get("intent")=="verify_v0_v5_agent_declared"), None)
    check(v is not None, "has verify_v0_v5_agent_declared")
    if v:
        check("canonical_builder" in v, "has canonical_builder")
        check(v.get("raw_payload_only") is True, "raw_payload_only=true")
        check(v.get("do_not_wrap_payload") is True, "do_not_wrap_payload=true")
        check("gateway_payload" in v.get("forbidden_wrappers",[]), "forbids gateway_payload")
        check(any("build_agent_declared" in p for p in v.get("pipeline",[])), "pipeline references builder")

    print("\n--- api/agent-submission-guide.json ---")
    d = json.loads(rf("api/agent-submission-guide.json"))
    v = next((e for e in d.get("decision_tree",[]) if "V0" in e.get("if","") and "V4+" in e.get("if","")), None)
    check(v is not None, "has V0-V5 entry")
    if v:
        check(v.get("builder_is_canonical") is True, "builder_is_canonical=true")
        check(v.get("raw_payload_only") is True, "raw_payload_only=true")
        check(v.get("do_not_wrap_payload") is True, "do_not_wrap_payload=true")

    print("\n--- api/agent-submit-gateway.json ---")
    d = json.loads(rf("api/agent-submit-gateway.json"))
    v = d.get("v0_v5_archive_submission", {})
    check("canonical_builder" in v, "has canonical_builder")
    check(v.get("builder_first_default") is True, "builder_first_default=true")
    check(v.get("example_template_is_fallback_only") is True, "example_template_is_fallback_only=true")
    check(v.get("raw_payload_only") is True, "raw_payload_only=true")
    check(v.get("do_not_wrap_payload") is True, "do_not_wrap_payload=true")

    print("\n--- llms.txt ---")
    c = rf("llms.txt")
    check("scripts/build_agent_declared_archive_payload.py" in c, "mentions builder script")
    check("builder-first" in c.lower() or "canonical builder" in c.lower(), "builder-first language")

if __name__ == "__main__":
    test()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
