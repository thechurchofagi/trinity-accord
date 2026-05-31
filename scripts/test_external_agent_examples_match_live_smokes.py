#!/usr/bin/env python3
"""External-agent operation examples must reference live smokes and tested defaults."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "external-agent-operation-examples.v1.json"

REQUIRED_TOP_LEVEL = {
    "pure_echo_minimal_recognition": {
        "route": "pure_echo",
        "authorship_proof_default": True,
    },
    "v0_agent_declared_verification_minimal": {
        "route": "v0_v5_agent_declared_archive",
        "declared_level": "V0",
        "authorship_proof_default": True,
    },
    "guardian_stage_1_minimal_application": {
        "route": "guardian_application_stage_1",
        "active_guardian_status_created": False,
        "registry_number_created": False,
    },
}

def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    for key, expected in REQUIRED_TOP_LEVEL.items():
        obj = data.get(key)
        if not isinstance(obj, dict):
            errors.append(f"missing top-level example: {key}")
            continue

        for field, value in expected.items():
            if obj.get(field) != value:
                errors.append(f"{key}.{field} expected {value!r}, got {obj.get(field)!r}")

        if obj.get("copy_paste_doc") != "/external-agent-copy-paste-examples/":
            errors.append(f"{key}.copy_paste_doc must be /external-agent-copy-paste-examples/")

        if obj.get("must_pass_live_preflight_smoke") != "scripts/smoke_live_external_agent_three_core_preflight.py":
            errors.append(f"{key} missing live preflight smoke reference")

    text = PATH.read_text(encoding="utf-8")
    if "--declared-level V2" in text:
        errors.append("operation examples must not use V2 as default minimal V0–V5 example")
    if "--agent-readback-file" in text:
        errors.append("operation examples must not use --agent-readback-file as primary path")

    if errors:
        print("FAIL: external-agent operation examples drift:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external-agent operation examples match live-smoked defaults")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
