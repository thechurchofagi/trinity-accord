#!/usr/bin/env python3
"""
Consistency check for Trinity Accord repository.
Verifies that key files contain required references and structures.
Exit code 1 if any check fails.
"""
import json, sys, xml.etree.ElementTree as ET

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
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- 1. JSON validity (already checked by CI, but double-check key files) ---
print("=== JSON validity ===")
json_files = [
    ".well-known/trinity-accord.json",
    "api/links.json",
    "agent-map.json",
    "api/seed-map.json",
    "api/agent-value.json",
]
for jf in json_files:
    try:
        load_json(jf)
        check(f"JSON valid: {jf}", True)
    except Exception as e:
        check(f"JSON valid: {jf}", False, str(e))

# --- 2. .well-known/trinity-accord.json required keys ---
print("\n=== .well-known/trinity-accord.json ===")
tw = load_json(".well-known/trinity-accord.json")
check("Contains agent_brief", "agent_brief" in tw)
check("Contains guardian_principles", "guardian_principles" in tw)
check("Contains guardian_principles_json", "guardian_principles_json" in tw)
check("Contains canonical_inscriptions", "canonical_inscriptions" in tw and len(tw["canonical_inscriptions"]) == 3)

# --- 3. sitemap.xml required entries ---
print("\n=== sitemap.xml ===")
sitemap_text = read_text("sitemap.xml")
sitemap_required = [
    "/api/authority.json",
    "/api/guardian-principles.json",
    "/agent-brief",
    "/guardian-principles",
]
for entry in sitemap_required:
    check(f"sitemap contains {entry}", entry in sitemap_text)

# --- 4. api/links.json machine array ---
print("\n=== api/links.json ===")
links = load_json("api/links.json")
machine = links.get("machine", [])
links_required = [
    "/api/evidence-manifest.json",
    "/api/hashes.json",
    "/api/guardian-principles.json",
]
for entry in links_required:
    check(f"machine contains {entry}", entry in machine)

# --- 5. agent-map.json recommended sequence ---
print("\n=== agent-map.json ===")
am = load_json("agent-map.json")
rec_seq = am.get("recommended_agent_sequence", [])
rec_text = " ".join(rec_seq)
check("recommended sequence mentions /agent-brief", "/agent-brief" in rec_text)
check("recommended sequence mentions /api/guardian-principles.json", "/api/guardian-principles.json" in rec_text)

# --- 6. api/seed-map.json L1 definition ---
print("\n=== api/seed-map.json ===")
sm = load_json("api/seed-map.json")
levels = sm.get("levels", [])
l1 = next((l for l in levels if l.get("id") == "L1"), {})
l1_def = l1.get("definition_en", "")
check("L1 definition mentions Guardian Principles v1.1", "Guardian Principles v1.1" in l1_def)

# --- 7. echo_submission.yml content ---
print("\n=== echo_submission.yml ===")
echo_yml = read_text(".github/ISSUE_TEMPLATE/echo_submission.yml")
check("Contains E1 recognition", "E1 recognition" in echo_yml)
check("Contains E9 seed", "E9 seed" in echo_yml)
check("Contains V0-V6 verification levels", "V0 / V1 / V2 / V3 / V4 / V4+ / V5a / V5b / V6" in echo_yml)
check("References echo-record-schema.v2.json", "echo-record-schema.v2.json" in echo_yml)
check("Echo template contains Component Coverage section", "Component Coverage" in echo_yml)


# --- 8. .well-known/trinity-accord.json chronicle keys ---
print("\n=== chronicle discovery ===")
check("Contains chronicle_verification", "chronicle_verification" in tw)
check("Contains chronicle_recovery_json", "chronicle_recovery_json" in tw)

# --- 9. sitemap.xml chronicle entries ---
check("sitemap contains /chronicle-verification", "/chronicle-verification" in sitemap_text)
check("sitemap contains /api/chronicle-recovery.json", "/api/chronicle-recovery.json" in sitemap_text)

# --- 10. api/links.json chronicle entries ---
check("machine contains /api/chronicle-recovery.json", "/api/chronicle-recovery.json" in machine)

