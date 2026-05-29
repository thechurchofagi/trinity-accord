#!/usr/bin/env python3
"""Gateway runtime contract must define runtime drift metadata."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "gateway-runtime-contract.v1.json"

ACTIVE_ECHO_TYPES = {
    "E1_recognition_echo",
    "E2_verification_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
    "E8_witness_echo",
    "E9_seed_echo",
}

REQUIRED_ROUTES = {
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
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
        print("FAIL: api/gateway-runtime-contract.v1.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))

    if data.get("schema") != "trinityaccord.gateway-runtime-contract.v1":
        errors.append("schema mismatch")

    if data.get("preflight_endpoint") != "https://trinity-agent-issue-gateway.onrender.com/gateway/preflight":
        errors.append("preflight_endpoint mismatch")
    if data.get("submit_endpoint") != "https://trinity-agent-issue-gateway.onrender.com/agent-submit":
        errors.append("submit_endpoint mismatch")

    for field in ["accepted", "preflight", "route_detected", "gateway_runtime", "gateway_schema", "diagnostics"]:
        if field not in data.get("required_preflight_response_fields", []):
            errors.append(f"required_preflight_response_fields missing {field}")

    for field in ["runtime_version", "schema_digest", "echo_type_enum_digest", "supported_routes_digest"]:
        if field not in data.get("gateway_runtime_required_fields", []):
            errors.append(f"gateway_runtime_required_fields missing {field}")

    enum_values = set(data.get("active_echo_type_values", []))
    if enum_values != ACTIVE_ECHO_TYPES:
        errors.append(f"active_echo_type_values mismatch: {sorted(enum_values)}")

    routes = set(data.get("required_supported_routes", []))
    missing_routes = sorted(REQUIRED_ROUTES - routes)
    if missing_routes:
        errors.append(f"required_supported_routes missing {missing_routes}")

    if data.get("short_ids_are_aliases_not_active_payload_values") is not True:
        errors.append("short_ids_are_aliases_not_active_payload_values must be true")

    expected = digest(data)
    if data.get("source_digest") != expected:
        errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")

    if errors:
        print("FAIL: gateway runtime contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: gateway runtime contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
