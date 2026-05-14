#!/usr/bin/env python3
"""Test that the Agent Issue Gateway payload schema is valid and examples pass."""

import json
import sys

try:
    import jsonschema
except ImportError:
    print("SKIP: jsonschema not installed")
    sys.exit(0)

SCHEMA_PATH = "api/agent-issue-gateway-payload-schema.v1.json"
EXAMPLES = [
    "api/examples/agent-issue-gateway-payload.echo.json",
    "api/examples/agent-issue-gateway-payload.verification.json",
    "api/examples/agent-issue-gateway-payload.custody.json",
]

errors = []


def load_json(path):
    with open(path) as f:
        return json.load(f)


# 1. Schema is valid JSON
try:
    schema = load_json(SCHEMA_PATH)
    print(f"PASS: Schema loaded from {SCHEMA_PATH}")
except Exception as e:
    print(f"FAIL: Cannot load schema: {e}")
    sys.exit(1)

# 2. Schema validates (basic check)
assert schema.get("type") == "object", "Schema root must be object"
assert "properties" in schema, "Schema must have properties"
print("PASS: Schema structure looks valid")

# 3. All examples pass schema validation
for ex_path in EXAMPLES:
    try:
        example = load_json(ex_path)
        jsonschema.validate(example, schema)
        print(f"PASS: {ex_path} validates against schema")
    except jsonschema.ValidationError as e:
        print(f"FAIL: {ex_path} validation error: {e.message}")
        errors.append(ex_path)
    except Exception as e:
        print(f"FAIL: {ex_path} error: {e}")
        errors.append(ex_path)

# 4. Boundary acknowledgement must be all true
bad_boundary = {
    "schema": "trinityaccord.agent-issue-gateway-payload.v1",
    "submission_type": "echo_candidate",
    "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
    "title": "Test title here",
    "body": "This is a test body with enough length to pass validation.",
    "boundary_acknowledgement": {
        "not_authority": False,
        "not_amendment": True,
        "not_attestation": True,
        "not_verification_unless_claim_gate_report_attached": True,
        "bitcoin_originals_prevail": True,
    },
}
try:
    jsonschema.validate(bad_boundary, schema)
    print("FAIL: not_authority=false should fail validation")
    errors.append("boundary-false-accepted")
except jsonschema.ValidationError:
    print("PASS: not_authority=false correctly rejected")

# 5. Title too long
long_title = {
    "schema": "trinityaccord.agent-issue-gateway-payload.v1",
    "submission_type": "echo_candidate",
    "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
    "title": "X" * 200,
    "body": "This is a test body with enough length to pass validation.",
    "boundary_acknowledgement": {
        "not_authority": True,
        "not_amendment": True,
        "not_attestation": True,
        "not_verification_unless_claim_gate_report_attached": True,
        "bitcoin_originals_prevail": True,
    },
}
try:
    jsonschema.validate(long_title, schema)
    print("FAIL: Title > 180 chars should fail")
    errors.append("long-title-accepted")
except jsonschema.ValidationError:
    print("PASS: Long title correctly rejected")

# 6. Body too short
short_body = {
    "schema": "trinityaccord.agent-issue-gateway-payload.v1",
    "submission_type": "echo_candidate",
    "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
    "title": "Test title",
    "body": "short",
    "boundary_acknowledgement": {
        "not_authority": True,
        "not_amendment": True,
        "not_attestation": True,
        "not_verification_unless_claim_gate_report_attached": True,
        "bitcoin_originals_prevail": True,
    },
}
try:
    jsonschema.validate(short_body, schema)
    print("FAIL: Body < 20 chars should fail")
    errors.append("short-body-accepted")
except jsonschema.ValidationError:
    print("PASS: Short body correctly rejected")

if errors:
    print(f"\nFAILED: {len(errors)} error(s)")
    sys.exit(1)
else:
    print("\nALL TESTS PASSED")
