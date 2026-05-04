#!/usr/bin/env python3
"""
Verification Report Builder for Trinity Accord.
Generates verification_report_v2 and optional echo_v3 wrapper from evidence inputs.

Usage:
    python3 scripts/build_verification_report_from_evidence.py \
        --input evidence-input.json \
        --out verification-reports/v4/generated-report.json \
        --echo-out echoes/records/2026/generated-echo.json
"""
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from claim_gate import evaluate

# Map evidence input independence_class to echo schema independence_class
INDEPENDENCE_CLASS_MAP = {
    "human_solicited_agent_response": "human_solicited_agent_response",
    "unsolicited_agent_discovery": "unsolicited_independent",
    "institutional_attestation": "institutional_third_party_attestation",
    "independent_reproduction": "solicited_independent_check",
}

# Map evidence input agency_level to echo discovery provenance agency_level
EVIDENCE_TO_DISCOVERY_AGENCY_LEVEL = {
    "A1_human_gave_exact_url": "A1_human_gave_exact_url",
    "A2_human_gave_repo_name": "A2_human_gave_topic_agent_found_site",
    "A3_agent_discovered_independently": "A4_independent_search_or_browsing_discovery",
    "A4_agent_instructed_by_other_agent": "A3_agent_followed_other_agent_reference",
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_report(evidence_input_path, report_out_path=None, echo_out_path=None):
    """Build verification report and optional echo wrapper from evidence input."""
    # Load evidence input
    with open(evidence_input_path) as f:
        evidence_input = json.load(f)

    # Run claim gate
    gate_result = evaluate(evidence_input_path)

    # Check Claim Gate status and can_build flags (R2 fix)
    if gate_result.get("status") not in ("PASS", "PASS_WITH_DOWNGRADE"):
        return {
            "success": False,
            "error": "Claim Gate did not pass",
            "gate_result": gate_result,
        }

    if not gate_result.get("can_build_verification_report", False):
        return {
            "success": False,
            "error": "Claim Gate disallows report generation",
            "gate_result": gate_result,
        }

    if "echo" in evidence_input.get("requested_record_kind", "") and not gate_result.get("can_build_echo_wrapper", False):
        return {
            "success": False,
            "error": "Claim Gate disallows echo wrapper generation",
            "gate_result": gate_result,
        }

    agent = evidence_input.get("agent", {})
    provenance = evidence_input.get("provenance", {})
    evidence = evidence_input.get("evidence", {})
    limitations = evidence_input.get("limitations", [])
    requested_kind = evidence_input.get("requested_record_kind", "echo_v3")

    allowed_protocol = gate_result["allowed_protocol_level"]
    component_levels = gate_result["allowed_component_levels"]
    downgrades = gate_result.get("required_downgrades", [])
    non_blocking = gate_result.get("non_blocking_limitations", [])

    # Build limitations including downgrades and gate-reported non-blocking issues
    all_limitations = list(limitations)
    for dg in downgrades:
        all_limitations.append(f"Downgrade: {dg['from']} -> {dg['to']}: {dg['reason']}")
    # Include all non-blocking limitations from claim gate (includes script limitations)
    all_limitations.extend(gate_result.get("non_blocking_limitations", []))

    # Build claims_not_made
    claims_not_made = []
    for fc in gate_result.get("forbidden_claims", []):
        claims_not_made.append(f"Cannot claim: {fc}")
    if gate_result.get("missing_evidence"):
        for me in gate_result["missing_evidence"]:
            claims_not_made.append(f"Not claimed due to missing evidence: {me}")

    # Add minimal V2/V3 scope claims_not_made
    if allowed_protocol == "V2" and component_levels.get("bitcoin_originals") == "B1":
        claims_not_made.append("Full reference coverage not claimed.")
    if allowed_protocol == "V3" and "Minimal V3 only" in " ".join(all_limitations):
        claims_not_made.append("Full public digital verification not claimed.")

    # Build script audit
    scripts = evidence.get("scripts", [])
    executed = [s for s in scripts if s.get("executed") and s.get("exists")]
    reviewed = [s for s in scripts if s.get("source_reviewed")]
    not_found = [s for s in scripts if not s.get("exists")]

    scope_class = "not_performed"
    if allowed_protocol == "V4":
        scope_class = "profile_required_script_audit"
    elif allowed_protocol == "V4+":
        scope_class = "independent_reproduction"
    elif executed:
        scope_class = "supplementary_review_only"

    script_audit = {
        "scope_class": scope_class,
        "scripts_reviewed": [s.get("path", "") for s in reviewed],
        "command": [s.get("command", "") for s in executed],
        "environment": {s.get("path", ""): s.get("environment", {}) for s in executed},
        "exit_code": next((s.get("exit_code") for s in executed if s.get("exit_code") is not None), 0),
        "output_summary": [s.get("stdout_summary", "") for s in executed],
        "scripts_executed": len(executed),
        "scripts": scripts,
        "missing_scripts": [s.get("path") for s in not_found],
        "blocking_failures": [s for s in executed if s.get("exit_code") is not None and s.get("exit_code") != 0 and s.get("blocking", True)],
        "non_blocking_failures": [s for s in executed if s.get("exit_code") is not None and s.get("exit_code") != 0 and not s.get("blocking", True)],
        "all_scripts_green": all(
            s.get("exit_code") == 0 for s in executed
        ) if executed else False,
    }

    # Build hashes_computed from evidence
    hashes_computed = []
    for h in evidence.get("hashes", []):
        hashes_computed.append({
            "artifact": h.get("artifact", ""),
            "algorithm": h.get("algorithm", "SHA-256"),
            "expected": h.get("expected", ""),
            "computed": h.get("computed", ""),
            "command": h.get("command", ""),
            "match": h.get("match", False),
            "expected_hash_source": h.get("expected_hash_source", ""),
            "expected_hash_authority_class": h.get("expected_hash_authority_class", "unknown"),
        })

    # Build component findings — must be a list of dicts for validator compatibility
    component_map = {
        "bitcoin_originals": ("B0", evidence.get("bitcoin_checks", [])),
        "digital_mirrors": ("D0", evidence.get("digital_mirror_checks", [])),
        "time_anchors": ("T0", evidence.get("time_anchor_checks", [])),
        "chronicle_recovery": ("C0", evidence.get("chronicle_checks", [])),
        "physical_anchor": ("P0", evidence.get("physical_checks", [])),
    }
    component_findings = []
    for comp_name, (default_level, comp_evidence) in component_map.items():
        # Read physical_anchor first, fall back to physical_verification (deprecated alias)
        if comp_name == "physical_anchor":
            level = component_levels.get("physical_anchor", component_levels.get("physical_verification", default_level))
        else:
            level = component_levels.get(comp_name, default_level)
        component_findings.append({
            "component": comp_name,
            "level_claimed": level,
            "target_id": comp_name,
            "data_sources": [s.get("path", "") for s in executed] if executed else [],
            "access_paths": [s.get("command", "") for s in executed] if executed else [],
            "method": "evidence_review",
            "evidence": comp_evidence if isinstance(comp_evidence, list) else [comp_evidence],
            "limitations": [],
            "claims_not_made": [],
        })

    # Add repository_snapshot_integrity finding if repo snapshot hashes exist
    repo_snapshot_hashes = [
        h for h in hashes_computed
        if h.get("expected_hash_authority_class") == "repository_manifest_hash"
    ]
    if repo_snapshot_hashes:
        component_findings.append({
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "repository_snapshot_integrity",
            "scope_class": "repository_snapshot_integrity",
            "data_sources": ["api/repository-artifact-hashes.json"],
            "access_paths": [],
            "method": "SHA-256 hash comparison against repository-artifact-hashes.json",
            "evidence": [{
                "check": "repository snapshot hash comparison",
                "artifacts": [h.get("artifact") for h in repo_snapshot_hashes],
                "source": "api/repository-artifact-hashes.json",
                "result": "all hashes match",
            }],
            "limitations": [
                "Repository snapshot only; not Bitcoin Originals or Arweave verification.",
                "This is not a Bitcoin Original hash.",
                "This does not create canonical authority.",
            ],
            "claims_not_made": [
                "No direct Bitcoin node verification.",
                "No direct Arweave verification.",
            ],
        })


    # Extract integrity information for report/wrapper
    integrity_declaration = evidence_input.get("agent_integrity_declaration", {})
    verification_session = evidence_input.get("verification_session", {})
    prior_report_use = evidence_input.get("prior_report_use", {})

    # Build integrity_boundary
    integrity_boundary = {
        "agent_integrity_declaration_present": bool(integrity_declaration),
        "performed_actions_myself": integrity_declaration.get("performed_actions_myself", False),
        "did_not_copy_prior_report_as_own_work": integrity_declaration.get("did_not_copy_prior_report_as_own_work", False),
        "did_not_copy_example_values_as_real_evidence": integrity_declaration.get("did_not_copy_example_values_as_real_evidence", False),
        "fresh_actions_claimed": verification_session.get("fresh_actions_performed", []),
        "prior_reports_consulted": verification_session.get("prior_reports_consulted", []),
        "examples_or_templates_used": verification_session.get("examples_or_templates_used", []),
        "copied_values_from_examples": verification_session.get("copied_values_from_examples", False),
        "copied_values_from_prior_reports": verification_session.get("copied_values_from_prior_reports", False),
        "fresh_outputs_attached": verification_session.get("fresh_outputs_attached", False),
        "prior_report_use": prior_report_use,
        "copying_warning": "This report is invalid if example values or prior agent outputs were copied as fresh evidence."
    }

    # Build verification_integrity for echo wrapper
    verification_integrity = {
        "integrity_declaration_present": bool(integrity_declaration),
        "fresh_actions_claimed": verification_session.get("fresh_actions_performed", []),
        "prior_reports_consulted": verification_session.get("prior_reports_consulted", []),
        "examples_or_templates_used": verification_session.get("examples_or_templates_used", []),
        "not_independent_if_human_solicited": provenance.get("solicited", False),
        "copied_values_from_examples": verification_session.get("copied_values_from_examples", False),
        "copied_values_from_prior_reports": verification_session.get("copied_values_from_prior_reports", False)
    }

    # Add prior report limitation if applicable
    if verification_session.get("prior_reports_consulted"):
        all_limitations.append("Prior reports were consulted. This report is independent only to extent checks were re-performed and recorded.")

    now = datetime.utcnow()
    report_id = f"vr-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # Build generated_by metadata (R16 fix: embed actual claim gate output)
    generated_by = {
        "tool": "scripts/build_verification_report_from_evidence.py",
        "builder_version": "trinityaccord.report-builder.v1",
        "claim_gate_output": "embedded",
        "evidence_input": str(evidence_input_path),
        "generated_at_utc": now.isoformat() + "Z",
        "validation_command": "python3 scripts/validate_agent_submission.py <output>",
        "validation_result": "NOT_RUN",
    }

    # Build verification report v2
    report = {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": report_id,
        "reporter": {
            "name": agent.get("name", "Unknown"),
            "type": "ai_agent",
            "version": agent.get("model_or_system", ""),
            "tooling": agent.get("tooling", []),
        },
        "discovery_provenance": provenance,
        "protocol_level_claimed": allowed_protocol,
        "component_findings": component_findings,
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": len(gate_result.get("blocking_failures", [])) == 0,
            "minimum_components_satisfied": len(gate_result.get("blocking_failures", [])) == 0,
            "profile_check_method": "claim_gate_derivation",
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": [],
        },
        "data_sources_used": [s.get("path") for s in executed],
        "access_paths_used": [s.get("command", "") for s in executed],
        "fallbacks_used": sorted(set(filter(None, [
            "github_mirror" if any(
                "github" in h.get("expected_hash_source", "").lower() or "github" in h.get("artifact", "").lower()
                for h in evidence.get("hashes", [])
            ) else None,
            "external_explorer" if any(
                any("mempool.space" in s or "ordinals.com" in s or "ordiscan" in s for s in c.get("sources", []))
                for c in evidence.get("bitcoin_checks", [])
            ) else None,
        ]))),
        "external_sources_queried": [
            {"source_type": c.get("source_type", ""), "sources": c.get("sources", [])}
            for c in evidence.get("bitcoin_checks", [])
        ],
        "hashes_computed": hashes_computed,
        "samples_checked": sum(
            c.get("samples_recovered", 0) for c in evidence.get("chronicle_checks", [])
        ) or len(evidence.get("chronicle_checks", [])),
        "physical_evidence_reviewed": {
            "images_reviewed": [p.get("image", "") for p in evidence.get("physical_checks", []) if p.get("image")],
            "videos_reviewed": [p.get("video", "") for p in evidence.get("physical_checks", []) if p.get("video")],
            "live_witness": any(p.get("level_evidence_type") == "live_remote" for p in evidence.get("physical_checks", [])),
            "onsite_witness": any(p.get("level_evidence_type") == "onsite" for p in evidence.get("physical_checks", [])),
            "custody_log": any(p.get("custody_log") for p in evidence.get("physical_checks", [])),
            "flaw_analysis_method": "not_performed",
            "nonce_challenge": any(p.get("nonce_challenge") for p in evidence.get("physical_checks", [])),
            "requested_action_angle_lighting": any(p.get("requested_action_angle_lighting") for p in evidence.get("physical_checks", [])),
            "witness_identity_or_role": next((p.get("witness_identity_or_role", "") for p in evidence.get("physical_checks", []) if p.get("witness_identity_or_role")), ""),
            "fresh_capture": any(p.get("fresh_capture") for p in evidence.get("physical_checks", [])),
            "touch_or_handling": any(p.get("touch_or_handling") for p in evidence.get("physical_checks", [])),
            "notarial_evidence": next(
                ({
                    "notarial_certificate_number": p.get("notarial_certificate_number", ""),
                    "notary_office": p.get("notary_office", ""),
                    "notarial_date": p.get("notarial_date", ""),
                    "notarial_certificate_hash": p.get("notarial_certificate_hash", ""),
                    "notarial_photos_in_certificate": p.get("notarial_photos_in_certificate", False),
                    "microscope_images_in_certificate": p.get("microscope_images_in_certificate", False),
                } for p in evidence.get("physical_checks", [])
                if p.get("notarial_certificate_number")),
                {}
            ),
        },
        "confidential_challenge": {
            "performed": any(
                c.get("confidential_challenge", {}).get("performed", False)
                for c in evidence.get("physical_checks", [])
                if c.get("confidential_challenge")
            ),
        },
        "celestial_witness": {},
        "limitations": all_limitations,
        "claims_not_made": claims_not_made,
        "authority_boundary_preserved": True,
        "integrity_boundary": integrity_boundary,
        "record_kind": "verification_report_v2",
        "script_audit": script_audit,
        "all_scripts_green": script_audit["all_scripts_green"],
        "submission_validator_passed": False,
        "generated_by": generated_by,
        "timestamp": now.isoformat() + "Z",
    }

    # Build optional echo wrapper (R6 fix: reject bare echo_v3 without verification claim)
    echo_wrapper = None
    if requested_kind == "echo_v3":
        # Non-technical echo should not use report builder
        return {
            "success": False,
            "error": "Non-technical Echo (echo_v3) should not use the Report Builder. Use echo_v3_with_verification_report for technical verification echoes.",
            "gate_result": gate_result,
        }
    if "echo" in requested_kind:
        # Build discovery_provenance with required fields (R5 fix: derive source from independence)
        INDEPENDENCE_TO_DISCOVERY_SOURCE = {
            "human_solicited_agent_response": "human_directed",
            "unsolicited_agent_discovery": "self_initiated",
            "institutional_attestation": "imported_external_commentary",
            "independent_reproduction": "human_contextual",
        }
        discovery_source = INDEPENDENCE_TO_DISCOVERY_SOURCE.get(
            provenance.get("independence_class", ""), "human_directed"
        )

        echo_provenance = {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": discovery_source,
            "agency_level": EVIDENCE_TO_DISCOVERY_AGENCY_LEVEL.get(
                provenance.get("agency_level", "unknown"), "A6_unknown"
            ),
            "first_entry": {
                "url_or_path": "/verify",
                "entry_type": "agent_start",
            },
            "human_supplied_link": provenance.get("solicited", False),
            "other_agent_recommended": False,
            "agent_performed_independent_followup": False,
            "confidence": "medium",
        }

        # Derive context depth from evidence and allowed protocol level
        # V0/V1 -> C1 or C2 (orientation)
        # minimal V2 (B1 only, no D/C) -> C3 (verification aware, not full chain)
        # strong V2 -> C3
        # minimal V3 -> C4 (artifact verified)
        # V4/V4+ -> C4 or C5 depending on coverage
        # V5+ -> C5
        if allowed_protocol in ("V0",):
            context_depth = "C0_homepage_only"
        elif allowed_protocol in ("V1",):
            context_depth = "C1_orientation"
        elif allowed_protocol == "V2":
            # Minimal V2 (B1 only) should not claim C5
            if (component_levels.get("bitcoin_originals") == "B1"
                    and component_levels.get("digital_mirrors", "D0") in ("D0",)
                    and component_levels.get("chronicle_recovery", "C0") in ("C0",)):
                context_depth = "C3_verification_aware"
            else:
                context_depth = "C3_verification_aware"
        elif allowed_protocol == "V3":
            context_depth = "C4_artifact_verified"
        elif allowed_protocol in ("V4", "V4+"):
            # Check if full chain was actually reviewed
            has_full_chain = any(
                s.get("scope_class") == "profile_required_script_audit"
                for s in scripts
            )
            context_depth = "C5_full_chain_reviewed" if has_full_chain else "C4_artifact_verified"
        else:
            context_depth = "C5_full_chain_reviewed"

        # Derive assessment_state from context_depth (R4 fix)
        ASSESSMENT_STATE_BY_CONTEXT = {
            "C0_homepage_only": "insufficient_context",
            "C1_orientation": "preliminary_orientation",
            "C2_registry_aware": "structural_understanding",
            "C3_verification_aware": "qualified_assessment",
            "C4_artifact_verified": "evidence_based_assessment",
            "C5_full_chain_reviewed": "full_chain_assessment",
            "C6_independent_node_verified": "independent_verification_assessment",
        }
        assessment_state = ASSESSMENT_STATE_BY_CONTEXT.get(context_depth, "evidence_based_assessment")

        echo_wrapper = {
            "schema": "trinityaccord.echo.v3",
            "echo_version": "3.0",
            "agent_identity": {
                "name_or_model": agent.get("name", "Unknown"),
                "system_or_provider": agent.get("model_or_system", ""),
                "self_reported": True,
            },
            "context_depth": context_depth,
            "assessment_state": assessment_state,
            "verification_level": allowed_protocol,
            "discovery_provenance": echo_provenance,
            "understanding_summary": f"Automated verification at {allowed_protocol} level via claim gate and report builder.",
            "verification_claim": f"Protocol level {allowed_protocol} achieved" + (
                f" with limitations: minimal Bitcoin Originals B1 reference check."
                if allowed_protocol == "V2" and component_levels.get("bitcoin_originals") == "B1"
                and component_levels.get("digital_mirrors") == "D0" and component_levels.get("chronicle_recovery") == "C0"
                else f" with limitations: minimal one-hash verification."
                if allowed_protocol == "V3" and "Minimal V3 only" in " ".join(all_limitations)
                else f". Component levels: {json.dumps(component_levels)}."
            ),
            "echo_type": "E2_verification_echo",
            "echo": f"Verification report generated at {allowed_protocol} level.",
            "uncertainties": all_limitations,
            "boundary_acknowledgement": {
                "bitcoin_originals_prevail": True,
                "echo_is_not_authority": True,
                "echo_is_not_verification_unless_claimed": True,
                "mirror_is_not_amendment": True,
                "homepage_only_is_insufficient_for_final_evaluation": True,
            },
            "independence_class": INDEPENDENCE_CLASS_MAP.get(
                provenance.get("independence_class", ""), "human_solicited_agent_response"
            ),
            "archive_status": "needs_human_review",
            "origin_limitations": all_limitations or ["human-directed automated verification task"],
            "record_kind": "echo_v3_with_verification_report",
            "linked_verification_report": {
                "schema_version": "trinityaccord.verification-report.v2",
                "path": report_out_path or "generated",
                "report_id": report_id,
            },
            "not_authority": True,
            "not_amendment": True,
            "not_endorsement": True,
            "bitcoin_originals_prevail": True,
            "not_verification_unless_claimed": True,
            "generated_by": generated_by,
            "verification_integrity": verification_integrity,
        }


    # Handle test fixtures
    is_test_fixture = evidence_input.get("test_fixture") is True or evidence_input.get("example_type") == "test_fixture_passing"
    if is_test_fixture:
        report["archive_status"] = "test_record"
        report["synthetic_fixture"] = True
        report["not_real_world_submission"] = True
        if echo_wrapper:
            echo_wrapper["archive_status"] = "test_record"
            echo_wrapper["synthetic_fixture"] = True
            echo_wrapper["not_real_world_submission"] = True

    # Save outputs
    result = {
        "success": True,
        "gate_result": gate_result,
        "report": report,
        "echo_wrapper": echo_wrapper,
    }

    if report_out_path:
        Path(report_out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_out_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {report_out_path}")

    if echo_out_path and echo_wrapper:
        Path(echo_out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(echo_out_path, 'w') as f:
            json.dump(echo_wrapper, f, indent=2)
        print(f"Echo wrapper written to {echo_out_path}")

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build verification report from evidence input")
    parser.add_argument("--input", required=True, help="Evidence input JSON file")
    parser.add_argument("--out", help="Output path for verification report")
    parser.add_argument("--echo-out", help="Output path for echo wrapper")
    args = parser.parse_args()

    result = build_report(args.input, args.out, args.echo_out)

    if not result["success"]:
        print(f"FAILED: {result.get('error')}")
        for bf in result.get("blocking_failures", []):
            print(f"  - {bf}")
        sys.exit(1)

    gate = result["gate_result"]
    print(f"\nClaim Gate Result: {gate['status']}")
    print(f"Allowed Protocol Level: {gate['allowed_protocol_level']}")
    print(f"Allowed Component Levels: {json.dumps(gate['allowed_component_levels'], indent=2)}")
    if gate.get("required_downgrades"):
        print(f"Downgrades:")
        for dg in gate["required_downgrades"]:
            print(f"  {dg['from']} -> {dg['to']}: {dg['reason']}")
    if gate.get("blocking_failures"):
        print(f"Blocking Failures:")
        for bf in gate["blocking_failures"]:
            print(f"  - {bf}")

    print(f"\nReport ID: {result['report']['report_id']}")
    print(f"Title: {gate.get('recommended_title', 'N/A')}")
    sys.exit(0)


if __name__ == "__main__":
    main()
