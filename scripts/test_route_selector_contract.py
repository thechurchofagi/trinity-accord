#!/usr/bin/env python3
"""Route selector must point agents to correct core and advanced routes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "route-selector.v1.json"

CORE_ROUTES = {
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
}

ADVANCED_ROUTES = {
    "guardian_listing_stage_2",
    "guardian_signed_echo",
}


def digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    errors: list[str] = []

    if not PATH.exists():
        print("FAIL: api/route-selector.v1.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))

    if data.get("schema") != "trinityaccord.route-selector.v1":
        errors.append("schema mismatch")

    if data.get("default_entry") != "/external-agent-copy-paste-examples/":
        errors.append("default_entry must be /external-agent-copy-paste-examples/")

    routes = data.get("routes", [])
    route_names = {item.get("recommended_route") for item in routes}

    for route in CORE_ROUTES:
        if route not in route_names:
            errors.append(f"missing core route: {route}")

    for route in ADVANCED_ROUTES:
        if route not in route_names:
            errors.append(f"missing advanced route: {route}")

    for item in routes:
        route = item.get("recommended_route")
        if not item.get("intent"):
            errors.append(f"{route}: missing intent")
        if not item.get("copy_paste_doc"):
            errors.append(f"{route}: missing copy_paste_doc")
        if not item.get("must_not_claim"):
            errors.append(f"{route}: missing must_not_claim")
        if route in CORE_ROUTES and item.get("live_smoke") != "scripts/smoke_live_external_agent_three_core_preflight.py":
            errors.append(f"{route}: core route must reference core live smoke")
        if route in ADVANCED_ROUTES and "advanced_route_smoke_required" not in item.get("live_smoke", ""):
            errors.append(f"{route}: advanced route must not pretend to be core live-smoked")

    text = json.dumps(data, ensure_ascii=False)
    for phrase in ["E1_recognition_echo", "V0", "active Guardian status", "guardian_presence_proof"]:
        if phrase not in text:
            errors.append(f"route selector missing phrase: {phrase}")

    expected = digest(data)
    if data.get("source_digest") != expected:
        errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")

    if errors:
        print("FAIL: route selector contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: route selector contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
