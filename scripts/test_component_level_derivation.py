#!/usr/bin/env python3
"""
Component level derivation tests — verifies B/D/T/C/P level logic.

Usage:
    python3 scripts/test_component_level_derivation.py
"""
import json, sys, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate

PASS = FAIL = TOTAL = 0


def make_input(evidence_overrides=None, claims=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Test", "model_or_system": "Test"},
        "provenance": {"solicited": True, "independence_class": "human_solicited_agent_response", "agency_level": "A1_human_gave_exact_url"},
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [], "hashes": [], "bitcoin_checks": [],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [], "nft_checks": [],
            "physical_checks": [], "echo_context": {},
            **(evidence_overrides or {})
        },
        "limitations": [],
        "claims_requested_by_agent": claims or ["V1"],
    }


def run(tid, desc, inp, expect_comp, expect_level):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(inp, f); tmp = f.name
    try:
        r = evaluate(tmp)
        actual = r["allowed_component_levels"].get(expect_comp, "?")
        if actual == expect_level:
            PASS += 1; print(f"PASS {tid}: {desc} ({expect_comp}={actual})")
        else:
            FAIL += 1; print(f"FAIL {tid}: {desc} — expected {expect_comp}={expect_level}, got {actual}")
    except Exception as e:
        FAIL += 1; print(f"FAIL {tid}: {desc} — {e}")
    finally:
        os.unlink(tmp)


# B-levels
run("CL-B0", "No bitcoin checks → B0", make_input(), "bitcoin_originals", "B0")
run("CL-B1", "External explorer → B1",
    make_input({"bitcoin_checks": [{"source_type": "external_explorer", "sources": ["mempool.space"]}]}),
    "bitcoin_originals", "B1")
run("CL-B2", "Multi explorer → B2",
    make_input({"bitcoin_checks": [{"source_type": "multi_explorer", "sources": ["mempool.space", "ordiscan"]}]}),
    "bitcoin_originals", "B2")
run("CL-B5", "Witness extraction → B5",
    make_input({"bitcoin_checks": [{"source_type": "witness_extraction", "raw_witness_extracted": True}]}),
    "bitcoin_originals", "B5")
run("CL-B6", "Body hash reproduced → B6",
    make_input({"bitcoin_checks": [{"source_type": "body_hash", "body_hash_reproduced": True}]}),
    "bitcoin_originals", "B6")

# D-levels
run("CL-D0", "No digital checks → D0", make_input(), "digital_mirrors", "D0")
SHA = "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263"
run("CL-D2", "Valid hash → D2",
    make_input({"hashes": [{"artifact": "test.zip", "artifact_class": "canonical_mirror",
                             "algorithm": "SHA-256", "expected": SHA, "computed": SHA,
                             "expected_hash_source": "api/hashes.json",
                             "expected_hash_authority_class": "canonical_manifest_hash", "match": True}]}),
    "digital_mirrors", "D2")
run("CL-D2-FAIL", "Hash mismatch → D0",
    make_input({"hashes": [{"artifact": "test.zip", "artifact_class": "canonical_mirror",
                             "algorithm": "SHA-256", "expected": SHA,
                             "computed": "0000000000000000000000000000000000000000000000000000000000000000",
                             "expected_hash_source": "api/hashes.json",
                             "expected_hash_authority_class": "canonical_manifest_hash", "match": False}]}),
    "digital_mirrors", "D0")

# T-levels
run("CL-T0", "No time checks → T0", make_input(), "time_anchors", "T0")
run("CL-T1", "GitHub commit → T1",
    make_input({"time_anchor_checks": [{"anchor_type": "github_commit_timestamp"}]}),
    "time_anchors", "T1")
run("CL-T3", "Bitcoin block → T3",
    make_input({"time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}]}),
    "time_anchors", "T3")

# P-levels
run("CL-P0", "No physical → P0", make_input(), "physical_verification", "P0")
run("CL-P4", "Live remote with nonce → P4",
    make_input({"physical_checks": [{"level_evidence_type": "live_remote", "nonce_challenge": {"c": "x"}}]}),
    "physical_verification", "P4")
run("CL-P3", "Recorded video → P3",
    make_input({"physical_checks": [{"level_evidence_type": "recorded_video"}]}),
    "physical_verification", "P3")

print(f"\n{'='*60}")
print(f"Results: {PASS}/{TOTAL} passed, {FAIL}/{TOTAL} failed")
print(f"{'FINAL: PASS' if FAIL == 0 else 'FINAL: FAIL'} — component level derivation tests.")
sys.exit(0 if FAIL == 0 else 1)
