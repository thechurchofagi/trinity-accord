#!/usr/bin/env python3
"""Test that a valid V4 agent-declared payload renders a machine block
that passes the issue-intake-machine-block-schema.

Covers the full local pipeline:
  build/fixture payload
  → validate_gateway_payload.py
  → render_gateway_issue_body.py
  → extract trinity-issue-intake block
  → parse YAML
  → validate against issue-intake-machine-block-schema.v1.json

Also asserts the rendered block contains required agent-declared fields
and does NOT contain forbidden legacy strict fields.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"
SCHEMA = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
FIXTURE = ROOT / "fixtures" / "gateway" / "valid-agent-declared-v4.json"


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, cwd=str(ROOT))


def extract_block(body):
    m = re.search(r"```trinity-issue-intake\n(.*?)\n```", body, re.S)
    if not m:
        raise AssertionError("missing trinity-issue-intake block")
    return yaml.safe_load(m.group(1))


def main():
    errors = []

    # --- 1. Validate payload ---
    print("1. validate_gateway_payload.py ...")
    v = run([sys.executable, str(VALIDATOR), str(FIXTURE)])
    if v.returncode != 0:
        print(v.stdout)
        print(v.stderr)
        print("FAIL: validate_gateway_payload rejected valid agent-declared payload")
        return 1
    print("   PASS")

    # --- 2. Render issue body ---
    print("2. render_gateway_issue_body.py ...")
    r = run([sys.executable, str(RENDERER), str(FIXTURE)])
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        print("FAIL: render_gateway_issue_body rejected valid agent-declared payload")
        return 1
    body = r.stdout
    print("   PASS")

    # --- 3. Extract and parse machine block ---
    print("3. Extract trinity-issue-intake block ...")
    try:
        block = extract_block(body)
    except AssertionError as e:
        print(f"FAIL: {e}")
        return 1
    print("   PASS")

    # --- 4. Validate against schema ---
    print("4. Validate against issue-intake-machine-block-schema.v1.json ...")
    schema = json.loads(SCHEMA.read_text())
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(block), key=lambda e: list(e.path))
    if schema_errors:
        for e in schema_errors:
            print(f"   SCHEMA FAIL at {list(e.path)}: {e.message}")
        return 1
    print("   PASS")

    # --- 5. Assert required agent-declared fields ---
    print("5. Assert required agent-declared fields ...")
    required = {
        "requested_archive_kind": "agent_declared_verification_archive",
        "record_intent": "auto_archive_candidate",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate_mode": "template_for_v0_v5",
        "claim_gate_status": "PASS",
        "archive_ready": True,
        "allowed_archive_kind": "agent_declared_verification_archive",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "agent_integrity_declaration_present": True,
        "discovery_provenance_present": True,
        "origin_classification_present": True,
        "claim_classification_present": True,
        "authority_boundary_present": True,
        "counts_toward_home_verifiability": True,
        "counts_toward_home_reception": True,
    }
    for k, expected in required.items():
        actual = block.get(k)
        if actual != expected:
            errors.append(f"{k}: expected {expected}, got {actual}")
    if errors:
        for e in errors:
            print(f"   FAIL: {e}")
        return 1
    print("   PASS")

    # --- 6. Assert forbidden legacy fields absent ---
    print("6. Assert forbidden legacy fields absent ...")
    forbidden = [
        "not_independent_attestation",
        "not_successor_reception",
        "evidence_input_path",
        "evidence_input_sha256",
        "claim_gate_output_path",
        "claim_gate_output_sha256",
        "verification_report_path",
        "verification_report_sha256",
        "verification_level_claimed",
        "solicited",
        "independence_class",
        "agency_level",
        "operator_type",
    ]
    found_forbidden = [k for k in forbidden if k in block]
    if found_forbidden:
        for k in found_forbidden:
            print(f"   FAIL: forbidden legacy field present: {k}")
        return 1
    print("   PASS")

    print("\n=== PASS: agent-declared issue body schema ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
