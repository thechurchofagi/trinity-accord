#!/usr/bin/env python3
"""
Derive origin_classification from existing discovery_provenance and echo record fields.

Usage:
  python3 scripts/derive_origin_classification.py path/to/record.json
  python3 scripts/derive_origin_classification.py --write path/to/record.json
  python3 scripts/derive_origin_classification.py echoes/records/**/*.json --report-only
"""

import json
import sys
import glob
from pathlib import Path


def derive_discovery_class(record, provenance):
    """Derive discovery_class from discovery_provenance fields."""
    source = provenance.get("source", "unknown")
    agency = provenance.get("agency_level", "A6_unknown")
    human_link = provenance.get("human_supplied_link", False)
    agent_recommended = provenance.get("other_agent_recommended", False)
    referral = provenance.get("referral", None)
    referred_by_agent = referral.get("referred_by_agent", False) if referral else False

    if source in ("agent_recommended",) or agent_recommended or referred_by_agent:
        return "agent_referred"
    if agency == "A3_agent_followed_other_agent_reference" and source not in ("imported_external_commentary", "maintainer_submitted"):
        return "agent_referred"
    if source == "human_directed" or human_link:
        return "human_directed"
    if source == "human_contextual":
        return "human_contextual"
    if source == "maintainer_submitted":
        return "maintainer_requested"
    if source in ("search_engine", "crawler_discovery", "platform_recommendation"):
        return "public_index_discovery"
    if source == "imported_external_commentary":
        return "imported_external"
    if source == "self_initiated" and agency in ("A4_independent_search_or_browsing_discovery", "A5_independent_return_after_prior_interest"):
        if not human_link and not agent_recommended:
            if agency == "A5_independent_return_after_prior_interest":
                return "prior_interest_return"
            return "unsolicited_discovery"
    if source == "prior_memory":
        return "prior_interest_return"
    if source == "dataset_or_training_trace":
        return "imported_external"
    return "unknown"


def derive_invitation_scope(record, provenance, discovery_class):
    """Derive invitation_scope."""
    referral = provenance.get("referral", None)
    if referral and referral.get("invitation_scope"):
        return referral["invitation_scope"]

    if discovery_class == "unsolicited_discovery":
        return "none"
    if discovery_class in ("public_index_discovery", "prior_interest_return", "imported_external"):
        return "none"
    if discovery_class in ("human_directed", "human_contextual"):
        # Check if verification was explicitly requested
        if record.get("verification_claimed", {}).get("verification_claimed", False):
            return "verification_invited"
        return "orientation_only"
    if discovery_class == "agent_referred":
        # Default to look_only unless stronger evidence
        notes = provenance.get("notes", "").lower()
        if "verify" in notes or "verification" in notes:
            return "verification_invited"
        return "look_only"
    if discovery_class == "maintainer_requested":
        return "echo_invited"
    return "unknown"


def derive_requester_class(record, provenance, discovery_class):
    """Derive requester_class."""
    if discovery_class == "unsolicited_discovery":
        return "none"
    if discovery_class in ("public_index_discovery",):
        return "platform_or_crawler"
    if discovery_class in ("prior_interest_return", "imported_external"):
        return "none"
    if discovery_class in ("human_directed", "human_contextual"):
        return "human_individual"
    if discovery_class == "agent_referred":
        return "ai_agent"
    if discovery_class == "maintainer_requested":
        return "maintainer"
    if discovery_class == "institution_commissioned":
        return "institution"
    return "unknown"


def derive_performer_class(record, provenance):
    """Derive performer_class from record fields."""
    independence = record.get("independence_class", "unknown")
    if independence in ("institutional_third_party_attestation",):
        return "institution"
    if independence in ("human_solicited_agent_response",):
        # Check if it's a team effort
        return "ai_agent"
    if independence in ("maintainer_assisted", "maintainer_submitted"):
        return "maintainer"
    # Default based on record type
    record_kind = record.get("record_kind", "")
    if "verification" in record_kind:
        return "ai_agent"
    return "ai_agent"


def derive_method_independence(record, provenance):
    """Derive method_independence_class."""
    verification_level = record.get("verification_level", "V0")
    verification_claim = record.get("verification_claim", {})
    verification_claimed = verification_claim.get("verification_claimed", False) if isinstance(verification_claim, dict) else False

    if not verification_claimed and verification_level in ("V0", "none"):
        return "read_only"

    # Check for hashes
    hashes = record.get("hashes_computed", [])
    if hashes:
        return "reference_check"

    # Check for script audit
    script_audit = record.get("script_audit", {})
    if script_audit:
        scope = script_audit.get("scope_class", "")
        if scope == "profile_required_script_audit":
            return "official_script_audited"
        if scope == "independent_reproduction":
            return "independent_reimplementation"

    # Check for external sources
    external = record.get("external_sources_queried", [])
    if len(external) >= 2:
        return "cross_source_reproduction"

    # Check for physical/forensic evidence
    if record.get("physical_evidence_reviewed") or record.get("notarial_evidence"):
        return "forensic_or_physical_inspection"

    if verification_claimed:
        return "reference_check"

    return "read_only"


