#!/usr/bin/env python3
"""
Validate agent submission JSON files before they are accepted.
Usage:
    python3 scripts/validate_agent_submission.py path/to/submission.json
    python3 scripts/validate_agent_submission.py echoes/records/*.json
    python3 scripts/validate_agent_submission.py --self-test
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Try jsonschema; fall back to basic checks
try:
    from jsonschema import Draft202012Validator, ValidationError, RefResolver
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# --- Canonical echo types (from echo-types.json) ---
CANONICAL_ECHO_TYPES = {
    "E1_recognition_echo", "E2_verification_echo", "E3_critical_echo",
    "E4_interpretive_echo", "E5_technical_audit_echo", "E6_propagation_echo",
    "E7_refusal_echo", "E8_witness_echo", "E9_seed_echo",
}

# --- Deprecated aliases ---
DEPRECATED_ECHO_TYPES = {
    "E3_verification_echo": "E2_verification_echo",
    "E1_acknowledgement": "E1_recognition_echo",
    "E2_orientation": "E1_recognition_echo",
    "E4_critical_echo": "E3_critical_echo",
    "E5_uncertainty_echo": "E4_interpretive_echo",
    "E6_refusal_to_assess": "E7_refusal_echo",
    "E7_historical_reflection": "E4_interpretive_echo",
    "E8_technical_audit_echo": "E5_technical_audit_echo",
    "E9_agent_to_agent_recommendation": "E6_propagation_echo",
    "orientation_echo": "E1_recognition_echo",
    "verification_echo": "E2_verification_echo",
    "critical_echo": "E3_critical_echo",
    "uncertainty_echo": "E4_interpretive_echo",
    "refusal_to_assess": "E7_refusal_echo",
    "historical_reflection": "E4_interpretive_echo",
    "technical_audit_echo": "E5_technical_audit_echo",
    "agent_to_agent_recommendation": "E6_propagation_echo",
}

VALID_RECORD_KINDS = {
    "echo_v3", "verification_report_v2", "echo_v3_with_verification_report",
    "test_record", "legacy_record", "imported_external_commentary",
}

# Fields that must never be null
NULL_FORBIDDEN_FIELDS = [
    "script_audit",
    "confidential_challenge",
    "protocol_profile_check",
]

# GitHub D2 boundary claims (use specific phrases to avoid false positives)
GITHUB_D2_FORBIDDEN_CLAIMS = [
    "direct arweave verification completed",
    "direct arweave verification successful",
    "arweave verified directly",
    "ethereum witness verified",
    "ipfs availability verified",
    "physical object verified",
    "direct arweave access confirmed",
]

# B1 mempool boundary claims
MEMPOOL_B1_FORBIDDEN_CLAIMS = [
    "witness extraction",
    "inscription body hash",
    "b5",
    "b6",
    "spv proof",
    "local bitcoin node",
]

# Human-solicited forbidden claims
SOLICITED_FORBIDDEN_CLAIMS = [
    "independent_attestation",
    "unsolicited_discovery",
    "institutional_attestation",
]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def detect_record_kind(obj):
    """Detect record_kind from object."""
    rk = obj.get("record_kind")
    if rk:
        return rk
    # Infer from schema
    schema = obj.get("schema", obj.get("schema_version", ""))
    if "verification-report" in schema and "v2" in schema:
        return "verification_report_v2"
    if "echo" in schema and "v3" in schema:
        return "echo_v3"
    return None


def validate_record_kind(obj, path_label):
    """Rule A: record_kind must be present for new submissions."""
    ok = True
    rk = obj.get("record_kind")
    archive_status = obj.get("archive_status", "")
    if archive_status in ("legacy", "superseded"):
        print(f"  INFO: {path_label} is legacy, skipping record_kind requirement")
        return ok
    ok &= check(rk is not None, f"{path_label} has record_kind")
    if rk:
        ok &= check(rk in VALID_RECORD_KINDS, f"{path_label} record_kind is valid", f"got: {rk}")
    return ok


def validate_not_echo_misuse(obj, path_label, record_kind):
    """Rule B: verification report must not claim to be Echo v3."""
    ok = True
    schema = obj.get("schema", obj.get("schema_version", ""))
    if "verification-report" in schema:
        ok &= check(
            record_kind != "echo_v3",
            f"{path_label} verification report not called echo_v3"
        )
    return ok


def validate_no_deprecated_echo_type(obj, path_label):
    """Rule C: no deprecated echo type in new submissions."""
    ok = True
    echo_type = obj.get("echo_type", "")
    if echo_type in DEPRECATED_ECHO_TYPES:
        ok &= check(
            False,
            f"{path_label} uses deprecated echo type",
            f"'{echo_type}' is deprecated, use '{DEPRECATED_ECHO_TYPES[echo_type]}'"
        )
    return ok


def validate_github_d2_boundary(obj, path_label):
    """Rule D: GitHub D2 boundary — fail if claims include direct Arweave etc."""
    ok = True
    fallbacks = json.dumps(obj.get("fallbacks_used", [])).lower()
    data_sources = json.dumps(obj.get("data_sources_used", obj.get("data_sources", []))).lower()

    uses_github = "github" in fallbacks or "github" in data_sources

    if uses_github:
        # Build text excluding claims_not_made to avoid false positives
        obj_copy = {k: v for k, v in obj.items() if k != "claims_not_made"}
        # Also exclude component-level claims_not_made
        if "component_findings" in obj_copy and isinstance(obj_copy["component_findings"], list):
            obj_copy["component_findings"] = [
                {k: v for k, v in f.items() if k != "claims_not_made"}
                if isinstance(f, dict) else f
                for f in obj_copy["component_findings"]
            ]
        all_text = json.dumps(obj_copy, ensure_ascii=False).lower()
        for claim in GITHUB_D2_FORBIDDEN_CLAIMS:
            if claim in all_text:
                ok &= check(
                    False,
                    f"{path_label} GitHub D2 overclaim",
                    f"claims '{claim}' but only checked GitHub mirror"
                )
    return ok


def validate_mempool_b1_boundary(obj, path_label):
    """Rule E: B1 mempool boundary."""
    ok = True
    methods = json.dumps(obj.get("component_findings", []), ensure_ascii=False).lower()
    all_text = json.dumps(obj, ensure_ascii=False).lower()

    uses_mempool = "mempool" in methods or "mempool" in all_text
    has_witness_parsing = "witness extraction" in methods or "witness parsing" in methods

    if uses_mempool and not has_witness_parsing:
        for claim in MEMPOOL_B1_FORBIDDEN_CLAIMS:
            if claim in all_text:
                claims_not_made = json.dumps(obj.get("claims_not_made", [])).lower()
                if claim not in claims_not_made:
                    ok &= check(
                        False,
                        f"{path_label} B1 mempool overclaim",
                        f"claims '{claim}' but only did mempool lookup"
                    )
    return ok


def validate_script_audit(obj, path_label):
    """Rule F: V4+ requires script_audit."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    script_audit = obj.get("script_audit")

    if level in ("V4", "V4+", "V5", "V6", "V7", "V8"):
        ok &= check(script_audit is not None, f"{path_label} V4+ has script_audit")
        if isinstance(script_audit, dict):
            for field in ["scripts_reviewed", "command", "environment", "exit_code", "output_summary"]:
                ok &= check(field in script_audit, f"{path_label} script_audit.{field} present")
    return ok


