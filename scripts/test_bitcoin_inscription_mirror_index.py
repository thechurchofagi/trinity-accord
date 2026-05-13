#!/usr/bin/env python3
"""
Test bitcoin inscription mirror index.
MIR001-MIR010
"""
import json, sys, subprocess
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

# MIR001: mirror schema valid
print("=== MIR001: mirror schema valid ===")
try:
    schema = load_json("api/bitcoin-inscription-mirror-schema.v1.json")
    schema_id = schema.get("$id", schema.get("schema", ""))
    check("MIR001 mirror schema valid",
          "bitcoin-inscription-mirror" in schema_id or "bitcoin-inscription-mirror" in schema.get("title", ""))
except Exception as e:
    check("MIR001 mirror schema valid", False, str(e))

# MIR002: index generated
print("\n=== MIR002: index generated ===")
try:
    index = load_json("api/bitcoin-inscription-mirror-index.json")
    check("MIR002 index generated", index.get("schema") == "trinityaccord.bitcoin-inscription-mirror-index.v1")
except Exception as e:
    check("MIR002 index generated", False, str(e))

# MIR003: exactly three canonical originals
print("\n=== MIR003: exactly three canonical originals ===")
canonical_count = index.get("counts", {}).get("canonical_originals", 0)
check("MIR003 exactly three canonical originals", canonical_count == 3, f"found {canonical_count}")

# MIR004: Star Ark Covenant exists in vision layer
print("\n=== MIR004: Star Ark Covenant in vision layer ===")
vision_records = [r for r in index.get("records", []) if r.get("classification", {}).get("layer") == "vision_layer"]
star_ark = [r for r in vision_records if "Star Ark" in r.get("inscription", {}).get("title", "")]
check("MIR004 Star Ark Covenant in vision layer", len(star_ark) > 0)

# MIR005: non-canonical records have amends_originals=false
print("\n=== MIR005: non-canonical amends_originals=false ===")
non_canonical = [r for r in index.get("records", []) if r.get("canonical_status") != "canonical_original"]
all_non_amending = all(not r.get("classification", {}).get("amends_originals") for r in non_canonical)
check("MIR005 non-canonical amends_originals=false", all_non_amending)

# MIR006: non-canonical records have creates_new_authority=false
print("\n=== MIR006: non-canonical creates_new_authority=false ===")
all_no_new_auth = all(not r.get("classification", {}).get("creates_new_authority") for r in non_canonical)
check("MIR006 non-canonical creates_new_authority=false", all_no_new_auth)

# MIR007: every record has raw_text_path or discovered_unverified status
print("\n=== MIR007: raw_text_path or discovered_unverified ===")
for r in index.get("records", []):
    has_raw = bool(r.get("content", {}).get("raw_text_path"))
    status = r.get("chain_verification", {}).get("verification_status", "")
    title = r.get("inscription", {}).get("title", "?")
    check(f"MIR007 {title}: raw or unverified", has_raw or status == "discovered_unverified" or status == "not_checked")

# MIR008: every verified record has content hash
print("\n=== MIR008: verified records have content hash ===")
for r in index.get("records", []):
    status = r.get("chain_verification", {}).get("verification_status", "")
    if status == "verified_onchain_match":
        has_hash = bool(r.get("content", {}).get("mirror_text_sha256"))
        title = r.get("inscription", {}).get("title", "?")
        check(f"MIR008 {title}: verified has hash", has_hash)

# MIR009: index counts match records
print("\n=== MIR009: index counts match records ===")
counts = index.get("counts", {})
records = index.get("records", [])
actual_canonical = len([r for r in records if r.get("canonical_status") == "canonical_original"])
actual_vision = len([r for r in records if r.get("classification", {}).get("layer") == "vision_layer"])
check("MIR009 canonical count matches", counts.get("canonical_originals") == actual_canonical)
check("MIR009 vision count matches", counts.get("vision_layer") == actual_vision)

# MIR010: GitHub mirror boundary present
print("\n=== MIR010: GitHub mirror boundary present ===")
ab = index.get("authority_boundary", {})
check("MIR010 github_mirrors_non_amending", ab.get("github_mirrors_non_amending") is True)
check("MIR010 verification_requires_onchain_check", ab.get("verification_requires_onchain_check") is True)

# MIR011: source_address matches authority.json bitcoin_authority_address
print("\n=== MIR011: source_address matches authority address ===")
try:
    auth = json.loads((ROOT / "api/authority.json").read_text(encoding="utf-8"))
    real_addr = auth.get("bitcoin_authority_address", "")
    check("MIR011 authority address is not placeholder", real_addr != "bc1p_trinity_accord_authority")
    check("MIR011 authority address is not empty", len(real_addr) > 10)
    for rec in records:
        sa = rec.get("inscription", {}).get("source_address", "")
        if sa:
            check(f"MIR011 {rec.get('inscription',{}).get('inscription_id','?')} source_address matches authority",
                  sa == real_addr, f"got {sa[:30]}... expected {real_addr[:30]}...")
except Exception as e:
    check("MIR011 source_address check", False, str(e))

# MIR012: canonical original txids match authority.json
print("\n=== MIR012: canonical original txids match authority.json ===")
try:
    auth = json.loads((ROOT / "api/authority.json").read_text(encoding="utf-8"))
    originals = {str(o["inscription_id"]): o["txid"] for o in auth.get("bitcoin_originals", [])}
    for rec in records:
        if rec.get("classification", {}).get("is_one_of_three_bitcoin_originals"):
            iid = rec.get("inscription", {}).get("inscription_id", "")
            mirror_txid = rec.get("inscription", {}).get("txid")
            auth_txid = originals.get(iid)
            check(f"MIR012 canonical {iid} txid present", mirror_txid is not None and mirror_txid != "")
            check(f"MIR012 canonical {iid} txid matches authority.json",
                  mirror_txid == auth_txid, f"mirror={mirror_txid} auth={auth_txid}")
except Exception as e:
    check("MIR012 canonical txid check", False, str(e))

# MIR013: no placeholder authority address remains
print("\n=== MIR013: no placeholder authority address ===")
try:
    placeholder = "bc1p_trinity_accord_authority"
    all_jsons = list((ROOT / "bitcoin-inscription-mirrors").rglob("*.json"))
    all_jsons.append(ROOT / "api" / "bitcoin-inscription-mirror-index.json")
    found_placeholder = False
    for jf in all_jsons:
        text = jf.read_text(encoding="utf-8")
        if placeholder in text:
            check(f"MIR013 no placeholder in {jf.name}", False, f"found '{placeholder}'")
            found_placeholder = True
    if not found_placeholder:
        check("MIR013 no placeholder authority address in any mirror file", True)
except Exception as e:
    check("MIR013 placeholder check", False, str(e))

# Summary
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL MIRROR INDEX TESTS PASSED")
    sys.exit(0)
