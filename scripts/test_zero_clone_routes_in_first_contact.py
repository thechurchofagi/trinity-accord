#!/usr/bin/env python3
"""Test that agent-first-contact.json contains zero-clone builder policy."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "api" / "agent-first-contact.json"
    if not path.exists():
        print(f"FAIL: {path} does not exist")
        return 1

    doc = json.loads(path.read_text(encoding="utf-8"))
    raw = json.dumps(doc)

    if "zero_clone_formal_builder_policy" not in doc:
        print("FAIL: zero_clone_formal_builder_policy missing")
        return 1

    zcp = doc["zero_clone_formal_builder_policy"]

    # Check that legacy paths are present (may be in historical context)
    builder_bundle = zcp.get("builder_bundle_manifest", {})
    if isinstance(builder_bundle, str):
        if "/api/record-chain-builder-bundles.v1.json" not in builder_bundle:
            print("FAIL: missing reference to /api/record-chain-builder-bundles.v1.json")
            return 1
    elif isinstance(builder_bundle, dict):
        if "/api/record-chain-builder-bundles.v1.json" not in builder_bundle.get("path", ""):
            print("FAIL: missing reference to /api/record-chain-builder-bundles.v1.json")
            return 1

    required_routes = [
        "echo",
        "verification",
        "guardian_application",
        "guardian_retirement",
        "propagation",
        "correction",
        "classification_update",
        "context_insufficient_notice",
    ]
    supported_routes = json.dumps(zcp.get("supported_zero_clone_routes", []))
    for route in required_routes:
        if route not in supported_routes:
            print(f"FAIL: route '{route}' not in supported_zero_clone_routes")
            return 1
    for retired_route in [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
    ]:
        if retired_route in supported_routes:
            print(f"FAIL: retired route '{retired_route}' must not be active in supported_zero_clone_routes")
            return 1

    if not zcp.get("do_not_handwrite_formal_payload"):
        print("FAIL: do_not_handwrite_formal_payload not true")
        return 1
    if not zcp.get("full_repo_clone_required_when_bundle_available") is False:
        print("FAIL: full_repo_clone_required_when_bundle_available not false")
        return 1

    print("PASS: test_zero_clone_routes_in_first_contact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