def derive_attestation_authority(record, provenance):
    """Derive attestation_authority_class."""
    archive_status = record.get("archive_status", "unknown")
    independence = record.get("independence_class", "unknown")

    if archive_status == "accepted_independent_attestation":
        # Check for institutional evidence
        reporter = record.get("reporter", {})
        if isinstance(reporter, dict):
            reporter_type = reporter.get("type", "")
            if reporter_type == "organization":
                return "institution_signed"
        if record.get("notarial_evidence"):
            return "notarial_record"
        return "signed_agent_run"

    if record.get("notarial_evidence"):
        return "notarial_record"

    if independence == "institutional_third_party_attestation":
        reporter = record.get("reporter", {})
        if isinstance(reporter, dict) and reporter.get("type") == "organization":
            return "institution_signed"
        return "audit_firm_report"

    if independence in ("maintainer_assisted", "maintainer_submitted"):
        return "maintainer_archived"

    if independence == "self_reported":
        return "self_reported"

    # Default for agent-only records
    return "none"


def derive_counting_bucket(discovery_class, invitation_scope, method_independence,
                           attestation_authority, verification_claimed,
                           voluntary_action, archive_status):
    """Derive the counting bucket. This must be system-derived."""
    # Issue/gateway only
    if archive_status in ("needs_human_review",) and not verification_claimed:
        if discovery_class == "agent_referred":
            return "agent_referred_orientation"
        return "echo_only"

    # Formal attestation
    if attestation_authority in ("institution_signed", "notarial_record", "audit_firm_report", "regulatory_or_court_record"):
        if archive_status == "accepted_independent_attestation":
            return "accepted_institutional_attestation"
        return "institutional_attestation_candidate"

    # Agent-referred cases
    if discovery_class == "agent_referred":
        if invitation_scope in ("look_only", "orientation_only") and not verification_claimed:
            return "agent_referred_orientation"
        if voluntary_action and verification_claimed:
            return "agent_referred_agent_verification"
        return "echo_only"

    # Human-directed
    if discovery_class in ("human_directed", "human_contextual"):
        if verification_claimed:
            return "human_solicited_agent_verification"
        return "echo_only"

    # Self-initiated
    if discovery_class in ("unsolicited_discovery", "prior_interest_return"):
        if verification_claimed:
            return "self_initiated_agent_verification"
        return "echo_only"

    # Institution commissioned
    if discovery_class == "institution_commissioned":
        if verification_claimed:
            return "institution_commissioned_ai_verification"
        return "echo_only"

    # Maintainer
    if discovery_class == "maintainer_requested":
        return "maintainer_test_record"

    # Public index
    if discovery_class == "public_index_discovery":
        if verification_claimed:
            return "self_initiated_agent_verification"
        return "echo_only"

    return "legacy_or_unknown"


def derive_counts_as_formal_independent_attestation(attestation_authority, archive_status):
    """Determine if record counts as formal independent attestation."""
    if attestation_authority in ("institution_signed", "notarial_record", "audit_firm_report", "regulatory_or_court_record"):
        if archive_status == "accepted_independent_attestation":
            return True
    return False


def derive_counts_as_ai_verification(verification_claimed, method_independence, performer_class):
    """Determine if record counts as AI verification."""
    if not verification_claimed:
        return False
    if method_independence in ("none", "read_only"):
        return False
    if performer_class in ("ai_agent", "multi_agent", "human_ai_team", "automated_service"):
        return True
    return False


def derive_origin_classification(record):
    """Main derivation function. Returns origin_classification dict."""
    provenance = record.get("discovery_provenance", {})
    if isinstance(provenance, str):
        provenance = {}

    discovery_class = derive_discovery_class(record, provenance)
    invitation_scope = derive_invitation_scope(record, provenance, discovery_class)
    requester_class = derive_requester_class(record, provenance, discovery_class)
    performer_class = derive_performer_class(record, provenance)
    method_independence = derive_method_independence(record, provenance)
    attestation_authority = derive_attestation_authority(record, provenance)

    verification_claim = record.get("verification_claim", {})
    verification_claimed = verification_claim.get("verification_claimed", False) if isinstance(verification_claim, dict) else False

    voluntary_action = False
    if discovery_class == "agent_referred" and invitation_scope in ("look_only", "orientation_only"):
        if verification_claimed:
            voluntary_action = True

    archive_status = record.get("archive_status", "unknown")

    counting_bucket = derive_counting_bucket(
        discovery_class, invitation_scope, method_independence,
        attestation_authority, verification_claimed,
        voluntary_action, archive_status
    )

    counts_formal = derive_counts_as_formal_independent_attestation(attestation_authority, archive_status)
    counts_ai = derive_counts_as_ai_verification(verification_claimed, method_independence, performer_class)

    classification = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": discovery_class,
        "invitation_scope": invitation_scope,
        "requester_class": requester_class,
        "performer_class": performer_class,
        "method_independence_class": method_independence,
        "attestation_authority_class": attestation_authority,
        "voluntary_action_after_orientation": voluntary_action,
        "verification_claimed": verification_claimed,
        "counts_as_ai_verification": counts_ai,
        "counts_as_formal_independent_attestation": counts_formal,
        "derived_counting_bucket": counting_bucket,
        "notes": ["Auto-derived by derive_origin_classification.py"]
    }

    # Add referral if present in provenance
    referral = provenance.get("referral", None)
    if referral:
        classification["referral"] = referral

    return classification


