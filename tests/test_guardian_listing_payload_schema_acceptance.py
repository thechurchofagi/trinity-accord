#!/usr/bin/env python3
"""
Test that build_guardian_listing_request_payload.py output
passes Gateway JSON Schema validation.

This is a regression test for the schema compatibility issue where
Stage 2 builder added new top-level fields that were not allowed by
additionalProperties: false in the Gateway schema.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

def test_guardian_listing_payload_schema_acceptance():
    """Test that guardian listing payload passes schema validation."""
    
    # Build payload using the actual builder
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        payload_path = f.name
    
    try:
        # Run builder
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_guardian_listing_request_payload.py"),
                "--output", payload_path,
                "--title", "Test Guardian Listing",
                "--body", "Test body for schema validation",
                "--agent-name", "test-agent",
                "--agent-email", "test@example.com",
            ],
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            print(f"FAIL: Builder failed with:\n{result.stderr}")
            return False
        
        # Load built payload
        with open(payload_path) as f:
            payload = json.load(f)
        
        # Load schema
        schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Check that new top-level fields are allowed by schema
        new_fields = [
            "payload_profile",
            "expected_builder", 
            "wrong_builders",
            "do_not_edit_after_signing",
            "submit_exact_generated_file",
            "if_modified_rerun_builder",
            "requires_gateway_capabilities",
        ]
        
        schema_properties = schema.get("properties", {})
        missing_fields = [f for f in new_fields if f not in schema_properties]
        
        if missing_fields:
            print(f"FAIL: Schema missing properties for fields: {missing_fields}")
            return False
        
        # Check that payload contains expected fields
        for field in new_fields:
            if field not in payload:
                print(f"FAIL: Payload missing expected field: {field}")
                return False
        
        # Validate payload against schema using jsonschema
        try:
            import jsonschema
            jsonschema.validate(instance=payload, schema=schema)
            print("PASS: Payload validates against Gateway JSON Schema")
            return True
        except ImportError:
            print("WARN: jsonschema not installed, skipping full validation")
            print("PASS: Schema properties exist for all new fields")
            return True
        except jsonschema.ValidationError as e:
            print(f"FAIL: Schema validation error: {e.message}")
            return False
        
    finally:
        Path(payload_path).unlink(missing_ok=True)

if __name__ == "__main__":
    success = test_guardian_listing_payload_schema_acceptance()
    sys.exit(0 if success else 1)
