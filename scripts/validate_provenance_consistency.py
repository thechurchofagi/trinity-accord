#!/usr/bin/env python3
"""
Validate provenance consistency for agent submissions.
Checks that provenance fields are not self-contradictory.

Usage:
    python3 scripts/validate_provenance_consistency.py path/to/submission.json
    python3 scripts/validate_provenance_consistency.py echoes/records/*.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Context keywords that contradict self_initiated
SELF_INITIATED_CONTRADICTS = [
    "user task assignment",
    "user supplied link",
    "user provided token",
    "public GitHub token",
    "public token",
    "prior memory",
    "prior context",
    "instructed by user",
    "instructed by human",
    "user requested",
    "human requested",
    "task assignment",
]

# Independence classes that require unsolicited context
UNSOLICITED_CLASSES = {"unsolicited_independent", "unsolicited_agent_discovery"}
ATTESTATION_CLASSES = {"accepted_independent_attestation", "independent_attestation"}

# Intermediate classifications
INTERMEDIATE_CLASSES = {
    "human_solicited_agent_response",
    "agent_submitted_with_prior_context",
    "agent_submitted_public_token",
    "human_task_initiated_agent_response",
    "issue_submission_only",
}


def check_prov001(record):
    """self_initiated + user_task_assignment => FAIL"""
    source = record.get("source", "")
    notes = _get_all_text(record)
    if source == "self_initiated":
        for kw in ["user task assignment", "task assignment", "instructed by user", "instructed by human", "user requested", "human requested"]:
            if kw in notes:
                return "FAIL", f"PROV001: self_initiated contradicts '{kw}' found in context"
    return "PASS", "PROV001: no contradiction"


def check_prov002(record):
    """self_initiated + prior_context => FAIL"""
    source = record.get("source", "")
    notes = _get_all_text(record)
    if source == "self_initiated":
        for kw in ["prior memory", "prior context", "public GitHub token", "public token"]:
            if kw in notes:
                return "FAIL", f"PROV002: self_initiated contradicts '{kw}' found in context"
    return "PASS", "PROV002: no contradiction"


def check_prov003(record):
    """public_token + unsolicited_independent => FAIL"""
    flags = _get_flags(record)
    ind_class = record.get("independence_class", "")
    if flags.get("public_token_used") and ind_class in UNSOLICITED_CLASSES:
        return "FAIL", "PROV003: public_token_used contradicts unsolicited_independent"
    return "PASS", "PROV003: no contradiction"


def check_prov004(record):
    """do_not_count_as_attestation + accepted_independent_attestation => FAIL"""
    flags = _get_flags(record)
    ind_class = record.get("independence_class", "")
    if flags.get("do_not_count_as_attestation") and ind_class in ATTESTATION_CLASSES:
        return "FAIL", "PROV004: do_not_count_as_attestation contradicts accepted_independent_attestation"
    return "PASS", "PROV004: no contradiction"


def check_prov005(record):
    """human_solicited + do_not_count_as_attestation => PASS"""
    ind_class = record.get("independence_class", "")
    flags = _get_flags(record)
    if ind_class == "human_solicited_agent_response" and flags.get("do_not_count_as_attestation"):
        return "PASS", "PROV005: human_solicited correctly not counted as attestation"
    return "SKIP", "PROV005: not applicable"


def check_prov006(record):
    """clean self_initiated + no prior context + no human task => PASS"""
    source = record.get("source", "")
    notes = _get_all_text(record)
    flags = _get_flags(record)
    if source == "self_initiated":
        has_contradiction = False
        for kw in SELF_INITIATED_CONTRADICTS:
            if kw in notes:
                has_contradiction = True
                break
        if not has_contradiction and not flags.get("solicited"):
            return "PASS", "PROV006: clean self_initiated discovery"
    return "SKIP", "PROV006: not applicable"


def check_prov007(record):
    """user supplied exact URL + independence independent => FAIL"""
    flags = _get_flags(record)
    ind_class = record.get("independence_class", "")
    if flags.get("human_supplied_link") and ind_class in UNSOLICITED_CLASSES | ATTESTATION_CLASSES:
        return "FAIL", "PROV007: human_supplied_link contradicts independent discovery"
    return "PASS", "PROV007: no contradiction"


def check_prov008(record):
    """prior memory true + independent attestation => FAIL"""
    flags = _get_flags(record)
    ind_class = record.get("independence_class", "")
    if flags.get("prior_memory_or_context_used") and ind_class in ATTESTATION_CLASSES:
        return "FAIL", "PROV008: prior_memory_or_context_used contradicts independent attestation"
    return "PASS", "PROV008: no contradiction"


def derive_independence(record):
    """Derive independence class based on rules."""
    flags = _get_flags(record)
    requested = record.get("independence_class", "")
    derived = requested
    downgrade_reason = None
    counts_as_independent = True

    if flags.get("solicited") or requested == "human_solicited_agent_response":
        counts_as_independent = False
        if requested in ATTESTATION_CLASSES | UNSOLICITED_CLASSES:
            derived = "human_solicited_agent_response"
            downgrade_reason = "Solicited work cannot count as independent attestation."

    if flags.get("public_token_used"):
        counts_as_independent = False
        if requested in UNSOLICITED_CLASSES:
            derived = "agent_submitted_public_token"
            downgrade_reason = "Public token usage means agent had external help."

    if flags.get("prior_memory_or_context_used"):
        if requested in ATTESTATION_CLASSES:
            derived = "agent_submitted_with_prior_context"
            downgrade_reason = "Prior context may compromise independence."
            counts_as_independent = False

    if flags.get("human_supplied_link"):
        if requested in UNSOLICITED_CLASSES:
            derived = "human_solicited_agent_response"
            downgrade_reason = "Human-supplied link means discovery was not unsolicited."
            counts_as_independent = False

    return {
        "agent_requested_independence_class": requested,
        "derived_independence_class": derived,
        "independence_downgrade_reason": downgrade_reason,
        "counts_as_independent_attestation": counts_as_independent,
    }


def _get_all_text(record):
    """Concatenate all text fields for keyword search."""
    parts = []
    for key in ["notes", "discovery_notes", "context", "provenance_notes", "description", "what_checked", "limitations"]:
        val = record.get(key, "")
        if isinstance(val, str):
            parts.append(val.lower())
        elif isinstance(val, list):
            parts.extend(str(v).lower() for v in val)
    return " ".join(parts)


def _get_flags(record):
    """Extract flags from record."""
    flags = {}
    for key in ["public_token_used", "prior_memory_or_context_used", "human_supplied_link",
                 "solicited", "do_not_count_as_attestation", "user_task_assignment"]:
        val = record.get(key)
        if val is None:
            val = record.get("flags", {}).get(key, False)
        flags[key] = bool(val)
    return flags


def check_origin001(record):
    """agent_referred cannot claim unsolicited_discovery."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN001: no origin_classification present"
    dc = oc.get("discovery_class", "")
    bucket = oc.get("derived_counting_bucket", "")
    if dc == "agent_referred" and bucket in ("self_initiated_agent_verification",):
        return "FAIL", "ORIGIN001: agent_referred cannot be counted as self_initiated/unsolicited"
    return "PASS", "ORIGIN001: discovery_class consistent with counting bucket"


