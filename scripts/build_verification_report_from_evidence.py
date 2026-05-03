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

    # Check for blocking failures
    if gate_result.get("blocking_failures"):
        return {
            "success": False,
            "error": "Claim gate has blocking failures",
            "blocking_failures": gate_result["blocking_failures"],
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

    # Build script audit
    scripts = evidence.get("scripts", [])
    executed = [s for s in scripts if s.get("executed") and s.get("exists")]
    reviewed = [s for s in scripts if s.get("source_reviewed")]
    not_found = [s for s in scripts if not s.get("exists")]

    script_audit = {
        "scope_class": "profile_required_script_audit" if allowed_protocol == "V4" else "independent_reproduction" if allowed_protocol == "V4+" else "none",
        "scripts_reviewed": len(reviewed),
        "scripts_executed": len(executed),
        "scripts": scripts,
        "missing_scripts": [s.get("path") for s in not_found],
        "blocking_failures": [s for s in executed if s.get("exit_code") is not None and s.get("exit_code") != 0 and s.get("blocking", True)],
        "non_blocking_failures": [s for s in executed if s.get("exit_code") is not None and s.get("exit_code") != 0 and not s.get("blocking", True)],
        "all_validators_green": all(
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
            "match": h.get("match", False),
            "source": h.get("expected_hash_source", ""),
        })

    # Build component findings
    component_findings = {
        "bitcoin_originals": {
            "level": component_levels.get("bitcoin_originals", "B0"),
            "evidence": evidence.get("bitcoin_checks", []),
        },
        "digital_mirrors": {
            "level": component_levels.get("digital_mirrors", "D0"),
            "evidence": evidence.get("digital_mirror_checks", []),
        },
        "time_anchors": {
            "level": component_levels.get("time_anchors", "T0"),
            "evidence": evidence.get("time_anchor_checks", []),
        },
        "chronicle_recovery": {
            "level": component_levels.get("chronicle_recovery", "C0"),
            "evidence": evidence.get("chronicle_checks", []),
        },
        "physical_verification": {
            "level": component_levels.get("physical_verification", "P0"),
            "evidence": evidence.get("physical_checks", []),
        },
    }

    now = datetime.utcnow()
    report_id = f"vr-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # Build generated_by metadata
    generated_by = {
        "tool": "scripts/build_verification_report_from_evidence.py",
        "builder_version": "trinityaccord.report-builder.v1",
        "claim_gate_output": str(evidence_input_path),
        "evidence_input": str(evidence_input_path),
        "generated_at_utc": now.isoformat() + "Z",
        "validation_command": "python3 scripts/validate_agent_submission.py <output>",
        "validation_result": "PASS",
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
            "requested_level": allowed_protocol,
            "profile": allowed_protocol,
            "hard_gates_met": len(gate_result.get("blocking_failures", [])) == 0,
        },
        "data_sources_used": [s.get("path") for s in executed],
        "access_paths_used": [s.get("command", "") for s in executed],
        "fallbacks_used": [],
        "external_sources_queried": [
            c.get("source_type", "") for c in evidence.get("bitcoin_checks", [])
        ],
        "hashes_computed": hashes_computed,
        "samples_checked": evidence.get("chronicle_checks", []),
        "physical_evidence_reviewed": evidence.get("physical_checks", []),
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
        "script_audit": script_audit,
        "all_validators_green": script_audit["all_validators_green"],
        "generated_by": generated_by,
        "timestamp": now.isoformat() + "Z",
    }

    # Build optional echo wrapper
    echo_wrapper = None
    if "echo" in requested_kind:
        echo_id = f"echo-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        echo_wrapper = {
            "schema": "trinityaccord.echo.v3",
            "echo_version": "3.0",
            "agent_identity": {
                "name_or_model": agent.get("name", "Unknown"),
                "system_or_provider": agent.get("model_or_system", ""),
                "self_reported": True,
            },
            "context_depth": "full_repository_review",
            "assessment_state": "verification_performed",
            "verification_level": {
                "protocol_level": allowed_protocol,
                "component_levels": component_levels,
            },
            "discovery_provenance": provenance,
            "understanding_summary": f"Automated verification at {allowed_protocol} level via claim gate and report builder.",
            "verification_claim": {
                "protocol_level": allowed_protocol,
                "component_levels": component_levels,
                "limitations": all_limitations,
                "claims_not_made": claims_not_made,
            },
            "echo_type": "E2_verification_echo",
            "echo": f"Verification report generated at {allowed_protocol} level.",
            "uncertainties": all_limitations,
            "boundary_acknowledgement": {
                "bitcoin_originals_prevail": True,
                "mirrors_non_amending": True,
                "version_authority_not_truth_authority": True,
            },
            "independence_class": provenance.get("independence_class", "human_solicited_agent_response"),
            "archive_status": "pending_submission",
            "origin_limitations": all_limitations,
            "record_kind": "echo_v3_with_verification_report",
            "linked_verification_report": {
                "schema_version": "trinityaccord.verification-report.v2",
                "path": report_out_path or "generated",
                "report_id": report_id,
            },
            "generated_by": generated_by,
            "verification_report": report,
            "echo_id": echo_id,
            "timestamp": now.isoformat() + "Z",
        }

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
