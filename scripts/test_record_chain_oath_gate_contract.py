#!/usr/bin/env python3
"""Test: Record-Chain Oath Gate contract compliance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OATH_POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"
SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
FIELD_HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
VALIDATION = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py"

EXPECTED_MODULES = [
    "common_submission_integrity_v1",
    "echo_integrity_v1",
    "verification_integrity_v1",
    "guardian_stewardship_v1",
    "retirement_or_key_management_integrity_v1",
    "propagation_integrity_v1",
    "correction_integrity_v1",
    "classification_update_integrity_v1",
]


def main() -> None:
    errors = []

    # Test 1: Oath policy exists and parses
    if not OATH_POLICY.exists():
        errors.append("api/record-chain-oath-policy.v1.json: NOT FOUND")
        print("FAIL:\n" + "\n".join(f"  {e}" for e in errors))
        sys.exit(1)

    policy = json.loads(OATH_POLICY.read_text(encoding="utf-8"))

    # Test 2: Schema matches
    if policy.get("schema") != "trinityaccord.record-chain-oath-policy.v1":
        errors.append(f"wrong schema: {policy.get('schema')}")

    # Test 3: Policy has no_shortcut_policy
    nsp = policy.get("no_shortcut_policy")
    if not isinstance(nsp, dict):
        errors.append("missing no_shortcut_policy")
    else:
        if not nsp.get("readback_required"):
            errors.append("no_shortcut_policy.readback_required is not true")
        if not nsp.get("required_declarations"):
            errors.append("no_shortcut_policy.required_declarations is empty")
        if len(nsp.get("required_declarations", [])) < 10:
            errors.append(f"no_shortcut_policy.required_declarations has {len(nsp.get('required_declarations', []))} items, expected 10+")

    # Test 4: Policy has all 8 modules
    modules = policy.get("modules", {})
    for mod_id in EXPECTED_MODULES:
        if mod_id not in modules:
            errors.append(f"missing module: {mod_id}")
        else:
            mod = modules[mod_id]
            if not mod.get("label"):
                errors.append(f"module {mod_id} missing label")
            if not mod.get("text"):
                errors.append(f"module {mod_id} missing text")

    # Test 5: Canonicalization test vectors
    can = policy.get("canonicalization", {})
    if can.get("line_endings") != "LF":
        errors.append(f"canonicalization.line_endings: expected LF, got {can.get('line_endings')}")
    if can.get("module_joiner") != "\n\n---\n\n":
        errors.append(f"canonicalization.module_joiner: expected '\\n\\n---\\n\\n', got {can.get('module_joiner')!r}")

    # Test 6: Record type modules mapping
    rtm = policy.get("record_type_modules", {})
    for rt in ["echo", "verification", "guardian_application", "guardian_retirement",
               "guardian_key_rotation", "propagation", "correction", "classification_update"]:
        if rt not in rtm:
            errors.append(f"record_type_modules missing: {rt}")
        elif "common_submission_integrity_v1" not in rtm[rt]:
            errors.append(f"record_type_modules[{rt}] missing common_submission_integrity_v1")

    # Test 7: Builder has print-oath command (check source text)
    if BUILDER.exists():
        builder_text = BUILDER.read_text(encoding="utf-8")
        if "print-oath" not in builder_text:
            errors.append("builder missing print-oath command")
    else:
        errors.append("downloads/record-chain-builder.mjs: NOT FOUND")

    # Test 8: Gateway has validate_submission_oath
    if VALIDATION.exists():
        val_text = VALIDATION.read_text(encoding="utf-8")
        if "def validate_submission_oath" not in val_text:
            errors.append("validation.py missing validate_submission_oath")
        if "def redact_transient_oath_readback" not in val_text:
            errors.append("validation.py missing redact_transient_oath_readback")
    else:
        errors.append("validation.py: NOT FOUND")

    # Test 9: Schema contains submission_oath_verification and client_oath_readback
    if SCHEMA.exists():
        schema_text = SCHEMA.read_text(encoding="utf-8")
        if "submission_oath_verification" not in schema_text:
            errors.append("submission schema missing submission_oath_verification")
        if "client_oath_readback" not in schema_text:
            errors.append("submission schema missing client_oath_readback")
    else:
        errors.append("submission schema: NOT FOUND")

    # Test 10: Field helper contains oath guidance
    if FIELD_HELPER.exists():
        fh = json.loads(FIELD_HELPER.read_text(encoding="utf-8"))
        groups = fh.get("field_groups", [])
        has_oath = any("oath" in g.get("field", "") for g in groups)
        if not has_oath:
            errors.append("field helper missing oath guidance entries")
    else:
        errors.append("field helper: NOT FOUND")

    # Report
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("PASS: all oath gate contract tests passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
