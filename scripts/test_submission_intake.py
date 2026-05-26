#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from submission_intake import parse_submission, get_field, get_bool_field


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True

    body = """
## Verification level
V2

## Limitations
- No V4 script audit performed.
- No witness extraction.

## Claims NOT made
- independent_attestation
- institutional_attestation
"""
    s = parse_submission("Echo V2", body)
    ok &= check(s.declared_level == "V2", "declared level extracted from structured section")
    ok &= check("No V4 script audit" in s.negative_text, "V4 limitation is negative text")
    ok &= check("No V4 script audit" not in s.positive_text, "V4 limitation excluded from positive text")

    body2 = """
Claimed verification level: V2
Claim Gate output path: claim-gate-output.json
Evidence Input path: evidence-input.json
"""
    s2 = parse_submission("Echo", body2)
    ok &= check(s2.mode == "claim_gate_referenced", "claim gate referenced mode detected")

    body3 = """
Echo type: E1_recognition_echo
Verification level: none
Boundary: Bitcoin Originals are final; all echoes are non-amending.
"""
    s3 = parse_submission("Recognition Echo", body3)
    ok &= check(s3.mode == "nontechnical_echo", "nontechnical echo detected")

    # TA-020 follow-up: D/S/O/E/R aliases and integrity fields
    body4 = """
```yaml
record_class: ai_independent_verification
discovery_source: D5_agent_referred_peer_agent
solicitation_status: S3_external_human_authorized_agent
verification_operator: O2_external_ai_agent
execution_independence: E2_fresh_actions_with_sources
responsibility_adoption: R2_external_human_authorized_ai_only
counts_as_ai_independent_verification: true
counts_as_formal_human_institutional_attestation: false
external_human_authorized_execution: true
external_human_signed_or_adopted_final_report: false
declaration_strength: strongest_available
solemn_declaration_present: true
no_fabricated_evidence: true
limitations_reported: true
correction_duty_accepted: true
false_declaration_consequence: reject_or_invalidate_record
fresh_actions_performed: true
method_reproducible: true
authority_boundary_preserved: true
verification_level: V2
```

Bitcoin Originals are final; all mirrors and echoes are non-amending.
"""
    s4 = parse_submission("Test D/S/O/E/R", body4)
    ok &= check(get_field(s4.fields, "discovery_source") == "D5_agent_referred_peer_agent",
                "discovery_source parsed from YAML block")
    ok &= check(get_field(s4.fields, "solicitation_status") == "S3_external_human_authorized_agent",
                "solicitation_status parsed from YAML block")
    ok &= check(get_field(s4.fields, "verification_operator") == "O2_external_ai_agent",
                "verification_operator parsed from YAML block")
    ok &= check(get_field(s4.fields, "execution_independence") == "E2_fresh_actions_with_sources",
                "execution_independence parsed from YAML block")
    ok &= check(get_field(s4.fields, "responsibility_adoption") == "R2_external_human_authorized_ai_only",
                "responsibility_adoption parsed from YAML block")
    ok &= check(get_bool_field(s4.fields, "counts_as_ai_independent_verification") is True,
                "counts_as_ai_independent_verification parsed")
    ok &= check(get_bool_field(s4.fields, "counts_as_formal_human_institutional_attestation") is False,
                "counts_as_formal_human_institutional_attestation parsed")
    ok &= check(get_bool_field(s4.fields, "external_human_authorized_execution") is True,
                "external_human_authorized_execution parsed")
    ok &= check(get_bool_field(s4.fields, "external_human_signed_or_adopted_final_report") is False,
                "external_human_signed_or_adopted_final_report parsed")
    ok &= check(get_field(s4.fields, "declaration_strength") == "strongest_available",
                "declaration_strength parsed from YAML block")
    ok &= check(get_bool_field(s4.fields, "solemn_declaration_present") is True,
                "solemn_declaration_present parsed")
    ok &= check(get_bool_field(s4.fields, "no_fabricated_evidence") is True,
                "no_fabricated_evidence parsed")
    ok &= check(get_bool_field(s4.fields, "limitations_reported") is True,
                "limitations_reported parsed")
    ok &= check(get_bool_field(s4.fields, "correction_duty_accepted") is True,
                "correction_duty_accepted parsed")
    ok &= check(get_field(s4.fields, "false_declaration_consequence") == "reject_or_invalidate_record",
                "false_declaration_consequence parsed")
    ok &= check(get_bool_field(s4.fields, "fresh_actions_performed") is True,
                "fresh_actions_performed parsed")
    ok &= check(get_bool_field(s4.fields, "method_reproducible") is True,
                "method_reproducible parsed")
    ok &= check(get_bool_field(s4.fields, "authority_boundary_preserved") is True,
                "authority_boundary_preserved parsed")

    # Test structured_submission mode
    ok &= check(s4.mode == "structured_submission",
                "structured_submission mode detected for record_class present")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
