#!/usr/bin/env python3
"""Validate Evidence Input JSON before Claim Gate.

Checks structure, integrity declarations, and evidence consistency.
Provides agent-friendly errors with path and fix suggestions.

Usage:
    python3 scripts/validate_evidence_input.py evidence-input.json
    python3 scripts/validate_evidence_input.py evidence-input.json --json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_evidence_input(data):
    """Validate evidence input and return (accepted, errors, warnings)."""
    errors = []
    warnings = []

    # 1. Top-level bitcoin_checks is forbidden
    if "bitcoin_checks" in data:
        errors.append({
            "code": "BITCOIN_CHECKS_TOP_LEVEL",
            "path": "bitcoin_checks",
            "message": "bitcoin_checks is not a top-level Evidence Input field.",
            "fix": "Move it to evidence.bitcoin_checks."
        })

    # 2. Must have evidence object
    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append({
            "code": "EVIDENCE_MISSING",
            "path": "evidence",
            "message": "Evidence Input must contain an 'evidence' object.",
            "fix": "Add an 'evidence' object with bitcoin_checks, scripts, hashes, etc."
        })
        return False, errors, warnings

    # 3. evidence.bitcoin_checks must be array if present
    bc = evidence.get("bitcoin_checks")
    if bc is not None and not isinstance(bc, list):
        errors.append({
            "code": "BITCOIN_CHECKS_NOT_ARRAY",
            "path": "evidence.bitcoin_checks",
            "message": "evidence.bitcoin_checks must be an array.",
            "fix": "Use an array of bitcoin check objects under evidence.bitcoin_checks."
        })

    # 4. Technical verification requires agent_integrity_declaration
    requested = data.get("requested_record_kind", "")
    is_technical = requested.startswith("verification_report") or requested.startswith("echo")

    integrity_decl = data.get("agent_integrity_declaration")
    if is_technical:
        if not isinstance(integrity_decl, dict):
            errors.append({
                "code": "INTEGRITY_DECLARATION_MISSING",
                "path": "agent_integrity_declaration",
                "message": "Technical verification requires agent_integrity_declaration before Claim Gate.",
                "fix": "Add all required integrity booleans and declaration_text before requesting verification."
            })
        else:
            # Check required boolean fields
            required_bools = [
                "performed_actions_myself",
                "did_not_copy_prior_report_as_own_work",
                "did_not_copy_example_values_as_real_evidence",
                "recorded_fresh_sources_commands_outputs",
                "will_report_limitations_and_downgrade_if_needed",
                "understands_verification_is_not_truth_or_endorsement",
                "understands_bitcoin_originals_remain_final_authority",
                "independence_claim_is_accurate",
            ]
            for field in required_bools:
                if integrity_decl.get(field) is not True:
                    errors.append({
                        "code": "INTEGRITY_BOOL_NOT_TRUE",
                        "path": f"agent_integrity_declaration.{field}",
                        "message": f"agent_integrity_declaration.{field} must be true.",
                        "fix": f"Set {field} to true in your integrity declaration."
                    })

            # declaration_text length check
            decl_text = integrity_decl.get("declaration_text", "")
            if len(decl_text) < 80:
                errors.append({
                    "code": "INTEGRITY_DECLARATION_TEXT_SHORT",
                    "path": "agent_integrity_declaration.declaration_text",
                    "message": f"declaration_text must be at least 80 characters (got {len(decl_text)}).",
                    "fix": "Write a substantive declaration describing your integrity process."
                })

    # 5. Technical verification requires verification_session
    v_session = data.get("verification_session")
    if is_technical:
        if not isinstance(v_session, dict):
            errors.append({
                "code": "VERIFICATION_SESSION_MISSING",
                "path": "verification_session",
                "message": "Technical verification requires verification_session before Claim Gate.",
                "fix": "Add verification_session with session_id, fresh_actions_performed, etc."
            })
        else:
            fresh = v_session.get("fresh_actions_performed", [])
            if not isinstance(fresh, list) or len(fresh) == 0:
                errors.append({
                    "code": "FRESH_ACTIONS_EMPTY",
                    "path": "verification_session.fresh_actions_performed",
                    "message": "verification_session.fresh_actions_performed must be a non-empty array.",
                    "fix": "Record at least one fresh action you actually performed."
                })

            if v_session.get("copied_values_from_examples") is True:
                errors.append({
                    "code": "COPIED_FROM_EXAMPLES",
                    "path": "verification_session.copied_values_from_examples",
                    "message": "copied_values_from_examples must be false.",
                    "fix": "Set copied_values_from_examples to false. Use real evidence, not example values."
                })

            if v_session.get("copied_values_from_prior_reports") is True:
                errors.append({
                    "code": "COPIED_FROM_PRIOR_REPORTS",
                    "path": "verification_session.copied_values_from_prior_reports",
                    "message": "copied_values_from_prior_reports must be false.",
                    "fix": "Set copied_values_from_prior_reports to false. Generate fresh evidence."
                })

            # fresh_outputs_attached check for V2+ technical claims
            if requested.startswith("verification_report_v2") or requested.startswith("verification_report_v3"):
                if v_session.get("fresh_outputs_attached") is not True:
                    errors.append({
                        "code": "FRESH_OUTPUTS_NOT_ATTACHED",
                        "path": "verification_session.fresh_outputs_attached",
                        "message": "fresh_outputs_attached must be true for V2+ technical claims.",
                        "fix": "Set fresh_outputs_attached to true and attach real outputs."
                    })

    # 6. External explorer checks
    if isinstance(bc, list):
        for i, check in enumerate(bc):
            if not isinstance(check, dict):
                continue
            source_type = check.get("source_type", "")

            if source_type == "external_explorer":
                # Warn that this is B1/B2 style evidence
                warnings.append({
                    "code": "EXTERNAL_EXPLORER_LIMIT",
                    "path": f"evidence.bitcoin_checks[{i}]",
                    "message": "External explorer evidence does not support B5/B6.",
                    "fix": "Use witness_extraction/body_hash evidence only if raw witness/body hash reproduction was actually performed."
                })

                # Warn if body_hash_reproduced is present
                if "body_hash_reproduced" in check:
                    warnings.append({
                        "code": "EXTERNAL_EXPLORER_BODY_HASH_FIELD",
                        "path": f"evidence.bitcoin_checks[{i}].body_hash_reproduced",
                        "message": "External explorer evidence should not include body_hash_reproduced.",
                        "fix": "Remove body_hash_reproduced unless true body hash evidence exists."
                    })

            if source_type == "body_hash":
                if check.get("body_hash_reproduced") is not True:
                    warnings.append({
                        "code": "HIGH_RISK_B6_CLAIM",
                        "path": f"evidence.bitcoin_checks[{i}]",
                        "message": "B6 requires source_type=body_hash and body_hash_reproduced=true from raw witness/body reconstruction.",
                        "fix": "Explorer lookup is B1/B2-style evidence; do not claim B6 unless raw witness/body hash reproduction was actually performed."
                    })

    # 7. Check for B6 claims in claims_requested_by_agent
    claims = data.get("claims_requested_by_agent", [])
    has_external_explorer = isinstance(bc, list) and any(
        isinstance(c, dict) and c.get("source_type") == "external_explorer" for c in bc
    )
    for claim in claims:
        if isinstance(claim, str) and "B6" in claim.upper() and has_external_explorer:
            errors.append({
                "code": "B6_CLAIMED_WITH_EXTERNAL_EXPLORER",
                "path": "claims_requested_by_agent",
                "message": "Cannot claim B6 with external explorer evidence only.",
                "fix": "Remove B6 from claims or provide body_hash evidence with body_hash_reproduced=true."
            })

    return len(errors) == 0, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_evidence_input.py evidence-input.json [--json]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    json_output = "--json" in sys.argv

    try:
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    accepted, errors, warnings = validate_evidence_input(data)

    if json_output:
        result = {
            "accepted": accepted,
            "errors": errors,
            "warnings": warnings
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if warnings:
            for w in warnings:
                print(f"WARNING: code={w['code']} path={w['path']} message={w['message']} fix={w['fix']}")
        if accepted:
            print("EVIDENCE INPUT VALIDATION PASS")
        else:
            for e in errors:
                print(f"FAIL: code={e['code']} path={e['path']} message={e['message']} fix={e['fix']}")

    sys.exit(0 if accepted else 1)


if __name__ == "__main__":
    main()
