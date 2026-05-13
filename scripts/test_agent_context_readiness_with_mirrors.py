#!/usr/bin/env python3
"""
Test agent context readiness with mirrors.
ACR001-ACR006
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def check(label, condition, detail=""):
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        errors.append(msg)
        print(msg)
    else:
        print(f"OK:   {label}")

def load_json(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

# ACR001: context readiness protocol requires mirror context pack
print("=== ACR001: protocol requires mirror pack ===")
clm = load_json("api/context-load-map.json")
must_load = clm.get("must_load_summary", [])
check("ACR001 mirror pack in must_load", any("bitcoin-inscription-mirrors" in p for p in must_load))

# ACR002: agent can reach CRL-3 with mirror quick-load and no verification claim
print("\n=== ACR002: CRL-3 with mirror quick-load ===")
crl = load_json("api/context-readiness-levels.json")
crl3 = next((l for l in crl.get("levels", []) if l.get("id") == "CRL-3"), None)
if crl3:
    check("ACR002 CRL-3 allows context statement", "context statement" in str(crl3.get("allowed_actions", [])))
else:
    check("ACR002 CRL-3 exists", False, "CRL-3 not found")

# ACR003: agent cannot claim V2+ from mirror-only content
print("\n=== ACR003: mirror-only cannot claim V2+ ===")
proto = load_json("api/agent-context-readiness-protocol.json")
check("ACR003 quick_load_not_sufficient_for_verification", proto.get("quick_load_mirror_not_sufficient_for_verification") is True)
check("ACR003 onchain_required_for_verification", proto.get("onchain_verification_required_for_verification_claims") is True)

# ACR004: vision layer loaded separately from core ontology
print("\n=== ACR004: vision layer separate from core ontology ===")
clm_packs = clm.get("must_load_summary", [])
has_core = any("core-ontology" in p for p in clm_packs)
has_vision = any("vision-layer" in p for p in clm_packs)
check("ACR004 core-ontology in must_load", has_core)
check("ACR004 vision-layer in must_load", has_vision)

# ACR005: legacy archive remains read_index_not_full_load
print("\n=== ACR005: legacy archive read_index_not_full_load ===")
read_index = clm.get("read_index_not_full_load", [])
check("ACR005 legacy-archive-index in read_index", any("legacy-archive-index" in p for p in read_index))

# ACR006: NFT context remains deferred unless pack prepared
print("\n=== ACR006: NFT context deferred ===")
deferred = clm.get("deferred", [])
check("ACR006 nft-chronicle-context in deferred", any("nft-chronicle" in p for p in deferred))

# Summary
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL AGENT CONTEXT READINESS WITH MIRRORS TESTS PASSED")
    sys.exit(0)
