#!/usr/bin/env python3
"""Test that api/external-agent-operation-examples.v1.json has required structure."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "api" / "external-agent-operation-examples.v1.json"
    if not path.exists():
        print(f"FAIL: {path} does not exist")
        return 1

    doc = json.loads(path.read_text(encoding="utf-8"))

    required_examples = [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
        "operational_canary",
    ]

    for name in required_examples:
        if name not in doc.get("examples", {}):
            print(f"FAIL: example '{name}' missing")
            return 1
        example = doc["examples"][name]
        if name != "operational_canary":
            if "command_template" not in example:
                print(f"FAIL: example '{name}' missing command_template")
                return 1

    # Gateway endpoints
    gw = doc.get("gateway", {})
    if "/gateway/preflight" not in gw.get("preflight", ""):
        print("FAIL: gateway preflight endpoint incorrect")
        return 1
    if "/agent-submit" not in gw.get("submit", ""):
        print("FAIL: gateway submit endpoint incorrect")
        return 1

    # No /gateway/submit
    raw = json.dumps(doc)
    if "/gateway/submit" in raw:
        print("FAIL: found /gateway/submit (should be /agent-submit)")
        return 1

    # E2 not offered as direct public example
    if "e2" in doc.get("examples", {}):
        print("FAIL: E2 offered as direct public example")
        return 1

    print("PASS: test_external_agent_operation_examples_contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
