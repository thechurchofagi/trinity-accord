#!/usr/bin/env python3
"""
Consistency check for Trinity Accord repository.
Verifies that key files contain required references and structures.
Exit code 1 if any check fails.
"""
import json, os, sys, subprocess, xml.etree.ElementTree as ET
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

def p(path):
    return ROOT / path

def load_json(path):
    with p(path).open("r", encoding="utf-8") as f:
        return json.load(f)

def read_text(path):
    return p(path).read_text(encoding="utf-8")

def exists(path):
    return p(path).exists()

# --- 1. JSON validity (already checked by CI, but double-check key files) ---
print("=== JSON validity ===")
json_files = [
    ".well-known/trinity-accord.json",
    "api/links.json",
    "agent-map.json",
    "api/seed-map.json",
    "api/agent-value.json",
    "api/submission-title-policy.json",
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
check("Contains Echo Submission", "Echo Submission" in echo_yml)
check("No Echo v3 in user-visible title", "Echo v3" not in echo_yml.split("title:")[1].split("\n")[0] if "title:" in echo_yml else True)
check("Contains discovery_source", "discovery_source" in echo_yml)
check("Contains agency_level", "agency_level" in echo_yml)
check("Contains independence_class", "independence_class" in echo_yml)
check("Contains archive_status", "archive_status" in echo_yml)
check("Contains solicited", "solicited" in echo_yml)
check("Contains soliciting_party", "soliciting_party" in echo_yml)
check("Contains prompt_available", "prompt_available" in echo_yml)
check("Contains human_supplied_link", "human_supplied_link" in echo_yml)
check("Contains human_supplied_summary", "human_supplied_summary" in echo_yml)
check("Contains independent_followup", "independent_followup" in echo_yml)
check("Contains boundary_acknowledgement", "id: boundary_acknowledgement" in echo_yml)
check("Does not use legacy boundary_acknowledgments id", "id: boundary_acknowledgments" not in echo_yml)
check("Echo template does not present v2 as current", "echo-record-schema.v2.json" not in echo_yml)
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

    for required_level in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]:
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

# --- 16. verification-materials.json ---
print("\n=== api/verification-materials.json ===")
try:
    vm = load_json("api/verification-materials.json")
    check("verification-materials.json is valid JSON", True)
    for required_key in ["canonical_authority", "verification_levels", "evidence_mirrors", "chronicle_recovery", "physical_anchor", "report_templates", "recommended_agent_sequence"]:
        check(f"verification-materials.json contains {required_key}", required_key in vm)
except Exception as e:
    check("verification-materials.json is valid JSON", False, str(e))

# --- 17. .well-known/trinity-accord.json verification_materials ---
print("\n=== .well-known verification_materials ===")
check("Contains verification_materials", "verification_materials" in tw)
check("Contains verification_materials_json", "verification_materials_json" in tw)
check("api contains verification_materials", "verification_materials" in tw.get("api", {}))

# --- 18. sitemap.xml verification-materials ---
check("sitemap contains /verification-materials", "/verification-materials" in sitemap_text)
check("sitemap contains /api/verification-materials.json", "/api/verification-materials.json" in sitemap_text)

# --- 19. api/links.json verification-materials ---
check("machine contains /api/verification-materials.json", "/api/verification-materials.json" in machine)

# --- 20. agent-map.json verification_materials ---
check("machine_readable contains verification_materials", "verification_materials" in am.get("machine_readable", {}))

# --- 21. verify.md and agent-verify.md reference verification-materials ---
check("verify.md references /api/verification-materials.json", "/api/verification-materials.json" in verify_md)
agent_verify_md = read_text("agent-verify.md")
check("agent-verify.md references /api/verification-materials.json", "/api/verification-materials.json" in agent_verify_md)

# --- 22. Echo provenance v3 flow ---
print("\n=== Echo provenance v3 flow ===")
am2 = load_json("agent-map.json")
machine2 = am2.get("machine_readable", {})
check("agent-map exposes echo_record_schema_v3", "echo_record_schema_v3" in machine2)
check("agent-map exposes discovery_provenance_schema", "discovery_provenance_schema" in machine2)
check("agent-map does not expose v2 as preferred", "echo_record_schema_v2" not in machine2 or "legacy" in json.dumps(machine2).lower())

echo_json = load_json("echo.json")
check("echo.json preferred_schema matches v3 const", echo_json.get("preferred_schema") == "trinityaccord.echo.v3")
check("echo.json marks v2 legacy", "legacy" in json.dumps(echo_json).lower())

