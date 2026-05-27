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

# Schema v1 or v2
schema_val = data.get("schema", "")
if "mirror-index" not in schema_val and "inscription" not in schema_val:
    errors.append(f"schema should be mirror-index, got {schema_val}")

# Counts - support both v1 and v2 structures
counts = data.get("counts", {})
total = counts.get("total_relevant_inscriptions") or sum(v for k, v in counts.items() if isinstance(v, int) and k != "unknown_or_pending")
if total != 8:
    errors.append(f"total inscriptions should be 8, got {total}")
canonical = counts.get("canonical_originals", 0)
if canonical != 3:
    errors.append(f"canonical_originals should be 3, got {canonical}")
post_original = counts.get("post_original_non_amending")
if post_original is None:
    # Compute from other counts
    post_original = total - canonical - counts.get("unknown_or_pending", 0)
if post_original != 5:
    errors.append(f"post_original_non_amending should be 5, got {post_original}")

# Records
records = data.get("records", [])
if len(records) != 8:
    errors.append(f"records length should be 8, got {len(records)}")

# IDs match
record_ids = {r.get("inscription_id") or r.get("inscription", {}).get("inscription_id") for r in records}
if record_ids != EXPECTED_IDS:
    errors.append(f"ID mismatch: missing={EXPECTED_IDS - record_ids}, extra={record_ids - EXPECTED_IDS}")

# Each record checks
for rec in records:
    ins_id = rec.get("inscription_id") or rec.get("inscription", {}).get("inscription_id")
    ins = rec.get("inscription", {})
    cls = rec.get("classification", {})
    content = rec.get("content", {})

    # raw_text_path exists (may be under content)
    raw_path = rec.get("raw_text_path") or content.get("raw_text_path", "")
    if raw_path:
        rtp = ROOT / raw_path
        if not rtp.exists():
            errors.append(f"{ins_id}: raw_text_path missing: {rtp}")

    # mirror_json_path exists - search for it in the mirror directories
    mjp_path = rec.get("mirror_json_path") or content.get("mirror_json_path", "")
    if not mjp_path:
        # Search for mirror file by inscription ID
        found = list(ROOT.glob(f"bitcoin-inscription-mirrors/**/{ins_id}*.json"))
        if not found:
            errors.append(f"{ins_id}: mirror_json_path not found in bitcoin-inscription-mirrors/")
    else:
        mjp = ROOT / mjp_path
        if not mjp.exists():
            errors.append(f"{ins_id}: mirror_json_path missing: {mjp}")

    # Non-originals
    if ins_id not in CANONICAL_IDS:
        if cls.get("is_one_of_three_bitcoin_originals"):
            errors.append(f"{ins_id}: should NOT be canonical original")
        if cls.get("amends_originals"):
            errors.append(f"{ins_id}: amends_originals should be false")
        if cls.get("creates_new_authority"):
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

# Source references (optional in v1)
source = data.get("source", {})
if source:
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
