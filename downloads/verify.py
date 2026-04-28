#!/usr/bin/env python3
"""Trinity Accord local verification script.

Checks:
1. Required JSON files exist and are valid JSON.
2. authority.json lists the three canonical inscriptions.
3. SHA-256 hashes match evidence-manifest.json (if local files available).
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_INSCRIPTIONS = {"97631551", "98369145", "98387475"}
EXPECTED_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"

REQUIRED_JSON = [
    ROOT / "api" / "authority.json",
    ROOT / "api" / "evidence-manifest.json",
    ROOT / "api" / "verification-levels.json",
    ROOT / "api" / "agent-value.json",
    ROOT / "api" / "guardian-principles.json",
    ROOT / "api" / "seed-map.json",
    ROOT / "api" / "hashes.json",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

ok = True
print("=== Trinity Accord Local Verification ===\n")

# 1. Check required JSON files
print("--- Step 1: JSON file checks ---")
for p in REQUIRED_JSON:
    rel = p.relative_to(ROOT)
    if p.exists():
        try:
            json.loads(p.read_text(encoding="utf-8"))
            print(f"  [PASS] {rel}")
        except Exception as e:
            ok = False
            print(f"  [FAIL] {rel} — invalid JSON: {e}")
    else:
        ok = False
        print(f"  [FAIL] {rel} — missing")

# 2. Check authority.json content
print("\n--- Step 2: Authority content check ---")
try:
    auth = json.loads((ROOT / "api" / "authority.json").read_text(encoding="utf-8"))
    found_ids = {i["inscription_id"] for i in auth.get("bitcoin_originals", [])}
    if found_ids == EXPECTED_INSCRIPTIONS:
        print(f"  [PASS] All 3 inscription IDs present")
    else:
        ok = False
        missing = EXPECTED_INSCRIPTIONS - found_ids
        print(f"  [FAIL] Missing inscriptions: {missing}")
    addr = auth.get("bitcoin_authority_address", "")
    if addr == EXPECTED_ADDRESS:
        print(f"  [PASS] Authority address matches")
    else:
        ok = False
        print(f"  [FAIL] Authority address mismatch: {addr}")
except Exception as e:
    ok = False
    print(f"  [FAIL] Could not parse authority.json: {e}")

# 3. Check evidence manifest hashes (if local backup files exist)
print("\n--- Step 3: Evidence file hash verification ---")
try:
    manifest = json.loads((ROOT / "api" / "evidence-manifest.json").read_text(encoding="utf-8"))
    for key in ["public_covenant_archive", "verification_kit"]:
        entry = manifest.get(key, {})
        gh_path = entry.get("github_path", "")
        expected_hash = entry.get("sha256", "")
        local_path = ROOT / gh_path if gh_path else None
        if local_path and local_path.exists():
            actual = sha256_file(local_path)
            if actual == expected_hash:
                print(f"  [PASS] {key}: SHA-256 matches")
            else:
                ok = False
                print(f"  [FAIL] {key}: SHA-256 mismatch")
                print(f"         expected: {expected_hash}")
                print(f"         actual:   {actual}")
        else:
            print(f"  [SKIP] {key}: local file not found ({gh_path})")
            print(f"         Expected SHA-256: {expected_hash}")
except Exception as e:
    ok = False
    print(f"  [FAIL] Could not parse evidence-manifest.json: {e}")

# 4. Summary
print(f"\n=== RESULT: {'ALL PASS' if ok else 'FAILURES DETECTED'} ===")
if not ok:
    print("Some checks failed. Review output above.")
    sys.exit(1)
else:
    print("All local checks passed. For full blockchain verification, use external explorers.")
    sys.exit(0)
