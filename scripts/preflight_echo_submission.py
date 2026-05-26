#!/usr/bin/env python3
"""
Preflight check for Echo submissions via API or freeform text.
Validates that an Echo file passes claim discipline gates before submission.

Usage:
  python3 scripts/preflight_echo_submission.py path/to/echo.md
  python3 scripts/preflight_echo_submission.py path/to/echo.md --strict
  python3 scripts/preflight_echo_submission.py path/to/echo.md --json
  python3 scripts/preflight_echo_submission.py path/to/echo.md --autofix-boundary
"""
import argparse
import json
import os
import re
import sys

# Import gate functions from triage
sys.path.insert(0, os.path.dirname(__file__))
from triage_echo_issue import (
    detect_boundary,
    missing_provenance_fields,
    detect_independence_overclaim_scoped,
    check_v4plus_claim_gate,
    check_bitcoin_component_claim_gate,
    check_chronicle_recovery_claim_gate,
    check_v5_full_public_digital_gate,
    detect_human_solicited_context,
    INDEPENDENCE_OVERCLAIM_PATTERNS,
)
from submission_intake import parse_submission, get_field, get_bool_field


def preflight_check(text):
    """Run all claim discipline checks on text. Returns list of issues."""
    issues = []

    intake = parse_submission("", text)
    positive_text = intake.positive_text
    raw_text = intake.raw_text

    # 1. Missing boundary
    if not detect_boundary(raw_text):
        issues.append({
            "type": "missing-boundary",
            "severity": "hard",
            "message": "Missing required authority boundary sentence.",
            "fix": "Add: Bitcoin Originals are final; all mirrors and echoes are non-amending.",
        })

    # 2. Missing provenance
    prov_missing = missing_provenance_fields(raw_text)
    if prov_missing:
        issues.append({
            "type": "missing-provenance-agency",
            "severity": "hard",
            "message": f"Missing provenance/agency fields: {', '.join(prov_missing)}",
            "fix": "Add Provenance/Agency block with solicited_status, independence_class, agency_level, operator_type.",
        })

    # 3. Independence overclaim (scoped)
    overclaim = detect_independence_overclaim_scoped(raw_text, positive_text)
    if overclaim:
        issues.append({
            "type": "independence-overclaim-risk",
            "severity": overclaim["severity"],
            "message": overclaim["reason"],
            "fix": "Replace independence wording with: human-solicited agent-performed verification run; not independent attestation.",
        })

    # 4. V4+ gate (positive text only)
    v4p = check_v4plus_claim_gate(positive_text)
    if v4p:
        issues.append({
            "type": "v4plus-overclaim-risk",
            "severity": "high",
            "message": f"V4+ claim missing evidence: {', '.join(v4p)}",
            "fix": "Add V4+ Reproduction Scope section with all required evidence fields.",
        })

    # 5. B5/B6 gate (positive text only)
    btc = check_bitcoin_component_claim_gate(positive_text)
    for level, missing in btc:
        issues.append({
            "type": "bitcoin-component-overclaim-risk",
            "severity": "high",
            "message": f"{level} claim missing evidence: {', '.join(missing)}",
            "fix": f"Add {level} evidence or downgrade to B1/B2.",
        })

    # 6. C5/175/175 gate (positive text only)
    c5 = check_chronicle_recovery_claim_gate(positive_text)
    if c5:
        issues.append({
            "type": "chronicle-overclaim-risk",
            "severity": "high",
            "message": f"C5/175/175 claim missing evidence: {', '.join(c5)}",
            "fix": "Add full recovery evidence or downgrade to C0/C1/C2/C3.",
        })

    # 7. V5/full public digital gate (positive text only)
    v5 = check_v5_full_public_digital_gate(positive_text)
    if v5:
        issues.append({
            "type": "v5-overclaim-risk",
            "severity": "high",
            "message": f"V5/full public digital claim missing coverage: {', '.join(v5)}",
            "fix": "Add all required public target coverage or list unavailable targets.",
        })

    # 8. V2 Claim Gate requirement (only for legacy freeform, not structured v3 submissions or TA-021 new schema)
    uses_new_schema = bool(get_field(intake.fields, "record_purpose"))
    if intake.declared_level == "V2" and intake.mode == "legacy_freeform_or_needs_format" and not uses_new_schema:
        issues.append({
            "type": "claim-gate-required",
            "severity": "hard",
            "message": "V2 reference verification claims require lightweight Evidence Input + Claim Gate output.",
            "fix": "Run `scripts/claim_gate.py` on a minimal V2 evidence input and include `evidence_input_path` and `claim_gate_output_path`.",
        })

    # 9. Integrity declaration hard gate for verification echoes
    # All verification Echo templates must start with Solemn Integrity Declaration
    has_integrity_declaration = bool(
        re.search(r"integrity.?declaration", raw_text, re.IGNORECASE)
        or re.search(r"solemn.*(integrity|declaration)", raw_text, re.IGNORECASE)
        or re.search(r"solemnly\s+declare", raw_text, re.IGNORECASE)
        or re.search(r"完整性声明", raw_text)
        or re.search(r"郑重声明", raw_text)
    )
    # Check if this is a verification echo (E2-E5, E8 types or V1+ level)
    echo_type_match = re.search(r"\b(E[2-5]|E8)\b", raw_text, re.IGNORECASE)
    vlevel_match = re.search(r"\bV[1-8]\b", raw_text, re.IGNORECASE)
    is_verification_echo = bool(echo_type_match or (vlevel_match and intake.declared_level not in (None, "none", "V0")))

    if is_verification_echo and not has_integrity_declaration:
        issues.append({
            "type": "missing-integrity-declaration",
            "severity": "hard",
            "message": "Verification Echo templates must include a Solemn Integrity Declaration.",
            "fix": "Add an 'integrity_declaration' or 'Solemn Integrity Declaration' section at the beginning of your submission. "
                   "State that your submission is truthful, evidence is not fabricated, and you understand the non-amending boundary.",
        })

    # 10. Hard field gate: integrity declaration machine fields
    # TA-020 follow-up: require machine-readable integrity declaration fields
    # Only hard-fail when record_class=ai_independent_verification is explicitly declared
    record_class_val = get_field(intake.fields, "record_class")
    is_ai_verification = record_class_val and "ai_independent_verification" in record_class_val.lower()
    if is_verification_echo and has_integrity_declaration and is_ai_verification:
        REQUIRED_INTEGRITY_FLAGS = {
            "declaration_strength": "strongest_available",
            "solemn_declaration_present": True,
            "no_fabricated_evidence": True,
            "no_prior_report_copied_as_own_work": True,
            "no_example_values_used_as_real_evidence": True,
            "limitations_reported": True,
            "correction_duty_accepted": True,
            "false_declaration_consequence": "reject_or_invalidate_record",
        }

        fields = intake.fields
        for field_name, expected in REQUIRED_INTEGRITY_FLAGS.items():
            actual_raw = get_field(fields, field_name)
            if not actual_raw:
                issues.append({
                    "type": "missing-integrity-declaration-field",
                    "severity": "hard",
                    "message": f"Integrity declaration missing required machine field: {field_name}",
                    "fix": f"Add '{field_name}: {expected}' to your integrity_declaration YAML block.",
                })
            elif isinstance(expected, bool):
                parsed = get_bool_field(fields, field_name)
                if parsed is not expected:
                    issues.append({
                        "type": "invalid-integrity-declaration-field",
                        "severity": "hard",
                        "message": f"Integrity declaration field '{field_name}' must be true, got: {actual_raw}",
                        "fix": f"Set '{field_name}: true' in your integrity_declaration YAML block.",
                    })
            elif isinstance(expected, str):
                if actual_raw.strip().lower() != expected.lower():
                    issues.append({
                        "type": "invalid-integrity-declaration-field",
                        "severity": "hard",
                        "message": f"Integrity declaration field '{field_name}' must be '{expected}', got: {actual_raw}",
                        "fix": f"Set '{field_name}: {expected}' in your integrity_declaration YAML block.",
                    })

    # 11. AI independent verification required fields
    # TA-020 follow-up: require fresh/reproducible/authority boundary fields
    record_class = get_field(intake.fields, "record_class")
    if record_class and "ai_independent_verification" in record_class.lower():
        ai_required = {
            "counts_as_ai_independent_verification": True,
            "counts_as_formal_human_institutional_attestation": False,
            "authority_boundary_preserved": True,
        }
        # fresh_actions_performed: required unless fresh_actions_claimed is non-empty
        fresh_claimed = get_field(intake.fields, "fresh_actions_claimed")
        if not fresh_claimed:
            ai_required["fresh_actions_performed"] = True
        ai_required["method_reproducible"] = True

        for field_name, expected in ai_required.items():
            actual_raw = get_field(intake.fields, field_name)
            if not actual_raw:
                issues.append({
                    "type": "missing-ai-verification-field",
                    "severity": "hard",
                    "message": f"AI independent verification missing required field: {field_name}",
                    "fix": f"Add '{field_name}: {expected}' to your echo metadata.",
                })
            elif isinstance(expected, bool):
                parsed = get_bool_field(intake.fields, field_name)
                if parsed is not expected:
                    issues.append({
                        "type": "invalid-ai-verification-field",
                        "severity": "hard",
                        "message": f"AI verification field '{field_name}' must be {expected}, got: {actual_raw}",
                        "fix": f"Set '{field_name}: {expected}' in your echo metadata.",
                    })

    # 12. External human authorization boundary
    # TA-020 follow-up: external_human_authorized_execution=true alone cannot count formal
    ext_auth = get_bool_field(intake.fields, "external_human_authorized_execution")
    if ext_auth is True:
        counts_formal = get_bool_field(intake.fields, "counts_as_formal_human_institutional_attestation")
        signed = get_bool_field(intake.fields, "external_human_signed_or_adopted_final_report")
        if counts_formal is True and signed is not True:
            issues.append({
                "type": "external-auth-cannot-count-formal",
                "severity": "hard",
                "message": "External human authorization alone cannot count as formal attestation. "
                           "counts_as_formal_human_institutional_attestation=true requires "
                           "external_human_signed_or_adopted_final_report=true.",
                "fix": "Either set counts_as_formal_human_institutional_attestation=false, or "
                       "provide external_human_signed_or_adopted_final_report=true with a formal_attestation_gate_reference.",
            })

    # === TA-021: New simplified submitter-facing field validation ===

    # 13. Required simplified fields for all submissions
    record_purpose = get_field(intake.fields, "record_purpose")
    discovery_autonomy = get_field(intake.fields, "discovery_autonomy")
    verifier_type = get_field(intake.fields, "verifier_type")
    verification_claimed = get_bool_field(intake.fields, "verification_claimed")

    # If any new field is present, validate using new schema
    uses_new_schema = any([record_purpose, discovery_autonomy, verifier_type, verification_claimed is not None])

    if uses_new_schema:
        # Required fields
        if not record_purpose:
            issues.append({
                "type": "missing-record-purpose",
                "severity": "hard",
                "message": "Missing required field: record_purpose",
                "fix": "Add 'record_purpose' with one of: echo_only, ai_independent_verification, human_verification, etc.",
            })

        if not discovery_autonomy:
            issues.append({
                "type": "missing-discovery-autonomy",
                "severity": "hard",
                "message": "Missing required field: discovery_autonomy",
                "fix": "Add 'discovery_autonomy': autonomous, non_autonomous, or unknown.",
            })

        if verifier_type is None or verifier_type == "":
            issues.append({
                "type": "missing-verifier-type",
                "severity": "hard",
                "message": "Missing required field: verifier_type",
                "fix": "Add 'verifier_type': none, ai_agent, human_individual, institution, multi_agent, human_ai_team, or unknown.",
            })

        if verification_claimed is None:
            issues.append({
                "type": "missing-verification-claimed",
                "severity": "hard",
                "message": "Missing required field: verification_claimed",
                "fix": "Add 'verification_claimed': true or false.",
            })

        # Conditional: non_autonomous_trigger required when non_autonomous
        if discovery_autonomy == "non_autonomous":
            trigger = get_field(intake.fields, "non_autonomous_trigger")
            if not trigger or trigger == "none":
                issues.append({
                    "type": "missing-non-autonomous-trigger",
                    "severity": "hard",
                    "message": "discovery_autonomy=non_autonomous requires non_autonomous_trigger",
                    "fix": "Add 'non_autonomous_trigger' with one of: project_requested, human_requested, agent_referred, etc.",
                })

        # Conditional: verification fields required when claimed
        if verification_claimed is True:
            if not get_field(intake.fields, "verification_level"):
                issues.append({
                    "type": "missing-verification-level",
                    "severity": "hard",
                    "message": "verification_claimed=true requires verification_level",
                    "fix": "Add 'verification_level' (V0-V8).",
                })

            if get_bool_field(intake.fields, "fresh_actions_performed") is not True:
                issues.append({
                    "type": "missing-fresh-actions",
                    "severity": "hard",
                    "message": "verification_claimed=true requires fresh_actions_performed=true",
                    "fix": "Add 'fresh_actions_performed: true'.",
                })

            if get_bool_field(intake.fields, "method_reproducible") is not True:
                issues.append({
                    "type": "missing-method-reproducible",
                    "severity": "hard",
                    "message": "verification_claimed=true requires method_reproducible=true",
                    "fix": "Add 'method_reproducible: true'.",
                })

        # Conditional: echo_only must not claim verification
        if record_purpose == "echo_only":
            if verification_claimed is True:
                issues.append({
                    "type": "echo-only-cannot-claim-verification",
                    "severity": "hard",
                    "message": "record_purpose=echo_only requires verification_claimed=false",
                    "fix": "Set 'verification_claimed: false' or change record_purpose.",
                })

            if get_bool_field(intake.fields, "counts_as_ai_independent_verification") is True:
                issues.append({
                    "type": "echo-only-cannot-count-ai-verification",
                    "severity": "hard",
                    "message": "record_purpose=echo_only requires counts_as_ai_independent_verification=false",
                    "fix": "Set 'counts_as_ai_independent_verification: false' or change record_purpose.",
                })

        # Conditional: ai_independent_verification requirements
        if record_purpose == "ai_independent_verification":
            if verifier_type not in {"ai_agent", "multi_agent", "human_ai_team"}:
                issues.append({
                    "type": "ai-verification-requires-ai-verifier",
                    "severity": "hard",
                    "message": "record_purpose=ai_independent_verification requires verifier_type is ai_agent, multi_agent, or human_ai_team",
                    "fix": "Set 'verifier_type' to ai_agent, multi_agent, or human_ai_team.",
                })

            if verification_claimed is not True:
                issues.append({
                    "type": "ai-verification-requires-claimed",
                    "severity": "hard",
                    "message": "record_purpose=ai_independent_verification requires verification_claimed=true",
                    "fix": "Set 'verification_claimed: true'.",
                })

            if get_bool_field(intake.fields, "counts_as_ai_independent_verification") is not True:
                issues.append({
                    "type": "ai-verification-must-count",
                    "severity": "hard",
                    "message": "record_purpose=ai_independent_verification requires counts_as_ai_independent_verification=true",
                    "fix": "Set 'counts_as_ai_independent_verification: true'.",
                })

            if get_bool_field(intake.fields, "counts_as_formal_human_institutional_attestation") is not False:
                issues.append({
                    "type": "ai-verification-cannot-count-formal",
                    "severity": "hard",
                    "message": "AI independent verification cannot count as formal human/institutional attestation",
                    "fix": "Set 'counts_as_formal_human_institutional_attestation: false'.",
                })

        # Conditional: AGI capability boundary
        capability_claim = get_field(intake.fields, "verifier_capability_claim")
        if capability_claim in {"agi_claimed", "agi_benchmark_asserted"}:
            boundary_fields = {
                "agi_claim_does_not_raise_verification_level": True,
                "agi_claim_does_not_create_authority": True,
                "agi_claim_does_not_count_as_formal_attestation": True,
            }
            for bf, expected in boundary_fields.items():
                if get_bool_field(intake.fields, bf) is not expected:
                    issues.append({
                        "type": "missing-agi-capability-boundary",
                        "severity": "hard",
                        "message": f"verifier_capability_claim={capability_claim} requires {bf}=true",
                        "fix": f"Add '{bf}: true' to your verifier_capability_boundary block.",
                    })

        # 14. Integrity declaration position check for new schema
        declaration_pos = get_field(intake.fields, "declaration_position")
        if declaration_pos and declaration_pos != "top_of_submission":
            issues.append({
                "type": "integrity-declaration-not-at-top",
                "severity": "hard",
                "message": "Solemn Integrity Declaration must be at top_of_submission",
                "fix": "Move the integrity declaration to the very beginning of your submission and set 'declaration_position: top_of_submission'.",
            })

        # 15. performed_claimed_actions (new canonical, with legacy alias)
        if get_bool_field(intake.fields, "performed_claimed_actions") is not True:
            # Check legacy alias
            if get_bool_field(intake.fields, "performed_actions_myself") is not True:
                if is_verification_echo:
                    issues.append({
                        "type": "missing-performed-claimed-actions",
                        "severity": "hard",
                        "message": "Integrity declaration requires performed_claimed_actions=true (or legacy performed_actions_myself=true)",
                        "fix": "Add 'performed_claimed_actions: true' to your integrity_declaration block.",
                    })

    return issues


def add_boundary_if_missing(text):
    """Add boundary sentence if missing."""
    if detect_boundary(text):
        return text, False
    boundary = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    return text.rstrip() + "\n\n" + boundary + "\n", True


def main():
    parser = argparse.ArgumentParser(description="Preflight check for Echo submissions")
    parser.add_argument("file", help="Path to Echo markdown file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any warnings")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--autofix-boundary", action="store_true", help="Auto-add boundary if missing")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r") as f:
        text = f.read()

    if args.autofix_boundary:
        text, added = add_boundary_if_missing(text)
        if added:
            with open(args.file, "w") as f:
                f.write(text)
            print(f"Added boundary sentence to {args.file}")

    issues = preflight_check(text)

    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        if not issues:
            print(f"✅ {args.file}: All preflight checks passed.")
        else:
            print(f"❌ {args.file}: {len(issues)} issue(s) found:\n")
            for i, issue in enumerate(issues, 1):
                severity = issue["severity"].upper()
                print(f"  {i}. [{severity}] {issue['type']}")
                print(f"     {issue['message']}")
                print(f"     Fix: {issue['fix']}")
                print()

    has_errors = any(i["severity"] in ("hard", "high") for i in issues)
    if has_errors or (args.strict and issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
