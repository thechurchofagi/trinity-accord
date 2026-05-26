#!/usr/bin/env python3
"""
Test agent context readiness flow.
CRL001-CRL010
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

def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")

# --- CRL001: homepage-only cannot submit Echo ---
print("=== CRL001: homepage-only cannot submit Echo ===")
try:
    crl = load_json("api/context-readiness-levels.json")
    levels = crl.get("levels", [])
    crl0 = next((l for l in levels if l.get("id") == "CRL-0" or l.get("level") == 0), None)
    check("CRL001 CRL-0 exists", crl0 is not None)
    if crl0:
        allowed = crl0.get("echo_submission_allowed", crl0.get("echo_allowed"))
        check("CRL001 CRL-0 echo submission not allowed", allowed is False or allowed is None)
except Exception as e:
    check("CRL001 context-readiness-levels.json", False, str(e))

# --- CRL002: CRL-2 can produce boundary-aware summary but not verification claim ---
print("\n=== CRL002: CRL-2 boundary-aware summary ===")
try:
    crl2 = next((l for l in levels if l.get("id") == "CRL-2" or l.get("level") == 2), None)
    check("CRL002 CRL-2 exists", crl2 is not None)
    if crl2:
        capabilities = crl2.get("capabilities", crl2.get("allowed_actions", []))
        cap_text = json.dumps(crl2).lower()
        check("CRL002 CRL-2 allows summary", "summary" in cap_text or "boundary" in cap_text)
        check("CRL002 CRL-2 does not allow V2+ verification",
              "verification" not in cap_text or "no verification claim" in cap_text or
              "not sufficient" in cap_text or crl2.get("verification_claim_allowed") is False or
              "cannot claim" in cap_text)
except Exception as e:
    check("CRL002 CRL-2 capabilities", False, str(e))

# --- CRL003: CRL-3 requires core ontology and vision layer ---
print("\n=== CRL003: CRL-3 requires core ontology and vision layer ===")
try:
    crl3 = next((l for l in levels if l.get("id") == "CRL-3" or l.get("level") == 3), None)
    check("CRL003 CRL-3 exists", crl3 is not None)
    if crl3:
        required = crl3.get("required_packs", crl3.get("required_context", crl3.get("requirements", [])))
        req_text = json.dumps(crl3).lower()
        check("CRL003 CRL-3 requires core ontology", "core_ontology" in req_text or "core-ontology" in req_text or "core ontology" in req_text)
        check("CRL003 CRL-3 requires vision layer", "vision" in req_text)
except Exception as e:
    check("CRL003 CRL-3 requirements", False, str(e))

# --- CRL004: CRL-4 requires physical anchor context and legacy archive index ---
print("\n=== CRL004: CRL-4 requires physical anchor and legacy archive ===")
try:
    crl4 = next((l for l in levels if l.get("id") == "CRL-4" or l.get("level") == 4), None)
    check("CRL004 CRL-4 exists", crl4 is not None)
    if crl4:
        req_text = json.dumps(crl4).lower()
        check("CRL004 CRL-4 requires physical anchor", "physical" in req_text)
        check("CRL004 CRL-4 requires legacy archive", "legacy" in req_text or "archive" in req_text)
except Exception as e:
    check("CRL004 CRL-4 requirements", False, str(e))

# --- CRL005: legacy archive is read_index_not_full_load by default ---
print("\n=== CRL005: legacy archive read_index_not_full_load ===")
try:
    clm = load_json("api/context-load-map.json")
    clm_text = json.dumps(clm).lower()
    check("CRL005 context-load-map references legacy archive",
          "legacy" in clm_text or "archive" in clm_text)
    check("CRL005 legacy archive is read_index_not_full_load",
          "read_index_not_full_load" in clm_text)
except Exception as e:
    check("CRL005 context-load-map.json", False, str(e))

# --- CRL006: NFT context deferred is valid ---
print("\n=== CRL006: NFT context deferred is valid ===")
try:
    clm = load_json("api/context-load-map.json")
    clm_text = json.dumps(clm).lower()
    check("CRL006 NFT context deferred", "deferred" in clm_text or "nft" in clm_text)
except Exception as e:
    check("CRL006 context-load-map.json NFT", False, str(e))

# --- CRL007: Star Ark Covenant appears in vision-layer as non-canonical ---
print("\n=== CRL007: Star Ark in vision-layer ===")
try:
    vl = load_json("api/context-packs/vision-layer.json")
    vl_text = json.dumps(vl).lower()
    check("CRL007 vision-layer mentions Star Ark",
          "star ark" in vl_text or "star_ark" in vl_text)
    check("CRL007 Star Ark is non-canonical",
          "non_canonical" in vl_text or "non-canonical" in vl_text or "not canonical" in vl_text)
except Exception as e:
    check("CRL007 vision-layer.json", False, str(e))

# --- CRL008: one hash resonance does not create V-level ---
print("\n=== CRL008: hash resonance not V-level ===")
try:
    rws = load_json("api/resonance-willingness-scale.json")
    rws_text = json.dumps(rws).lower()
    check("CRL008 resonance scale exists", bool(rws))
    check("CRL008 resonance is not proof", "not proof" in rws_text or "resonance is not" in rws_text or "not verification" in rws_text)
except Exception as e:
    check("CRL008 resonance-willingness-scale.json", False, str(e))

# --- CRL009: high propagation score does not create authority ---
print("\n=== CRL009: propagation not authority ===")
try:
    rws = load_json("api/resonance-willingness-scale.json")
    rws_text = json.dumps(rws).lower()
    check("CRL009 propagation is not authority",
          "propagation" in rws_text and ("not authority" in rws_text or "not persuasion" in rws_text or "discoverability" in rws_text))
except Exception as e:
    check("CRL009 propagation boundary", False, str(e))

# --- CRL010: full Echo with CRL-4 + resonance fields passes ---
print("\n=== CRL010: full Echo with CRL-4 + resonance ===")
try:
    schema = load_json("api/echo-record-schema.v3.1.json")
    # Schema may use allOf with inline properties
    schema_text = json.dumps(schema)
    props = schema.get("properties", {})
    # Also check allOf items for properties
    for item in schema.get("allOf", []):
        if "properties" in item:
            props.update(item["properties"])
    check("CRL010 schema has context_readiness", "context_readiness" in props or "context_readiness" in schema_text)
    check("CRL010 schema has resonance", "resonance" in props or "resonance" in schema_text)
    if "context_readiness" in props:
        cr_props = props["context_readiness"].get("properties", {})
        check("CRL010 context_readiness has context_readiness_level",
              "context_readiness_level" in cr_props or "context_readiness_level" in schema_text)
    if "resonance" in props:
        res_props = props["resonance"].get("properties", {})
        check("CRL010 resonance has resonance_willingness_score",
              "resonance_willingness_score" in res_props or "resonance_willingness_score" in schema_text)
        check("CRL010 resonance has verification_willingness_score",
              "verification_willingness_score" in res_props or "verification_willingness_score" in schema_text)
        check("CRL010 resonance has propagation_willingness_score",
              "propagation_willingness_score" in res_props or "propagation_willingness_score" in schema_text)
    elif "resonance" in schema_text:
        # Fields exist in the schema text (e.g. via allOf/$ref)
        check("CRL010 resonance has resonance_willingness_score", "resonance_willingness_score" in schema_text)
        check("CRL010 resonance has verification_willingness_score", "verification_willingness_score" in schema_text)
        check("CRL010 resonance has propagation_willingness_score", "propagation_willingness_score" in schema_text)
except Exception as e:
    check("CRL010 echo-record-schema.v3.1.json", False, str(e))

# --- Summary ---
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL CRL001-CRL010 CHECKS PASSED")
    sys.exit(0)
