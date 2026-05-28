#!/usr/bin/env python3
"""Before-leaving report schema must match output policy required fields."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "api" / "agent-before-leaving-report-schema.v1.json"
POLICY = ROOT / "api" / "agent-output-policy.v1.json"

def main() -> int:
    errors: list[str] = []

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))

    required = set(schema.get("required", []))
    policy_required = set(
        policy.get("agent_exit_readback_policy", {}).get("required_fields", [])
    )

    missing = sorted(policy_required - required)
    extra = sorted(required - policy_required)

    if missing:
        errors.append(f"schema missing policy required fields: {missing}")
    if extra:
        errors.append(f"schema has required fields not in policy: {extra}")

    ref = policy.get("agent_exit_readback_policy", {}).get("before_leaving_report_schema")
    if ref != "/api/agent-before-leaving-report-schema.v1.json":
        errors.append("output policy must reference before_leaving report schema")

    if schema.get("additionalProperties") is not False:
        errors.append("schema must set additionalProperties=false")

    if errors:
        print("FAIL: before_leaving report schema errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: before_leaving report schema matches output policy")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
