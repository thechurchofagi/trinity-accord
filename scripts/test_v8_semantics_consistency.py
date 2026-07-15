#!/usr/bin/env python3
"""Enforce the current multidimensional model and V8's historical-only status."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"V8_SEMANTICS_CONSISTENCY_FAIL: {message}")


def main() -> int:
    model = load("api/verification-claim-model.v1.json")
    profiles = load("api/protocol-verification-profiles.json")

    current_ids = {item.get("id") for item in profiles.get("profiles", [])}
    require("V8" not in current_ids, "V8 must not be a current verification profile")
    require(
        current_ids == {
            "context_only",
            "reference_checked",
            "integrity_checked",
            "independent_reproduction",
            "full_public_digital",
        },
        "current protocol profiles must use multidimensional digital-profile IDs",
    )

    compatibility = model.get("legacy_v_compatibility", {})
    require("V8" in compatibility.get("new_submission_forbidden_values", []), "new submissions must forbid V8")
    require("V8" in compatibility.get("retired_mapping", {}), "historical V8 mapping must remain explicit")
    require(
        "Historical V4+/V6/V7/V8" in compatibility.get("boundary", ""),
        "historical-only boundary must name V8",
    )
    require(
        "V8 is the highest current verification level." in model.get("prohibited_claims", []),
        "current policy must prohibit presenting V8 as the highest current level",
    )

    print("V8_SEMANTICS_CONSISTENCY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
