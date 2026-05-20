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
require(len(index) == 175, f"index should contain exactly 175 entries, found {len(index)}")

# Uniqueness check
seen_keys = set()
valid = 0
empty = []
missing = []
malformed = []

for item in index:
    contract = item.get("contract", "").lower()
    token_id = str(item.get("token_id", ""))
    key = (contract, token_id)
    if key in seen_keys:
        malformed.append(f"{key}: duplicate contract/token_id in index")
    else:
        seen_keys.add(key)

    file_name = item.get("file")
    if not file_name:
        malformed.append(f"{contract} {token_id}: missing file")
        continue
    p = DIR / file_name
    if not p.exists():
        missing.append(file_name)
        continue
    text = p.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        empty.append(file_name)
        continue
    if "# " not in text:
        malformed.append(f"{file_name}: missing '# ' heading")
        continue
    if "**Contract**:" not in text:
        malformed.append(f"{file_name}: missing '**Contract**:'")
        continue
    if "**Token ID**:" not in text:
        malformed.append(f"{file_name}: missing '**Token ID**:'")
        continue
    if "## Description" not in text:
        malformed.append(f"{file_name}: missing '## Description'")
        continue
    valid += 1

require(valid == 175, f"expected exactly 175 non-empty valid descriptions, found {valid}")
require(len(empty) == 0, f"empty description files found: {empty[:10]}")
require(len(missing) == 0, f"missing description files found: {missing[:10]}")
require(len(malformed) == 0, f"malformed description files found: {malformed[:10]}")

if errors:
    print("NFT_TEXT_DESCRIPTION_MIRROR_INTEGRITY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("NFT_TEXT_DESCRIPTION_MIRROR_INTEGRITY_OK")
