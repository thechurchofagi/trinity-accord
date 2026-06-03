#!/usr/bin/env python3
"""Runtime contract, route selector, and error diagnostics must forbid invented values.

Since Gateway v1 retirement, all three files may be retired pointers.
When retired, this test verifies the pointer is correct and does NOT contain
active payload fields. Active field checks only apply to non-retired files.
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

RETIRED_SCHEMA = "trinityaccord.gateway-v1-retired-pointer.v1"


def is_retired(data: dict) -> bool:
    return data.get("schema") == RETIRED_SCHEMA


def validate_retired_pointer(name: str, data: dict, errors: list[str]) -> None:
    """Validate a retired pointer has correct structure and no active fields."""
    if data.get("status") != "historical_archive_only":
        errors.append(f"{name}: status must be historical_archive_only")
    if data.get("not_active_runtime") is not True:
        errors.append(f"{name}: not_active_runtime must be true")
    if data.get("replacement") != "/api/record-chain-status.json":
        errors.append(f"{name}: replacement must point to /api/record-chain-status.json")
    # Must NOT contain active fields
    active_fields = [
        "active_echo_type_values", "forbidden_invented_values",
        "homepage_is_discovery_only", "do_not_infer_payload_fields_from_homepage",
        "do_not_handwrite_formal_payloads", "readback_hash_field_policy",
        "error_codes", "invented_value_diagnostics",
    ]
    for field in active_fields:
        if field in data:
            errors.append(f"{name}: retired pointer must not contain active field: {field}")


def main() -> int:
    errors: list[str] = []

    # Load all three files
    files = {}
    for name, path in [
        ("gateway-runtime-contract", "api/gateway-runtime-contract.v1.json"),
        ("route-selector", "api/route-selector.v1.json"),
        ("gateway-error-diagnostics", "api/gateway-error-diagnostics.v1.json"),
    ]:
        p = ROOT / path
        if not p.exists():
            print(f"FAIL: {path} missing")
            return 1
        files[name] = json.loads(p.read_text(encoding="utf-8"))

    all_retired = all(is_retired(v) for v in files.values())

    if all_retired:
        # All three are retired pointers - validate each
        for name, data in files.items():
            validate_retired_pointer(name, data, errors)
    else:
        # Some files are active - run full checks on active ones
        runtime = files["gateway-runtime-contract"]
        selector = files["route-selector"]
        diagnostics = files["gateway-error-diagnostics"]

        if not is_retired(runtime):
            active = set(runtime.get("active_echo_type_values", []))
            if "E1_read_oriented_echo" in active or "read_oriented_echo" in active:
                errors.append("runtime contract must not include invented echo type as active value")
            if runtime.get("homepage_is_discovery_only") is not True:
                errors.append("gateway-runtime-contract: homepage_is_discovery_only must be true")
            if runtime.get("do_not_infer_payload_fields_from_homepage") is not True:
                errors.append("gateway-runtime-contract: do_not_infer_payload_fields_from_homepage must be true")
            if runtime.get("do_not_handwrite_formal_payloads") is not True:
                errors.append("gateway-runtime-contract: do_not_handwrite_formal_payloads must be true")
            rt_forbidden = set(runtime.get("forbidden_invented_values", []))
            missing = sorted(FORBIDDEN_VALUES - rt_forbidden)
            if missing:
                errors.append(f"gateway-runtime-contract: forbidden_invented_values missing {missing}")
            policy = runtime.get("readback_hash_field_policy", {})
            if policy.get("builder_generated_field") != "agent_readback_sha256":
                errors.append("gateway-runtime-contract: readback_hash_field_policy must be agent_readback_sha256")
        else:
            validate_retired_pointer("gateway-runtime-contract", runtime, errors)

        if not is_retired(selector):
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
                errors.append("route-selector: readback_hash_field_policy must be agent_readback_sha256")
        else:
            validate_retired_pointer("route-selector", selector, errors)

        if not is_retired(diagnostics):
            diag_text = json.dumps(diagnostics, ensure_ascii=False)
            for code in ["INVENTED_ECHO_TYPE_FROM_FIRST_CONTACT", "INVENTED_READBACK_HASH_FIELD"]:
                if code not in diag_text:
                    errors.append(f"gateway-error-diagnostics missing {code}")
            for value in FORBIDDEN_VALUES:
                if value not in diag_text:
                    errors.append(f"gateway-error-diagnostics missing invented value {value}")
        else:
            validate_retired_pointer("gateway-error-diagnostics", diagnostics, errors)

    if errors:
        print("FAIL: runtime/route selector invented value guard errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if all_retired:
        print("PASS: all three Gateway v1 artifacts are correctly retired pointers (no active fields present)")
    else:
        print("PASS: runtime contract, route selector, and diagnostics forbid invented first-contact values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