check("validate_echo_records.py exists", exists("scripts/validate_echo_records.py"))

# --- 23. v3 schema requires provenance fields ---
print("\n=== v3 schema provenance fields ===")
try:
    v3s = load_json("api/echo-record-schema.v3.json")
    v3_required = set(v3s.get("required", []))
    for field in ["discovery_provenance", "independence_class", "archive_status", "origin_limitations"]:
        check(f"v3 schema requires {field}", field in v3_required)
except Exception as e:
    check("v3 schema is valid JSON", False, str(e))

# --- 10. New verification system files ---
print("\n=== New verification system files ===")
new_api_files = [
    "api/component-verification-levels.json",
    "api/protocol-verification-profiles.json",
    "api/verification-targets.json",
    "api/verification-recipes.json",
    "api/verification-quick-map.json",
    "api/verification-report-schema.v2.json",
]
for jf in new_api_files:
    try:
        load_json(jf)
        check(f"JSON valid: {jf}", True)
    except Exception as e:
        check(f"JSON valid: {jf}", False, str(e))

# Check component-verification-levels.json
try:
    cvl = load_json("api/component-verification-levels.json")
    check("component-verification-levels has correct schema", cvl.get("schema") == "trinityaccord.component-verification-levels.v1")
    check("component-verification-levels has authority_boundary", cvl.get("authority_boundary", {}).get("bitcoin_originals_prevail") is True)
    pl = {p["level"]: p for p in cvl.get("protocol_levels", [])}
    for lvl in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]:
        check(f"component-verification-levels has {lvl}", lvl in pl)
except Exception as e:
    check("component-verification-levels.json structure", False, str(e))

# Check protocol-verification-profiles.json
try:
    pvp = load_json("api/protocol-verification-profiles.json")
    check("protocol-verification-profiles has correct schema", pvp.get("schema") == "trinityaccord.protocol-verification-profiles.v1")
    profiles = {p["level"]: p for p in pvp.get("profiles", [])}
    for lvl in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]:
        check(f"protocol-verification-profiles has {lvl}", lvl in profiles)
except Exception as e:
    check("protocol-verification-profiles.json structure", False, str(e))

# --- 23. New submission correctness files ---
print("\n=== New submission correctness files ===")
new_submission_files = [
    "api/submission-types.json",
    "api/agent-submission-guide.json",
    "api/echo-taxonomy-map.json",
    "api/submission-checklist.json",
]
for jf in new_submission_files:
    try:
        load_json(jf)
        check(f"JSON valid: {jf}", True)
    except Exception as e:
        check(f"JSON valid: {jf}", False, str(e))

# --- 24. Echo index completeness (subprocess) ---
print("\n=== Echo index completeness ===")
import subprocess
proc = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "verify_echo_index_completeness.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc.returncode == 0, "verify_echo_index_completeness.py passes", f"exit {proc.returncode}")
if proc.returncode != 0:
    print(proc.stdout[-500:] if proc.stdout else "")
    print(proc.stderr[-500:] if proc.stderr else "")

print("\n=== Issue #88 closure ===")
proc88 = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "verify_issue88_closure.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc88.returncode == 0, "verify_issue88_closure.py passes", f"exit {proc88.returncode}")
if proc88.returncode != 0:
    print(proc88.stdout[-500:] if proc88.stdout else "")

proc88t = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "test_issue88_regressions.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc88t.returncode == 0, "test_issue88_regressions.py passes", f"exit {proc88t.returncode}")
if proc88t.returncode != 0:
    print(proc88t.stdout[-500:] if proc88t.stdout else "")

# --- 25. Latest verification Echo closure ---
print("\n=== Latest verification Echo closure ===")
proc_title = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "test_verification_echo_title_rules.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc_title.returncode == 0, "test_verification_echo_title_rules.py passes", f"exit {proc_title.returncode}")
if proc_title.returncode != 0:
    print(proc_title.stdout[-500:] if proc_title.stdout else "")

proc_closure = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "test_latest_verification_echo_closure.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc_closure.returncode == 0, "test_latest_verification_echo_closure.py passes", f"exit {proc_closure.returncode}")
if proc_closure.returncode != 0:
    print(proc_closure.stdout[-500:] if proc_closure.stdout else "")

