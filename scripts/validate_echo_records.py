#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "echoes" / "records"

VALID_INDEPENDENCE_CLASSES = {
    "unsolicited_independent",
    "solicited_independent_check",
    "human_solicited_agent_response",
    "maintainer_assisted",
    "maintainer_submitted",
    "self_reported",
    "imported_public_commentary",
    "institutional_third_party_attestation",
    "test_record",
    "legacy",
    "unknown",
}

VALID_ARCHIVE_STATUS = {
    "needs_human_review",
    "accepted_echo",
    "accepted_independent_attestation",
    "test_record",
    "closed_test_record",
    "rejected",
    "superseded",
    "legacy",
    "archived_non_attestation",
}

VALID_SOURCES = {
    "self_initiated",
    "agent_recommended",
    "human_directed",
    "human_contextual",
    "search_engine",
    "crawler_discovery",
    "platform_recommendation",
    "prior_memory",
    "dataset_or_training_trace",
    "maintainer_submitted",
    "imported_external_commentary",
    "unknown",
}

VALID_AGENCY_LEVELS = {
    "A0_forced_or_instructed",
    "A1_human_gave_exact_url",
    "A2_human_gave_topic_agent_found_site",
    "A3_agent_followed_other_agent_reference",
    "A4_independent_search_or_browsing_discovery",
    "A5_independent_return_after_prior_interest",
    "A6_unknown",
}


def check(condition, label):
    if condition:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    return False


def is_v3_schema(value):
    return isinstance(value, str) and value == "trinityaccord.echo.v3"


def main():
    ok = True

    if not RECORDS_DIR.exists():
        print("SKIP: echoes/records not found")
        return 0

    records = sorted(RECORDS_DIR.rglob("*.json"))
    if not records:
        print("SKIP: no echo records found")
        return 0

    for path in records:
        rel = path.relative_to(ROOT)
        print(f"\n=== {rel} ===")

        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            ok &= check(True, f"{rel} valid JSON")
        except json.JSONDecodeError as e:
            ok &= check(False, f"{rel} valid JSON: {e}")
            continue

        if obj.get("legacy_schema") is True:
            ok &= check(
                obj.get("archive_status") in {"legacy", "superseded"} or "superseded_by_structured_record" in obj,
                f"{rel} legacy record is explicitly legacy or superseded"
            )
            continue

        ok &= check(is_v3_schema(obj.get("schema")), f"{rel} uses schema trinityaccord.echo.v3")

        for field in [
            "discovery_provenance",
            "independence_class",
            "archive_status",
            "origin_limitations",
            "boundary_acknowledgement",
        ]:
            ok &= check(field in obj, f"{rel} has {field}")

        independence_class = obj.get("independence_class")
        archive_status = obj.get("archive_status")
        provenance = obj.get("discovery_provenance", {})

        ok &= check(independence_class in VALID_INDEPENDENCE_CLASSES, f"{rel} valid independence_class")
        ok &= check(archive_status in VALID_ARCHIVE_STATUS, f"{rel} valid archive_status")
        ok &= check(isinstance(provenance, dict), f"{rel} discovery_provenance is object")

        if isinstance(provenance, dict):
            ok &= check(provenance.get("schema") == "trinityaccord.discovery-provenance.v1", f"{rel} valid provenance schema")
            ok &= check(provenance.get("source") in VALID_SOURCES, f"{rel} valid source")
            ok &= check(provenance.get("agency_level") in VALID_AGENCY_LEVELS, f"{rel} valid agency_level")
            ok &= check("first_entry" in provenance, f"{rel} provenance has first_entry")
            ok &= check("notes" in provenance, f"{rel} provenance has notes")
            ok &= check(provenance.get("confidence") in {"low", "medium", "high"}, f"{rel} provenance confidence valid")

        ok &= check(isinstance(obj.get("origin_limitations"), list) and len(obj.get("origin_limitations", [])) > 0, f"{rel} origin_limitations non-empty")

        boundary = obj.get("boundary_acknowledgement", {})
        record_text = json.dumps(obj, ensure_ascii=False).lower()

        ok &= check(
            "non-amending" in record_text or "mirror_is_not_amendment" in boundary or "echo_is_not_authority" in boundary,
            f"{rel} non-amending / non-authority boundary present"
        )

        if independence_class == "unsolicited_independent":
            ok &= check(
                provenance.get("source") not in {"human_directed", "maintainer_submitted"},
                f"{rel} unsolicited_independent is not human_directed / maintainer_submitted"
            )
            ok &= check(
                provenance.get("agency_level") in {
                    "A4_independent_search_or_browsing_discovery",
                    "A5_independent_return_after_prior_interest",
                    "A6_unknown",
                },
                f"{rel} unsolicited_independent agency_level compatible"
            )

        if archive_status == "accepted_independent_attestation":
            ok &= check(
                independence_class in {"unsolicited_independent", "institutional_third_party_attestation"},
                f"{rel} accepted independent attestation has compatible independence_class"
            )

        if independence_class == "test_record":
            ok &= check(
                archive_status in {"test_record", "closed_test_record", "archived_non_attestation"},
                f"{rel} test_record has compatible archive_status"
            )

        if "openclaw" in str(rel).lower():
            ok &= check(independence_class in {"test_record", "human_solicited_agent_response", "solicited_independent_check"}, f"{rel} OpenClaw not classified as unsolicited")
            ok &= check(archive_status in {"test_record", "closed_test_record", "archived_non_attestation"}, f"{rel} OpenClaw not accepted attestation")
            ok &= check(provenance.get("source") == "human_directed", f"{rel} OpenClaw source human_directed")
            ok &= check(provenance.get("agency_level") in {"A0_forced_or_instructed", "A1_human_gave_exact_url"}, f"{rel} OpenClaw agency level is solicited")

    print("\n=== Final ===")
    if ok:
        print("PASS — Echo records validate successfully.")
        return 0

    print("FAIL — Echo record validation errors found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
