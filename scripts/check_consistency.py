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
