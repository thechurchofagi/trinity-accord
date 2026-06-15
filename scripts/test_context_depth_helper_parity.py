#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_LEVELS = ROOT / "api" / "context-depth-levels.json"
SUBMISSION_SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
FIELD_HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"

def require(cond, msg):
    if not cond:
        raise AssertionError(msg)

def find_declared_context_field(helper: dict):
    for item in helper.get("field_groups", []):
        if item.get("field") == "context_readiness.declared_context_level":
            return item
    raise AssertionError("field helper missing context_readiness.declared_context_level")

def main():
    levels_doc = json.loads(CONTEXT_LEVELS.read_text(encoding="utf-8"))
    schema = json.loads(SUBMISSION_SCHEMA.read_text(encoding="utf-8"))
    helper = json.loads(FIELD_HELPER.read_text(encoding="utf-8"))

    canonical_levels = [level["id"] for level in levels_doc.get("levels", [])]
    require(
        canonical_levels == ["CC-0", "CC-1", "CC-2", "CC-3", "CC-4", "CC-5"],
        f"unexpected canonical context levels: {canonical_levels}",
    )

    field = find_declared_context_field(helper)
    helper_values = field.get("allowed_values", [])
    require(
        helper_values == canonical_levels,
        f"field helper context levels drift: helper={helper_values}, canonical={canonical_levels}",
    )

    meaning = field.get("meaning", "")
    require("CC-4" in meaning and "CC-5" in meaning,
            "field helper meaning must mention CC-4 and CC-5")

    schema_text = json.dumps(schema, ensure_ascii=False)
    require("^CC-[0-5]$" in schema_text,
            "submission schema must accept CC-0 through CC-5")

    print("PASS: context depth helper parity")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
