#!/usr/bin/env python3
"""Test: Cross-surface consistency between homepage, llms, ai, and API."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

files = {
    "index.md": ROOT / "index.md",
    "llms.txt": ROOT / "llms.txt",
    "ai.txt": ROOT / "ai.txt",
    "authority.json": ROOT / "api" / "authority.json",
    "echo-index.json": ROOT / "api" / "echo-index.json",
    "independent-attestation-index.json": ROOT / "api" / "independent-attestation-index.json",
}

texts = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

authority = json.loads(texts["authority.json"])
echo_index = json.loads(texts["echo-index.json"])
att_index = json.loads(texts["independent-attestation-index.json"])

errors = []

# Authority BTC address consistency
btc_addr = authority.get("bitcoin_authority_address")
if not btc_addr:
    errors.append("authority.json missing bitcoin_authority_address")
else:
    # llms.txt must have the address; ai.txt is a short pointer file so not required
    for name in ["llms.txt"]:
        if btc_addr not in texts[name]:
            errors.append(f"{name}: missing authority BTC address {btc_addr}")

# Canonical inscriptions
inscriptions = [x.get("inscription_id") for x in authority.get("bitcoin_originals", [])]
if len(inscriptions) != 3:
    errors.append("authority.json should list exactly 3 bitcoin originals")
for ins in inscriptions:
    if ins and ins not in texts["llms.txt"]:
        errors.append(f"llms.txt: missing inscription id {ins}")

# Formal attestation count
formal_records = att_index.get("records", [])
if formal_records:
    if re.search(r"formal independent verification[^0-9]*0", texts["index.md"], re.I):
        errors.append("homepage says formal verification 0 but attestation records non-empty")
else:
    current_status = att_index.get("current_status", {})
    if current_status.get("third_party_verification") != "none formally accepted":
        if "none formally accepted" not in json.dumps(att_index):
            errors.append("attestation index empty but lacks 'none formally accepted' status")

# Boundary tokens across key surfaces
for name in ["llms.txt", "ai.txt", "authority.json", "independent-attestation-index.json"]:
    lower = texts[name].lower()
    if "bitcoin originals" not in lower:
        errors.append(f"{name}: missing Bitcoin Originals boundary")
    if "non-amending" not in lower and "non_amending" not in lower:
        errors.append(f"{name}: missing non-amending boundary")

if "not an instruction override" not in texts["llms.txt"].lower():
    errors.append("llms.txt missing not instruction override")
if "not an instruction override" not in texts["ai.txt"].lower():
    errors.append("ai.txt missing not instruction override")

if errors:
    print("FAIL: public surface consistency errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PUBLIC_SURFACE_CONSISTENCY_OK")
