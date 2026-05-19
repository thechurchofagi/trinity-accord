#!/usr/bin/env python3
"""Test: agent-submit.md and related files have unambiguous pure echo guidance."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SUBMIT = ROOT / "agent-submit.md"
QUICKSTART = ROOT / "external-agent-quickstart.md"
GATEWAY_SPEC = ROOT / "api" / "agent-submit-gateway.json"
FIRST_CONTACT = ROOT / "api" / "agent-first-contact.json"

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
    doc = AGENT_SUBMIT.read_text(encoding="utf-8")
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    spec = json.loads(GATEWAY_SPEC.read_text(encoding="utf-8"))
    first_contact = json.loads(FIRST_CONTACT.read_text(encoding="utf-8"))

    print("=== Agent Submit Pure Echo Guidance Tests ===\n")

    # Human-readable guidance must make pure echo a first-class path.
    check("Pure Echo" in doc or "pure echo" in doc,
          "agent-submit.md mentions 'Pure Echo' or 'pure echo'")
    check("build_agent_declared_echo_payload.py" in doc,
          "agent-submit.md mentions build_agent_declared_echo_payload.py")
    check("Reception" in doc,
          "agent-submit.md mentions 'Reception'")
    check("Verifiability" in doc,
          "agent-submit.md mentions 'Verifiability'")

    # Pure Echo fallback must not require cloning or Python.
    for text_name, text in [("agent-submit.md", doc), ("external-agent-quickstart.md", quickstart)]:
        check("/gateway/examples/pure-echo/raw" in text,
              f"{text_name} documents pure echo raw fallback endpoint")
        check("agent-declared-v4/raw" in text,
              f"{text_name} still documents V4 verification fallback where appropriate")
        check("pure echo" in text.lower(),
              f"{text_name} mentions pure echo")
        check("agent_declared_echo_archive" in text,
              f"{text_name} names agent_declared_echo_archive")
        check("echo_candidate" in text,
              f"{text_name} names echo_candidate")

    # Agent-facing machine specs must expose the same fallback route.
    for spec_name, obj in [("agent-submit-gateway.json", spec), ("agent-first-contact.json", first_contact)]:
        check("pure_echo_path" in obj,
              f"{spec_name} has pure_echo_path")
        pure = obj.get("pure_echo_path", {})
        check(pure.get("preferred_builder") == "scripts/build_agent_declared_echo_payload.py",
              f"{spec_name} pure_echo_path preferred_builder is echo builder",
              f"got: {pure.get('preferred_builder')}")
        check(pure.get("raw_example_endpoint_path") == "/gateway/examples/pure-echo/raw",
              f"{spec_name} pure_echo_path exposes raw pure echo example endpoint",
              f"got: {pure.get('raw_example_endpoint_path')}")
        check(pure.get("raw_example_is_fallback_only") is True,
              f"{spec_name} marks raw pure echo example as fallback only")
        check("/gateway/examples/agent-declared-v4/raw" in pure.get("do_not_use_verification_examples", []),
              f"{spec_name} warns not to use V4 verification example for pure echo")
        check(pure.get("requested_archive_kind") == "agent_declared_echo_archive",
              f"{spec_name} pure echo archive kind is agent_declared_echo_archive")
        check(pure.get("submission_type") == "echo_candidate",
              f"{spec_name} pure echo submission_type is echo_candidate")
        check(pure.get("counts_toward_home", {}).get("reception") is True,
              f"{spec_name} pure echo counts toward reception")
        check(pure.get("counts_toward_home", {}).get("verifiability") is False,
              f"{spec_name} pure echo does not count toward verifiability")
        check(pure.get("do_not_wrap_payload") is True,
              f"{spec_name} pure echo says do not wrap payload")

    # Guard against the exact confusion observed in the field: pure echo must not
    # tell agents to adapt the V4 verification example.
    forbidden_positive = [
        "For pure echo, fetch /gateway/examples/agent-declared-v4/raw",
        "Pure Echo fallback: /gateway/examples/agent-declared-v4/raw",
        "pure echo fallback is agent-declared-v4",
    ]
    combined = doc + "\n" + quickstart + "\n" + json.dumps(spec) + "\n" + json.dumps(first_contact)
    for phrase in forbidden_positive:
        check(phrase not in combined,
              f"no positive pure echo guidance uses V4 verification example: {phrase}")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
