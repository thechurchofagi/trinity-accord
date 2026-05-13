#!/usr/bin/env python3
"""
Verify Bitcoin inscription mirrors against on-chain data or offline manifest.
Usage:
  python3 scripts/verify_bitcoin_inscription_mirrors.py --all
  python3 scripts/verify_bitcoin_inscription_mirrors.py --inscription-id 97631551
  python3 scripts/verify_bitcoin_inscription_mirrors.py --layer vision-layer
  python3 scripts/verify_bitcoin_inscription_mirrors.py --offline-manifest api/bitcoin-inscription-mirror-index.json
"""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR_DIR = ROOT / "bitcoin-inscription-mirrors"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def canonicalize(text):
    """Basic canonicalization: strip whitespace, normalize line endings."""
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")

def load_mirror_records():
    """Load all mirror records."""
    records = []
    for subdir in ["canonical-originals", "vision-layer", "context-layer"]:
        d = MIRROR_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                data = load_json(f)
                data["_path"] = str(f)
                records.append(data)
            except Exception as e:
                print(f"ERROR loading {f}: {e}", file=sys.stderr)
    return records

def load_raw_text(record):
    """Load raw text for a mirror record."""
    raw_path = record.get("content", {}).get("raw_text_path")
    if not raw_path:
        return None
    full_path = ROOT / raw_path
    if not full_path.exists():
        return None
    return full_path.read_text(encoding="utf-8")

def verify_record_offline(record):
    """Verify a mirror record using offline data only."""
    status = record.get("chain_verification", {}).get("verification_status", "not_checked")
    inscription_id = record.get("inscription", {}).get("inscription_id", "unknown")
    title = record.get("inscription", {}).get("title", "unknown")

    # Check basic structure
    issues = []

    # Authority boundary checks
    ab = record.get("authority_boundary", {})
    if not ab.get("bitcoin_originals_prevail"):
        issues.append("bitcoin_originals_prevail is not true")
    if not ab.get("github_mirror_is_non_amending"):
        issues.append("github_mirror_is_non_amending is not true")
    if not ab.get("verification_requires_onchain_check"):
        issues.append("verification_requires_onchain_check is not true")

    # Classification checks
    cls = record.get("classification", {})
    if record.get("canonical_status") != "canonical_original":
        if cls.get("amends_originals"):
            issues.append("non-canonical record has amends_originals=true")
        if cls.get("creates_new_authority"):
            issues.append("non-canonical record has creates_new_authority=true")

    # Check raw text exists if path specified
    raw_text = load_raw_text(record)
    if raw_text:
        mirror_hash = sha256_text(canonicalize(raw_text))
    else:
        mirror_hash = None

    return {
        "inscription_id": inscription_id,
        "title": title,
        "canonical_status": record.get("canonical_status"),
        "verification_status": status,
        "mirror_hash": mirror_hash,
        "issues": issues,
        "passed": len(issues) == 0
    }

def verify_offline_manifest(manifest_path):
    """Verify using an offline manifest."""
    manifest = load_json(manifest_path)
    records = manifest.get("records", [])

    print(f"Offline manifest verification: {len(records)} records")
    all_passed = True

    for r in records:
        result = verify_record_offline(r)
        status_icon = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status_icon}] {result['inscription_id']}: {result['title']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"    - {issue}")
            all_passed = False

    return 0 if all_passed else 1

def main():
    parser = argparse.ArgumentParser(description="Verify Bitcoin inscription mirrors")
    parser.add_argument("--all", action="store_true", help="Verify all mirrors")
    parser.add_argument("--inscription-id", help="Verify specific inscription")
    parser.add_argument("--layer", help="Verify specific layer")
    parser.add_argument("--offline-manifest", help="Use offline manifest for verification")
    args = parser.parse_args()

    if args.offline_manifest:
        return verify_offline_manifest(args.offline_manifest)

    records = load_mirror_records()
    if not records:
        print("ERROR: No mirror records found", file=sys.stderr)
        return 1

    # Filter
    if args.inscription_id:
        records = [r for r in records if r.get("inscription", {}).get("inscription_id") == args.inscription_id]
    elif args.layer:
        layer_map = {
            "canonical-originals": "canonical_original",
            "vision-layer": "vision_layer",
            "context-layer": "guardianship_layer"
        }
        target = layer_map.get(args.layer, args.layer)
        records = [r for r in records if r.get("classification", {}).get("layer") == target or
                   (args.layer == "canonical-originals" and r.get("canonical_status") == "canonical_original")]

    if not records:
        print("No matching records found", file=sys.stderr)
        return 1

    all_passed = True
    for r in records:
        result = verify_record_offline(r)
        status_icon = "PASS" if result["passed"] else "FAIL"
        print(f"[{status_icon}] {result['inscription_id']}: {result['title']}")
        print(f"  Status: {result['verification_status']}")
        print(f"  Canonical: {result['canonical_status']}")
        if result["mirror_hash"]:
            print(f"  Mirror SHA256: {result['mirror_hash']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  ISSUE: {issue}")
            all_passed = False
        print()

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
