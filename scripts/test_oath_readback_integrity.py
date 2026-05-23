#!/usr/bin/env python3
"""Tests for oath_readback_integrity helper."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_readback_integrity import (
    normalize_oath_readback_integrity,
    payload_has_authorship_proof,
    sha256_text,
    validate_oath_readback_integrity,
)


def test_sha256_text():
    assert sha256_text("hello") == hashlib.sha256(b"hello").hexdigest()
    assert sha256_text("") == hashlib.sha256(b"").hexdigest()
    assert len(sha256_text("test")) == 64


def test_validate_missing_hash():
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": "x" * 200,
            }
        }
    }
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 1
    assert errors[0]["code"] == "READBACK_SHA256_MISSING"
    assert errors[0]["repairable"] is True
    assert errors[0]["requires_resign"] is False


def test_validate_mismatch():
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": "x" * 200,
                "agent_readback_sha256": "0" * 64,
            }
        }
    }
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 1
    assert errors[0]["code"] == "READBACK_SHA256_MISMATCH"


def test_validate_valid():
    readback = "I understand this oath and will act in good faith." * 5
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": readback,
                "agent_readback_sha256": sha256_text(readback),
            }
        }
    }
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 0


def test_validate_signed_missing_hash():
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": "x" * 200,
            }
        },
        "authorship_proof": {
            "signed_payload_sha256": "a" * 64,
        }
    }
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 1
    assert errors[0]["code"] == "READBACK_SHA256_MISSING"
    assert errors[0]["repairable"] is False
    assert errors[0]["requires_resign"] is True


def test_normalize_unsigned():
    readback = "x" * 200
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": readback,
            }
        }
    }
    normalize_oath_readback_integrity(payload, mutate=True)
    oath = payload["agent_integrity_declaration"]["verification_oath"]
    assert oath["agent_readback_sha256"] == sha256_text(readback)


def test_normalize_strips_whitespace():
    readback = "  hello world  "
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": readback,
            }
        }
    }
    normalize_oath_readback_integrity(payload, mutate=True)
    oath = payload["agent_integrity_declaration"]["verification_oath"]
    assert oath["agent_readback_sha256"] == sha256_text("hello world")


def test_normalize_no_oath():
    payload = {"some_other_field": True}
    result = normalize_oath_readback_integrity(payload, mutate=True)
    assert result == payload


def test_normalize_no_readback():
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "oath_read": True,
            }
        }
    }
    result = normalize_oath_readback_integrity(payload, mutate=True)
    assert "agent_readback_sha256" not in result["agent_integrity_declaration"]["verification_oath"]


def test_payload_has_authorship_proof():
    assert payload_has_authorship_proof({"authorship_proof": {"signed_payload_sha256": "abc"}}) is True
    assert payload_has_authorship_proof({"authorship_proof": {}}) is False
    assert payload_has_authorship_proof({}) is False


def test_validate_after_normalize_roundtrip():
    readback = "I will act honestly and in good faith. " * 6
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "agent_readback": readback,
            }
        }
    }
    errors_before = validate_oath_readback_integrity(payload)
    assert len(errors_before) == 1

    normalize_oath_readback_integrity(payload, mutate=True)
    errors_after = validate_oath_readback_integrity(payload)
    assert len(errors_after) == 0


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
