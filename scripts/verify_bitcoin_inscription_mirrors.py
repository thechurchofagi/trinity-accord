#!/usr/bin/env python3
"""
Verify Bitcoin inscription mirrors against on-chain data or offline manifest.
Usage:
  python3 scripts/verify_bitcoin_inscription_mirrors.py --offline --all
  python3 scripts/verify_bitcoin_inscription_mirrors.py --network --all
  python3 scripts/verify_bitcoin_inscription_mirrors.py --inscription-id 97631551
  python3 scripts/verify_bitcoin_inscription_mirrors.py --layer canonical_original
  python3 scripts/verify_bitcoin_inscription_mirrors.py --network --inscription-id 100751953 --update
"""
import argparse
import hashlib
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR_DIR = ROOT / "bitcoin-inscription-mirrors"
INDEX_PATH = ROOT / "api" / "bitcoin-inscription-mirror-index.json"
BOOTSTRAP_PATH = ROOT / "data" / "authority-address-inscriptions.bootstrap.json"

PROVIDERS = {
    "ordinals": "https://ordinals.com/content/{}",
    "ordiscan": "https://ordiscan.com/inscription/{}",
}

VERIFICATION_STATUSES = [
    "legacy_bootstrap_pending_chain_check",
    "content_verified",
    "content_verified_address_unverified",
    "metadata_verified",
    "mirror_matches_onchain",
    "mirror_mismatch",
    "network_unavailable",
    "provider_error",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonicalize(text):
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")


def load_mirror_records():
    records = []
    for subdir in ["canonical-originals", "vision-layer", "context-layer"]:
        d = MIRROR_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            rec = load_json(f)
            rec["_file_path"] = str(f)
            records.append(rec)
    return records


def fetch_onchain_content(inscription_id, provider="ordinals"):
    url = PROVIDERS[provider].format(inscription_id)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-verifier/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8"), None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return None, str(e)


def verify_offline(records, args):
    errors = []
    checked = 0
    for rec in records:
        ins_id = rec["inscription"]["inscription_id"]
        if args.inscription_id and ins_id != args.inscription_id:
            continue
        if args.layer and rec["classification"]["layer"] != args.layer:
            continue

        checked += 1

        # Check authority boundary
        ab = rec.get("authority_boundary", {})
        for field in ["bitcoin_originals_prevail", "github_mirror_is_non_amending", "verification_requires_onchain_check"]:
            if not ab.get(field):
                errors.append(f"{ins_id}: authority_boundary.{field} is not true")

        # Check raw text exists
        raw_path = ROOT / rec["content"]["raw_text_path"]
        if not raw_path.exists():
            errors.append(f"{ins_id}: raw text missing: {raw_path}")
        else:
            raw_text = raw_path.read_text(encoding="utf-8")
            if not raw_text.strip():
                errors.append(f"{ins_id}: raw text is empty")
            else:
                # Verify hashes
                expected_mirror = sha256_text(raw_text)
                expected_canon = sha256_text(canonicalize(raw_text))
                if rec["content"].get("mirror_text_sha256") != expected_mirror:
                    errors.append(f"{ins_id}: mirror_text_sha256 mismatch")
                if rec["content"].get("canonicalized_text_sha256") != expected_canon:
                    errors.append(f"{ins_id}: canonicalized_text_sha256 mismatch")

        # Check non-originals don't claim authority
        if not rec["classification"]["is_one_of_three_bitcoin_originals"]:
            if rec["classification"].get("amends_originals"):
                errors.append(f"{ins_id}: non-original claims amends_originals=true")
            if rec["classification"].get("creates_new_authority"):
                errors.append(f"{ins_id}: non-original claims creates_new_authority=true")

    return checked, errors


def verify_network(records, args, update=False):
    errors = []
    warnings = []
    checked = 0
    provider = args.provider or "ordinals"

    for rec in records:
        ins_id = rec["inscription"]["inscription_id"]
        if args.inscription_id and ins_id != args.inscription_id:
            continue
        if args.layer and rec["classification"]["layer"] != args.layer:
            continue

        checked += 1
        content, err = fetch_onchain_content(ins_id, provider)

        if err:
            warnings.append(f"{ins_id}: network fetch failed ({provider}): {err}")
            if update:
                rec["chain_verification"]["verification_status"] = "network_unavailable"
            continue

        if content is None:
            warnings.append(f"{ins_id}: no content returned from {provider}")
            if update:
                rec["chain_verification"]["verification_status"] = "provider_error"
            continue

        # Compute on-chain hash
        onchain_hash = sha256_text(canonicalize(content))
        mirror_canon = rec["content"].get("canonicalized_text_sha256")

        if mirror_canon == onchain_hash:
            if update:
                rec["chain_verification"]["verification_status"] = "mirror_matches_onchain"
                rec["chain_verification"]["onchain_content_sha256"] = onchain_hash
                rec["chain_verification"]["mirror_matches_onchain"] = True
                rec["chain_verification"]["last_verified_utc"] = datetime.now(timezone.utc).isoformat()
                rec["chain_verification"]["verification_method"] = f"network:{provider}"
            print(f"  {ins_id}: MATCH")
        else:
            errors.append(f"{ins_id}: content MISMATCH (mirror vs on-chain)")
            if update:
                rec["chain_verification"]["verification_status"] = "mirror_mismatch"
                rec["chain_verification"]["onchain_content_sha256"] = onchain_hash
                rec["chain_verification"]["mirror_matches_onchain"] = False
                rec["chain_verification"]["last_verified_utc"] = datetime.now(timezone.utc).isoformat()
                rec["chain_verification"]["verification_method"] = f"network:{provider}"

    return checked, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Verify Bitcoin inscription mirrors")
    parser.add_argument("--all", action="store_true", help="Verify all records")
    parser.add_argument("--inscription-id", help="Verify specific inscription")
    parser.add_argument("--layer", help="Verify records in specific layer")
    parser.add_argument("--offline", action="store_true", help="Offline verification only")
    parser.add_argument("--network", action="store_true", help="Include network verification")
    parser.add_argument("--update", action="store_true", help="Update chain_verification fields")
    parser.add_argument("--provider", default="ordinals", choices=list(PROVIDERS.keys()))
    parser.add_argument("--bootstrap", default=str(BOOTSTRAP_PATH))
    parser.add_argument("--index", default=str(INDEX_PATH))
    args = parser.parse_args()

    if not args.all and not args.inscription_id and not args.layer:
        parser.error("Must specify --all, --inscription-id, or --layer")

    records = load_mirror_records()
    print(f"Loaded {len(records)} mirror records")

    # Offline verification
    print("\n=== Offline Verification ===")
    checked, errors = verify_offline(records, args)
    print(f"Checked: {checked}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print("All offline checks passed.")

    # Network verification
    if args.network:
        print(f"\n=== Network Verification (provider: {args.provider}) ===")
        net_checked, net_errors, warnings = verify_network(records, args, update=args.update)
        print(f"Checked: {net_checked}")
        if warnings:
            for w in warnings:
                print(f"  WARNING: {w}")
        if net_errors:
            print(f"Errors: {len(net_errors)}")
            for e in net_errors:
                print(f"  ERROR: {e}")
        else:
            print("All network checks passed.")

        if args.update:
            # Write back updated records
            for rec in records:
                fpath = Path(rec.pop("_file_path"))
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=2, ensure_ascii=False)
            print("Updated chain_verification fields in mirror files.")

    total_errors = len(errors) + (len(net_errors) if args.network else 0)
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