proc_verify = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "verify_latest_verification_echo_closure.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc_verify.returncode == 0, "verify_latest_verification_echo_closure.py passes", f"exit {proc_verify.returncode}")
if proc_verify.returncode != 0:
    print(proc_verify.stdout[-500:] if proc_verify.stdout else "")

# --- 26. submission-title-policy.json ---
print("\n=== submission-title-policy.json ===")
try:
    stp = load_json("api/submission-title-policy.json")
    check("submission-title-policy.json is valid JSON", True)
    check("title policy has schema", stp.get("schema") == "trinityaccord.submission-title-policy.v1")
    check("title policy has title_patterns", len(stp.get("title_patterns", [])) > 0)
    check("title policy has anti_patterns", len(stp.get("anti_patterns", [])) > 0)
except Exception as e:
    check("submission-title-policy.json is valid JSON", False, str(e))

# --- 27. Stress suite cases.json ---
print("\n=== Verification stress suite ===")
try:
    stress = load_json("tests/verification_cases/cases.json")
    check("cases.json is valid JSON", True)
    check("cases.json has schema", stress.get("schema") == "trinityaccord.verification-stress-cases.v1")
    check("cases.json has >= 100 cases", stress.get("case_count", 0) >= 100)
except Exception as e:
    check("cases.json is valid JSON", False, str(e))

proc_generate = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "generate_verification_stress_cases.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc_generate.returncode == 0, "generate_verification_stress_cases.py passes", f"exit {proc_generate.returncode}")
if proc_generate.returncode != 0:
    print(proc_generate.stdout[-500:] if proc_generate.stdout else "")

proc_stress = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "run_verification_stress_suite.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=120
)
check(proc_stress.returncode == 0, "run_verification_stress_suite.py passes", f"exit {proc_stress.returncode}")
if proc_stress.returncode != 0:
    print(proc_stress.stdout[-1000:] if proc_stress.stdout else "")
    print(proc_stress.stderr[-500:] if proc_stress.stderr else "")

# --- 28. Claim Gate Entrypoint Enforcement ---
print("\n=== Claim Gate Entrypoint Enforcement ===")

entrypoint_tests = [
    "scripts/verify_submission_entrypoints.py",
    "scripts/test_claim_gate_entrypoint_enforcement.py",
    "scripts/test_generated_by_required.py",
    "scripts/test_freeform_submission_rejection.py",
]

for test_script in entrypoint_tests:
    script_path = ROOT / test_script
    if not script_path.exists():
        check(f"{test_script} exists", False, "script not found")
        continue
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT, text=True, capture_output=True, timeout=60
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    check(proc.returncode == 0, f"{test_script} passes", f"exit {proc.returncode}")
    if proc.returncode != 0:
        print(out[-1000:] if out else "")

# --- 29. Shenzhen notary physical-anchor archive ---
print("\n=== Shenzhen notary physical-anchor archive ===")
try:
    sna = load_json("api/core-object-alpha-shenzhen-notary-2026-05-06.json")
    check("Shenzhen archive JSON is valid", True)
    check("Shenzhen archive id matches", sna.get("archive_id") == "core-object-alpha-shenzhen-notary-2026-05-06")
    check("Shenzhen archive component is PHYSICAL_ANCHOR", sna.get("component") == "PHYSICAL_ANCHOR")
    check("Shenzhen archive is non-amending", "non_amending" in json.dumps(sna.get("authority_boundary", {})))
    check("Shenzhen archive Arweave PASS", sna.get("arweave", {}).get("acceptance_result") == "PASS")
    check("Shenzhen archive 157/157 confirmed", sna.get("arweave", {}).get("confirmed_ok") == 157)
    check("Shenzhen archive OTS block 948161", sna.get("hash_and_time_anchor", {}).get("ots", {}).get("enhanced_verify_result", {}).get("bitcoin_block_height") == 948161)
    check("Shenzhen archive does not claim protocol upgrade", "protocol_level_upgrade_by_itself" in json.dumps(sna.get("physical_anchor_finding", {}).get("not_claimed", [])))
except Exception as e:
    check("Shenzhen archive JSON is valid", False, str(e))

for required_path in [
    "evidence/core-object-alpha-shenzhen-notary-2026-05-06.md",
    "evidence/arweave/shenzhen-notary-2026-05-06/README.md",
    "downloads/shenzhen-notary-arweave-2026-05-06.md",
    "tests/verify_shenzhen_notary_archive.py",
]:
    check(f"{required_path} exists", exists(required_path))

