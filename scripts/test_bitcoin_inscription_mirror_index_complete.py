#!/usr/bin/env python3
"""Test: aggregate Bitcoin inscription mirror index is complete and correct."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "api" / "bitcoin-inscription-mirror-index.json"

EXPECTED_IDS = {"97631551", "98369145", "98387475", "100385359", "100550942", "100751953", "103034280", "103635270"}
CANONICAL_IDS = {"97631551", "98369145", "98387475"}

errors = []

if not INDEX_PATH.exists():
    print("FAIL: index file does not exist")
    sys.exit(1)

data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

# Schema v2
if "v2" not in data.get("schema", ""):
    errors.append(f"schema should be v2, got {data.get('schema')}")

# Counts
counts = data.get("counts", {})
if counts.get("total_relevant_inscriptions") != 8:
    errors.append(f"total_relevant_inscriptions should be 8, got {counts.get('total_relevant_inscriptions')}")
if counts.get("canonical_originals") != 3:
    errors.append(f"canonical_originals should be 3, got {counts.get('canonical_originals')}")
if counts.get("post_original_non_amending") != 5:
    errors.append(f"post_original_non_amending should be 5, got {counts.get('post_original_non_amending')}")
if counts.get("unknown_or_pending") != 0:
    errors.append(f"unknown_or_pending should be 0, got {counts.get('unknown_or_pending')}")

# Records
records = data.get("records", [])
if len(records) != 8:
    errors.append(f"records length should be 8, got {len(records)}")

# IDs match
record_ids = {r["inscription_id"] for r in records}
if record_ids != EXPECTED_IDS:
    errors.append(f"ID mismatch: missing={EXPECTED_IDS - record_ids}, extra={record_ids - EXPECTED_IDS}")

# Each record checks
for rec in records:
    ins_id = rec["inscription_id"]

    # mirror_json_path exists
    mjp = ROOT / rec.get("mirror_json_path", "")
    if not mjp.exists():
        errors.append(f"{ins_id}: mirror_json_path missing: {mjp}")

    # raw_text_path exists
    rtp = ROOT / rec.get("raw_text_path", "")
    if not rtp.exists():
        errors.append(f"{ins_id}: raw_text_path missing: {rtp}")

    # Non-originals
    if ins_id not in CANONICAL_IDS:
        if rec.get("is_one_of_three_bitcoin_originals"):
            errors.append(f"{ins_id}: should NOT be canonical original")
        if rec.get("amends_originals"):
            errors.append(f"{ins_id}: amends_originals should be false")
        if rec.get("creates_new_authority"):
            errors.append(f"{ins_id}: creates_new_authority should be false")

    # Chain verification assertions
    cv = rec.get("chain_verification", {})
    if cv.get("verification_status") != "mirror_matches_onchain":
        errors.append(f"{ins_id}: verification_status should be mirror_matches_onchain, got {cv.get('verification_status')}")
    if cv.get("mirror_matches_onchain") is not True:
        errors.append(f"{ins_id}: mirror_matches_onchain should be true")
    if not cv.get("onchain_content_sha256"):
        errors.append(f"{ins_id}: onchain_content_sha256 should be non-empty")
    if not cv.get("last_verified_utc"):
        errors.append(f"{ins_id}: last_verified_utc should be non-empty")

# Source references
source = data.get("source", {})
if "legacy_archive" not in source:
    errors.append("source missing legacy_archive reference")
if "generated_by" not in source:
    errors.append("source missing generated_by reference")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: mirror index complete test")
    sys.exit(0)
