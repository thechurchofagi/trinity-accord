#!/usr/bin/env python3
"""Test: Bitcoin inscription mirror stack is linked from public entrypoints."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

errors = []

# Test 1: index.md links to authority-address-inscriptions
index = (ROOT / "index.md").read_text(encoding="utf-8")
if "/authority-address-inscriptions/" not in index:
    errors.append("index.md: missing link to /authority-address-inscriptions/")
if "bitcoin-inscription-mirror-index.json" not in index:
    errors.append("index.md: missing link to mirror index")

# Test 2: well-known links both page and API
wk = json.loads((ROOT / ".well-known" / "trinity-accord.json").read_text(encoding="utf-8"))
if "/authority-address-inscriptions/" not in json.dumps(wk):
    errors.append("well-known: missing authority_address_inscriptions")
if "/api/bitcoin-inscription-mirror-index.json" not in json.dumps(wk):
    errors.append("well-known: missing bitcoin_inscription_mirror_index")

# Test 3: llms.txt links both page and API
llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
if "/authority-address-inscriptions/" not in llms:
    errors.append("llms.txt: missing link to /authority-address-inscriptions/")
if "bitcoin-inscription-mirror-index.json" not in llms:
    errors.append("llms.txt: missing link to mirror index")

# Test 4: agent-brief mentions stack boundary
brief = (ROOT / "agent-brief.md").read_text(encoding="utf-8")
if "stack boundary" not in brief.lower() and "inscription stack" not in brief.lower():
    errors.append("agent-brief.md: missing inscription stack boundary")

# Test 5: api/links.json includes page and API
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))
links_str = json.dumps(links)
if "/authority-address-inscriptions" not in links_str:
    errors.append("api/links.json: missing /authority-address-inscriptions")
if "bitcoin-inscription-mirror-index.json" not in links_str:
    errors.append("api/links.json: missing mirror index")

# Test 6: None say all eight are canonical authority
all_files_content = index + llms + brief
if "all eight are canonical" in all_files_content.lower():
    errors.append("public files incorrectly state all eight are canonical")
if "all 8 are canonical" in all_files_content.lower():
    errors.append("public files incorrectly state all 8 are canonical")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: entrypoints test")
    sys.exit(0)
