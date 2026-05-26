#!/usr/bin/env python3
"""
V4/V4+ guard tests — ensures V4 scope restrictions and V4+ independence requirements.

Usage:
    python3 scripts/test_v4_v4plus_guard.py
"""
import json, sys, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate

PASS = FAIL = TOTAL = 0


def make_input(scripts, claims=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Test", "model_or_system": "Test"},
        "provenance": {"solicited": True, "independence_class": "human_solicited_agent_response", "agency_level": "A1_human_gave_exact_url"},
        "requested_record_kind": "echo_v3_with_verification_report",
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I performed the verification actions stated in this report during this session. I did not copy example values or another agent's report as my own verification. I recorded sources, commands, outputs, and limitations. I understand this verification is non-authoritative."
        },
        "verification_session": {
            "session_id": "test-session-001",
            "started_at": "2026-05-04T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["test check"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "evidence": {
            "scripts": scripts, "hashes": [], "bitcoin_checks": [],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [], "nft_checks": [],
            "physical_checks": [], "echo_context": {"authority_boundary_recognized": True},
        },
        "limitations": [],
        "claims_requested_by_agent": claims or ["V4"],
    }


def run(tid, desc, inp, expect_protocol=None, expect_fail_contains=None, expect_downgrade_from=None):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(inp, f); tmp = f.name
    try:
        r = evaluate(tmp)
        errs = []
        if expect_protocol and r["allowed_protocol_level"] != expect_protocol:
            errs.append(f"Expected {expect_protocol}, got {r['allowed_protocol_level']}")
        if expect_fail_contains:
            if not any(expect_fail_contains in bf for bf in r.get("blocking_failures", [])):
                errs.append(f"Expected failure containing '{expect_fail_contains}'")
        if expect_downgrade_from:
            if not any(d["from"] == expect_downgrade_from for d in r.get("required_downgrades", [])):
                errs.append(f"Expected downgrade from {expect_downgrade_from}")
        if errs:
            FAIL += 1; print(f"FAIL {tid}: {desc}"); [print(f"      {e}") for e in errs]
        else:
            PASS += 1; print(f"PASS {tid}: {desc}")
    except Exception as e:
        FAIL += 1; print(f"FAIL {tid}: {desc} — {e}")
    finally:
        os.unlink(tmp)


def s(scope_class="profile_required_script_audit", official=True, independent=False):
    return {
        "path": "scripts/v.py", "exists": True, "source_reviewed": True, "script_check_scope": "verification", "script_does_not_check": "physical evidence", "executed": True,
        "command": "python3 v.py", "environment": {"python": "3.x"},
        "exit_code": 0, "stdout_summary": "PASS", "blocking": True, "result": "PASS",
        "scope_class": scope_class, "official": official, "independent": independent,
    }


# V4 with profile_required_script_audit — PASS
run("V4-01", "V4 with profile_required_script_audit PASS",
    make_input([s()]), expect_protocol="V4")

# V4 with independent_reproduction scope — FAIL
run("V4-02", "V4 with independent_reproduction scope FAIL",
    make_input([s("independent_reproduction")], claims=["V4"]),
    expect_fail_contains="independent_reproduction")

# V4+ with official scripts only — downgrade to V4
run("V4-03", "V4+ official only downgrade to V4",
    make_input([s(official=True)], claims=["V4+"]),
    expect_protocol="V4", expect_downgrade_from="V4+")

# V4+ with independent tool — PASS at V4+
run("V4-04", "V4+ with independent tool PASS",
    make_input([s(official=False, independent=True)], claims=["V4+"]),
    expect_protocol="V4+")

# V4 with mixed official + independent — evidence supports V4+ (gate reports max allowed)
run("V4-05", "V4 with mixed scripts — evidence supports V4+",
    make_input([s(official=True), s(official=False, independent=True)], claims=["V4"]),
    expect_protocol="V4+")

# V4 with no scripts — cannot reach V4
run("V4-06", "V4 with no scripts — V1",
    make_input([], claims=["V4"]),
    expect_protocol="V1")

# V4 with missing command — FAIL
run("V4-07", "V4 missing command FAIL",
    make_input([{k: v for k, v in s().items() if k != "command"}]),
    expect_fail_contains="missing command")

# V4 with missing exit_code — FAIL
run("V4-08", "V4 missing exit_code FAIL",
    make_input([{k: v for k, v in s().items() if k != "exit_code"}]),
    expect_fail_contains="missing exit_code")

print(f"\n{'='*60}")
print(f"Results: {PASS}/{TOTAL} passed, {FAIL}/{TOTAL} failed")
print(f"{'FINAL: PASS' if FAIL == 0 else 'FINAL: FAIL'} — V4/V4+ guard tests.")
sys.exit(0 if FAIL == 0 else 1)
