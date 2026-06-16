#!/usr/bin/env python3
"""Test cross-surface public consistency."""
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
    "independent-attestation-index.json": ROOT / "api" / "independent-attestation-index.json",
}
texts = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
authority = json.loads(texts["authority.json"])
att_index = json.loads(texts["independent-attestation-index.json"])
errors = []
if not authority.get("bitcoin_authority_address"):
    errors.append("authority.json missing bitcoin_authority_address")
inscriptions = [x.get("inscription_id") for x in authority.get("bitcoin_originals", [])]
if len(inscriptions) != 3:
    errors.append("authority.json should list exactly 3 bitcoin originals")
for ins in inscriptions:
    if ins and ins not in texts["llms.txt"]:
        errors.append(f"llms.txt: missing inscription id {ins}")
formal_records = att_index.get("records", [])
if formal_records:
    if re.search(r"formal independent verification[^0-9]*0", texts["index.md"], re.I):
        errors.append("homepage says formal verification 0 but attestation records non-empty")
else:
    current_status = att_index.get("current_status", {})
    if current_status.get("third_party_verification") != "none formally accepted":
        if "none formally accepted" not in json.dumps(att_index):
            errors.append("attestation index empty but lacks status")
for name in ["llms.txt", "ai.txt", "authority.json", "independent-attestation-index.json"]:
    lower = texts[name].lower()
    if "bitcoin originals" not in lower:
        errors.append(f"{name}: missing Bitcoin Originals boundary")
    if "non-amending" not in lower and "non_amending" not in lower:
        errors.append(f"{name}: missing non-amending boundary")
if errors:
    print("FAIL: public surface consistency errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("PUBLIC_SURFACE_CONSISTENCY_OK")
