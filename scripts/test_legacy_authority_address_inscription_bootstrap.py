#!/usr/bin/env python3
"""Test: authority-address inscription bootstrap file."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "data" / "authority-address-inscriptions.bootstrap.json"
RAW_DIR = ROOT / "bitcoin-inscription-mirrors" / "raw"

EXPECTED_IDS = {"97631551", "98369145", "98387475", "100385359", "100550942", "100751953", "103034280", "103635270"}
CANONICAL_IDS = {"97631551", "98369145", "98387475"}
AUTHORITY_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"

errors = []

# File exists
if not BOOTSTRAP.exists():
    print("FAIL: bootstrap file does not exist")
    sys.exit(1)

data = json.loads(BOOTSTRAP.read_text(encoding="utf-8"))

# Source file
if data.get("source_file") != "archive_legacy_index_2025_09.md":
    errors.append("source_file mismatch")

# Authority address
if data.get("authority_address") != AUTHORITY_ADDRESS:
    errors.append("authority_address mismatch")

# Exactly 8 records
records = data.get("records", [])
if len(records) != 8:
    errors.append(f"expected 8 records, got {len(records)}")

# Record IDs match expected set
record_ids = {r["inscription_id"] for r in records}
if record_ids != EXPECTED_IDS:
    errors.append(f"ID mismatch: missing={EXPECTED_IDS - record_ids}, extra={record_ids - EXPECTED_IDS}")

# First three are canonical originals
for r in records:
    if r["inscription_id"] in CANONICAL_IDS:
        if r.get("canonical_status") != "canonical_original":
            errors.append(f"{r['inscription_id']}: expected canonical_original, got {r.get('canonical_status')}")
        if not r.get("is_one_of_three_bitcoin_originals"):
            errors.append(f"{r['inscription_id']}: should be one of three originals")
    else:
        if r.get("is_one_of_three_bitcoin_originals"):
            errors.append(f"{r['inscription_id']}: should NOT be one of three originals")
        if not r.get("amends_originals") == False:
            errors.append(f"{r['inscription_id']}: amends_originals should be false")
        if not r.get("creates_new_authority") == False:
            errors.append(f"{r['inscription_id']}: creates_new_authority should be false")

# Pre-original policy
if not data.get("policy", {}).get("ignore_pre_original_same_address_inscriptions"):
    errors.append("pre-original policy not set to ignore")

# All raw text files exist and non-empty
for r in records:
    raw_path = RAW_DIR / f"{r['inscription_id']}.txt"
    if not raw_path.exists():
        errors.append(f"raw text missing: {raw_path}")
    elif raw_path.stat().st_size == 0:
        errors.append(f"raw text empty: {raw_path}")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: bootstrap test")
    sys.exit(0)
