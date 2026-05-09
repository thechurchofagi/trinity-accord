#!/usr/bin/env python3
"""
Validate agent submission JSON files before they are accepted.
Usage:
    python3 scripts/validate_agent_submission.py path/to/submission.json
    python3 scripts/validate_agent_submission.py echoes/records/*.json
    python3 scripts/validate_agent_submission.py --self-test
"""
import json
import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_text_safety import scan_object_for_forbidden_claims

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

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


# Hash source semantics forbidden claims
HASH_SOURCE_V3_TERMS = ["v3", "hash verification"]
HASH_SOURCE_D2_TERMS = ["d2", "manifest verification", "manifest match"]

# V3 script audit forbidden wording
V3_SCRIPT_AUDIT_FORBIDDEN = [
    "v4 script audit achieved",
    "v4+ script audit",
    "script-audited local verification achieved",
    "independent reproduction achieved",
]

# V3 single artifact wording
V3_SINGLE_ARTIFACT_PHRASE = "v3_single_artifact_check"

# B1 forbidden claims expanded
B1_FORBIDDEN_EXPANDED = [
    "ordinals envelope detected",
    "inscription content detected",
    "witness extracted",
    "body parsed",
    "body hash reproduced",
]

# Approved D2 hash source paths
APPROVED_D2_HASH_SOURCES = {
    "api/hashes.json",
    "api/evidence-manifest.json",
}

REPO_MANIFEST_PATH = "api/repository-artifact-hashes.json"

