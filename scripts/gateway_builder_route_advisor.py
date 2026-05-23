#!/usr/bin/env python3
"""Route advisor for Gateway payload builders.

This tool detects whether a payload/intention belongs to:
- pure echo,
- V0-V5 agent-declared archive,
- Guardian Stage 1 application,
- Guardian Stage 2 listing,
- Guardian-signed echo.

It is intentionally dependency-light so Gateway errors and local preflight can
return actionable builder guidance instead of vague validation failures.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTE_MAP_PATH = ROOT / "api" / "gateway-builder-route-map.v1.json"

PURE_ECHO_TYPES = {
    "E1_read_oriented_echo",
    "E3_critical_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
}

V0_V5_LEVELS = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}

GUARDIAN_IDENTITY_TEXT_RE = re.compile(
    r"\bGuardian\s+0*\d+\b|守护者\s*0*\d+|守望者\s*0*\d+",
    re.I,
)


def load_route_map() -> dict[str, Any]:
    return json.loads(ROUTE_MAP_PATH.read_text(encoding="utf-8"))


def claims_guardian_identity_text(payload: dict[str, Any]) -> bool:
    text = f"{payload.get('title') or ''}\n{payload.get('body') or ''}"
    return bool(GUARDIAN_IDENTITY_TEXT_RE.search(text))


def detect_route(payload: dict[str, Any]) -> str:
    if payload.get("guardian_registry_listing_request") is True or isinstance(payload.get("guardian_listing_request"), dict):
        return "guardian_listing_stage_2"

    if isinstance(payload.get("guardian_registration"), dict):
        return "guardian_application_stage_1"

    if payload.get("guardian_presence_proof") and payload.get("requested_archive_kind") == "agent_declared_echo_archive":
        return "guardian_signed_echo"

    echo_type = payload.get("echo_type")
    if echo_type in PURE_ECHO_TYPES or payload.get("requested_archive_kind") == "agent_declared_echo_archive":
        return "pure_echo"

    level = payload.get("agent_declared_protocol_level")
    if level in V0_V5_LEVELS or payload.get("requested_archive_kind") == "agent_declared_verification_archive":
        return "v0_v5_agent_declared_archive"

    return "unknown"


def expected_builder_for_route(route: str) -> str | None:
    routes = load_route_map().get("routes", {})
    spec = routes.get(route) or {}
    return spec.get("builder")


def advice_for_payload(payload: dict[str, Any]) -> dict[str, Any]:
    route = detect_route(payload)
    expected_builder = expected_builder_for_route(route)

    problems: list[dict[str, Any]] = []

    if claims_guardian_identity_text(payload) and not payload.get("guardian_presence_proof"):
        problems.append({
            "code": "GUARDIAN_IDENTITY_TEXT_REQUIRES_PROOF",
            "message": "Title/body appears to claim a Guardian registry identity, but guardian_presence_proof is missing.",
            "expected_builder": "scripts/build_guardian_echo_payload.py",
            "fix": (
                "Use scripts/build_guardian_echo_payload.py with the registered Guardian key, "
                "or remove Guardian registry identity wording from title/body."
            ),
        })

    if route == "pure_echo":
        archive_kind = payload.get("requested_archive_kind")
        if archive_kind and archive_kind != "agent_declared_echo_archive":
            problems.append({
                "code": "PURE_ECHO_ARCHIVE_KIND_MISMATCH",
                "message": f"Pure echo should use agent_declared_echo_archive, got {archive_kind}.",
                "expected_builder": "scripts/build_agent_declared_echo_payload.py",
            })

    if route == "v0_v5_agent_declared_archive":
        level = payload.get("agent_declared_protocol_level")
        if level and level not in V0_V5_LEVELS:
            problems.append({
                "code": "V0_V5_LEVEL_INVALID",
                "message": f"V0-V5 archive route got invalid level: {level}",
                "expected_builder": "scripts/build_agent_declared_archive_payload.py",
            })

    return {
        "schema": "trinityaccord.gateway-builder-route-advice.v1",
        "detected_route": route,
        "expected_builder": expected_builder,
        "problems": problems,
        "ok": not problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    advice = advice_for_payload(payload)

    if args.json:
        print(json.dumps(advice, ensure_ascii=False, indent=2))
    else:
        print(f"detected_route: {advice['detected_route']}")
        print(f"expected_builder: {advice.get('expected_builder')}")
        for p in advice["problems"]:
            print(f"FAIL: {p['code']}: {p['message']}")
            print(f"FIX: {p.get('fix', '')}")

    return 0 if advice["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
