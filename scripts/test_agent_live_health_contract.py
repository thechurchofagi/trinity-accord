#!/usr/bin/env python3
"""Agent live-health snapshot must expose stable endpoints and observability pointers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "agent-live-health.v1.json"

REQUIRED_ENDPOINTS = ["site", "gateway", "preflight", "submit"]
REQUIRED_HEALTH_INPUTS = [
    "links",
    "well_known",
    "first_contact",
    "formal_builder_bundles",
    "external_agent_examples",
]

def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    endpoints = data.get("stable_endpoints", {})
    for key in REQUIRED_ENDPOINTS:
        if key not in endpoints:
            errors.append(f"stable_endpoints missing {key}")

    if endpoints.get("preflight", "").endswith("/gateway/preflight") is not True:
        errors.append("preflight endpoint must end with /gateway/preflight")
    if endpoints.get("submit", "").endswith("/agent-submit") is not True:
        errors.append("submit endpoint must end with /agent-submit")
    if "/gateway/submit" in json.dumps(data, sort_keys=True):
        errors.append("live-health must not contain stale /gateway/submit")

    inputs = data.get("health_inputs", {})
    for key in REQUIRED_HEALTH_INPUTS:
        if key not in inputs:
            errors.append(f"health_inputs missing {key}")

    if not data.get("source_digest"):
        errors.append("source_digest required")

    if errors:
        print("FAIL: agent live-health contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: agent live-health contract is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
