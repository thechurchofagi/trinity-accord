#!/usr/bin/env python3
"""Route selector must be a retired pointer to record-chain-first replacement.

Since round 7/10, route-selector.v1.json is retired. This test verifies
the retired pointer is correct and does NOT require an active route selector.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "route-selector.v1.json"

RETIRED_SCHEMA = "trinityaccord.gateway-v1-retired-pointer.v1"
EXPECTED_REPLACEMENT = "/api/record-chain-status.json"


def main() -> int:
    errors: list[str] = []

    if not PATH.exists():
        print("FAIL: api/route-selector.v1.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))

    # Must be a retired pointer, not an active route selector
    if data.get("schema") != RETIRED_SCHEMA:
        errors.append(f"schema must be {RETIRED_SCHEMA}, got {data.get('schema')}")

    if data.get("status") != "historical_archive_only":
        errors.append(f"status must be historical_archive_only, got {data.get('status')}")

    if data.get("not_active_runtime") is not True:
        errors.append("not_active_runtime must be true")

    if data.get("not_primary_path") is not True:
        errors.append("not_primary_path must be true")

    replacement = data.get("replacement", "")
    if replacement != EXPECTED_REPLACEMENT:
        errors.append(f"replacement must be {EXPECTED_REPLACEMENT}, got {replacement}")

    # Verify the replacement target exists
    replacement_path = ROOT / replacement.lstrip("/")
    if not replacement_path.exists():
        errors.append(f"replacement target does not exist: {replacement}")

    # Verify boundary fields exist
    boundary = data.get("boundary", {})
    if not boundary.get("not_authority"):
        errors.append("boundary.not_authority must be true")
    if not boundary.get("bitcoin_originals_prevail"):
        errors.append("boundary.bitcoin_originals_prevail must be true")

    # Must NOT contain active route-selector fields
    active_fields = ["routes", "default_entry", "forbidden_invented_values",
                     "homepage_is_discovery_only", "do_not_infer_payload_fields_from_homepage"]
    for field in active_fields:
        if field in data:
            errors.append(f"retired pointer must not contain active field: {field}")

    if errors:
        print("FAIL: route selector contract errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: route selector is correctly retired to record-chain-first replacement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
