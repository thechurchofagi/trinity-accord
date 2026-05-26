#!/usr/bin/env python3
"""
Build the Bitcoin inscription mirror index from mirror records.
Scans bitcoin-inscription-mirrors/**/*.json, validates, and generates
api/bitcoin-inscription-mirror-index.json.
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR_DIR = ROOT / "bitcoin-inscription-mirrors"
INDEX_PATH = ROOT / "api" / "bitcoin-inscription-mirror-index.json"
SCHEMA_PATH = ROOT / "api" / "bitcoin-inscription-mirror-schema.v1.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def scan_mirrors():
    """Scan all JSON files in mirror directory."""
    records = []
    for subdir in ["canonical-originals", "vision-layer", "context-layer"]:
        d = MIRROR_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                data = load_json(f)
                data["_source_path"] = str(f.relative_to(ROOT))
                records.append(data)
            except Exception as e:
                print(f"ERROR loading {f}: {e}", file=sys.stderr)
    return records

def validate_record(record, schema):
    """Basic validation of a mirror record."""
    errors = []
    required = schema.get("required", [])
    for field in required:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    # Check authority_boundary
    ab = record.get("authority_boundary", {})
    if not ab.get("bitcoin_originals_prevail"):
        errors.append("authority_boundary.bitcoin_originals_prevail must be true")
    if not ab.get("github_mirror_is_non_amending"):
        errors.append("authority_boundary.github_mirror_is_non_amending must be true")
    if not ab.get("verification_requires_onchain_check"):
        errors.append("authority_boundary.verification_requires_onchain_check must be true")

    # Check no placeholder source_address
    sa = record.get("inscription", {}).get("source_address", "")
    if sa == "bc1p_trinity_accord_authority":
        errors.append("source_address is placeholder 'bc1p_trinity_accord_authority', must use real authority address")

    return errors

def build_index():
    """Build the mirror index."""
    schema = load_json(SCHEMA_PATH)
    records = scan_mirrors()

    if not records:
        print("ERROR: No mirror records found", file=sys.stderr)
        return 1

    # Validate and classify
    canonical = []
    vision = []
    final_seal = []
    first_echo = []
    guardianship = []
    unknown = []
    all_errors = []

    for r in records:
        errs = validate_record(r, schema)
        if errs:
            all_errors.extend([f"{r.get('_source_path', '?')}: {e}" for e in errs])

        status = r.get("canonical_status", "")
        layer = r.get("classification", {}).get("layer", "")

        if status == "canonical_original":
            canonical.append(r)
        elif layer == "vision_layer":
            vision.append(r)
        elif layer == "final_seal_layer":
            final_seal.append(r)
        elif layer == "first_echo_layer":
            first_echo.append(r)
        elif layer == "guardianship_layer":
            guardianship.append(r)
        else:
            unknown.append(r)

    # Enforce exactly three canonical originals
    if len(canonical) != 3:
        all_errors.append(f"Expected 3 canonical originals, found {len(canonical)}")

    # Enforce canonical originals have txid (not null/empty)
    for r in canonical:
        txid = r.get("inscription", {}).get("txid")
        iid = r.get("inscription", {}).get("inscription_id", "?")
        if not txid:
            all_errors.append(f"Canonical original {iid} missing txid")

    # Enforce non-amending for non-canonical
    for r in vision + final_seal + first_echo + guardianship + unknown:
        if r.get("classification", {}).get("amends_originals"):
            all_errors.append(f"{r.get('_source_path')}: non-canonical record has amends_originals=true")
        if r.get("classification", {}).get("creates_new_authority"):
            all_errors.append(f"{r.get('_source_path')}: non-canonical record has creates_new_authority=true")

    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Build index records (without _source_path)
    index_records = []
    for r in records:
        rec = {k: v for k, v in r.items() if k != "_source_path"}
        index_records.append(rec)

    index = {
        "schema": "trinityaccord.bitcoin-inscription-mirror-index.v1",
        "purpose": "Quick-load GitHub mirror index for Bitcoin inscriptions associated with the Trinity Accord.",
        "authority_boundary": {
            "canonical_original_count": 3,
            "canonical_authority": "three_bitcoin_originals_only",
            "github_mirrors_non_amending": True,
            "verification_requires_onchain_check": True
        },
        "counts": {
            "canonical_originals": len(canonical),
            "vision_layer": len(vision),
            "final_seal_layer": len(final_seal),
            "first_echo_layer": len(first_echo),
            "guardianship_layer": len(guardianship),
            "unknown_or_pending": len(unknown)
        },
        "records": index_records
    }

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index built: {len(records)} records")
    print(f"  Canonical originals: {len(canonical)}")
    print(f"  Vision layer: {len(vision)}")
    print(f"  Final seal layer: {len(final_seal)}")
    print(f"  First echo layer: {len(first_echo)}")
    print(f"  Guardianship layer: {len(guardianship)}")
    print(f"  Unknown/pending: {len(unknown)}")
    return 0

if __name__ == "__main__":
    sys.exit(build_index())
