#!/usr/bin/env python3
"""Test that JSON schema enforces oath field strictness.

Validates that:
  - oath boolean fields use const:true in the agent-declared branch
  - agent_readback_char_count has minimum:160 in the agent-declared branch
  - schema rejects payloads where oath fields are false or missing
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
VALIDATOR_PAYLOAD = ROOT / "scripts" / "validate_gateway_payload.py"

PASS = 0
FAIL = 0


def check(condition, desc):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {desc}")
    else:
        FAIL += 1
        print(f"  FAIL: {desc}")


def run(cmd, expect_fail=False):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if expect_fail:
        return r.returncode != 0, r.stdout + r.stderr
    return r.returncode == 0, r.stdout + r.stderr


def test_schema_oath_const_true():
    """Agent-declared branch must have const:true for oath booleans."""
    global PASS, FAIL
    print("\n--- Schema oath const:true ---")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    # Find the agent-declared branch
    all_of = schema.get("allOf", [])
    agent_branch = None
    for branch in all_of:
        props = branch.get("if", {}).get("properties", {})
        if props.get("requested_archive_kind", {}).get("const") == "agent_declared_verification_archive":
            agent_branch = branch
            break

    check(agent_branch is not None, "agent-declared branch exists")

    if not agent_branch:
        return

    then_props = agent_branch.get("then", {}).get("properties", {})
    then_required = agent_branch.get("then", {}).get("required", [])

    # Oath fields inherit from top-level (not overridden in then.properties)
    # Verify they are required in the agent-declared branch
    for field in ["verification_oath_present", "oath_read", "readback_required", "agent_readback_present", "agent_readback_char_count"]:
        check(field in then_required, f"{field} is required in agent-declared branch")

    # Verify top-level constraints apply (const:true, minimum:160)
    top_props = schema.get("properties", {})
    for field in ["verification_oath_present", "oath_read", "readback_required", "agent_readback_present"]:
        prop = top_props.get(field, {})
        check(prop.get("const") is True, f"top-level {field} has const:true (inherited by agent-declared)")

    readback = top_props.get("agent_readback_char_count", {})
    check(readback.get("minimum") == 160, "top-level agent_readback_char_count minimum is 160 (inherited)")


def test_schema_top_level_oath_strict():
    """Top-level properties should also have const:true for oath booleans."""
    global PASS, FAIL
    print("\n--- Top-level oath strictness ---")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    props = schema.get("properties", {})

    for field in ["verification_oath_present", "oath_read", "readback_required", "agent_readback_present"]:
        prop = props.get(field, {})
        check(prop.get("const") is True, f"top-level {field} has const:true")

    readback = props.get("agent_readback_char_count", {})
    check(readback.get("minimum") == 160, "top-level agent_readback_char_count minimum is 160")


def test_payload_validator_rejects_false_oath():
    """Payload validator must reject oath fields set to false."""
    global PASS, FAIL
    print("\n--- Payload validator rejects false oath ---")

    if not VALIDATOR_PAYLOAD.exists():
        FAIL += 1
        print("  FAIL: validate_gateway_payload.py not found")
        return

    # Build a minimal valid payload then set oath to false
    payload = {
        "submission_type": "verification_report_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS"},
        "agent_name_or_model": "TestAgent",
        "system_or_provider": "TestProvider",
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "boundary_sentence": "This is a test boundary sentence that is long enough.",
        "agent_integrity_declaration": {
            "agent_integrity_declaration_present": True,
            "verification_oath": {
                "verification_oath_present": False,  # FAIL: must be true
                "oath_read": True,
                "oath_version": "v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback_present": True,
                "agent_readback_char_count": 200,
                "agent_readback_sha256": "b" * 64,
            },
        },
    }

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f)
        bad_path = f.name

    ok, msg = run([sys.executable, str(VALIDATOR_PAYLOAD), bad_path], expect_fail=True)
    Path(bad_path).unlink(missing_ok=True)

    check(ok, "payload with oath_present=false rejected")


def test_payload_validator_rejects_short_readback():
    """Payload validator must reject readback < 160 chars."""
    global PASS, FAIL
    print("\n--- Payload validator rejects short readback ---")

    if not VALIDATOR_PAYLOAD.exists():
        FAIL += 1
        print("  FAIL: validate_gateway_payload.py not found")
        return

    payload = {
        "submission_type": "verification_report_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS"},
        "agent_name_or_model": "TestAgent",
        "system_or_provider": "TestProvider",
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "boundary_sentence": "This is a test boundary sentence that is long enough.",
        "agent_integrity_declaration": {
            "agent_integrity_declaration_present": True,
            "verification_oath": {
                "verification_oath_present": True,
                "oath_read": True,
                "oath_version": "v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback_present": True,
                "agent_readback_char_count": 50,  # FAIL: < 160
                "agent_readback_sha256": "b" * 64,
            },
        },
    }

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f)
        bad_path = f.name

    ok, msg = run([sys.executable, str(VALIDATOR_PAYLOAD), bad_path], expect_fail=True)
    Path(bad_path).unlink(missing_ok=True)

    check(ok, "payload with readback_count=50 rejected")


def main():
    global PASS, FAIL
    print("=== Agent-Declared Oath Schema Strictness Tests ===")

    test_schema_oath_const_true()
    test_schema_top_level_oath_strict()
    test_payload_validator_rejects_false_oath()
    test_payload_validator_rejects_short_readback()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
