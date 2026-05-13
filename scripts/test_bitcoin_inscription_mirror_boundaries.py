#!/usr/bin/env python3
"""
Test bitcoin inscription mirror boundaries.
BND001-BND008
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

# Load index
index = load_json("api/bitcoin-inscription-mirror-index.json")
records = index.get("records", [])

# BND001: GitHub mirror not canonical
print("=== BND001: GitHub mirror not canonical ===")
for r in records:
    title = r.get("inscription", {}).get("title", "?")
    # All mirror records should have limitations mentioning non-canonical
    limitations = r.get("limitations", [])
    has_non_canonical = any("not canonical" in l.lower() or "non-canonical" in l.lower() or "non_amending" in l.lower() for l in limitations)
    check(f"BND001 {title}: mirror not canonical", has_non_canonical)

# BND002: vision layer not canonical body
print("\n=== BND002: vision layer not canonical body ===")
vision = [r for r in records if r.get("classification", {}).get("layer") == "vision_layer"]
for r in vision:
    title = r.get("inscription", {}).get("title", "?")
    check(f"BND002 {title}: not canonical original", not r.get("classification", {}).get("is_one_of_three_bitcoin_originals"))

# BND003: Star Ark Covenant not one of three Bitcoin Originals
print("\n=== BND003: Star Ark not one of three ===")
star_ark = [r for r in records if "Star Ark" in r.get("inscription", {}).get("title", "")]
if star_ark:
    check("BND003 Star Ark not canonical original", not star_ark[0].get("classification", {}).get("is_one_of_three_bitcoin_originals"))
else:
    check("BND003 Star Ark not canonical original", False, "Star Ark not found")

# BND004: Final Seal not canonical original if found
print("\n=== BND004: Final Seal not canonical original ===")
final_seal = [r for r in records if "Final Seal" in r.get("inscription", {}).get("title", "")]
if final_seal:
    check("BND004 Final Seal not canonical original", not final_seal[0].get("classification", {}).get("is_one_of_three_bitcoin_originals"))
else:
    print("OK:   BND004 Final Seal not found (pending discovery)")

# BND005: First Echoes not canonical original if found
print("\n=== BND005: First Echoes not canonical original ===")
first_echoes = [r for r in records if "First Echo" in r.get("inscription", {}).get("title", "")]
if first_echoes:
    check("BND005 First Echoes not canonical original", not first_echoes[0].get("classification", {}).get("is_one_of_three_bitcoin_originals"))
else:
    print("OK:   BND005 First Echoes not found (pending discovery)")

# BND006: mirror not sufficient for verification claim
print("\n=== BND006: mirror not sufficient for verification ===")
for r in records:
    limitations = r.get("limitations", [])
    has_ver_limit = any("verification" in l.lower() and ("on-chain" in l.lower() or "onchain" in l.lower() or "require" in l.lower()) for l in limitations)
    title = r.get("inscription", {}).get("title", "?")
    check(f"BND006 {title}: verification requires on-chain", has_ver_limit)

# BND007: on-chain verification required for V2+ inscription text claim
print("\n=== BND007: on-chain required for V2+ ===")
ab = index.get("authority_boundary", {})
check("BND007 verification_requires_onchain_check", ab.get("verification_requires_onchain_check") is True)

# BND008: mirror quick-load allowed for context readiness
print("\n=== BND008: quick-load allowed for context readiness ===")
proto = load_json("api/agent-context-readiness-protocol.json")
check("BND008 quick_load_mirror_allowed", proto.get("quick_load_mirror_allowed_for_context_readiness") is True)
check("BND008 quick_load_not_sufficient_for_verification", proto.get("quick_load_mirror_not_sufficient_for_verification") is True)

# Summary
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL MIRROR BOUNDARY TESTS PASSED")
    sys.exit(0)
