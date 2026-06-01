#!/usr/bin/env python3
"""Test gateway payload readback SHA256 validation."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_readback_integrity import (
    sha256_text,
    validate_oath_readback_integrity,
)


def test_missing_hash_fails():
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


def test_mismatch_fails():
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


def test_valid_passes():
    readback = "I understand this oath completely and will act in good faith." * 5
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


def test_no_oath_passes():
    payload = {"some_field": True}
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 0


def test_no_readback_passes():
    payload = {
        "agent_integrity_declaration": {
            "verification_oath": {
                "oath_read": True,
            }
        }
    }
    errors = validate_oath_readback_integrity(payload)
    assert len(errors) == 0


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
