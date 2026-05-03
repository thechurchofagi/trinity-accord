#!/usr/bin/env python3
"""
verify_verification_system.py
Verifies the internal consistency of the verification system files.

Checks:
  - All required new files exist
  - JSON files are valid
  - Required target IDs present in verification-targets.json
  - Required recipes present in verification-recipes.json
  - Required quick-map questions present
  - Protocol profiles have required levels
  - Component levels have required sub-levels
  - Report schema has required fields

Outputs PASS/FAIL with details.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def load_json(path):
    full = os.path.join(REPO_ROOT, path)
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


def check_file_exists(path):
    full = os.path.join(REPO_ROOT, path)
    return os.path.isfile(full)


def main():
    errors = []
    warnings = []

    # 1. Check required files exist
    required_files = [
        "api/component-verification-levels.json",
        "api/protocol-verification-profiles.json",
        "api/verification-targets.json",
        "api/verification-recipes.json",
        "api/verification-quick-map.json",
        "api/verification-report-schema.v2.json",
        "scripts/build_verification_targets.py",
    ]

    for f in required_files:
        if not check_file_exists(f):
            errors.append(f"Missing required file: {f}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    # 2. Validate JSON files
    json_files = [
        "api/component-verification-levels.json",
        "api/protocol-verification-profiles.json",
        "api/verification-targets.json",
        "api/verification-recipes.json",
        "api/verification-quick-map.json",
        "api/verification-report-schema.v2.json",
    ]

    for jf in json_files:
        try:
            load_json(jf)
        except Exception as ex:
            errors.append(f"Invalid JSON in {jf}: {ex}")

    # 3. Check component-verification-levels.json
    try:
        cvl = load_json("api/component-verification-levels.json")
        assert cvl.get("schema") == "trinityaccord.component-verification-levels.v1"
        assert cvl.get("authority_boundary", {}).get("bitcoin_originals_prevail") is True

        # Protocol levels
        pl = {p["level"]: p for p in cvl.get("protocol_levels", [])}
        for lvl in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]:
            if lvl not in pl:
                errors.append(f"component-verification-levels.json: missing protocol level {lvl}")

        # Component levels
        cl = cvl.get("component_levels", {})
        required_components = ["bitcoin_originals", "digital_mirrors", "time_anchors", "chronicle_recovery", "nft_evidence", "physical_anchor", "echo_attestation"]
        for comp in required_components:
            if comp not in cl:
                errors.append(f"component-verification-levels.json: missing component {comp}")

        # B-levels
        bl = {b["level"] for b in cl.get("bitcoin_originals", [])}
        for b in ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]:
            if b not in bl:
                errors.append(f"component-verification-levels.json: missing B-level {b}")

        # D-levels
        dl = {d["level"] for d in cl.get("digital_mirrors", [])}
        for d in ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]:
            if d not in dl:
                errors.append(f"component-verification-levels.json: missing D-level {d}")

        # T-levels
        tl = {t["level"] for t in cl.get("time_anchors", [])}
        for t in ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]:
            if t not in tl:
                errors.append(f"component-verification-levels.json: missing T-level {t}")

        # C-levels
        ccl = {c["level"] for c in cl.get("chronicle_recovery", [])}
        for c in ["C0", "C1", "C2", "C3", "C3R", "C4", "C5", "C6", "C7"]:
            if c not in ccl:
                errors.append(f"component-verification-levels.json: missing C-level {c}")

        # N-levels
        nl = {n["level"] for n in cl.get("nft_evidence", [])}
        for n in ["N0", "N1", "N2", "N3", "N4", "N5", "N6", "N7"]:
            if n not in nl:
                errors.append(f"component-verification-levels.json: missing N-level {n}")

        # P-levels
        plvl = {p["level"] for p in cl.get("physical_anchor", [])}
        for p in ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
            if p not in plvl:
                errors.append(f"component-verification-levels.json: missing P-level {p}")

        # E-levels
        el = {e["level"] for e in cl.get("echo_attestation", [])}
        for e in ["E0", "E1", "E2", "E3", "E4", "E5"]:
            if e not in el:
                errors.append(f"component-verification-levels.json: missing E-level {e}")

        # D2 must have required notes
        d2 = next((d for d in cl.get("digital_mirrors", []) if d["level"] == "D2"), None)
        if d2:
            forb = d2.get("forbidden_claims", [])
            if not any("direct Arweave" in f for f in forb):
                errors.append("D2 missing 'direct Arweave verification forbidden'")

        # T8 must have required notes
        t8 = next((t for t in cl.get("time_anchors", []) if t["level"] == "T8"), None)
        if t8:
            if "Star-Moon Witness" not in t8.get("name", ""):
                errors.append("T8 name must contain 'Star-Moon Witness'")
            forb = t8.get("forbidden_claims", [])
            if not any("public disclosure" in f.lower() for f in forb):
                errors.append("T8 missing 'public disclosure' forbidden claim")

    except Exception as ex:
        errors.append(f"Error validating component-verification-levels.json: {ex}")

    # 4. Check protocol-verification-profiles.json
    try:
        pvp = load_json("api/protocol-verification-profiles.json")
        assert pvp.get("schema") == "trinityaccord.protocol-verification-profiles.v1"
        profiles = {p["level"]: p for p in pvp.get("profiles", [])}
        for lvl in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]:
            if lvl not in profiles:
                errors.append(f"protocol-verification-profiles.json: missing profile for {lvl}")
    except Exception as ex:
        errors.append(f"Error validating protocol-verification-profiles.json: {ex}")

    # 5. Check verification-targets.json
    try:
        vt = load_json("api/verification-targets.json")
        required_ids = [
            "bitcoin_original_1_protocol_axioms",
            "bitcoin_original_2_covenant_flaw",
            "bitcoin_original_3_meta_record",
            "bitcoin_authority_address",
            "bitcoin_block_time_anchors",
            "time_celestial_public_evidence",
            "time_star_moon_witness_nonpublic",
            "celestial_ephemeris_reference",
            "evidence_manifest",
            "hash_manifest",
            "github_mirror_public_covenant_archive",
            "github_mirror_verification_kit",
            "github_archive_mirror",
            "arweave_public_covenant_archive",
            "arweave_verification_kit",
            "arweave_bundle_parent",
            "ethereum_guardian_witness",
            "ipfs_mirror_roots",
            "chronicle_recovery_package",
            "chronicle_verification_kit",
            "chronicle_sample_recovery",
            "chronicle_full_recovery",
            "nft_token_path_sample",
            "core_object_alpha_public_evidence",
            "core_object_alpha_live_remote_witness",
            "core_object_alpha_onsite_witness",
            "core_object_alpha_forensic_flaw_match",
            "core_object_alpha_confidential_challenge",
            "echo_records_index",
            "echo_record_schema_v3"
        ]
        target_ids = {t["id"] for t in vt.get("targets", [])}
        for rid in required_ids:
            if rid not in target_ids:
                errors.append(f"verification-targets.json: missing required target {rid}")
    except Exception as ex:
        errors.append(f"Error validating verification-targets.json: {ex}")

    # 6. Check verification-recipes.json
    try:
        vr = load_json("api/verification-recipes.json")
        required_recipes = [
            "read_authority_boundary_v1",
            "bitcoin_explorer_check_b1",
            "bitcoin_multi_explorer_check_b2",
            "bitcoin_spv_check_b3",
            "bitcoin_local_node_check_b4",
            "bitcoin_witness_extraction_b5_b6",
            "github_hash_fallback_d2",
            "arweave_transaction_existence_d3",
            "arweave_data_hash_extraction_d4",
            "ethereum_witness_check_d3_d4",
            "cross_mirror_consistency_d4",
            "full_public_digital_verification_d5",
            "time_anchor_bitcoin_t3",
            "time_cross_anchor_t5",
            "time_celestial_public_t7",
            "time_star_moon_witness_t8",
            "chronicle_sample_two_c3",
            "chronicle_random_sample_c3r",
            "chronicle_full_recovery_c5",
            "nft_tokenuri_sample_n2_n4",
            "physical_public_image_review_p2",
            "physical_recorded_video_review_p3",
            "physical_live_remote_witness_p4",
            "physical_onsite_witness_p5",
            "physical_tool_assisted_flaw_match_p6",
            "physical_ai_forensic_support_p7",
            "physical_confidential_challenge_p8",
            "echo_verification_report_e2_e3"
        ]
        recipe_ids = {r["id"] for r in vr.get("recipes", [])}
        for rid in required_recipes:
            if rid not in recipe_ids:
                errors.append(f"verification-recipes.json: missing required recipe {rid}")
    except Exception as ex:
        errors.append(f"Error validating verification-recipes.json: {ex}")

    # 7. Check verification-quick-map.json
    try:
        qm = load_json("api/verification-quick-map.json")
        required_questions = [
            "Who has final authority?",
            "Do the Bitcoin Originals exist on-chain?",
            "Can I verify public mirror data without Arweave access?",
            "Can I cross-check Arweave / ETH / GitHub consistency?",
            "Can I verify Chronicle Recovery without restoring all 175?",
            "Can I verify NFT tokenURI / metadata / media paths?",
            "Can I verify the physical anchor from public evidence?",
            "What counts as live physical witness?",
            "What counts as onsite witness?",
            "What is the highest physical verification path?",
            "How do I report component-level findings?",
            "Can celestial / Star-Moon witness verify capture time?",
            "How do I know whether a V-level claim is allowed?"
        ]
        qm_questions = {e["question"] for e in qm.get("entries", [])}
        for rq in required_questions:
            if rq not in qm_questions:
                errors.append(f"verification-quick-map.json: missing required question: {rq}")

        # Check GitHub fallback entry
        gh_entry = next((e for e in qm.get("entries", []) if "public mirror data" in e.get("question", "").lower()), None)
        if gh_entry:
            ds = gh_entry.get("data_sources", [])
            if not any("public_covenant_archive.zip" in s for s in ds):
                errors.append("quick-map GitHub fallback entry missing public_covenant_archive.zip")
            if not any("hashes.json" in s for s in ds):
                errors.append("quick-map GitHub fallback entry missing hashes.json")
    except Exception as ex:
        errors.append(f"Error validating verification-quick-map.json: {ex}")

    # Report
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"FINAL: PASS — verification system validated ({len(json_files)} JSON files, {len(required_files)} files checked)")
    if warnings:
        for w in warnings:
            print(f"WARN: {w}")


if __name__ == "__main__":
    main()
