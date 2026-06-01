#!/usr/bin/env python3
"""Test Gateway schema descriptions reference V0-V5 agent-declared path."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    text = json.dumps(data)

    props = data.get("properties", {})

    # Test 1: requested_archive_kind description mentions agent_declared_verification_archive
    rak = props.get("requested_archive_kind", {})
    rak_desc = rak.get("description", "")
    check(
        "requested_archive_kind description mentions agent_declared_verification_archive",
        "agent_declared_verification_archive" in rak_desc,
        f"description: {rak_desc[:200]}",
    )

    # Test 2: requested_archive_kind description mentions V0
    check(
        "requested_archive_kind description mentions V0",
        "V0" in rak_desc,
        f"description: {rak_desc[:200]}",
    )

    # Test 3: requested_archive_kind description mentions V6+
    check(
        "requested_archive_kind description mentions V6+",
        "V6+" in rak_desc,
        f"description: {rak_desc[:200]}",
    )

    # Test 4: description does not unconditionally map verification_report_candidate -> verification_report_archive
    check(
        "requested_archive_kind description does NOT unconditionally map report_candidate -> verification_report_archive",
        "verification_report_candidate -> verification_report_archive" not in rak_desc
        or "V6+" in rak_desc,
        f"description: {rak_desc[:200]}",
    )

    # Test 5: record_intent description mentions V0-V5
    ri = props.get("record_intent", {})
    ri_desc = ri.get("description", "")
    check(
        "record_intent description mentions V0",
        "V0" in ri_desc,
        f"description: {ri_desc[:200]}",
    )

    # Test 6: agent_declared_protocol_level exists
    check(
        "agent_declared_protocol_level property exists",
        "agent_declared_protocol_level" in props,
    )

    # Test 7: evidence_requirement_mode exists
    check(
        "evidence_requirement_mode property exists",
        "evidence_requirement_mode" in props,
    )

    # Test 8: verification_oath has minLength 160
    oath_props = (
        props.get("agent_integrity_declaration", {})
        .get("properties", {})
        .get("verification_oath", {})
        .get("properties", {})
    )
    readback = oath_props.get("agent_readback", {})
    check(
        "agent_readback minLength is 160",
        readback.get("minLength") == 160,
        f"minLength: {readback.get('minLength')}",
    )

    # Test 9: verification_oath has required fields
    oath_required = (
        props.get("agent_integrity_declaration", {})
        .get("properties", {})
        .get("verification_oath", {})
        .get("required", [])
    )
    check(
        "verification_oath has required fields",
        len(oath_required) > 0,
        f"required: {oath_required}",
    )
    check(
        "verification_oath required includes agent_readback",
        "agent_readback" in oath_required,
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
