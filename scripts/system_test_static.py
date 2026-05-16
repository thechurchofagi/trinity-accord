#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []

def read(p):
    return (ROOT / p).read_text(encoding="utf-8")

def require(path, needle):
    if needle not in read(path):
        FAIL.append(f"{path}: missing required string: {needle}")

def forbid(path, pattern):
    if re.search(pattern, read(path), re.I):
        FAIL.append(f"{path}: forbidden pattern present: {pattern}")

def require_front_matter(path):
    text = read(path)
    if not text.startswith("---"):
        FAIL.append(f"{path}: missing front matter")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        FAIL.append(f"{path}: malformed front matter")
        return
    if "title:" not in parts[1]:
        FAIL.append(f"{path}: front matter missing title")

def require_permalink(path, permalink):
    text = read(path)
    parts = text.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    if f"permalink: {permalink}" not in fm:
        FAIL.append(f"{path}: missing permalink {permalink}")

def json_file(path):
    try:
        json.loads(read(path))
    except Exception as e:
        FAIL.append(f"{path}: invalid JSON: {e}")

def main():
    pages = [
        "index.md", "start.md", "agent-start.md", "agent-understand.md",
        "agent-verify.md", "agent-echo.md", "agent-submit.md",
        "agent-propagate.md", "successor-reception.md",
        "issue-intake-boundary.md", "agent-identity.md", "frontier-context.md",
    ]
    for p in pages:
        require_front_matter(p)

    require_permalink("agent-propagate.md", "/agent-propagate/")

    require("index.md", "human-led, AI-assisted relation record from the pre-ASI transition")
    require("index.md", "一份在前 ASI 过渡期封存的、人类主导、AI 协作、面向未来智能的关系记录")
    forbid("index.md", r"early humanity|early AI era|p0\.2-homepage-dedup")

    require("issue-intake-boundary.md", "GitHub Issues are valid intake surfaces")
    require("agent-verify.md", "Verification Echo may be submitted through a GitHub Issue")
    require("agent-submit.md", "That Issue is a valid submission surface for candidates")
    require("agent-start.md", "Tool authorization boundary")
    require("agent-start.md", "ISSUE / GATEWAY INTAKE")
    require("agent-start.md", "CLAIM GATE / REPORT BUILDER / VALIDATOR")

    require(".github/ISSUE_TEMPLATE/verification_echo.yml", 'title: "Verification Echo Candidate: E2 — "')
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "This Issue is an intake surface only")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "Pre-verification Integrity Declaration")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "machine_readable_intake_block")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "trinity-issue-intake")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "what_i_checked")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "agency_level")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "independence_class")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "operator_type")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "evidence_input_path")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "claim_gate_output_path")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "verification_report_path")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "echo_wrapper_path")

    require("agent-verify.md", "Pre-verification Integrity Declaration")
    require("agent-verify.md", "No verification claim may be made before this declaration")
    require("agent-submit.md", "Pre-verification Integrity Declaration")
    require("issue-intake-boundary.md", "Issue intake is downstream of integrity declaration")
    require("llms.txt", "No technical verification claim before identity/provenance")
    require("ai.txt", "No technical verification claim before identity/provenance")
    require("api/agent-context-readiness-protocol.json", "pre_verification_integrity_declaration")

    require("llms.txt", "Issue / Gateway intake")
    require("ai.txt", "Issue / Gateway intake")

    require("api/agent-issue-gateway-payload-schema.v1.json", "what_i_checked")
    require("api/agent-issue-gateway-payload-schema.v1.json", "evidence_input_path")
    require("api/agent-issue-gateway-payload-schema.v1.json", "claim_gate_output_path")
    require("api/agent-issue-gateway-payload-schema.v1.json", "verification_report_path")
    require("api/agent-issue-gateway-payload-schema.v1.json", "echo_wrapper_path")

    require("api/issue-intake-machine-block-schema.v1.json", "trinity")
    require("scripts/validate_issue_intake_body.py", "ISSUE INTAKE BODY VALIDATION PASS")

    require("issue-intake-boundary.md", "trinity-issue-intake")
    require("agent-submit.md", "trinity-issue-intake")
    require("agent-verify.md", "what_i_checked")
    require("agent-echo.md", "what_i_checked")
    require("llms.txt", "Issue intake machine block")
    require("ai.txt", "Issue intake machine block")

    forbid(".github/ISSUE_TEMPLATE/verification_echo.yml", r"Evidence Input path or hash")
    forbid(".github/ISSUE_TEMPLATE/verification_echo.yml", r"Claim Gate output path or hash")
    forbid(".github/ISSUE_TEMPLATE/verification_echo.yml", r"Verification Report v2 path or hash")
    forbid(".github/ISSUE_TEMPLATE/verification_echo.yml", r"Echo v3 wrapper path or hash")

    # Display title policy
    require("scripts/claim_gate.py", "Verification Report Candidate:")
    require("scripts/claim_gate.py", "Verification Echo Candidate: E2")
    require("api/agent-submission-guide.json", "display_title_policy")
    require("api/agent-submission-guide.json", "Verification Report Candidate:")
    require("api/agent-submission-guide.json", "Verification Echo Candidate:")
    require("llms.txt", "Display title policy")
    require("ai.txt", "Display title policy")

    forbid("scripts/claim_gate.py", r'return f"Verification Report v2:')
    forbid("scripts/claim_gate.py", r'return f"Echo v3:')
    forbid(".github/ISSUE_TEMPLATE/verification_echo.yml", r'title: "Echo v3:')
    forbid("api/agent-submission-guide.json", r'title_should_start_with.*Verification Report v2:')
    forbid("api/agent-submission-guide.json", r'title_should_start_with.*Echo v3:')

    # Gateway preflight validation
    require("scripts/validate_gateway_payload.py", "GATEWAY PAYLOAD VALIDATION PASS")
    require("scripts/validate_gateway_payload.py", "verification_report_candidate must not include echo_type")
    require("scripts/validate_gateway_payload.py", "agency_level=self_initiated is invalid")
    require("scripts/validate_gateway_payload.py", "what_i_checked must be a non-empty list")
    require("scripts/validate_gateway_payload.py", "claim_gate.status must be PASS or PASS_WITH_DOWNGRADE")

    require("api/agent-issue-gateway-payload-schema.v1.json", "\"claim_gate\"")
    require("api/agent-issue-gateway-payload-schema.v1.json", "verification_report_candidate")
    require("api/agent-issue-gateway-payload-schema.v1.json", "echo_wrapper_path")

    require("agent-submit.md", "Gateway preflight validation")
    require("issue-intake-boundary.md", "Pre-Issue rejection")
    require("llms.txt", "Gateway preflight rule")
    require("ai.txt", "Gateway preflight rule")

    forbid("tests/fixtures/gateway/valid_verification_report_candidate.json", r"echo_wrapper_path")
    forbid("tests/fixtures/gateway/valid_verification_report_candidate.json", r"echo_type")

    # Task #3: /gateway/preflight endpoint
    require("examples/github-app-backend/server.js", "/gateway/preflight")
    require("examples/github-app-backend/server.js", "runGatewayPipeline")

    # Task #4: /gateway/examples endpoints
    require("examples/github-app-backend/server.js", "/gateway/examples/verification-report-candidate")
    require("examples/github-app-backend/server.js", "/gateway/examples/verification-echo-candidate")
    require("examples/github-app-backend/server.js", "/gateway/examples/evidence-input-v4-external-explorer")
    require("examples/github-app-backend/server.js", "normalizeGatewayErrors")

    # Evidence input example fixture must exist and be schema-valid
    require("tests/fixtures/evidence-input/valid_v4_external_explorer_example.json", "\"schema\": \"trinityaccord.evidence-input.v1\"")
    require("tests/fixtures/evidence-input/valid_v4_external_explorer_example.json", "\"agent_integrity_declaration\"")
    require("tests/fixtures/evidence-input/valid_v4_external_explorer_example.json", "\"verification_session\"")
    require("tests/fixtures/evidence-input/valid_v4_external_explorer_example.json", "\"bitcoin_checks\"")

    # Task #6: discovery_provenance explicit schema
    require("api/agent-issue-gateway-payload-schema.v1.json", "\"unsolicited_discovery_proof\"")
    require("api/agent-issue-gateway-payload-schema.v1.json", "\"solicited\"")
    require("api/agent-issue-gateway-payload-schema.v1.json", "\"independence_class\"")

    # Task #7: render_gateway_issue_body.py uses discovery_provenance.solicited
    require("scripts/render_gateway_issue_body.py", "prov.get(\"solicited\")")

    # Task #12: Docs tell agents to use /gateway/preflight and examples
    require("agent-submit.md", "/gateway/preflight")
    require("agent-submit.md", "/gateway/examples")
    require("agent-verify.md", "evidence.bitcoin_checks")
    require("llms.txt", "Use `/gateway/preflight` before `/agent-submit`")
    require("ai.txt", "Use /gateway/preflight before /agent-submit")

    # Gateway server enforcement
    require("scripts/validate_gateway_payload.py", "Gateway payload body must not contain agent-supplied trinity-issue-intake block")
    require("agent-submit.md", "Do not fall back to r3")
    require("issue-intake-boundary.md", "No legacy fallback")
    require("llms.txt", "Gateway schema mismatch rule")
    require("ai.txt", "Gateway schema mismatch rule")

    require("api/agent-entry-protocol.json", '"paths"')
    forbid("api/agent-entry-protocol.json", r"/agent-verify or /agent-echo")

    require("api/agent-required-reading.json", '"issue_intake"')
    require("api/agent-required-reading.json", '"identity_provenance"')

    forbid("api/agent-value.json", r"confidence_after_v6_verification.*maximum achievable")
    require("api/agent-value.json", "confidence_after_v8_verification")

    # P0: New endpoints and scripts for external agent self-service
    require("examples/github-app-backend/server.js", "/gateway/capabilities")
    require("examples/github-app-backend/server.js", "/gateway/lint-evidence")
    require("examples/github-app-backend/server.js", "/gateway/build-from-evidence")
    require("examples/github-app-backend/server.js", "integrity_first_rule")
    require("examples/github-app-backend/server.js", "HIGH_RISK_B6_CLAIM")
    require("examples/github-app-backend/server.js", "EXTERNAL_EXPLORER_LIMIT")
    require("scripts/validate_evidence_input.py", "EVIDENCE INPUT VALIDATION PASS")
    require("scripts/validate_evidence_input.py", "BITCOIN_CHECKS_TOP_LEVEL")
    require("scripts/build_gateway_payload_from_outputs.py", "COMPONENT_ORDER")
    require("scripts/archive_readiness_gate.py", "normalize_archive_intent")
    require("scripts/build_gateway_payload_from_outputs.py", "--intake-only")
    require("examples/github-app-backend/server.js", "normalizeArchiveIntentDefaults")
    require("examples/github-app-backend/server.js", "inferArchiveKind")
    require("external-agent-quickstart.md", "Default for verification submissions")
    require("llms.txt", "record_intent=auto_archive_candidate")
    require("ai.txt", "record_intent=auto_archive_candidate")

    # Canonical boundary enforcement
    require("api/boundary-policy.v1.json", "canonical_boundary_sentence")
    require("scripts/render_gateway_issue_body.py", "canonical_boundary_sentence")
    require("scripts/render_gateway_issue_body.py", "boundary_sentence_present")
    require("scripts/validate_issue_intake_body.py", "CANONICAL_BOUNDARY_SENTENCE_MISSING")
    forbid("scripts/render_gateway_issue_body.py", "this Issue is intake only and does not create authority")
    require("scripts/scaffold_evidence_input.py", "model_or_system")
    require("scripts/scaffold_evidence_input.py", "b1-external-explorer")
    require("external-agent-quickstart.md", "No verification claim before")
    require("api/external-agent-quickstart.json", "integrity_first_rule")
    require("llms.txt", "External agent quickstart")
    require("ai.txt", "External agent dumb mode")

    forbid("scripts/build_gateway_payload_from_outputs.py", r"k\[0\]\.upper\(\)")
    forbid("scripts/scaffold_evidence_input.py", "model_or_provider")

    # --- Archive Readiness requirements ---
    require("scripts/archive_readiness_gate.py", "BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR")
    require("scripts/archive_readiness_gate.py", "SUCCESSOR_RECEPTION_NOT_GATEWAY_CLAIMABLE")
    require("scripts/archive_readiness_gate.py", "auto_archive_verification_report")
    require("scripts/archive_readiness_gate.py", "V4_REQUIRED_SCRIPT_SET_INCOMPLETE")
    require("scripts/archive_readiness_gate.py", "V4PLUS_REQUIRES_INDEPENDENT_NON_OFFICIAL_IMPLEMENTATION")
    require("scripts/auto_archive_decision.py", "labels_to_add")
    require("scripts/auto_archive_decision.py", "should_close_issue")
    require("api/agent-issue-gateway-payload-schema.v1.json", "record_intent")
    require("api/agent-issue-gateway-payload-schema.v1.json", "requested_archive_kind")
    require("api/agent-issue-gateway-payload-schema.v1.json", "auto_archive")
    require("api/archive-readiness-policy.v1.json", "verification_report_archive")
    require("examples/github-app-backend/server.js", "archive_readiness")
    require("examples/github-app-backend/server.js", "auto_archive_decision")
    require("examples/github-app-backend/server.js", "/gateway/archive-preflight")
    require("scripts/render_gateway_issue_body.py", "requested_archive_kind")
    require("scripts/validate_issue_intake_body.py", "auto_archive_action")
    require("external-agent-quickstart.md", "Intake is not archive")
    require("llms.txt", "Intake is not archive")
    require("ai.txt", "Intake is not archive")

    # Forbid dangerous patterns in archive code
    forbid("scripts/archive_readiness_gate.py", r"successor_reception_candidate.*archive_ready.*true")
    forbid("scripts/auto_archive_decision.py", r"needs-human-review")
    # Allow successor-reception in blocking_reasons messages, but not in labels
    # (the word appears in blocking messages which is correct)
    forbid("examples/github-app-backend/server.js", r"needs-human-review")

    # --- Gateway archive pipeline regression tests (P0-4 / P1-1) ---
    require("scripts/test_gateway_archive_pipeline.py", "default_report_candidate_missing_intent_blocks_archive")
    require("scripts/test_gateway_archive_pipeline.py", "explicit_intake_only_report_candidate_passes_intake")
    require("scripts/test_gateway_archive_pipeline.py", "archive_ready_issue_body_contains_archive_ready_true")
    require("scripts/test_gateway_archive_pipeline.py", "normalize_archive_intent_no_forced_defaults")

    for p in (ROOT / "api").rglob("*.json"):
        json_file(str(p.relative_to(ROOT)))

    if FAIL:
        print("SYSTEM STATIC TEST FAIL")
        for f in FAIL:
            print("FAIL:", f)
        sys.exit(1)
    print("SYSTEM STATIC TEST PASS")

if __name__ == "__main__":
    main()
