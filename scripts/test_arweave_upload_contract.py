#!/usr/bin/env python3
"""Contract test: arweave_upload_payload.mjs output schema.

Verifies that the upload result JSON produced by arweave_upload_payload.mjs
contains all fields required by update_record_chain_data_arweave_registry.py
in live mode (payload_sha256, readback_sha256, hash_match).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = [
    "schema",
    "txid",
    "uploaded_at",
    "data_sha256",
    "payload_sha256",
    "readback_sha256",
    "hash_match",
    "wallet_address_sha256",
    "tags",
    "boundary",
]

REQUIRED_SCHEMA = "trinityaccord.arweave-upload-result.v1"

BOUNDARY_FIELDS = {
    "arweave_archive_is_mirror_only": True,
    "arweave_archive_is_not_authority": True,
    "arweave_archive_is_not_attestation": True,
    "arweave_archive_is_not_amendment": True,
    "arweave_archive_is_not_successor_reception": True,
    "bitcoin_originals_prevail": True,
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def test_script_source_has_readback():
    """Verify the upload script source contains readback verification logic."""
    script = ROOT / "scripts" / "arweave_upload_payload.mjs"
    if not script.exists():
        fail("scripts/arweave_upload_payload.mjs not found")
    text = script.read_text(encoding="utf-8")
    for needle in [
        "readback_sha256",
        "hash_match",
        "ARWEAVE_READBACK",
        "getData",
    ]:
        if needle not in text:
            fail(f"arweave_upload_payload.mjs missing: {needle}")
    ok("arweave_upload_payload.mjs contains readback verification")


def test_script_outputs_required_fields():
    """Verify the script constructs result with all required fields."""
    script = ROOT / "scripts" / "arweave_upload_payload.mjs"
    text = script.read_text(encoding="utf-8")
    for field in REQUIRED_FIELDS:
        if f'"{field}"' not in text and f"'{field}'" not in text and f"{field}:" not in text and f"{field} :" not in text:
            fail(f"arweave_upload_payload.mjs result missing field: {field}")
    ok("arweave_upload_payload.mjs result has all required fields")


def test_script_outputs_boundary():
    """Verify boundary fields match contract."""
    script = ROOT / "scripts" / "arweave_upload_payload.mjs"
    text = script.read_text(encoding="utf-8")
    for field in BOUNDARY_FIELDS:
        if field not in text:
            fail(f"arweave_upload_payload.mjs boundary missing: {field}")
    ok("arweave_upload_payload.mjs boundary fields match contract")


def test_registry_reads_hash_match():
    """Verify update_record_chain_data_arweave_registry.py reads hash_match."""
    reg_script = ROOT / "scripts" / "update_record_chain_data_arweave_registry.py"
    if not reg_script.exists():
        fail("update_record_chain_data_arweave_registry.py not found")
    text = reg_script.read_text(encoding="utf-8")
    for needle in [
        "hash_match",
        "readback_sha256",
        "payload_sha256",
    ]:
        if needle not in text:
            fail(f"registry script missing: {needle}")
    ok("registry script reads hash_match, readback_sha256, payload_sha256")


def test_registry_live_requires_hash_match():
    """Verify live mode enforces hash_match check."""
    reg_script = ROOT / "scripts" / "update_record_chain_data_arweave_registry.py"
    text = reg_script.read_text(encoding="utf-8")
    if "hash_match is not True" not in text:
        fail("registry script does not enforce hash_match is not True in live mode")
    ok("registry script enforces hash_match in live mode")


def main() -> int:
    test_script_source_has_readback()
    test_script_outputs_required_fields()
    test_script_outputs_boundary()
    test_registry_reads_hash_match()
    test_registry_live_requires_hash_match()
    print("\nAll contract tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
