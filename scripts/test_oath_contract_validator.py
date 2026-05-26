#!/usr/bin/env python3
"""Test oath contract validator."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_contracts import (
    validate_oath_contract,
    build_verification_oath_v2,
    build_guardian_listing_oath_v1,
    load_oath_text,
    VERIFICATION_OATH_TRUE_FIELDS,
    GUARDIAN_LISTING_OATH_TRUE_FIELDS,
)


def test_valid_oath():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert errors == [], f"Expected no errors: {errors}"
    print("PASS: test_valid_oath")


def test_missing_honesty():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    del oath["honesty_oath_present"]
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert any("honesty_oath_present" in e for e in errors), f"Expected honesty error: {errors}"
    print("PASS: test_missing_honesty")


def test_missing_good_faith():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    del oath["good_faith_oath_present"]
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert any("good_faith_oath_present" in e for e in errors), f"Expected good_faith error: {errors}"
    print("PASS: test_missing_good_faith")


def test_bad_schema():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    oath["schema"] = "wrong.schema"
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert any("schema" in e for e in errors), f"Expected schema error: {errors}"
    print("PASS: test_bad_schema")


def test_readback_hash_mismatch():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    oath["agent_readback_sha256"] = "0" * 64
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert any("readback_sha256" in e for e in errors), f"Expected readback hash error: {errors}"
    print("PASS: test_readback_hash_mismatch")


def test_not_oath_read():
    oath_text = load_oath_text(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
    oath = build_verification_oath_v2(oath_text)
    oath["oath_read"] = False
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.verification-oath.v2"},
        required_true=VERIFICATION_OATH_TRUE_FIELDS,
    )
    assert any("oath_read" in e for e in errors), f"Expected oath_read error: {errors}"
    print("PASS: test_not_oath_read")


if __name__ == "__main__":
    test_valid_oath()
    test_missing_honesty()
    test_missing_good_faith()
    test_bad_schema()
    test_readback_hash_mismatch()
    test_not_oath_read()