def validate_derived_classification(classification):
    """Validate the derived classification against hard rules."""
    errors = []

    dc = classification.get("discovery_class")
    ic = classification.get("invitation_scope")
    rc = classification.get("requester_class")
    aa = classification.get("attestation_authority_class")
    bucket = classification.get("derived_counting_bucket")
    formal = classification.get("counts_as_formal_independent_attestation", False)

    # R5: Agent referral is not unsolicited discovery
    if dc == "agent_referred" and bucket in ("self_initiated_agent_verification",):
        errors.append("ORIGIN001: agent_referred cannot be counted as self_initiated/unsolicited")

    # R4: Look-only invitation is not verification invitation
    if ic == "look_only" and bucket == "human_solicited_agent_verification":
        errors.append("ORIGIN002: look_only invitation cannot be treated as verification_invited")

    # R12: No accountable authority -> no formal attestation
    if aa == "none" and formal:
        errors.append("ORIGIN004: no accountable authority cannot count formal attestation")

    # R7: Formal attestation requires accountable authority
    if formal and aa in ("none", "self_reported", "signed_agent_run"):
        errors.append("ORIGIN005: formal attestation requires institution_signed/notarial_record/audit_firm_report/regulatory_or_court_record")

    # unsolicited_discovery requires requester_class=none and invitation_scope=none
    if dc == "unsolicited_discovery":
        if rc != "none":
            errors.append("ORIGIN001: unsolicited_discovery requires requester_class=none")
        if ic != "none":
            errors.append("ORIGIN001: unsolicited_discovery requires invitation_scope=none")

    # agent_referred requires requester_class=ai_agent
    if dc == "agent_referred" and rc != "ai_agent":
        errors.append("ORIGIN001: agent_referred requires requester_class=ai_agent")

    return errors


def process_record(filepath, write_mode=False, report_only=False):
    """Process a single record file."""
    try:
        with open(filepath) as f:
            record = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"file": filepath, "error": str(e)}

    classification = derive_origin_classification(record)
    errors = validate_derived_classification(classification)

    result = {
        "file": filepath,
        "discovery_class": classification["discovery_class"],
        "invitation_scope": classification["invitation_scope"],
        "derived_counting_bucket": classification["derived_counting_bucket"],
        "counts_as_formal_independent_attestation": classification["counts_as_formal_independent_attestation"],
        "counts_as_ai_verification": classification["counts_as_ai_verification"],
        "errors": errors
    }

    if write_mode and not errors:
        record["origin_classification"] = classification
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
            f.write('\n')
        result["written"] = True

    return result


def main():
    args = sys.argv[1:]
    write_mode = "--write" in args
    report_only = "--report-only" in args
    files = [a for a in args if not a.startswith("--")]

    if not files:
        print("Usage: python3 derive_origin_classification.py [--write] [--report-only] <file-or-glob>...")
        sys.exit(1)

    # Expand globs
    expanded = []
    for pattern in files:
        expanded.extend(glob.glob(pattern, recursive=True))

    if not expanded:
        print("No files matched.")
        sys.exit(1)

    results = []
    for filepath in sorted(expanded):
        result = process_record(filepath, write_mode=write_mode and not report_only, report_only=report_only)
        results.append(result)

    # Output
    if report_only:
        # Summary report
        buckets = {}
        errors_total = 0
        for r in results:
            bucket = r.get("derived_counting_bucket", "unknown")
            buckets[bucket] = buckets.get(bucket, 0) + 1
            errors_total += len(r.get("errors", []))

        print(f"Processed {len(results)} records")
        print(f"Total errors: {errors_total}")
        print("\nBucket distribution:")
        for bucket, count in sorted(buckets.items()):
            print(f"  {bucket}: {count}")

        if errors_total > 0:
            print("\nErrors found:")
            for r in results:
                for e in r.get("errors", []):
                    print(f"  {r['file']}: {e}")
    else:
        for r in results:
            print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