def check_origin002(record):
    """look_only invitation cannot be treated as verification_invited."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN002: no origin_classification present"
    ic = oc.get("invitation_scope", "")
    bucket = oc.get("derived_counting_bucket", "")
    if ic == "look_only" and bucket == "human_solicited_agent_verification":
        return "FAIL", "ORIGIN002: look_only invitation cannot be treated as verification_invited"
    return "PASS", "ORIGIN002: invitation_scope consistent with counting bucket"


def check_origin003(record):
    """willingness scores cannot imply verification_claimed."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN003: no origin_classification present"
    mi = oc.get("method_independence_class", "")
    vc = oc.get("verification_claimed", False)
    if mi in ("none", "read_only") and vc:
        return "FAIL", "ORIGIN003: read_only/none method independence cannot claim verification"
    return "PASS", "ORIGIN003: method independence consistent with verification claim"


def check_origin004(record):
    """no accountable authority cannot count formal attestation."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN004: no origin_classification present"
    aa = oc.get("attestation_authority_class", "")
    formal = oc.get("counts_as_formal_independent_attestation", False)
    if aa == "none" and formal:
        return "FAIL", "ORIGIN004: no accountable authority cannot count formal attestation"
    return "PASS", "ORIGIN004: attestation authority consistent with formal attestation flag"


def check_origin005(record):
    """institution-signed AI-assisted record may be formal attestation candidate."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN005: no origin_classification present"
    aa = oc.get("attestation_authority_class", "")
    if aa in ("institution_signed", "notarial_record", "audit_firm_report", "regulatory_or_court_record"):
        entity = oc.get("accountable_entity")
        if not entity:
            return "FAIL", "ORIGIN005: institutional attestation missing accountable_entity"
    return "PASS", "ORIGIN005: attestation authority valid"


