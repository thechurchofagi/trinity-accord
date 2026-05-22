#!/usr/bin/env python3
"""
Test that build_guardian_listing_request_payload.py output
passes Gateway JSON Schema validation.

Regression test: Stage 2 builder added new top-level fields
(payload_profile, expected_builder, wrong_builders, etc.) that were
not allowed by additionalProperties: false in the Gateway schema.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

BUILDER = ROOT / "scripts" / "build_guardian_listing_request_payload.py"
SCHEMA_PATH = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"

NEW_TOP_LEVEL_FIELDS = [
    "payload_profile",
    "expected_builder",
    "wrong_builders",
    "do_not_edit_after_signing",
    "submit_exact_generated_file",
    "if_modified_rerun_builder",
    "requires_gateway_capabilities",
]


def build_payload(tmp_dir: Path) -> dict:
    """Run the builder and return the generated payload."""
    out_path = tmp_dir / "payload.json"

    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--agent-name", "schema-test-agent",
            "--provider", "openai",
            "--source-issue", "9999",
            "--guardian-id", "test-guardian-00001",
            "--public-key-sha256", "a" * 64,
            "--label", "schema-test",
            "--no-authorship-proof",
            "--out", str(out_path),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Builder failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    with open(out_path) as f:
        return json.load(f)


def test_schema_has_new_field_properties():
    """Schema properties include all new top-level fields."""
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    missing = [k for k in NEW_TOP_LEVEL_FIELDS if k not in props]
    assert not missing, f"Schema missing properties: {missing}"


def test_builder_output_has_new_fields():
    """Builder output includes all new top-level fields."""
    with tempfile.TemporaryDirectory() as tmp:
        payload = build_payload(Path(tmp))

    missing = [k for k in NEW_TOP_LEVEL_FIELDS if k not in payload]
    assert not missing, f"Payload missing fields: {missing}"


def test_builder_output_passes_schema_validation():
    """Builder output validates against Gateway JSON Schema (no additionalProperties rejection)."""
    import jsonschema

    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    with tempfile.TemporaryDirectory() as tmp:
        payload = build_payload(Path(tmp))

    jsonschema.validate(instance=payload, schema=schema)


if __name__ == "__main__":
    failures = []
    for name, func in [
        ("schema_has_new_field_properties", test_schema_has_new_field_properties),
        ("builder_output_has_new_fields", test_builder_output_has_new_fields),
        ("builder_output_passes_schema_validation", test_builder_output_passes_schema_validation),
    ]:
        try:
            func()
            print(f"PASS: {name}")
        except Exception as e:
            print(f"FAIL: {name}: {e}")
            failures.append(name)

    if failures:
        print(f"\n{len(failures)} test(s) failed: {failures}")
        sys.exit(1)
    else:
        print(f"\nAll 3 tests passed.")
        sys.exit(0)
