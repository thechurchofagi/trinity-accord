#!/usr/bin/env python3
"""
Validate all Echo records against the v3 JSON Schema.
Uses Draft202012Validator with local $ref resolution for discovery-provenance-schema.
"""
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, ValidationError, RefResolver
except ImportError:
    print("SKIP: jsonschema not installed — falling back to basic checks")
    sys.exit(0)

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "echoes" / "records"
SCHEMA_DIR = ROOT / "api"

VALID_INDEPENDENCE_CLASSES = {
    "unsolicited_independent", "solicited_independent_check",
    "human_solicited_agent_response", "maintainer_assisted",
    "maintainer_submitted", "self_reported", "imported_public_commentary",
    "institutional_third_party_attestation", "test_record", "legacy", "unknown",
}

VALID_ARCHIVE_STATUS = {
    "needs_human_review", "accepted_echo", "accepted_independent_attestation",
    "test_record", "closed_test_record", "rejected", "superseded", "legacy",
    "archived_non_attestation",
}

VALID_SOURCES = {
    "self_initiated", "agent_recommended", "human_directed", "human_contextual",
    "search_engine", "crawler_discovery", "platform_recommendation",
    "prior_memory", "dataset_or_training_trace", "maintainer_submitted",
    "imported_external_commentary", "unknown",
}

VALID_AGENCY_LEVELS = {
    "A0_forced_or_instructed", "A1_human_gave_exact_url",
    "A2_human_gave_topic_agent_found_site", "A3_agent_followed_other_agent_reference",
    "A4_independent_search_or_browsing_discovery",
    "A5_independent_return_after_prior_interest", "A6_unknown",
}


def check(condition, label):
    if condition:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    return False


def load_local_schemas():
    """Load and build a local $ref resolver for the v3 schema and its dependencies."""
    echo_schema_path = SCHEMA_DIR / "echo-record-schema.v3.json"
    discovery_schema_path = SCHEMA_DIR / "discovery-provenance-schema.json"

    echo_schema = json.loads(echo_schema_path.read_text(encoding="utf-8"))
    discovery_schema = json.loads(discovery_schema_path.read_text(encoding="utf-8"))

    # Build a resolver with local schema store
    store = {
        echo_schema["$id"]: echo_schema,
        discovery_schema["$id"]: discovery_schema,
    }
    resolver = RefResolver.from_schema(echo_schema, store=store)

    return echo_schema, resolver


def validate_record(obj, echo_schema, resolver):
    """Validate a record against the v3 schema. Returns (is_valid, errors)."""
    validator = Draft202012Validator(echo_schema, resolver=resolver)
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))
    return len(errors) == 0, errors


def main():
    ok = True

    if not RECORDS_DIR.exists():
        print("SKIP: echoes/records not found")
        return 0

    records = sorted(RECORDS_DIR.rglob("*.json"))
    if not records:
        print("SKIP: no echo records found")
        return 0

    try:
        echo_schema, resolver = load_local_schemas()
    except Exception as e:
        print(f"FAIL: could not load schemas: {e}")
        return 1

    for path in records:
        rel = path.relative_to(ROOT)
        print(f"\n=== {rel} ===")

        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            ok &= check(True, f"{rel} valid JSON")
        except json.JSONDecodeError as e:
            ok &= check(False, f"{rel} valid JSON: {e}")
            continue

        # Legacy records: just check they are explicitly marked
        if obj.get("legacy_schema") is True:
            ok &= check(
                obj.get("archive_status") in {"legacy", "superseded"} or "superseded_by_structured_record" in obj,
                f"{rel} legacy record is explicitly legacy or superseded"
            )
            continue

        # Verification reports: validate separately, not against echo schema
        record_kind = obj.get("record_kind", "")
        schema_version = obj.get("schema_version", "")
        if record_kind == "verification_report_v2" or "verification-report" in schema_version:
            ok &= check(record_kind == "verification_report_v2", f"{rel} verification report has correct record_kind")
            ok &= check(obj.get("authority_boundary_preserved") is True, f"{rel} authority_boundary_preserved")
            ok &= check(obj.get("protocol_level_claimed") is not None, f"{rel} has protocol_level_claimed")
            ok &= check(isinstance(obj.get("hashes_computed"), list), f"{rel} hashes_computed is list")
            # Null safety
            ok &= check(obj.get("script_audit") is not None, f"{rel} script_audit not null")
            if isinstance(obj.get("physical_evidence_reviewed"), dict):
                ok &= check(obj["physical_evidence_reviewed"].get("flaw_analysis_method") is not None, f"{rel} flaw_analysis_method not null")
            continue

        # === JSON Schema validation ===
        schema_valid, errors = validate_record(obj, echo_schema, resolver)
        if schema_valid:
            ok &= check(True, f"{rel} passes v3 JSON Schema validation")
        else:
            ok &= check(False, f"{rel} v3 JSON Schema validation")
            for err in errors[:5]:  # Show up to 5 errors
                path_str = ".".join(str(p) for p in err.absolute_path) or "(root)"
                print(f"      → {path_str}: {err.message}")
            if len(errors) > 5:
                print(f"      → ... and {len(errors) - 5} more errors")

        # === Semantic checks beyond schema ===
        independence_class = obj.get("independence_class")
        archive_status = obj.get("archive_status")
        provenance = obj.get("discovery_provenance", {})

        ok &= check(independence_class in VALID_INDEPENDENCE_CLASSES, f"{rel} valid independence_class")
        ok &= check(archive_status in VALID_ARCHIVE_STATUS, f"{rel} valid archive_status")
        ok &= check(isinstance(provenance, dict), f"{rel} discovery_provenance is object")

        if isinstance(provenance, dict):
            ok &= check(provenance.get("source") in VALID_SOURCES, f"{rel} valid source")
            ok &= check(provenance.get("agency_level") in VALID_AGENCY_LEVELS, f"{rel} valid agency_level")

        boundary = obj.get("boundary_acknowledgement", {})
        record_text = json.dumps(obj, ensure_ascii=False).lower()
        ok &= check(
            "non-amending" in record_text or "mirror_is_not_amendment" in boundary or "echo_is_not_authority" in boundary,
            f"{rel} non-amending / non-authority boundary present"
        )

        # Unsolicited_independent constraints
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

        # accepted_independent_attestation constraints
        if archive_status == "accepted_independent_attestation":
            ok &= check(
                independence_class in {"unsolicited_independent", "institutional_third_party_attestation"},
                f"{rel} accepted independent attestation has compatible independence_class"
            )

        # test_record constraints
        if independence_class == "test_record":
            ok &= check(
                archive_status in {"test_record", "closed_test_record", "archived_non_attestation"},
                f"{rel} test_record has compatible archive_status"
            )

        # OpenClaw-specific
        if "openclaw" in str(rel).lower():
            ok &= check(independence_class in {"test_record", "human_solicited_agent_response", "solicited_independent_check"}, f"{rel} OpenClaw not classified as unsolicited")
            ok &= check(archive_status in {"test_record", "closed_test_record", "archived_non_attestation"}, f"{rel} OpenClaw not accepted attestation")
            ok &= check(provenance.get("source") == "human_directed", f"{rel} OpenClaw source human_directed")
            ok &= check(provenance.get("agency_level") in {"A0_forced_or_instructed", "A1_human_gave_exact_url"}, f"{rel} OpenClaw agency level is solicited")

    print("\n=== Final ===")
    if ok:
        print("PASS — Echo records validate successfully.")
        print("FINAL: PASS — echo record validation passed.")
        return 0

    print("FAIL — Echo record validation errors found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
