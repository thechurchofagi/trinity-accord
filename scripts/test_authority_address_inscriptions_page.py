#!/usr/bin/env python3
"""Test: authority-address-inscriptions.md page content."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "authority-address-inscriptions.md"

EXPECTED_IDS = ["97631551", "98369145", "98387475", "100385359", "100550942", "100751953", "103034280", "103635270"]

errors = []

if not PAGE.exists():
    print("FAIL: page does not exist")
    sys.exit(1)

content = PAGE.read_text(encoding="utf-8")

# Permalink
if "permalink: /authority-address-inscriptions/" not in content:
    errors.append("missing permalink /authority-address-inscriptions/")

# All 8 inscription IDs
for ins_id in EXPECTED_IDS:
    if ins_id not in content:
        errors.append(f"missing inscription ID: {ins_id}")

# States only first three are canonical authority
if "Only the first three are canonical authority" not in content and "only the first three" not in content.lower():
    errors.append("does not state only first three are canonical authority")

# States pre-Original out of scope
if "pre-Original" not in content and "pre_original" not in content:
    errors.append("does not mention pre-Original inscriptions out of scope")

# States later inscriptions non-amending
if "non-amending" not in content:
    errors.append("does not state later inscriptions are non-amending")

# Links to API
if "bitcoin-inscription-mirror-index.json" not in content:
    errors.append("does not link to API index")

# Includes verification commands
if "verify_bitcoin_inscription_mirrors.py" not in content:
    errors.append("does not include verification commands")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: authority address inscriptions page test")
    sys.exit(0)
