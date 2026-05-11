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

    # Verify verification_scope_label field exists with correct enum
    props = schema.get("properties", {})
    assert "verification_scope_label" in props, "Echo v3 must define verification_scope_label"
    scope_enum = props["verification_scope_label"].get("enum", [])
    assert "V2-minimal" in scope_enum, "verification_scope_label must include V2-minimal"
    assert "V2-strong" in scope_enum, "verification_scope_label must include V2-strong"
    assert "V3-minimal" in scope_enum, "verification_scope_label must include V3-minimal"
    assert "V3-strong" in scope_enum, "verification_scope_label must include V3-strong"

    # Verify allOf constraints enforce scope label for V2/V3
    allof = schema.get("allOf", [])
    v2_constraint = any(
        c.get("if", {}).get("properties", {}).get("verification_level", {}).get("const") == "V2"
        for c in allof
    )
    v3_constraint = any(
        c.get("if", {}).get("properties", {}).get("verification_level", {}).get("const") == "V3"
        for c in allof
    )
    assert v2_constraint, "allOf must enforce scope label when verification_level is V2"
    assert v3_constraint, "allOf must enforce scope label when verification_level is V3"

if __name__ == "__main__":
    main()