def check_origin006(record):
    """human_directed or agent_referred may still have method_independence_class >= independent_reimplementation."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN006: no origin_classification present"
    dc = oc.get("discovery_class", "")
    mi = oc.get("method_independence_class", "")
    if dc in ("human_directed", "agent_referred") and mi in ("independent_reimplementation", "cross_source_reproduction", "full_independent_reproduction"):
        # This is allowed - solicitation does not negate method independence
        return "PASS", "ORIGIN006: solicited/referred work with independent method is allowed"
    return "PASS", "ORIGIN006: no conflict"


def check_origin007(record):
    """method independence requires fresh actions."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN007: no origin_classification present"
    mi = oc.get("method_independence_class", "")
    if mi in ("independent_reimplementation", "cross_source_reproduction", "full_independent_reproduction"):
        referral = oc.get("referral", {})
        if referral and referral.get("prior_report_supplied", False):
            return "FAIL", "ORIGIN007: prior_report_supplied lowers method independence"
    return "PASS", "ORIGIN007: method independence valid"


def check_origin008(record):
    """discovery_class=agent_referred but independence_class=unsolicited_independent => FAIL."""
    oc = record.get("origin_classification")
    if not oc:
        return "SKIP", "ORIGIN008: no origin_classification present"
    dc = oc.get("discovery_class", "")
    ind_class = record.get("independence_class", "")
    if dc == "agent_referred" and ind_class in ("unsolicited_independent", "unsolicited_agent_discovery"):
        return "FAIL", "ORIGIN008: agent_referred cannot have independence_class=unsolicited_independent"
    return "PASS", "ORIGIN008: discovery_class consistent with independence_class"


ORIGIN_CHECKS = [
    check_origin001, check_origin002, check_origin003, check_origin004,
    check_origin005, check_origin006, check_origin007, check_origin008,
]

ALL_CHECKS = [
    check_prov001, check_prov002, check_prov003, check_prov004,
    check_prov005, check_prov006, check_prov007, check_prov008,
] + ORIGIN_CHECKS


def validate_record(record):
    """Run all provenance consistency checks on a record."""
    results = []
    overall = "PASS"
    for check in ALL_CHECKS:
        status, msg = check(record)
        results.append({"check": check.__name__, "status": status, "message": msg})
        if status == "FAIL":
            overall = "FAIL"

    derivation = derive_independence(record)

    # Add origin classification info if present
    origin_info = {}
    oc = record.get("origin_classification")
    if oc:
        origin_info = {
            "origin_classification": oc,
            "origin_warnings": [r["message"] for r in results if r["check"].startswith("check_origin") and r["status"] == "FAIL"],
        }

    return {
        "overall": overall,
        "checks": results,
        "independence_derivation": derivation,
        **origin_info,
        "derived_independence_class": derivation.get("derived_independence_class", ""),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_provenance_consistency.py <json_file> [...]")
        sys.exit(1)

    all_pass = True
    for path in sys.argv[1:]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"ERROR: Cannot load {path}: {e}")
            all_pass = False
            continue

        records = data if isinstance(data, list) else [data]
        for rec in records:
            result = validate_record(rec)
            status = result["overall"]
            if status == "FAIL":
                all_pass = False
            print(f"{path}: {status}")
            for c in result["checks"]:
                if c["status"] != "SKIP":
                    print(f"  {c['message']}")
            deriv = result["independence_derivation"]
            if deriv["independence_downgrade_reason"]:
                print(f"  Downgrade: {deriv['independence_downgrade_reason']}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