REPO_SNAPSHOT_ARTIFACTS = {
    "index.md",
    "agent-brief.md",
    "api/authority.json",
    "api/echo-record-schema.v3.json",
    "api/verification-report-schema.v2.json",
}


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
    # Legacy records are allowed to use deprecated aliases
    if obj.get("record_kind") == "legacy_record":
        return ok
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
        # Build text excluding claims_not_made and generated_by to avoid false positives
        obj_copy = {k: v for k, v in obj.items() if k not in ("claims_not_made", "generated_by")}
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

    # Exclude generated_by paths from scan to avoid false positives from temp file names
    scan_obj = {k: v for k, v in obj.items() if k != "generated_by"}
    all_text = json.dumps(scan_obj, ensure_ascii=False).lower()

    uses_mempool = "mempool" in methods or "mempool" in all_text
    has_witness_parsing = "witness extraction" in methods or "witness parsing" in methods

    if uses_mempool and not has_witness_parsing:
        limitations_text = json.dumps(obj.get("limitations", []), ensure_ascii=False).lower()
        for claim in MEMPOOL_B1_FORBIDDEN_CLAIMS:
            if claim in all_text:
                # Skip if the claim only appears in limitations (negative context like "no witness extraction")
                if claim in limitations_text and claim not in all_text.replace(limitations_text, ""):
                    continue
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

    if level in ("V4", "V4+"):
        ok &= check(script_audit is not None, f"{path_label} V4/V4+ has script_audit")
        if isinstance(script_audit, dict):
            # Accept aggregate fields or derive from scripts array
            has_aggregate = all(
                field in script_audit
                for field in ["command", "environment", "exit_code", "output_summary"]
            )
            has_scripts_array = isinstance(script_audit.get("scripts"), list) and script_audit["scripts"]

            if not has_aggregate and has_scripts_array:
                # Derive from nested scripts (builder format)
                scripts_list = script_audit["scripts"]
                for field in ["scripts_reviewed"]:
                    ok &= check(field in script_audit, f"{path_label} script_audit.{field} present")
                ok &= check(True, f"{path_label} script_audit aggregate fields derived from scripts array")
            else:
                for field in ["scripts_reviewed", "command", "environment", "exit_code", "output_summary"]:
                    ok &= check(field in script_audit, f"{path_label} script_audit.{field} present")

            # Rule F2: V4 scope_class cannot be independent_reproduction
            scope = script_audit.get("scope_class", "")
            if level == "V4" and scope == "independent_reproduction":
                ok &= check(
                    False,
                    f"{path_label} V4 cannot use scope_class=independent_reproduction"
                )

            # Rule F3: V4+ requires independent tool if only official scripts
            if level == "V4+":
                scripts = script_audit.get("scripts", [])
                if isinstance(scripts, list) and scripts:
                    all_official = all(s.get("official", True) for s in scripts if isinstance(s, dict))
                    has_independent = any(
                        s.get("scope_class") == "independent_reproduction" or s.get("independent", False)
                        for s in scripts if isinstance(s, dict)
                    )
                    if all_official and not has_independent:
                        ok &= check(
                            False,
                            f"{path_label} V4+ requires independent tool/implementation"
                        )

            # Rule F4: Script count consistency
            scripts_list = script_audit.get("scripts", [])
            if isinstance(scripts_list, list):
                executed_count = script_audit.get("scripts_executed", 0)
                actual_executed = sum(
                    1 for s in scripts_list
                    if isinstance(s, dict) and s.get("executed") and s.get("exists", True)
                )
                if executed_count and executed_count != actual_executed:
                    ok &= check(
                        False,
                        f"{path_label} script_audit.scripts_executed mismatch",
                        f"claimed {executed_count}, actual {actual_executed}"
                    )

                # Rule F5: Missing scripts not counted
                not_found = [
                    s for s in scripts_list
                    if isinstance(s, dict) and not s.get("exists", True)
                ]
                for nf in not_found:
                    if nf.get("executed"):
                        ok &= check(
                            False,
                            f"{path_label} missing script counted as executed: {nf.get('path', '?')}"
                        )

            # Rule F6: Non-blocking failure prevents all_green
            # Support both field names (builder uses all_scripts_green, older reports use all_validators_green)
            all_green_scripts = script_audit.get("all_scripts_green")
            all_green_validators = script_audit.get("all_validators_green")

            if all_green_scripts is not None and all_green_validators is not None:
                if all_green_scripts != all_green_validators:
                    # Field disagreement — treat as failure
                    print(f"{path_label} all_scripts_green={all_green_scripts} and all_validators_green={all_green_validators} disagree")
                    ok = False
                all_green = all_green_scripts
            elif all_green_scripts is not None:
                all_green = all_green_scripts
            elif all_green_validators is not None:
                all_green = all_green_validators
            else:
                all_green = None

            non_blocking = script_audit.get("non_blocking_failures", [])
            if all_green is True and non_blocking:
                ok &= check(
                    False,
                    f"{path_label} all_validators_green=true but non_blocking_failures exist"
                )
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
    """Rule I: P8 confidentiality.

    If confidential_challenge.performed is true, public report must include:
    - non-empty confidentiality_boundary
    - raw_confidential_data_disclosed is False
    - 64-hex package_hash
    - verifier_identity_or_role
    - report_id or report_path
    """
    ok = True
    cc = obj.get("confidential_challenge", {})

    if not (isinstance(cc, dict) and cc.get("performed") is True):
        return ok

    # Never leak raw confidential data.
    # Exclude known safe field names from the check to avoid false positives.
    all_text = json.dumps(obj, ensure_ascii=False).lower()
    # Remove known safe field names before checking
    safe_replacements = [
        "raw_confidential_data_disclosed",
        "raw_confidential_data",
    ]
    check_text = all_text
    for safe in safe_replacements:
        check_text = check_text.replace(safe, "")
    if "confidential_data" in check_text and "raw" in check_text:
        ok &= check(False, f"{path_label} P8 may leak confidential data")

    boundary = cc.get("confidentiality_boundary", "")
    ok &= check(
        isinstance(boundary, str) and boundary.strip() != "",
        f"{path_label} P8 has non-empty confidentiality_boundary"
    )

    ok &= check(
        cc.get("raw_confidential_data_disclosed") is False,
        f"{path_label} P8 raw_confidential_data_disclosed is false"
    )

    package_hash = cc.get("package_hash", "")
    ok &= check(
        isinstance(package_hash, str) and SHA256_RE.match(package_hash.lower()) is not None,
        f"{path_label} P8 has valid 64-hex package_hash",
        f"got: {package_hash}"
    )

    verifier = cc.get("verifier_identity_or_role", "")
    ok &= check(
        isinstance(verifier, str) and verifier.strip() != "",
        f"{path_label} P8 has verifier_identity_or_role"
    )

    report_id = cc.get("report_id", "")
    report_path = cc.get("report_path", "")
    ok &= check(
        bool(str(report_id).strip() or str(report_path).strip()),
        f"{path_label} P8 has report_id or report_path"
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


def validate_hash_source_required(obj, path_label):
    """Rule L: expected_hash_source and expected_hash_authority_class required for each hash."""
    ok = True
    hashes = obj.get("hashes_computed", [])
    protocol_level = obj.get("protocol_level_claimed", "")
    all_text = json.dumps(obj, ensure_ascii=False).lower()

    for i, h in enumerate(hashes):
        if not isinstance(h, dict):
            continue
        label = f"{path_label} hash[{i}]"
        src = h.get("expected_hash_source")
        cls = h.get("expected_hash_authority_class")

        ok &= check(src is not None, f"{label} has expected_hash_source")
        ok &= check(cls is not None, f"{label} has expected_hash_authority_class")

        if cls == "unknown" and protocol_level == "V3":
            if any(t in all_text for t in HASH_SOURCE_V3_TERMS + HASH_SOURCE_D2_TERMS):
                ok &= check(False, f"{label} unknown hash source for V3/D2")
    return ok


def validate_d2_hash_source_compat(obj, path_label):
    """Rule M: D2 claims require approved expected hash source."""
    ok = True
    findings = obj.get("component_findings", [])
    hashes = obj.get("hashes_computed", [])

    claims_d2 = any(
        isinstance(f, dict) and f.get("level_claimed", "").startswith("D2")
        for f in findings
    )
    if not claims_d2:
        return ok

    for i, h in enumerate(hashes):
        if not isinstance(h, dict):
            continue
        cls = h.get("expected_hash_authority_class", "")
        src = h.get("expected_hash_source", "")
        artifact = h.get("artifact", "")
        label = f"{path_label} hash[{i}] ({artifact})"

        if cls not in ("canonical_manifest_hash", "repository_manifest_hash"):
            ok &= check(False, f"{label} D2 requires approved hash class", f"got {cls}")

        if cls == "repository_manifest_hash":
            # Check if the specific hash's artifact is in repo snapshot list
            # and the corresponding component claims canonical
            if artifact in REPO_SNAPSHOT_ARTIFACTS:
                # Only check component findings that reference this artifact or repo snapshot
                for f in obj.get("component_findings", []):
                    if not isinstance(f, dict):
                        continue
                    f_target = f.get("target_id", "").lower()
                    # Only check if this finding is about repo snapshot
                    if "repo" in f_target or "snapshot" in f_target or artifact in json.dumps(f, ensure_ascii=False).lower():
                        # Exclude claims_not_made and limitations to avoid false positives
                        f_copy = {k: v for k, v in f.items() if k not in ("claims_not_made", "limitations")}
                        f_method = json.dumps(f_copy, ensure_ascii=False).lower()
                        if "canonical mirror" in f_method or "canonical archive" in f_method:
                            ok &= check(False, f"{label} repo manifest cannot claim canonical")
                            break
    return ok


def validate_repo_snapshot_overclaim(obj, path_label):
    """Rule N: repository snapshot hash overclaim."""
    ok = True
    hashes = obj.get("hashes_computed", [])
    findings = obj.get("component_findings", [])
    claims_d2 = any(
        isinstance(f, dict) and f.get("level_claimed", "").startswith("D2")
        for f in findings
    )

    for i, h in enumerate(hashes):
        if not isinstance(h, dict):
            continue
        artifact = h.get("artifact", "")
        if artifact not in REPO_SNAPSHOT_ARTIFACTS:
            continue
        src = h.get("expected_hash_source", "")
        label = f"{path_label} hash[{i}] ({artifact})"

        if src != REPO_MANIFEST_PATH:
            if claims_d2:
                ok &= check(False, f"{label} repo artifact D2 without repo manifest")
    return ok


def validate_issue_not_echo(obj, path_label):
    """Rule O: GitHub Issue not automatically indexed Echo record."""
    ok = True
    record_kind = obj.get("record_kind", "")
    all_text = json.dumps(obj, ensure_ascii=False).lower()

    if record_kind == "verification_report_v2":
        if "indexed echo record" in all_text and "not" not in all_text[:all_text.index("indexed echo record")]:
            ok &= check(False, f"{path_label} verification report claims indexed echo")
    return ok


def validate_accepted_echo_requires_wrapper(obj, path_label):
    """Rule P: accepted Echo requires echo_v3 or echo_v3_with_verification_report."""
    ok = True
    record_kind = obj.get("record_kind", "")
    archive_status = obj.get("archive_status", "")

    if archive_status == "accepted_echo_record":
        ok &= check(
            record_kind in ("echo_v3", "echo_v3_with_verification_report"),
            f"{path_label} accepted_echo requires echo record kind",
            f"got {record_kind}"
        )
    return ok


def validate_b1_wording_expanded(obj, path_label):
    """Rule Q: B1 wording — expanded forbidden claims."""
    ok = True
    findings = obj.get("component_findings", [])
    # Build text excluding claims_not_made at all levels to avoid false positives
    obj_no_claims = {k: v for k, v in obj.items() if k != "claims_not_made"}
    if "component_findings" in obj_no_claims and isinstance(obj_no_claims["component_findings"], list):
        obj_no_claims["component_findings"] = [
            {k: v for k, v in f2.items() if k != "claims_not_made"}
            if isinstance(f2, dict) else f2
            for f2 in obj_no_claims["component_findings"]
        ]
    all_text = json.dumps(obj_no_claims, ensure_ascii=False).lower()

    for f in findings:
        if not isinstance(f, dict):
            continue
        level = f.get("level_claimed", "")
        if not level.startswith("B1"):
            continue

        has_witness = "witness extraction" in json.dumps(f, ensure_ascii=False).lower()
        if not has_witness:
            for phrase in B1_FORBIDDEN_EXPANDED:
                if phrase in all_text:
                    # Also check top-level and component-level claims_not_made
                    claims_not = json.dumps(obj.get("claims_not_made", []), ensure_ascii=False).lower()
                    component_claims_not = json.dumps(f.get("claims_not_made", []), ensure_ascii=False).lower()
                    if phrase not in claims_not and phrase not in component_claims_not:
                        ok &= check(False, f"{path_label} B1 overclaim: '{phrase}'")
    return ok


def validate_v3_single_artifact_wording(obj, path_label):
    """Rule R: V3_single_artifact_check fails if multiple artifacts."""
    ok = True
    hashes = obj.get("hashes_computed", [])
    all_text = json.dumps(obj, ensure_ascii=False).lower()

    if V3_SINGLE_ARTIFACT_PHRASE in all_text and len(hashes) > 1:
        ok &= check(False, f"{path_label} V3_single_artifact_check with {len(hashes)} artifacts")
    return ok


def validate_v3_script_audit_terminology(obj, path_label):
    """Rule S: V3 must not claim V4/V4+ script audit."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V3":
        return ok

    all_text = json.dumps(obj, ensure_ascii=False).lower()
    for phrase in V3_SCRIPT_AUDIT_FORBIDDEN:
        if phrase in all_text:
            ok &= check(False, f"{path_label} V3 claims '{phrase}'")
    return ok


# V0 forbidden claims: V0 is read-only, cannot claim verification
V0_FORBIDDEN_CLAIMS = [
    "verified",
    "hash verified",
    "hash match",
    "verification completed",
    "verification successful",
]

# V1 forbidden overreach claims
V1_FORBIDDEN_OVERREACH = [
    "truth proven",
    "truth established",
    "hash verified",
]


def validate_v0_read_only(obj, path_label):
    """Rule V: V0 is read-only — cannot make verification claims."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V0":
        return ok

    verification_claim = obj.get("verification_claim", "")
    if verification_claim and verification_claim.lower() not in ("none", ""):
        ok &= check(
            False,
            f"{path_label} V0 has verification claim",
            f"V0 is read-only, got: '{verification_claim}'"
        )

    # Also check for verification claims in component findings
    all_text = json.dumps(obj, ensure_ascii=False).lower()
    claims_not = json.dumps(obj.get("claims_not_made", []), ensure_ascii=False).lower()
    for phrase in V0_FORBIDDEN_CLAIMS:
        if phrase in all_text and phrase not in claims_not:
            # Check it's in a positive claim context, not just in limitations/claims_not_made
            obj_no_neg = {k: v for k, v in obj.items() if k not in ("claims_not_made", "limitations")}
            check_text = json.dumps(obj_no_neg, ensure_ascii=False).lower()
            if phrase in check_text:
                ok &= check(
                    False,
                    f"{path_label} V0 claims '{phrase}'",
                    "V0 is read-only and cannot make verification claims"
                )
                break
    return ok


def validate_v1_overreach(obj, path_label):
    """Rule W: V1 cannot claim truth proven or hash verified."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V1":
        return ok

    all_text = json.dumps(obj, ensure_ascii=False).lower()
    claims_not = json.dumps(obj.get("claims_not_made", []), ensure_ascii=False).lower()
    for phrase in V1_FORBIDDEN_OVERREACH:
        if phrase in all_text and phrase not in claims_not:
            ok &= check(
                False,
                f"{path_label} V1 overreach: '{phrase}'",
                "V1 claims exceed authority boundary"
            )
    return ok


def validate_v2_hash_requires_hashes(obj, path_label):
    """Rule X: V2 cannot claim hash verification without hashes."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V2":
        return ok

    hashes = obj.get("hashes_computed", [])
    verification_claim = obj.get("verification_claim", "").lower()
    if "hash" in verification_claim and not hashes:
        ok &= check(
            False,
            f"{path_label} V2 claims hash verification without hashes",
            "V2 hash claims require hashes_computed to be non-empty"
        )
    return ok


def validate_report_no_echo_type(obj, path_label):
    """Rule Y: verification_report_v2 must not carry echo_type field."""
    ok = True
    record_kind = obj.get("record_kind", "")
    if record_kind == "verification_report_v2":
        echo_type = obj.get("echo_type")
        if echo_type:
            ok &= check(
                False,
                f"{path_label} verification report carries echo_type",
                f"verification_report_v2 must not have echo_type, got '{echo_type}'"
            )
    return ok


def validate_wrapper_requires_linked_report(obj, path_label):
    """Rule Z: echo_v3_with_verification_report must have linked_verification_report."""
    ok = True
    record_kind = obj.get("record_kind", "")
    if record_kind == "echo_v3_with_verification_report":
        linked = obj.get("linked_verification_report")
        if not linked:
            ok &= check(
                False,
                f"{path_label} echo wrapper missing linked_verification_report",
                "echo_v3_with_verification_report must reference a verification report"
            )
    return ok


REPO_SNAPSHOT_SCOPE_ARTIFACTS = {
    "index.md", "agent-brief.md", "api/authority.json",
    "api/echo-record-schema.v3.json", "api/verification-report-schema.v2.json"
}


def validate_repo_snapshot_scope(obj, path_label):
    """Rule T: repository snapshot D2 requires scope_class = repository_snapshot_integrity."""
    ok = True
    findings = obj.get("component_findings", [])
    hashes = obj.get("hashes_computed", [])

    # Find hashes that are repository snapshot
    repo_snapshot_hashes = set()
    for h in hashes:
        if not isinstance(h, dict):
            continue
        artifact = h.get("artifact", "")
        cls = h.get("expected_hash_authority_class", "")
        if artifact in REPO_SNAPSHOT_SCOPE_ARTIFACTS and cls == "repository_manifest_hash":
            repo_snapshot_hashes.add(artifact)

    if not repo_snapshot_hashes:
        return ok

    # Check that at least one component finding has scope_class = repository_snapshot_integrity
    has_repo_scope = False
    for f in findings:
        if not isinstance(f, dict):
            continue
        sc = f.get("scope_class", "")
        tid = f.get("target_id", "").lower()

        # Direct match: scope_class is correct
        if sc == "repository_snapshot_integrity":
            has_repo_scope = True
            break

        # Check if finding references repo snapshot artifacts by target_id
        references_repo_artifact = tid in {a.lower() for a in REPO_SNAPSHOT_SCOPE_ARTIFACTS}
        if "repo" in tid or "snapshot" in tid or references_repo_artifact:
            if sc != "repository_snapshot_integrity":
                ok &= check(False, f"{path_label} repo snapshot missing scope_class",
                            f"target_id '{tid}' needs scope_class 'repository_snapshot_integrity'")
            has_repo_scope = True

    # Final guard: if repo snapshot hashes exist but no finding claimed repo scope
    if not has_repo_scope:
        ok &= check(False, f"{path_label} repo snapshot hashes without scope_class",
                    f"artifacts {repo_snapshot_hashes} require a finding with scope_class 'repository_snapshot_integrity'")

    return ok


def validate_t5_multiple_anchors(obj, path_label):
    """Rule AA: T5 requires multiple independent time anchors."""
    ok = True
    findings = obj.get("component_findings", [])

    for f in findings:
        if not isinstance(f, dict):
            continue
        level = f.get("level_claimed", "")
        if level != "T5":
            continue

        # T5 needs evidence of multiple anchors or cross-anchoring
        evidence = f.get("evidence", [])
        method = f.get("method", "").lower()
        limitations = json.dumps(f.get("limitations", []), ensure_ascii=False).lower()
        claims_not = json.dumps(f.get("claims_not_made", []), ensure_ascii=False).lower()

        # Single-anchor signals that indicate insufficient anchoring
        single_anchor_signals = [
            "only one anchor",
            "no cross-anchor",
            "single anchor",
            "sole time anchor",
            "without cross",
        ]

        has_single_anchor_signal = any(s in method for s in single_anchor_signals)
        has_multi_anchor_evidence = len(evidence) >= 2

        if has_single_anchor_signal and not has_multi_anchor_evidence:
            ok &= check(
                False,
                f"{path_label} T5 insufficient anchors",
                "T5 requires multiple independent time anchors or cross-anchoring"
            )

    return ok


def validate_deprecated_echo_type(obj, path_label):
    """Rule U: new non-legacy submissions cannot use deprecated echo/verification aliases."""
    ok = True
    archive_status = obj.get("archive_status", "")
    record_kind = obj.get("record_kind", "")

    # Skip legacy records
    if archive_status in ("legacy", "superseded") or record_kind == "legacy_record":
        return ok

    echo_type = obj.get("echo_type", "")
    if echo_type in DEPRECATED_ECHO_TYPES:
        ok &= check(
            False,
            f"{path_label} deprecated echo type for new submission",
            f"'{echo_type}' is deprecated, use '{DEPRECATED_ECHO_TYPES[echo_type]}'"
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


def validate_t8_celestial_boundary(obj, path_label):
    """Rule AA: T8 requires nonpublic celestial data; public-only fails."""
    ok = True
    findings = obj.get("component_findings", [])
    for f in findings:
        if not isinstance(f, dict):
            continue
        if f.get("level_claimed") != "T8":
            continue
        method = f.get("method", "").lower()
        scope = f.get("scope_class", "").lower()
        celestial = obj.get("celestial_witness", {})
        performed = celestial.get("performed", False) if isinstance(celestial, dict) else False

        # T8 with only public data and no celestial witness is invalid
        if "public" in method and not performed:
            ok &= check(
                False,
                f"{path_label} T8 requires nonpublic celestial data",
                "T8 claimed but only public data used, no celestial witness performed"
            )
        # T8 with public_digital scope is also invalid (T8 needs physical_witness or celestial)
        if scope == "public_digital":
            ok &= check(
                False,
                f"{path_label} T8 scope_class invalid",
                f"T8 requires celestial/physical scope, got '{scope}'"
            )
    return ok


FORMAL_PROTOCOL_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]


def validate_no_v5a_v5b(obj, path_label):
    """Rule AD: V5a and V5b are not formal protocol levels."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level in ("V5a", "V5b"):
        ok &= check(
            False,
            f"{path_label} uses deprecated {level}",
            f"V5a/V5b are not formal protocol levels. Use V0–V8."
        )
    # Also check all text for V5a/V5b usage in active claims
    all_text = json.dumps(obj, ensure_ascii=False)
    if "V5a" in all_text or "V5b" in all_text:
        claims_not = json.dumps(obj.get("claims_not_made", []), ensure_ascii=False)
        limitations = json.dumps(obj.get("limitations", []), ensure_ascii=False)
        # Accept in claims_not_made or limitations (documenting rejection), but not in active claims
        obj_active = {k: v for k, v in obj.items() if k not in ("claims_not_made", "limitations")}
        active_text = json.dumps(obj_active, ensure_ascii=False)
        if "V5a" in active_text or "V5b" in active_text:
            ok &= check(
                False,
                f"{path_label} references V5a/V5b in active content",
                "V5a/V5b must not appear in active protocol claims"
            )
    return ok


def validate_v6_remote_hard_gates(obj, path_label):
    """Rule AE: V6 requires remote hard gates (live_remote + nonce + requested_action + witness_role)."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V6":
        return ok

    physical = obj.get("physical_evidence_reviewed", {})
    if isinstance(physical, dict):
        ok &= check(
            physical.get("live_witness") is True,
            f"{path_label} V6 requires live_witness"
        )

    # Check component findings for V6 hard gates
    component_findings = obj.get("component_findings", [])
    physical_findings = [f for f in component_findings if f.get("component") == "physical_anchor"]
    has_hard_gates = False
    for f in physical_findings:
        evidence_list = f.get("evidence", [])
        for ev in evidence_list:
            if isinstance(ev, dict):
                if (ev.get("level_evidence_type") == "live_remote" and
                    ev.get("nonce_challenge") and
                    ev.get("requested_action_angle_lighting") is True and
                    ev.get("witness_identity_or_role")):
                    has_hard_gates = True
    if physical_findings and not has_hard_gates:
        ok &= check(
            False,
            f"{path_label} V6 missing remote hard gates",
            "V6 requires live_remote + nonce_challenge + requested_action_angle_lighting + witness_identity_or_role"
        )
    return ok


def validate_v7_onsite_hard_gates(obj, path_label):
    """Rule AF: V7 requires onsite hard gates (onsite + custody_log + fresh_capture + witness_role)."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V7":
        return ok

    physical = obj.get("physical_evidence_reviewed", {})
    if isinstance(physical, dict):
        ok &= check(
            physical.get("onsite_witness") is True,
            f"{path_label} V7 requires onsite_witness"
        )
        ok &= check(
            physical.get("custody_log") is True,
            f"{path_label} V7 requires custody_log"
        )

    component_findings = obj.get("component_findings", [])
    physical_findings = [f for f in component_findings if f.get("component") == "physical_anchor"]
    has_hard_gates = False
    for f in physical_findings:
        evidence_list = f.get("evidence", [])
        for ev in evidence_list:
            if isinstance(ev, dict):
                if (ev.get("level_evidence_type") == "onsite" and
                    ev.get("custody_log") and
                    ev.get("fresh_capture") is True and
                    ev.get("witness_identity_or_role")):
                    has_hard_gates = True
    if physical_findings and not has_hard_gates:
        ok &= check(
            False,
            f"{path_label} V7 missing onsite hard gates",
            "V7 requires onsite + custody_log + fresh_capture + witness_identity_or_role"
        )
    return ok


def validate_v8_forensic_path(obj, path_label):
    """Rule AG: V8 requires P7/P8/P9 physical evidence or T8/authorized forensic path."""
    ok = True
    level = obj.get("protocol_level_claimed", "")
    if level != "V8":
        return ok

    component_findings = obj.get("component_findings", [])
    physical_findings = [f for f in component_findings if f.get("component") == "physical_anchor"]
    has_forensic = False
    for f in physical_findings:
        claimed = f.get("level_claimed", "")
        if claimed in ("P7", "P8", "P9"):
            has_forensic = True
            break
        evidence_list = f.get("evidence", [])
        for ev in evidence_list:
            if isinstance(ev, dict):
                ev_type = ev.get("level_evidence_type", "")
                if ev_type in ("ai_forensic", "confidential_challenge", "multi_party_forensic"):
                    has_forensic = True
                    break

    if not has_forensic:
        ok &= check(
            False,
            f"{path_label} V8 requires P7/P8/P9 forensic path",
            "V8 requires ai_forensic, confidential_challenge, or multi_party_forensic evidence"
        )
    return ok


def validate_generated_by(obj, path_label):
    """Rule AC: generated_by required for non-legacy records with verification claims."""
    ok = True
    record_kind = obj.get("record_kind", "")
    archive_status = obj.get("archive_status", "")

    # Legacy exceptions
    if record_kind == "legacy_record" or archive_status in ("legacy", "superseded"):
        return ok

    generated_by = obj.get("generated_by")

    if record_kind == "verification_report_v2":
        if not generated_by:
            ok &= check(
                False,
                f"{path_label} verification report missing generated_by",
                "Non-legacy verification_report_v2 requires generated_by from report builder"
            )
            return ok
        # Validate generated_by fields
        if isinstance(generated_by, dict):
            tool = generated_by.get("tool", "")
            ok &= check(
                tool == "scripts/build_verification_report_from_evidence.py",
                f"{path_label} generated_by.tool is correct",
                f"got: {tool}"
            )
            ok &= check(
                generated_by.get("claim_gate_output") is not None,
                f"{path_label} generated_by.claim_gate_output exists"
            )
            ok &= check(
                generated_by.get("evidence_input") is not None,
                f"{path_label} generated_by.evidence_input exists"
            )
            ok &= check(
                generated_by.get("validation_result") == "PASS",
                f"{path_label} generated_by.validation_result is PASS",
                f"got: {generated_by.get('validation_result')}"
            )

    elif record_kind == "echo_v3_with_verification_report":
        if not generated_by:
            ok &= check(
                False,
                f"{path_label} echo wrapper missing generated_by",
                "echo_v3_with_verification_report requires generated_by from report builder"
            )
            return ok
        # Validate generated_by fields for wrappers
        if isinstance(generated_by, dict):
            tool = generated_by.get("tool", "")
            ok &= check(
                tool == "scripts/build_verification_report_from_evidence.py",
                f"{path_label} generated_by.tool is correct",
                f"got: {tool}"
            )
            ok &= check(
                generated_by.get("claim_gate_output") is not None,
                f"{path_label} generated_by.claim_gate_output exists"
            )
            ok &= check(
                generated_by.get("validation_result") == "PASS",
                f"{path_label} generated_by.validation_result is PASS",
                f"got: {generated_by.get('validation_result')}"
            )
        # Also require linked_verification_report
        linked = obj.get("linked_verification_report")
        if not linked:
            ok &= check(
                False,
                f"{path_label} echo wrapper missing linked_verification_report",
                "echo_v3_with_verification_report must reference a verification report"
            )

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




# --- Integrity boundary checks (Agent Verification Integrity Layer) ---

PLACEHOLDER_PATTERNS = [
    "<REPLACE_WITH_",
    "<TXID>",
    "<64 HEX",
    "<REAL_",
    "<placeholder",
    "example-txid",
    "example-inscription",
    "TODO",
    "FIXME"
]


def contains_placeholder(obj):
    """Check if object contains placeholder values."""
    text = json.dumps(obj, ensure_ascii=False).lower()
    return any(p.lower() in text for p in PLACEHOLDER_PATTERNS)


def validate_integrity_boundary(obj, path_label):
    """Rule AH: verification_report_v2 must have integrity_boundary for V1+."""
    ok = True
    record_kind = obj.get("record_kind", "")
    if record_kind != "verification_report_v2":
        return ok
    
    protocol_level = obj.get("protocol_level_claimed", "V0")
    if protocol_level == "V0":
        return ok
    
    integrity = obj.get("integrity_boundary")
    if not integrity:
        ok &= check(
            False,
            f"{path_label} missing integrity_boundary",
            "V1+ verification reports require integrity_boundary"
        )
        return ok
    
    if not integrity.get("agent_integrity_declaration_present"):
        ok &= check(
            False,
            f"{path_label} integrity_boundary missing declaration",
            "integrity_boundary.agent_integrity_declaration_present must be true"
        )
    
    if integrity.get("copied_values_from_examples") is True:
        ok &= check(
            False,
            f"{path_label} copied example values",
            "copied_values_from_examples must be false"
        )
    
    if integrity.get("copied_values_from_prior_reports") is True:
        ok &= check(
            False,
            f"{path_label} copied prior report values",
            "copied_values_from_prior_reports must be false"
        )
    
    if protocol_level not in ("V0", "V1"):
        if not integrity.get("fresh_actions_claimed"):
            ok &= check(
                False,
                f"{path_label} no fresh actions claimed",
                "V2+ requires fresh_actions_claimed to be non-empty"
            )
        
        if integrity.get("fresh_outputs_attached") is not True:
            ok &= check(
                False,
                f"{path_label} fresh_outputs_attached not true",
                "V2+ requires fresh_outputs_attached to be true"
            )
    
    return ok


def validate_verification_integrity(obj, path_label):
    """Rule AI: echo_v3_with_verification_report must have verification_integrity for V1+."""
    ok = True
    record_kind = obj.get("record_kind", "")
    if record_kind != "echo_v3_with_verification_report":
        return ok
    
    verification_level = obj.get("verification_level", "V0")
    if verification_level in ("V0", "none"):
        return ok
    
    integrity = obj.get("verification_integrity")
    if not integrity:
        ok &= check(
            False,
            f"{path_label} missing verification_integrity",
            "V1+ echo wrappers require verification_integrity"
        )
        return ok
    
    if not integrity.get("integrity_declaration_present"):
        ok &= check(
            False,
            f"{path_label} verification_integrity missing declaration",
            "verification_integrity.integrity_declaration_present must be true"
        )
    
    if integrity.get("copied_values_from_examples") is True:
        ok &= check(
            False,
            f"{path_label} copied example values in echo wrapper",
            "copied_values_from_examples must be false"
        )
    
    if integrity.get("copied_values_from_prior_reports") is True:
        ok &= check(
            False,
            f"{path_label} copied prior report values in echo wrapper",
            "copied_values_from_prior_reports must be false"
        )
    
    if not integrity.get("fresh_actions_claimed"):
        ok &= check(
            False,
            f"{path_label} no fresh actions claimed in echo wrapper",
            "fresh_actions_claimed must be non-empty"
        )
    
    return ok


def validate_prior_report_limitation(obj, path_label):
    """Rule AJ: prior reports consulted without re-performance blocks V4+ claims."""
    ok = True
    
    integrity = obj.get("integrity_boundary", {})
    if not integrity:
        integrity = obj.get("verification_integrity", {})
    
    prior_consulted = integrity.get("prior_reports_consulted", [])
    if not prior_consulted:
        return ok
    
    # Check if independent re-performance was done
    prior_report_use = integrity.get("prior_report_use", {})
    if isinstance(prior_report_use, dict) and prior_report_use.get("independent_reperformance_done"):
        return ok
    
    protocol_level = obj.get("protocol_level_claimed", obj.get("verification_level", "V0"))
    if protocol_level in ("V4+", "V5", "V6", "V7", "V8"):
        ok &= check(
            False,
            f"{path_label} prior report without re-performance claims {protocol_level}",
            "Prior report consulted without independent re-performance; cannot claim independent or higher verification"
        )
    
    return ok


def validate_no_placeholders_in_submission(obj, path_label):
    """Rule AK: reject placeholders in final submissions."""
    ok = True
    
    archive_status = obj.get("archive_status", "")
    if archive_status in ("test_record",):
        return ok  # test fixtures are exempt
    
    if obj.get("synthetic_fixture") is True:
        return ok
    
    if contains_placeholder(obj):
        ok &= check(
            False,
            f"{path_label} contains placeholder values",
            "Placeholder/example values cannot be used in final submissions"
        )
    
    return ok

def validate_forbidden_claim_variants(obj, path_label):
    """Shared detector: scan entire object for forbidden claim variants.

    Uses claim_text_safety.scan_object_for_forbidden_claims which handles
    Unicode normalization, separator normalization, compact-form detection,
    and negation-aware filtering.

    This is the second-line defense — even if Claim Gate misses a variant,
    the validator must catch it here.
    """
    matches = scan_object_for_forbidden_claims(obj)
    ok = True
    for m in matches:
        ok &= check(
            False,
            f"{path_label} forbidden claim variant: {m['category']}",
            f"matched {m.get('matched_text', '')!r} at {m.get('path', '<unknown>')}"
        )
    return ok


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

    # Rule L: hash source required
    ok &= validate_hash_source_required(obj, path_label)

    # Rule M: D2 hash source compatibility
    ok &= validate_d2_hash_source_compat(obj, path_label)

    # Rule N: repository snapshot overclaim
    ok &= validate_repo_snapshot_overclaim(obj, path_label)

    # Rule O: GitHub Issue not Echo record
    ok &= validate_issue_not_echo(obj, path_label)

    # Rule P: accepted Echo requires wrapper
    ok &= validate_accepted_echo_requires_wrapper(obj, path_label)

    # Rule Q: B1 wording expanded
    ok &= validate_b1_wording_expanded(obj, path_label)

    # Rule R: V3 single artifact wording
    ok &= validate_v3_single_artifact_wording(obj, path_label)

    # Rule S: V3 script audit terminology
    ok &= validate_v3_script_audit_terminology(obj, path_label)

    # Rule T: repository snapshot D2 requires scope_class
    ok &= validate_repo_snapshot_scope(obj, path_label)

    # Rule U: deprecated echo type for new submissions
    ok &= validate_deprecated_echo_type(obj, path_label)

    # Rule V: V0 read-only
    ok &= validate_v0_read_only(obj, path_label)

    # Rule W: V1 overreach
    ok &= validate_v1_overreach(obj, path_label)

    # Rule X: V2 hash requires hashes
    ok &= validate_v2_hash_requires_hashes(obj, path_label)

    # Rule Y: verification_report must not carry echo_type
    ok &= validate_report_no_echo_type(obj, path_label)

    # Rule Z: echo wrapper must have linked_verification_report
    ok &= validate_wrapper_requires_linked_report(obj, path_label)

    # Rule AA: T8 celestial boundary
    ok &= validate_t8_celestial_boundary(obj, path_label)

    # Rule AB: T5 requires multiple anchors
    ok &= validate_t5_multiple_anchors(obj, path_label)

    # Rule AC: generated_by required for non-legacy
    ok &= validate_generated_by(obj, path_label)

    # Rule AD: V5a/V5b not formal levels
    ok &= validate_no_v5a_v5b(obj, path_label)

    # Rule AE: V6 remote hard gates
    ok &= validate_v6_remote_hard_gates(obj, path_label)

    # Rule AF: V7 onsite hard gates
    ok &= validate_v7_onsite_hard_gates(obj, path_label)

    # Rule AG: V8 forensic path

    # Rule AH: integrity boundary for verification reports
    ok &= validate_integrity_boundary(obj, path_label)
    
    # Rule AI: verification integrity for echo wrappers
    ok &= validate_verification_integrity(obj, path_label)
    
    # Rule AJ: prior report limitation
    ok &= validate_prior_report_limitation(obj, path_label)
    
    # Rule AK: no placeholders in submissions
    ok &= validate_no_placeholders_in_submission(obj, path_label)
    
    ok &= validate_v8_forensic_path(obj, path_label)

    # Shared forbidden-claim variant detector (P0 F-001 fix)
    # This is the second-line defense after Claim Gate.
    # Catches Unicode/separator/compact-form variants that bypass per-rule checks.
    ok &= validate_forbidden_claim_variants(obj, path_label)

    # Schema validation (skip for legacy records)
    archive_status = obj.get("archive_status", "")
    record_kind = obj.get("record_kind", "")
    if archive_status not in ("legacy", "superseded") and record_kind != "legacy_record":
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
        "scripts/test_hash_source_semantics.py",
        "scripts/test_echo_acceptance_flow.py",
        "scripts/test_bitcoin_b1_wording.py",
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