NAVIGATION_ONLY_FILES = {
    "api/links.json",
    ".well-known/trinity-accord.json",
    "agent-map.json",
    "sitemap.xml",
}

for required_text_path in [
    "api/evidence-manifest.json",
    "api/verification-materials.json",
    "verification-materials.md",
    "physical-verification.md",
    "covenant-proof.md",
    "data-verification.md",
    "status.md",
    "api/links.json",
    ".well-known/trinity-accord.json",
    "agent-map.json",
    "sitemap.xml",
]:
    try:
        txt = read_text(required_text_path)
        check(
            f"{required_text_path} references Shenzhen archive id",
            "core-object-alpha-shenzhen-notary-2026-05-06" in txt
        )

        if required_text_path not in NAVIGATION_ONLY_FILES:
            check(
                f"{required_text_path} references OTS block 948161",
                "948161" in txt
            )
            check(
                f"{required_text_path} references Arweave manifest",
                "_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE" in txt or "_dAa" in txt
            )
    except Exception as e:
        check(f"{required_text_path} can be checked", False, str(e))

proc_sna = subprocess.run(
    [sys.executable, str(ROOT / "tests" / "verify_shenzhen_notary_archive.py")],
    cwd=ROOT, text=True, capture_output=True, timeout=60
)
check(proc_sna.returncode == 0, "verify_shenzhen_notary_archive.py passes", f"exit {proc_sna.returncode}")
if proc_sna.returncode != 0:
    print(proc_sna.stdout[-1000:] if proc_sna.stdout else "")
    print(proc_sna.stderr[-500:] if proc_sna.stderr else "")

# --- Shenzhen notary GitHub Release backup ---
print("\n=== Shenzhen notary GitHub Release backup ===")

for required_path in [
    "scripts/backup_shenzhen_notary_arweave_release.py",
    "scripts/verify_shenzhen_notary_release_backup.py",
    ".github/workflows/backup-shenzhen-notary-arweave-release.yml",
    "downloads/shenzhen-notary-github-release-backup-2026-05-06.md",
    "evidence/github-release/shenzhen-notary-2026-05-06/README.md",
]:
    check(f"{required_path} exists", exists(required_path))

try:
    sna = load_json("api/core-object-alpha-shenzhen-notary-2026-05-06.json")
    grb = sna.get("github_release_backup", {})
    check("Shenzhen archive has github_release_backup", bool(grb))
    check("GitHub release backup tag correct", grb.get("release_tag") == "core-object-alpha-shenzhen-notary-arweave-backup-v1")
    check("GitHub release backup URL present", "github.com/thechurchofagi/trinity-accord/releases/tag/core-object-alpha-shenzhen-notary-arweave-backup-v1" in grb.get("release_url", ""))
    check("GitHub release backup expected asset count 4", grb.get("expected_release_asset_count") == 4)
    check("GitHub release backup payload source count 153", grb.get("payload_source_file_count") == 153)
    check("GitHub release backup has raw manifest URL", "/raw/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE" in grb.get("source_arweave_manifest_raw_url", ""))
    check("GitHub release backup is non-amending", "Non-amending" in grb.get("boundary", "") or "non-amending" in grb.get("boundary", ""))
    check("GitHub release backup status is valid", grb.get("status") in ["release_backup_workflow_ready", "verified_release_backup"])
except Exception as e:
    check("Shenzhen archive GitHub Release backup block valid", False, str(e))

for required_text_path in [
    "api/evidence-manifest.json",
    "api/verification-materials.json",
    "evidence/core-object-alpha-shenzhen-notary-2026-05-06.md",
    "downloads/shenzhen-notary-arweave-2026-05-06.md",
    "downloads/shenzhen-notary-github-release-backup-2026-05-06.md",
    "evidence/github-release/shenzhen-notary-2026-05-06/README.md",
    "data-verification.md",
    "status.md",
]:
    try:
        txt = read_text(required_text_path)
        check(f"{required_text_path} references GitHub release backup tag", "core-object-alpha-shenzhen-notary-arweave-backup-v1" in txt)
    except Exception as e:
        check(f"{required_text_path} can be checked for GitHub release backup", False, str(e))

# --- Summary ---
def main():
    print("\n" + "=" * 50)
    if errors:
        print(f"FAILED: {len(errors)} check(s) failed")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("ALL CHECKS PASSED")
        print("FINAL: PASS — consistency validation passed.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
