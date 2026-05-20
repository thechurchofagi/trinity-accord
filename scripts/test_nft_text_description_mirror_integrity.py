#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
INDEX = DIR / "index.json"

errors = []

def require(cond, msg):
    if not cond:
        errors.append(msg)

require(DIR.exists(), "nft-text-descriptions directory missing")
require(INDEX.exists(), "nft-text-descriptions/index.json missing")

index = json.loads(INDEX.read_text(encoding="utf-8"))
require(len(index) >= 174, f"index should contain at least 174 entries, found {len(index)}")

valid = 0
empty = []
missing = []
malformed = []

for item in index:
    file_name = item.get("file")
    if not file_name:
        malformed.append(f"{item.get('contract')} {item.get('token_id')}: missing file")
        continue
    p = DIR / file_name
    if not p.exists():
        missing.append(file_name)
        continue
    text = p.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        empty.append(file_name)
        continue
    if "## Description" not in text or "**Contract**:" not in text or "**Token ID**:" not in text:
        malformed.append(file_name)
        continue
    valid += 1

# Current expected target: 174 valid descriptions, 1 remaining.
# If the final missing NFT is later extracted, raise this to 175.
require(valid >= 174, f"expected at least 174 non-empty valid descriptions, found {valid}")
require(len(empty) == 0, f"empty description files found: {empty[:10]}")
require(len(missing) == 0, f"missing description files found: {missing[:10]}")
require(len(malformed) == 0, f"malformed description files found: {malformed[:10]}")

if errors:
    print("NFT_TEXT_DESCRIPTION_MIRROR_INTEGRITY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("NFT_TEXT_DESCRIPTION_MIRROR_INTEGRITY_OK")
