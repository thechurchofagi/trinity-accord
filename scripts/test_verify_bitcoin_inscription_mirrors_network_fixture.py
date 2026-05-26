#!/usr/bin/env python3
"""Test: network verification with mock provider (no real network needed)."""
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

# Import the verifier module
sys.path.insert(0, str(ROOT / "scripts"))
import verify_bitcoin_inscription_mirrors as verifier

errors = []


def mock_fetch_ok(inscription_id, provider="ordinals"):
    """Mock provider that returns matching content."""
    raw_path = ROOT / "bitcoin-inscription-mirrors" / "raw" / f"{inscription_id}.txt"
    if raw_path.exists():
        return raw_path.read_text(encoding="utf-8"), None
    return None, "not found"


def mock_fetch_mismatch(inscription_id, provider="ordinals"):
    """Mock provider that returns mismatched content."""
    return "This is completely different content that should not match.", None


def mock_fetch_fail(inscription_id, provider="ordinals"):
    """Mock provider that fails."""
    return None, "connection refused"


# Test 1: Mock provider returns matching content
records = verifier.load_mirror_records()
for rec in records:
    ins_id = rec["inscription"]["inscription_id"]
    content, err = mock_fetch_ok(ins_id)
    if content is None:
        errors.append(f"Mock fetch failed for {ins_id}")
        continue
    onchain_hash = verifier.sha256_text(verifier.canonicalize(content))
    mirror_hash = rec["content"].get("canonicalized_text_sha256")
    if onchain_hash != mirror_hash:
        errors.append(f"Hash mismatch for {ins_id}")

# Test 2: Mismatch detection
for rec in records:
    ins_id = rec["inscription"]["inscription_id"]
    content, err = mock_fetch_mismatch(ins_id)
    onchain_hash = verifier.sha256_text(verifier.canonicalize(content))
    mirror_hash = rec["content"].get("canonicalized_text_sha256")
    if onchain_hash == mirror_hash:
        errors.append(f"Should have detected mismatch for {ins_id}")

# Test 3: Failure handling
content, err = mock_fetch_fail("97631551")
if content is not None:
    errors.append("Should have returned None on failure")
if err is None:
    errors.append("Should have returned error message on failure")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: network fixture test")
    sys.exit(0)
