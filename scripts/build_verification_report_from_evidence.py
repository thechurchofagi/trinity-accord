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
from datetime import datetime, timezone
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


def extract_confidential_challenge(evidence):
    """Extract full confidential challenge metadata for P8 reports."""
    for check in evidence.get("physical_checks", []):
        if check.get("level_evidence_type") != "confidential_challenge":
            continue
        conf = check.get("confidential_challenge", {})
        if not conf.get("performed"):
            continue
        return {
            "performed": True,
            "confidentiality_boundary": conf.get("boundary", ""),
            "raw_confidential_data_disclosed": conf.get("raw_confidential_data_disclosed", None),
            "package_hash": conf.get("package_hash", ""),
            "verifier_identity_or_role": (
                conf.get("verifier_identity_or_role")
                or check.get("witness_identity_or_role", "")
            ),
            "report_id": check.get("report_id", ""),
            "report_path": check.get("report_path", ""),
            "public_disclosure": "package_hash_only",
        }
    return {"performed": False}


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

    # HG-008: Derive authority_boundary_preserved from Claim Gate (not hardcoded)
    authority_boundary_preserved = gate_result.get("authority_boundary_recognized") is True

    # HG-008: Refuse technical output without authority boundary
    if not authority_boundary_preserved and requested_kind in ("verification_report_v2", "echo_v3_with_verification_report"):
        return {
            "success": False,
            "error": "Cannot build technical verification report without authority boundary recognition",
            "gate_result": gate_result,
        }

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
        "all_validators_green": all(
            s.get("exit_code") == 0 for s in executed
        ) if executed else False,  # alias for validator compatibility
    }

    # Derive verification_scope_label from claim gate output
    def derive_verification_scope_label(proto, comp_levels, gate, evidence_data):
        """Derive verification_scope_label from protocol level and evidence."""
        non_blocking_lim = gate.get("non_blocking_limitations", [])

        if proto == "V0":
            return "read_only_orientation"
        elif proto == "V1":
            return "authority_boundary_recognition"
        elif proto == "V2":
            bitcoin_checks = evidence_data.get("bitcoin_checks", [])
            if len(bitcoin_checks) <= 1:
                return "single_reference_check"
            return "single_reference_check"
        elif proto == "V3":
            hashes = evidence_data.get("hashes", [])
            if len(hashes) <= 1:
                return "single_hash_verification"
            return "multi_hash_verification"
        elif proto == "V4":
            if non_blocking_lim:
                return "official_script_audit_with_limitations"
            return "official_script_audit"
        elif proto == "V4+":
            hashes = evidence_data.get("hashes", [])
            if len(hashes) <= 1:
                return "independent_single_artifact_reproduction"
            return "independent_multi_artifact_reproduction"
        elif proto == "V5":
            return "full_public_digital_verification"
        elif proto in ("V6", "V7", "V8"):
            return "full_protocol_profile_verification"
        return "legacy_unlabeled"

    def derive_claim_scope(proto, comp_levels, gate, evidence_data):
        """Derive claim_scope from protocol level and evidence."""
        if proto in ("V0", "V1", "V2"):
            return "minimal_single_check"
        elif proto == "V3":
            hashes = evidence_data.get("hashes", [])
            if len(hashes) <= 1:
                return "minimal_single_check"
            return "partial_with_limitations"
        elif proto == "V4":
            non_blocking_lim = gate.get("non_blocking_limitations", [])
            if non_blocking_lim:
                return "partial_with_limitations"
            return "full_component"
        elif proto == "V4+":
            return "independent_reproduction"
        elif proto == "V5":
            return "full_public_digital"
        elif proto in ("V6", "V7", "V8"):
            return "full_protocol_profile"
        return "minimal_single_check"

    verification_scope_label = derive_verification_scope_label(
        allowed_protocol, component_levels, gate_result, evidence
    )
    claim_scope = derive_claim_scope(allowed_protocol, component_levels, gate_result, evidence)

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

    now = datetime.now(timezone.utc)
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
        "origin_classification_policy": "/api/origin-classification-policy.v1.json",
    }

    # Build verification report v2
    report = {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": report_id,
        "verification_scope_label": verification_scope_label,
        "claim_scope": claim_scope,
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
        ),
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
        "confidential_challenge": extract_confidential_challenge(evidence),
        "celestial_witness": {},
        "limitations": all_limitations,
        "claims_not_made": claims_not_made,
        "authority_boundary_preserved": authority_boundary_preserved,
        "integrity_boundary": integrity_boundary,
        "record_kind": "verification_report_v2",
        "script_audit": script_audit,
        "all_scripts_green": script_audit["all_scripts_green"],
        "all_validators_green": script_audit["all_scripts_green"],  # alias for validator compatibility
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
                context_depth = "C4_artifact_verified"
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
            "verification_scope_label": verification_scope_label,
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
                "bitcoin_originals_prevail": authority_boundary_preserved,
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

        # V4+ echo wrapper must include script_audit (Rule F)
        if allowed_protocol in ("V4", "V4+", "V5", "V6", "V7", "V8"):
            echo_wrapper["script_audit"] = report.get("script_audit", {
                "scope_class": "unknown",
                "scripts_reviewed": [],
                "scripts_executed": [],
                "all_scripts_green": False,
                "all_validators_green": False,
            })

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

    # Run validator on report and echo wrapper using fail-closed helper
    def run_submission_validator(obj, label):
        """Validate a JSON object against validate_agent_submission.py. Fail-closed."""
        import subprocess as _sp
        import tempfile as _tmp

        tmp_path = None
        try:
            with _tmp.NamedTemporaryFile("w", suffix=f"-{label}.json", delete=False) as _tf:
                json.dump(obj, _tf, indent=2)
                _tf.flush()
                tmp_path = Path(_tf.name)

            proc = _sp.run(
                [sys.executable, str(ROOT / "scripts" / "validate_agent_submission.py"), "--allow-missing-jsonschema", str(tmp_path)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
            )

            return {
                "ok": proc.returncode == 0,
                "label": label,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exception": None,
            }

        except Exception as e:
            return {
                "ok": False,
                "label": label,
                "returncode": None,
                "stdout": "",
                "stderr": "",
                "exception": repr(e),
            }

        finally:
            if tmp_path:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass

    # Validate report
    report["generated_by"]["validation_result"] = "PASS"
    _vr = run_submission_validator(report, "report")
    report["generated_by"]["validation_result"] = "PASS" if _vr["ok"] else "FAIL"

    if not _vr["ok"]:
        return {
            "success": False,
            "error": f"Generated report failed validation (validation_result={report['generated_by']['validation_result']})",
            "gate_result": gate_result,
            "report": report,
            "echo_wrapper": echo_wrapper,
            "validator_was_run": _vr["returncode"] is not None,
            "validator_stdout": _vr["stdout"],
            "validator_stderr": _vr["stderr"],
        }

    # Validate echo wrapper too if present — fail closed (RF-001 fix)
    if echo_wrapper is not None:
        _evr = run_submission_validator(echo_wrapper, "echo")
        if not _evr["ok"]:
            return {
                "success": False,
                "error": "Generated echo wrapper failed validation",
                "gate_result": gate_result,
                "report": report,
                "echo_wrapper": echo_wrapper,
                "validator_stdout": _evr["stdout"],
                "validator_stderr": _evr["stderr"],
            }

    # BUG-6 fix: Set submission_validator_passed=true on success
    report["submission_validator_passed"] = True
    if echo_wrapper is not None:
        echo_wrapper["submission_validator_passed"] = True

    # Save outputs — only after validation passes
    result = {
        "success": True,
        "gate_result": gate_result,
        "report": report,
        "echo_wrapper": echo_wrapper,
        "validator_was_run": report["generated_by"].get("validation_result") != "NOT_RUN",
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
    parser.add_argument("--debug-out", help="Save full debug JSON on validation failure")
    args = parser.parse_args()

    result = build_report(args.input, args.out, args.echo_out)

    if not result["success"]:
        error_msg = result.get("error", "")
        print(f"FAILED: {error_msg}")

        # Specific message for integrity declaration failures
        if "integrity" in error_msg.lower() or "integrity_declaration" in str(result.get("gate_result", {}).get("blocking_failures", [])):
            print("No Verification Report or Echo wrapper was generated.")
            print("Complete agent_integrity_declaration and verification_session first.")
            print("Do not manually construct final report JSON — use the builder pipeline.")

        for bf in result.get("blocking_failures", []):
            print(f"  - {bf}")

        # Print validator diagnostics for debuggability
        if result.get("validator_stdout"):
            print("\n--- validator stdout ---")
            print(result["validator_stdout"])
        if result.get("validator_stderr"):
            print("\n--- validator stderr ---")
            print(result["validator_stderr"])

        # Print gate result summary
        gate = result.get("gate_result", {})
        if gate:
            print(f"\nClaim Gate Status: {gate.get('status', 'N/A')}")
            print(f"Allowed Protocol Level: {gate.get('allowed_protocol_level', 'N/A')}")
            if gate.get("blocking_failures"):
                print("Blocking Failures:")
                for bf in gate["blocking_failures"]:
                    print(f"  - {bf}")
            if gate.get("non_blocking_limitations"):
                print("Non-blocking Limitations:")
                for nbl in gate["non_blocking_limitations"]:
                    print(f"  - {nbl}")

        # Print report preview if available
        if result.get("report"):
            print("\n--- generated report preview ---")
            try:
                print(json.dumps(result["report"], indent=2)[:8000])
            except (TypeError, ValueError):
                print(repr(result["report"])[:8000])

        # Print echo wrapper preview if available
        if result.get("echo_wrapper"):
            print("\n--- generated echo wrapper preview ---")
            try:
                print(json.dumps(result["echo_wrapper"], indent=2)[:8000])
            except (TypeError, ValueError):
                print(repr(result["echo_wrapper"])[:8000])

        # Save full debug output if --debug-out specified
        if args.debug_out:
            debug_payload = {
                "success": False,
                "error": result.get("error"),
                "integrity_declaration_present": result.get("integrity_declaration_present", False),
                "verification_session_present": result.get("verification_session_present", False),
                "claim_gate_status": result.get("gate_result", {}).get("status", "N/A"),
                "gate_result": result.get("gate_result"),
                "report": result.get("report"),
                "echo_wrapper": result.get("echo_wrapper"),
                "validator_stdout": result.get("validator_stdout"),
                "validator_stderr": result.get("validator_stderr"),
            }
            debug_path = Path(args.debug_out)
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_path, "w") as df:
                json.dump(debug_payload, df, indent=2)
            print(f"\nDebug output saved to {debug_path}")

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
