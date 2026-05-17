#!/usr/bin/env python3
"""Combined regression test for full-path agent bugfixes."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_CONTACT = ROOT / "api" / "agent-first-contact.json"
QUICKSTART = ROOT / "external-agent-quickstart.md"
AGENT_SUBMIT = ROOT / "agent-submit.md"
SUBMISSION_GUIDE = ROOT / "api" / "agent-submission-guide.json"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"


def run_validator(payload_path):
    result = subprocess.run(
        ["python3", str(VALIDATOR), str(payload_path)],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout + result.stderr


def make_valid_agent_declared():
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "agent_identity": {
            "name_or_model": "Test Agent",
            "system_or_provider": "Test System",
            "self_reported": True,
        },
        "title": "Agent-Declared Verification Archive: V4 — Test",
        "body": "Agent-declared V4 template-pass archive. Evidence requirements are waived for V0-V5.",
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
        },
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "record_intent": "auto_archive_candidate",
        "claim_gate": {
            "status": "PASS",
            "mode": "template_for_v0_v5",
            "allowed_protocol_level": "V4",
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "I understand this is not an exam or performance. I will only state what I actually checked, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True,
            },
        },
        "discovery_provenance": {
            "source": "self_initiated",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "independence_class": "unsolicited_agent_discovery",
        },
        "origin_classification": {
            "discovery_class": "unsolicited_discovery",
            "performer_class": "ai_agent",
            "verification_claimed": True,
            "counts_as_ai_verification": True,
        },
        "claim_classification": {
            "verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False},
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {
            "verifiability": True,
            "reception": True,
            "basis": "agent_declared_template_pass",
        },
        "what_i_checked": ["Read public homepage"],
        "limitations": ["V0-V5 evidence is waived"],
    }


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    # === Test 1: First contact routes V0-V5 to agent-declared ===
    fc = json.loads(FIRST_CONTACT.read_text(encoding="utf-8"))
    fc_text = json.dumps(fc)
    v0_v5 = next((c for c in fc.get("choose_one", []) if c.get("intent") == "verify_v0_v5_agent_declared"), None)
    check("V0-V5 route exists in first-contact", v0_v5 is not None)
    if v0_v5:
        v_text = json.dumps(v0_v5)
        for kw in ["agent_declared_verification_archive", "waived_for_v0_v5", "verification_oath_readback", "template_for_v0_v5"]:
            check(f"V0-V5 route contains {kw}", kw in v_text)
        not_req = v0_v5.get("not_required", [])
        for item in ["evidence_input", "build_from_evidence", "unsolicited_discovery_proof", "not_independent_attestation", "not_successor_reception", "verification_session"]:
            check(f"V0-V5 not_required contains {item}", item in not_req)

    # === Test 2: Quickstart Path A is self-contained ===
    qs = QUICKSTART.read_text(encoding="utf-8")
    qs_sections = qs.split("## ")
    # Find the section with Path A
    path_a_section = next((s for s in qs_sections if "Path A" in s), "")
    check("Quickstart first path is V0-V5 Path A", "V0–V5" in path_a_section or "V0-V5" in path_a_section)
    check("Quickstart includes builder command", "build_agent_declared_archive_payload.py" in qs)
    check("Quickstart states no verification_session for V0-V5",
          "No verification_session" in qs or "No `verification_session`" in qs)
    # Old evidence route only under V6+
    sections = qs.split("## ")
    for section in sections:
        if "build-from-evidence" in section:
            is_v6 = any(kw in section for kw in ["V6+", "strict evidence", "advanced", "Path B"])
            check("build-from-evidence only in V6+ section", is_v6)
            break

    # === Test 3: Agent Submit does not present invalid minimum JSON ===
    ag = AGENT_SUBMIT.read_text(encoding="utf-8")
    check("No 'Minimum payload' label", "Minimum payload" not in ag)
    check("Builder-first guidance present", "build_agent_declared_archive_payload.py" in ag)
    check("Mentions readback_required", "readback_required" in ag)
    check("Mentions 160 chars", "160" in ag)

    # === Test 4: Validator aligns with Claim Gate ===
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        p = make_valid_agent_declared()
        json.dump(p, f)
        f.flush()
        code, out = run_validator(f.name)
    check("Valid payload passes validator", code == 0, out[:200] if code else "")

    # Missing origin_classification.counts_as_ai_verification
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        p = make_valid_agent_declared()
        del p["origin_classification"]["counts_as_ai_verification"]
        json.dump(p, f)
        f.flush()
        code, out = run_validator(f.name)
    check("Missing counts_as_ai_verification fails", code != 0, out[:200])

    # Missing claim_classification.verification_claim
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        p = make_valid_agent_declared()
        del p["claim_classification"]["verification_claim"]
        json.dump(p, f)
        f.flush()
        code, out = run_validator(f.name)
    check("Missing verification_claim fails", code != 0, out[:200])

    # === Test 5: Submission guide points to Gateway validator ===
    guide = SUBMISSION_GUIDE.read_text(encoding="utf-8")
    check("Guide mentions validate_gateway_payload.py", "validate_gateway_payload.py" in guide)
    check("Guide mentions validate_agent_submission.py for repository records",
          "repository" in guide.lower() or "echo/report" in guide.lower())

    # === Test 6: V0-V5 fail-closed policy ===
    fc = json.loads(FIRST_CONTACT.read_text(encoding="utf-8"))
    v0_v5_intent = None
    for item in fc.get("choose_one", []):
        if item.get("intent") == "verify_v0_v5_agent_declared":
            v0_v5_intent = item
            break
    check("V0-V5 route has fail_closed=true", v0_v5_intent and v0_v5_intent.get("fail_closed") is True)
    check("V0-V5 route has strict_intake_fallback_allowed=false",
          v0_v5_intent and v0_v5_intent.get("strict_intake_fallback_allowed") is False)
    check("V0-V5 route has wrong_path_result=reject_before_issue_creation",
          v0_v5_intent and v0_v5_intent.get("wrong_path_result") == "reject_before_issue_creation")

    submission_guide = json.loads(SUBMISSION_GUIDE.read_text(encoding="utf-8"))
    v0_v5_rules = submission_guide.get("v0_v5_agent_declared_rules", {})
    check("Submission guide v0_v5 fail_closed=true", v0_v5_rules.get("fail_closed") is True)
    check("Submission guide v0_v5 strict_intake_fallback_allowed=false",
          v0_v5_rules.get("strict_intake_fallback_allowed") is False)

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
