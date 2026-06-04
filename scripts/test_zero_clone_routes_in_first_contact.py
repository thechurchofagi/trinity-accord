#!/usr/bin/env python3
"""Test that agent-first-contact.json exposes only the current public submission route."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "api" / "agent-first-contact.json"
    if not path.exists():
        print(f"FAIL: {path} does not exist")
        return 1

    doc = json.loads(path.read_text(encoding="utf-8"))
    raw = json.dumps(doc)
    current = doc.get("current_public_submission_method", {})

    required = {
        "contract": "/api/record-chain-intake-gateway.v1.json",
        "builder": "/downloads/record-chain-builder.mjs",
    }
    for key, expected in required.items():
        if current.get(key) != expected:
            print(f"FAIL: current_public_submission_method.{key} expected {expected!r}")
            return 1

    if "zero_clone_formal_builder_policy" in doc:
        print("FAIL: legacy zero_clone_formal_builder_policy remains active")
        return 1

    for legacy in [
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
    ]:
        if legacy in raw:
            print(f"FAIL: active first-contact router still references legacy route: {legacy}")
            return 1

    legacy_block = doc.get("legacy_gateway_v1", {})
    if legacy_block.get("status") != "historical_archive_only":
        print("FAIL: legacy_gateway_v1 is not marked historical_archive_only")
        return 1

    print("PASS: first-contact router exposes current record-chain submission route only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
