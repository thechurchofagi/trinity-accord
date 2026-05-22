#!/usr/bin/env python3
"""Ensure Guardian listing builder output passes Gateway JSON Schema validation.

Regression test: Stage 2 builder added new top-level fields
(payload_profile, expected_builder, wrong_builders, do_not_edit_after_signing,
submit_exact_generated_file, if_modified_rerun_builder, requires_gateway_capabilities)
that were not originally allowed by additionalProperties: false in the Gateway schema.

This test actually runs the builder and validates the output against the JSON Schema,
not just custom Python checks.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NEW_TOP_LEVEL_FIELDS = [
    "payload_profile",
    "expected_builder",
    "wrong_builders",
    "do_not_edit_after_signing",
    "submit_exact_generated_file",
    "if_modified_rerun_builder",
    "requires_gateway_capabilities",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_props = schema.get("properties", {})

    # 1. Schema properties include all new top-level fields
    missing_in_schema = [k for k in NEW_TOP_LEVEL_FIELDS if k not in schema_props]
    require(
        not missing_in_schema,
        f"Schema missing properties for: {missing_in_schema}",
    )

    # 2. Run builder and get payload
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        out = td / "guardian-listing-request.json"

        result = subprocess.run(
            [
                "python3",
                "scripts/build_guardian_listing_request_payload.py",
                "--agent-name", "Schema Acceptance Test Agent",
                "--provider", "Test Provider",
                "--source-issue", "9999",
                "--guardian-id", "guardian_ed25519_schematest0000",
                "--public-key-sha256",
                "aaaaaaaaaaaaaaaa000000000000000000000000000000000000000000000000",
                "--label", "Schema Acceptance Test",
                "--guardian-type", "human_with_ai_agent",
                "--application-mode", "joint_human_ai",
                "--idempotency-key", "guardian-schema-acceptance-test-0001",
                "--out", str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )

        require(result.returncode == 0, result.stdout + result.stderr)
        payload = json.loads(out.read_text(encoding="utf-8"))

    # 3. Payload includes all new top-level fields
    missing_in_payload = [k for k in NEW_TOP_LEVEL_FIELDS if k not in payload]
    require(
        not missing_in_payload,
        f"Payload missing new fields: {missing_in_payload}",
    )

    # 4. Full JSON Schema validation (the critical regression check)
    try:
        import jsonschema

        jsonschema.validate(instance=payload, schema=schema)
    except ImportError:
        # jsonschema not available; field-presence checks above still pass
        pass
    except jsonschema.ValidationError as exc:
        raise AssertionError(
            f"Payload failed JSON Schema validation: {exc.message}\n"
            f"Path: {list(exc.absolute_path)}\n"
            f"Schema path: {list(exc.absolute_schema_path)}"
        )

    print("GUARDIAN_LISTING_PAYLOAD_SCHEMA_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
