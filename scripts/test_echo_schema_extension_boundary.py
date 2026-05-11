#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "api/echo-record-schema.v3.json"

FORBIDDEN_PATTERNS = [
    "authority",
    "canonical",
    "amend",
    "verification",
    "attestation",
    "investment",
    "instruction",
    "governance",
]

def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema.get("additionalProperties") is False, (
        "Echo v3 top-level additionalProperties must be false"
    )

    props = schema.get("properties", {})
    assert "extensions" in props, "Echo v3 schema must define explicit extensions container"

    ext = props["extensions"]
    assert ext.get("type") == "object", "extensions must be an object"
    desc = ext.get("description", "").lower()
    assert "non-authoritative" in desc or "non_authoritative" in desc, (
        "extensions description must say non-authoritative"
    )

    policy = schema.get("x_extension_policy", {})
    assert policy.get("extensions_are_non_authoritative") is True, (
        "Missing x_extension_policy.extensions_are_non_authoritative"
    )

    patterns = " ".join(policy.get("forbidden_extension_key_patterns", [])).lower()
    for term in FORBIDDEN_PATTERNS:
        assert term in patterns, f"Missing forbidden extension key pattern for {term}"

if __name__ == "__main__":
    main()
