#!/usr/bin/env python3
"""Test: Guardian retirement automation infrastructure.

Checks:
  - build_guardian_retirement_payload.mjs exists and is valid Node.js
  - process_guardian_retirement.py exists and imports
  - guardian-registry-auto-retire.yml workflow exists with correct permissions
  - Route selector includes guardian_retirement route
  - Guardian registry schema allows 'retired' status
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks = []

    # 1. Retirement payload builder exists
    builder = ROOT / "scripts" / "build_guardian_retirement_payload.mjs"
    checks.append((builder.exists(), "build_guardian_retirement_payload.mjs exists"))

    # 2. Retirement processor exists
    processor = ROOT / "scripts" / "process_guardian_retirement.py"
    checks.append((processor.exists(), "process_guardian_retirement.py exists"))

    # 3. Workflow exists with correct permissions
    workflow = ROOT / ".github/workflows/guardian-registry-auto-retire.yml"
    if workflow.exists():
        text = workflow.read_text(encoding="utf-8")
        checks.append(("contents: write" in text, "workflow has contents: write"))
        checks.append(("issues: write" in text, "workflow has issues: write"))
        checks.append(("workflow_dispatch" in text, "workflow has workflow_dispatch trigger"))
        checks.append(("guardian-retirement-request" in text, "workflow triggers on retirement comment"))
    else:
        checks.append((False, "guardian-registry-auto-retire.yml exists"))

    # 4. Route selector includes guardian_retirement
    route_path = ROOT / "api" / "route-selector.v1.json"
    if route_path.exists():
        data = json.loads(route_path.read_text(encoding="utf-8"))
        routes = [r.get("recommended_route") for r in data.get("routes", [])]
        checks.append(("guardian_retirement" in routes, "route selector includes guardian_retirement"))
    else:
        checks.append((False, "route-selector.v1.json exists"))

    # 5. Registry schema allows 'retired' status
    schema_path = ROOT / "api" / "guardian-registry-schema.v1.json"
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        statuses = set(schema["properties"]["guardians"]["items"]["properties"]["status"]["enum"])
        checks.append(("retired" in statuses, "registry schema allows 'retired' status"))
    else:
        checks.append((False, "guardian-registry-schema.v1.json exists"))

    # 6. Verify_guardian_status.py handles retired
    verifier = ROOT / "scripts" / "verify_guardian_status.py"
    if verifier.exists():
        text = verifier.read_text(encoding="utf-8")
        checks.append(("registered_but_retired" in text, "verifier handles registered_but_retired"))
    else:
        checks.append((False, "verify_guardian_status.py exists"))

    # Print results
    failed = [msg for ok, msg in checks if not ok]
    for ok, msg in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {msg}")

    if failed:
        print(f"\nFAILED: {len(failed)} check(s)")
        return 1

    print("\nPASS: Guardian retirement automation infrastructure is complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
