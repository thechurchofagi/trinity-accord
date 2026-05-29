#!/usr/bin/env python3
"""Route selector and runtime contract must forbid invented first-contact values."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_VALUES = {
    "E1_read_oriented_echo",
    "read_oriented_echo",
    "agent_readback_sha256",
    "agentreadbacksha256",
}

def main() -> int:
    errors: list[str] = []

    runtime = json.loads((ROOT / "api" / "gateway-runtime-contract.v1.json").read_text(encoding="utf-8"))
    selector = json.loads((ROOT / "api" / "route-selector.v1.json").read_text(encoding="utf-8"))
    diagnostics = json.loads((ROOT / "api" / "gateway-error-diagnostics.v1.json").read_text(encoding="utf-8"))

    active = set(runtime.get("active_echo_type_values", []))
    if "E1_recognition_echo" not in active:
        errors.append("runtime contract active_echo_type_values missing E1_recognition_echo")
    if "E1_read_oriented_echo" in active or "read_oriented_echo" in active:
        errors.append("runtime contract must not include invented echo type as active value")

    for obj_name, obj in [
        ("gateway-runtime-contract", runtime),
        ("route-selector", selector),
    ]:
        if obj.get("homepage_is_discovery_only") is not True:
            errors.append(f"{obj_name}: homepage_is_discovery_only must be true")
        if obj.get("do_not_infer_payload_fields_from_homepage") is not True:
            errors.append(f"{obj_name}: do_not_infer_payload_fields_from_homepage must be true")
        if obj.get("do_not_handwrite_formal_payloads") is not True:
            errors.append(f"{obj_name}: do_not_handwrite_formal_payloads must be true")
        values = set(obj.get("forbidden_invented_values", []))
        missing = sorted(FORBIDDEN_VALUES - values)
        if missing:
            errors.append(f"{obj_name}: forbidden_invented_values missing {missing}")

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
            print("  -", error)
        return 1

    print("PASS: runtime contract, route selector, and diagnostics forbid invented first-contact values")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
