#!/usr/bin/env python3
"""Runtime contract and route selector must forbid invented first-contact values.

Since round 7/10, route-selector.v1.json is retired. When it is a retired pointer,
this test skips active-field checks on route-selector and only validates the
gateway-runtime-contract and gateway-error-diagnostics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_VALUES = {
    "E1_read_oriented_echo",
    "read_oriented_echo",
    "agentreadbacksha256",
    "agent_readback_hash",
    "readback_sha256",
    "readback_hash_sha256",
    "agent_readback_digest",
}


def is_retired_pointer(data: dict) -> bool:
    """Check if route-selector is a retired pointer, not an active route selector."""
    return data.get("schema") == "trinityaccord.gateway-v1-retired-pointer.v1"


def main() -> int:
    errors: list[str] = []

    # gateway-runtime-contract is always required
    runtime_path = ROOT / "api" / "gateway-runtime-contract.v1.json"
    if not runtime_path.exists():
        print("FAIL: api/gateway-runtime-contract.v1.json missing")
        return 1
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

    # gateway-error-diagnostics is always required
    diag_path = ROOT / "api" / "gateway-error-diagnostics.v1.json"
    if not diag_path.exists():
        print("FAIL: api/gateway-error-diagnostics.v1.json missing")
        return 1
    diagnostics = json.loads(diag_path.read_text(encoding="utf-8"))

    # route-selector may be retired
    selector_path = ROOT / "api" / "route-selector.v1.json"
    if not selector_path.exists():
        print("FAIL: api/route-selector.v1.json missing")
        return 1
    selector = json.loads(selector_path.read_text(encoding="utf-8"))
    selector_retired = is_retired_pointer(selector)

    # Check active echo type values in runtime contract (always applies)
    active = set(runtime.get("active_echo_type_values", []))
    if "E1_read_oriented_echo" in active or "read_oriented_echo" in active:
        errors.append("runtime contract must not include invented echo type as active value")

    # Check runtime contract fields (always applies)
    if runtime.get("homepage_is_discovery_only") is not True:
        errors.append("gateway-runtime-contract: homepage_is_discovery_only must be true")
    if runtime.get("do_not_infer_payload_fields_from_homepage") is not True:
        errors.append("gateway-runtime-contract: do_not_infer_payload_fields_from_homepage must be true")
    if runtime.get("do_not_handwrite_formal_payloads") is not True:
        errors.append("gateway-runtime-contract: do_not_handwrite_formal_payloads must be true")
    runtime_forbidden = set(runtime.get("forbidden_invented_values", []))
    missing = sorted(FORBIDDEN_VALUES - runtime_forbidden)
    if missing:
        errors.append(f"gateway-runtime-contract: forbidden_invented_values missing {missing}")

    # Check readback_hash_field_policy in runtime contract
    policy = runtime.get("readback_hash_field_policy", {})
    if policy.get("builder_generated_field") != "agent_readback_sha256":
        errors.append("gateway-runtime-contract: readback_hash_field_policy.builder_generated_field must be agent_readback_sha256")

    # route-selector checks: only if NOT retired
    if not selector_retired:
        # Active route selector — full checks
        if selector.get("homepage_is_discovery_only") is not True:
            errors.append("route-selector: homepage_is_discovery_only must be true")
        if selector.get("do_not_infer_payload_fields_from_homepage") is not True:
            errors.append("route-selector: do_not_infer_payload_fields_from_homepage must be true")
        if selector.get("do_not_handwrite_formal_payloads") is not True:
            errors.append("route-selector: do_not_handwrite_formal_payloads must be true")
        sel_forbidden = set(selector.get("forbidden_invented_values", []))
        missing_sel = sorted(FORBIDDEN_VALUES - sel_forbidden)
        if missing_sel:
            errors.append(f"route-selector: forbidden_invented_values missing {missing_sel}")
        sel_policy = selector.get("readback_hash_field_policy", {})
        if sel_policy.get("builder_generated_field") != "agent_readback_sha256":
            errors.append("route-selector: readback_hash_field_policy.builder_generated_field must be agent_readback_sha256")
    else:
        # Retired pointer — verify it does NOT contain active payload fields
        active_fields = ["routes", "default_entry", "forbidden_invented_values",
                         "homepage_is_discovery_only", "do_not_infer_payload_fields_from_homepage"]
        for field in active_fields:
            if field in selector:
                errors.append(f"retired route-selector must not contain active field: {field}")

    # gateway-error-diagnostics checks (always applies)
    diag_text = json.dumps(diagnostics, ensure_ascii=False)
    for code in ["INVENTED_ECHO_TYPE_FROM_FIRST_CONTACT", "INVENTED_READBACK_HASH_FIELD"]:
        if code not in diag_text:
            errors.append(f"gateway-error-diagnostics missing {code}")

    for value in FORBIDDEN_VALUES:
        if value not in diag_text:
            errors.append(f"gateway-error-diagnostics missing invented value {value}")

    if errors:
        print("FAIL: runtime/route selector invented value guard errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if selector_retired:
        print("PASS: runtime contract forbids invented values; route-selector is retired pointer (skipped active checks)")
    else:
        print("PASS: runtime contract, route selector, and diagnostics forbid invented first-contact values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