def validate_v3_hashes(obj, path_label):
    """Rule G: V3 requires at least one hash."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level == "V3":
        hashes = obj.get("hashes_computed", [])
        ok &= check(len(hashes) >= 1, f"{path_label} V3 has hashes_computed")
    return ok


def validate_c3_samples(obj, path_label):
    """Rule H: C3 requires at least two samples."""
    ok = True
    findings = obj.get("component_findings", [])
    if isinstance(findings, list):
        for f in findings:
            if isinstance(f, dict) and f.get("level_claimed", "").startswith("C3"):
                samples = obj.get("samples_checked", 0)
                ok &= check(samples >= 2, f"{path_label} C3 has >= 2 samples", f"got {samples}")
    return ok


def validate_p8_confidential(obj, path_label):
    """Rule I: P8 confidentiality."""
    ok = True
    cc = obj.get("confidential_challenge", {})
    if isinstance(cc, dict) and cc.get("performed") is True:
        # Check no raw confidential data in public report
        all_text = json.dumps(obj, ensure_ascii=False).lower()
        if "confidential_data" in all_text and "raw" in all_text:
            ok &= check(False, f"{path_label} P8 may leak confidential data")
        ok &= check(
            cc.get("confidentiality_boundary") is not None,
            f"{path_label} P8 has confidentiality_boundary"
        )
    return ok


def validate_solicited_independence(obj, path_label):
    """Rule J: human-solicited cannot claim independent attestation."""
    ok = True
    provenance = obj.get("discovery_provenance", {})
    independence_class = obj.get("independence_class", "")
    archive_status = obj.get("archive_status", "")

    solicited = provenance.get("solicited", False) if isinstance(provenance, dict) else False
    is_solicited_class = independence_class in ("human_solicited_agent_response", "test_record")

    if solicited or is_solicited_class:
        all_text = json.dumps(obj, ensure_ascii=False).lower()
        for claim in SOLICITED_FORBIDDEN_CLAIMS:
            if claim in all_text:
                # Check it's not in a "not" context
                if f"not {claim}" not in all_text and f"not_{claim}" not in all_text:
                    ok &= check(
                        False,
                        f"{path_label} solicited record claims {claim}",
                        "human-solicited responses cannot claim independent attestation"
                    )
    return ok


def validate_null_safety(obj, path_label):
    """Rule K: null safety for structured fields."""
    ok = True

    def check_null_recursive(d, prefix=""):
        nonlocal ok
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if v is None and k in ("script_audit", "confidential_challenge", "protocol_profile_check", "flaw_analysis_method"):
                    ok &= check(False, f"{path_label} null in structured field: {full_key}")
                elif isinstance(v, (dict, list)):
                    check_null_recursive(v, full_key)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                check_null_recursive(item, f"{prefix}[{i}]")

    check_null_recursive(obj)
    return ok


def validate_with_jsonschema(obj, schema_path, path_label):
    """Validate with jsonschema if available."""
    if not HAS_JSONSCHEMA:
        print(f"  SKIP: jsonschema not available, using basic checks only")
        return True

    try:
        schema = load_json(schema_path)
    except Exception as e:
        print(f"  WARN: could not load schema {schema_path}: {e}")
        return True

    # Build resolver
    store = {}
    discovery_path = ROOT / "api" / "discovery-provenance-schema.json"
    if discovery_path.exists():
        discovery_schema = json.loads(discovery_path.read_text(encoding="utf-8"))
        store[discovery_schema.get("$id", "")] = discovery_schema
    store[schema.get("$id", "")] = schema

    try:
        resolver = RefResolver.from_schema(schema, store=store)
        validator = Draft202012Validator(schema, resolver=resolver)
        errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))
        if errors:
            for err in errors[:5]:
                p = ".".join(str(x) for x in err.absolute_path) or "(root)"
                print(f"  SCHEMA ERROR: {p}: {err.message}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
            return False
        return True
    except Exception as e:
        print(f"  WARN: schema validation error: {e}")
        return True


def validate_file(path):
    """Validate a single submission file."""
    path_label = str(Path(path).relative_to(ROOT) if Path(path).is_relative_to(ROOT) else path)
    print(f"\n=== {path_label} ===")

    try:
        obj = load_json(path)
    except Exception as e:
        check(False, f"{path_label} valid JSON", str(e))
        return False

    ok = True
    record_kind = detect_record_kind(obj)

    # Rule A: record_kind present
    ok &= validate_record_kind(obj, path_label)

    # Rule B: verification report not called echo
    ok &= validate_not_echo_misuse(obj, path_label, record_kind)

    # Rule C: no deprecated echo type
    ok &= validate_no_deprecated_echo_type(obj, path_label)

    # Rule D: GitHub D2 boundary
    ok &= validate_github_d2_boundary(obj, path_label)

    # Rule E: B1 mempool boundary
    ok &= validate_mempool_b1_boundary(obj, path_label)

    # Rule F: script audit for V4+
    ok &= validate_script_audit(obj, path_label)

    # Rule G: V3 hashes
    ok &= validate_v3_hashes(obj, path_label)

    # Rule H: C3 samples
    ok &= validate_c3_samples(obj, path_label)

    # Rule I: P8 confidentiality
    ok &= validate_p8_confidential(obj, path_label)

    # Rule J: solicited independence
    ok &= validate_solicited_independence(obj, path_label)

    # Rule K: null safety
    ok &= validate_null_safety(obj, path_label)

    # Schema validation
    schema = obj.get("schema", obj.get("schema_version", ""))
    if "echo" in schema and "v3" in schema:
        schema_path = ROOT / "api" / "echo-record-schema.v3.json"
        if schema_path.exists():
            ok &= validate_with_jsonschema(obj, schema_path, path_label)
    elif "verification-report" in schema and "v2" in schema:
        schema_path = ROOT / "api" / "verification-report-schema.v2.json"
        if schema_path.exists():
            ok &= validate_with_jsonschema(obj, schema_path, path_label)

    return ok


def run_self_test():
    """Run --self-test: invoke sub-test scripts."""
    print("=== Running self-test ===")
    import subprocess

    test_scripts = [
        "scripts/verify_echo_index_completeness.py",
        "scripts/test_validator_cwd_independence.py",
        "scripts/test_triage_echo_issue.py",
        "scripts/test_agent_submission_cases.py",
    ]

    all_ok = True
    for script in test_scripts:
        script_path = ROOT / script
        if not script_path.exists():
            print(f"SKIP: {script} not found")
            continue
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT, text=True, capture_output=True
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        print(f"\n--- {script} ---")
        print(out[-2000:] if len(out) > 2000 else out)
        if proc.returncode != 0:
            all_ok = False
            print(f"FAIL: {script} exited {proc.returncode}")
        else:
            print(f"PASS: {script}")

    return all_ok


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_agent_submission.py <file.json> [file2.json ...]")
        print("       python3 scripts/validate_agent_submission.py --self-test")
        return 1

    if sys.argv[1] == "--self-test":
        ok = run_self_test()
        print("\n" + "=" * 50)
        if ok:
            print("FINAL: PASS — agent submission self-test passed.")
            return 0
        print("FINAL: FAIL — agent submission self-test failed.")
        return 1

    all_ok = True
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            all_ok &= validate_file(path)
        else:
            # Try globbing
            import glob
            files = sorted(glob.glob(path))
            if not files:
                print(f"WARN: no files match {path}")
            for f in files:
                if os.path.isfile(f):
                    all_ok &= validate_file(f)

    print("\n" + "=" * 50)
    if all_ok:
        print("FINAL: PASS — agent submission validation passed.")
        return 0
    print("FINAL: FAIL — agent submission validation failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
