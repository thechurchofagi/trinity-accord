#!/usr/bin/env python3
"""
Claim downgrade suggestion tests.

Usage:
    python3 scripts/test_claim_downgrade_suggestions.py
"""
import json, sys, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate

PASS = FAIL = TOTAL = 0


def make_input(evidence_overrides=None, claims=None, provenance_overrides=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Test", "model_or_system": "Test"},
        "provenance": {
            "solicited": True, "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url", **(provenance_overrides or {})
        },
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


def run(tid, desc, inp, expect_downgrades=None):
    """expect_downgrades: list of (from, to) tuples"""
    global PASS, FAIL, TOTAL
    TOTAL += 1
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(inp, f); tmp = f.name
    try:
        r = evaluate(tmp)
        downgrades = r.get("required_downgrades", [])
        errs = []
        for frm, to in (expect_downgrades or []):
            found = any(d["from"] == frm and d["to"] == to for d in downgrades)
            if not found:
                errs.append(f"Expected downgrade {frm} -> {to} not found in {downgrades}")
        if errs:
            FAIL += 1; print(f"FAIL {tid}: {desc}"); [print(f"      {e}") for e in errs]
        else:
            PASS += 1; print(f"PASS {tid}: {desc}")
    except Exception as e:
        FAIL += 1; print(f"FAIL {tid}: {desc} — {e}")
    finally:
        os.unlink(tmp)


# V4+ official only → downgrade to V4
run("CD-01", "V4+ official only → V4",
    make_input(
        {"scripts": [{"path": "scripts/v.py", "exists": True, "source_reviewed": True,
                       "executed": True, "command": "python3 v.py", "environment": {"python": "3.x"},
                       "exit_code": 0, "stdout_summary": "PASS", "blocking": True, "result": "PASS",
                       "official": True, "script_check_scope": "hash verification",
                       "script_does_not_check": "physical evidence"}]},
        claims=["V4+"]),
    expect_downgrades=[("V4+", "V4")])

# V4+ independent tool → no downgrade
run("CD-02", "V4+ independent tool → no downgrade",
    make_input(
        {"scripts": [{"path": "scripts/v.py", "exists": True, "source_reviewed": True,
                       "executed": True, "command": "python3 v.py", "environment": {"python": "3.x"},
                       "exit_code": 0, "stdout_summary": "PASS", "blocking": True, "result": "PASS",
                       "official": False, "independent": True,
                       "script_check_scope": "hash verification",
                       "script_does_not_check": "physical evidence"}]},
        claims=["V4+"]),
    expect_downgrades=[])

# B1 local manifest only → allowed level V1 (no explicit protocol requested, so no downgrade entry)
run("CD-03", "B1 local manifest only → allowed level V1",
    make_input({"bitcoin_checks": [{"source_type": "local_manifest", "sources": ["api/authority.json"]}]},
               claims=["B1"]),
    expect_downgrades=[])

# Requested V5 with insufficient evidence → downgrade
run("CD-04", "V5 insufficient evidence → downgrade",
    make_input(claims=["V5"]),
    expect_downgrades=[("V5", "V1")])

print(f"\n{'='*60}")
print(f"Results: {PASS}/{TOTAL} passed, {FAIL}/{TOTAL} failed")
print(f"{'FINAL: PASS' if FAIL == 0 else 'FINAL: FAIL'} — claim downgrade suggestion tests.")
sys.exit(0 if FAIL == 0 else 1)