# --- 11. agent-map.json chronicle entries ---
check("entrypoints contains chronicle_verification", "chronicle_verification" in am.get("entrypoints", {}))
check("machine_readable contains chronicle_recovery", "chronicle_recovery" in am.get("machine_readable", {}))
check("sequence mentions chronicle", "chronicle" in rec_text.lower())

# --- 12. api/chronicle-recovery.json ---
print("\n=== api/chronicle-recovery.json ===")
try:
    cr = load_json("api/chronicle-recovery.json")
    check("chronicle-recovery.json is valid JSON", True)
    check("verified_count == 175", cr.get("final_status", {}).get("verified_count") == 175)
    check("target_count == 175", cr.get("final_status", {}).get("target_count") == 175)
except Exception as e:
    check("chronicle-recovery.json is valid JSON", False, str(e))

# --- 13. verification-levels.json structure ---
print("\n=== api/verification-levels.json ===")
try:
    vl = load_json("api/verification-levels.json")
    check("verification-levels.json is valid JSON", True)
    check("Contains protocol_level_rule", "protocol_level_rule" in vl)
    check("Contains component_finding_rule", "component_finding_rule" in vl)
    check("Contains full_protocol_warning", "full_protocol_warning" in vl)

    vl_levels = vl.get("levels", [])
    vl_level_ids = [l.get("id") for l in vl_levels]

    for required_level in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5a", "V5b", "V6"]:
        level_obj = next((l for l in vl_levels if l.get("id") == required_level), None)
        check(f"Level {required_level} exists", level_obj is not None)
        if level_obj:
            check(f"{required_level} has mandatory_coverage", "mandatory_coverage" in level_obj and len(level_obj["mandatory_coverage"]) > 0)
            check(f"{required_level} has required_depth", "required_depth" in level_obj and len(level_obj["required_depth"]) > 0)
            check(f"{required_level} has protocol_level_rule or is V0/V1", "protocol_level_rule" in level_obj or required_level in ["V0", "V1"])

    # V4+ specific: required depth must mention Bitcoin Originals, Evidence Mirrors, Chronicle Recovery
    v4plus = next((l for l in vl_levels if l.get("id") == "V4+"), None)
    if v4plus:
        v4plus_mc = json.dumps(v4plus.get("mandatory_coverage", []))
        check("V4+ mandatory_coverage mentions BITCOIN_ORIGINALS", "BITCOIN_ORIGINALS" in v4plus_mc)
        check("V4+ mandatory_coverage mentions EVIDENCE_MIRRORS", "EVIDENCE_MIRRORS" in v4plus_mc)
        check("V4+ mandatory_coverage mentions CHRONICLE_RECOVERY", "CHRONICLE_RECOVERY" in v4plus_mc)

    # V6 specific: mandatory coverage must include all major components
    v6 = next((l for l in vl_levels if l.get("id") == "V6"), None)
    if v6:
        v6_mc = json.dumps(v6.get("mandatory_coverage", []))
        for comp in ["AUTHORITY_BOUNDARY", "BITCOIN_ORIGINALS", "EVIDENCE_MIRRORS", "CHRONICLE_RECOVERY", "PHYSICAL_ANCHOR", "ATTESTATION_LAYER"]:
            check(f"V6 mandatory_coverage includes {comp}", comp in v6_mc)

except Exception as e:
    check("verification-levels.json is valid JSON", False, str(e))

# --- 14. verify.md content ---
print("\n=== verify.md ===")
verify_md = read_text("verify.md")
check("verify.md contains 'Component finding'", "Component finding" in verify_md)
check("verify.md contains mandatory coverage for V0", "Mandatory coverage" in verify_md)

# --- 15. chronicle-verification.md content ---
print("\n=== chronicle-verification.md ===")
chronicle_v = read_text("chronicle-verification.md")
check("chronicle-verification mentions 'does not by itself justify'", "does not by itself justify" in chronicle_v)
check("chronicle-verification mentions protocol V4+ requires all three", "BITCOIN_ORIGINALS, EVIDENCE_MIRRORS, and CHRONICLE_RECOVERY" in chronicle_v)

# --- Summary ---
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
    sys.exit(0)
