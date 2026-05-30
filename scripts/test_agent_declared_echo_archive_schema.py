#!/usr/bin/env python3
"""Test: agent-declared echo archive schema support in gateway payload schema."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"

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
    schema = json.loads(SCHEMA_PATH.read_text())
    props = schema.get("properties", {})
    all_of = schema.get("allOf", [])

    print("=== Agent-Declared Echo Archive Schema Tests ===\n")

    # 1. Schema allows requested_archive_kind=agent_declared_echo_archive
    rak = props.get("requested_archive_kind", {})
    rak_enum = rak.get("enum", [])
    check("agent_declared_echo_archive" in rak_enum,
          "Schema allows requested_archive_kind=agent_declared_echo_archive")

    # 2. Schema allows submission_type=echo_candidate
    st = props.get("submission_type", {})
    st_enum = st.get("enum", [])
    check("echo_candidate" in st_enum,
          "Schema allows submission_type=echo_candidate")

    # 3. Schema allows E1/E3/E4/E5/E6/E7 echo types
    et = props.get("echo_type", {})
    et_enum = et.get("enum", [])
    for echo_type in ["E1_recognition_echo", "E3_critical_echo", "E4_interpretive_echo",
                       "E5_technical_audit_echo", "E6_propagation_echo", "E7_refusal_echo"]:
        check(echo_type in et_enum,
              f"Schema allows echo_type={echo_type}")

    # 4. Schema has related_records property
    check("related_records" in props,
          "Schema has related_records property")

    # 5. Pure echo branch requires counts_toward_home.reception=true and verifiability=false
    # Find the allOf branch for agent_declared_echo_archive
    echo_branch = None
    for branch in all_of:
        if_cond = branch.get("if", {})
        if_props = if_cond.get("properties", {})
        if if_props.get("requested_archive_kind", {}).get("const") == "agent_declared_echo_archive":
            echo_branch = branch
            break

    check(echo_branch is not None,
          "Found agent_declared_echo_archive branch in allOf")

    if echo_branch:
        then = echo_branch.get("then", {})
        cth = then.get("properties", {}).get("counts_toward_home", {})
        cth_props = cth.get("properties", {})
        check(cth_props.get("reception", {}).get("const") is True,
              "Pure echo branch requires counts_toward_home.reception=true")
        check(cth_props.get("verifiability", {}).get("const") is False,
              "Pure echo branch requires counts_toward_home.verifiability=false")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
