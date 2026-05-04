#!/usr/bin/env python3
"""
Claim Gate for Trinity Accord.
Evaluates evidence inputs and derives allowed protocol/component levels.

Usage:
    python3 scripts/claim_gate.py evidence-input.json
    python3 scripts/claim_gate.py evidence-input.json --output claim-gate-output.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTOCOL_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]
B_LEVELS = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
D_LEVELS = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]
T_LEVELS = ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
C_LEVELS = ["C0", "C1", "C2", "C3", "C3R", "C4", "C5", "C6", "C7"]
N_LEVELS = ["N0", "N1", "N2", "N3", "N4", "N5", "N6", "N7"]
P_LEVELS = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]

SHA256_RE = re.compile(r'^[a-f0-9]{64}$')

FORBIDDEN_CLAIMS = [
    "truth proven", "investment value confirmed", "religious authority established",
    "AI instruction override",
]

SOLICITED_FORBIDDEN = ["independent_attestation", "unsolicited_discovery", "institutional_attestation"]


def level_index(levels, val):
    """Return index of val in levels list, or -1 if not found."""
    try:
        return levels.index(val)
    except ValueError:
        return -1


def max_by_order(levels, a, b):
    """Return the higher of two level values according to the levels list."""
    return b if level_index(levels, b) > level_index(levels, a) else a


def has_p7_forensic_path(evidence):
    return any(
        check.get("level_evidence_type") == "ai_forensic"
        and check.get("model_or_tool")
        and check.get("confidence") is not None
        and (
            check.get("flaw_analysis_method")
            or check.get("feature_match_method")
            or check.get("microscopy_comparison")
        )
        and (
            check.get("signed_or_attributable_report") is True
            or check.get("report_id")
            or check.get("report_path")
        )
        for check in evidence.get("physical_checks", [])
    )


def has_p8_confidential_path(evidence):
    for check in evidence.get("physical_checks", []):
        if check.get("level_evidence_type") != "confidential_challenge":
            continue
        conf = check.get("confidential_challenge", {})
        if (
            conf.get("performed") is True
            and conf.get("boundary")
            and conf.get("raw_confidential_data_disclosed") is False
        ):
            return True
    return False


def has_p9_multi_party_path(evidence):
    return any(
        check.get("level_evidence_type") == "multi_party_forensic"
        and check.get("independent_witness_count", 0) >= 2
        for check in evidence.get("physical_checks", [])
    )


def has_t8_authorized_celestial_path(evidence):
    return any(
        check.get("anchor_type") == "star_moon_witness"
        and check.get("nonpublic_boundary") is True
        and check.get("authorized") is True
        for check in evidence.get("time_anchor_checks", [])
    )


def level_at_least(levels, claimed, minimum):
    """Check if claimed level is at least minimum."""
    return level_index(levels, claimed) >= level_index(levels, minimum)


def derive_b_level(evidence):
    """Derive Bitcoin component level from evidence."""
    bitcoin_checks = evidence.get("bitcoin_checks", [])
    if not bitcoin_checks:
        return "B0"

    max_level = "B0"
    for check in bitcoin_checks:
        source_type = check.get("source_type", "")
        sources = check.get("sources", [])
        has_external = any(
            s not in ("api/authority.json", "authority.json", "/api/authority.json")
            for s in sources
        )

        if source_type == "body_hash" and check.get("body_hash_reproduced"):
            candidate = "B6"
        elif source_type == "witness_extraction" and check.get("raw_witness_extracted"):
            candidate = "B5"
        elif source_type == "local_node":
            candidate = "B4"
        elif source_type == "spv_proof":
            candidate = "B3"
        elif source_type == "multi_explorer":
            candidate = "B2"
        elif source_type == "external_explorer" and has_external:
            candidate = "B1"
        elif source_type == "local_manifest" or (source_type == "" and not has_external):
            candidate = "B0"
        else:
            candidate = "B0"

        if level_index(B_LEVELS, candidate) > level_index(B_LEVELS, max_level):
            max_level = candidate

    return max_level


def derive_d_level(evidence):
    """Derive Digital component level from evidence."""
    hashes = evidence.get("hashes", [])
    digital_checks = evidence.get("digital_mirror_checks", [])
    repo_checks = evidence.get("repository_snapshot_checks", [])

    max_level = "D0"

    if digital_checks or repo_checks:
        max_level = max_by_order(D_LEVELS, max_level, "D1")

    for h in hashes:
        if (
            SHA256_RE.match(h.get("expected", ""))
            and SHA256_RE.match(h.get("computed", ""))
            and h.get("match") is True
            and h.get("expected_hash_source")
            and h.get("expected_hash_authority_class", "unknown") != "unknown"
        ):
            max_level = max_by_order(D_LEVELS, max_level, "D2")
            break

    for check in digital_checks:
        if check.get("level_evidence_type") == "external_pointer_existence":
            if check.get("external_pointer_exists") is True:
                max_level = max_by_order(D_LEVELS, max_level, "D3")

        if check.get("level_evidence_type") == "cross_mirror_consistency":
            channels = check.get("channels_compared", [])
            if len(channels) >= 2 and check.get("content_hashes_match") is True:
                max_level = max_by_order(D_LEVELS, max_level, "D4")

        if check.get("level_evidence_type") == "full_public_digital_data_verification":
            if (
                check.get("all_required_public_digital_targets_checked") is True
                and check.get("all_unavailable_targets_listed") is True
            ):
                max_level = max_by_order(D_LEVELS, max_level, "D5")

        if check.get("level_evidence_type") == "independent_full_digital_reproduction":
            if check.get("independent_tool_or_implementation") is True:
                max_level = max_by_order(D_LEVELS, max_level, "D6")

        if check.get("level_evidence_type") == "multi_party_digital_attestation":
            if check.get("independent_verifier_count", 0) >= 2:
                max_level = max_by_order(D_LEVELS, max_level, "D7")

    return max_level


def derive_t_level(evidence):
    """Derive Time component level from evidence."""
    time_checks = evidence.get("time_anchor_checks", [])
    if not time_checks:
        return "T0"

    max_level = "T0"
    for check in time_checks:
        anchor_type = check.get("anchor_type", "")
        if anchor_type == "star_moon_witness" and check.get("nonpublic_boundary") and check.get("authorized"):
            candidate = "T8"
        elif anchor_type == "bitcoin_block_time":
            candidate = "T3"
        elif anchor_type in ("eth_timestamp", "arweave_timestamp"):
            candidate = "T2"
        elif anchor_type == "github_commit_timestamp":
            candidate = "T1"
        else:
            candidate = "T0"

        if level_index(T_LEVELS, candidate) > level_index(T_LEVELS, max_level):
            max_level = candidate

    return max_level


def derive_c_level(evidence):
    """Derive Chronicle component level from evidence."""
    chronicle_checks = evidence.get("chronicle_checks", [])
    if not chronicle_checks:
        return "C0"

    max_level = "C0"
    for check in chronicle_checks:
        samples_recovered = check.get("samples_recovered", 0)
        full_recovery = check.get("full_recovery", False)
        has_package_hash = check.get("package_hash_valid", False)

        candidate = "C0"

        if check.get("pointer_check") is True or check.get("recovery_pointer_exists") is True:
            candidate = "C1"

        if has_package_hash:
            candidate = max_by_order(C_LEVELS, candidate, "C2")

        if samples_recovered >= 2:
            candidate = max_by_order(C_LEVELS, candidate, "C3")

        if check.get("scripted_recovery_verification") is True:
            candidate = max_by_order(C_LEVELS, candidate, "C4")

        if full_recovery and samples_recovered >= 175:
            candidate = max_by_order(C_LEVELS, candidate, "C5")

        if check.get("chain_source_pointer_verification") is True:
            candidate = max_by_order(C_LEVELS, candidate, "C6")

        if (
            check.get("multi_party_chronicle_attestation") is True
            and check.get("independent_verifier_count", 0) >= 2
        ):
            candidate = max_by_order(C_LEVELS, candidate, "C7")

        max_level = max_by_order(C_LEVELS, max_level, candidate)

    return max_level


def derive_n_level(evidence):
    """Derive NFT evidence component level from evidence."""
    nft_checks = evidence.get("nft_checks", [])
    if not nft_checks:
        return "N0"

    max_level = "N0"
    for check in nft_checks:
        if check.get("full_path_reproduction") is True:
            candidate = "N7"
        elif check.get("random_sample_full_path") is True:
            candidate = "N6"
        elif check.get("cid_or_hash_match") is True:
            candidate = "N5"
        elif check.get("media_recovered") is True:
            candidate = "N4"
        elif check.get("metadata_recovered") is True:
            candidate = "N3"
        elif check.get("token_uri_checked") is True:
            candidate = "N2"
        elif check.get("contract_or_token_id_checked") is True:
            candidate = "N1"
        else:
            candidate = "N0"
        max_level = max_by_order(N_LEVELS, max_level, candidate)
    return max_level


def derive_p_level(evidence):
    """Derive Physical component level from evidence."""
    physical_checks = evidence.get("physical_checks", [])
    if not physical_checks:
        return "P0"

    max_level = "P0"
    for check in physical_checks:
        ev_type = check.get("level_evidence_type", "")
        has_nonce = check.get("nonce_challenge") is not None
        has_custody = check.get("custody_log") is not None
        conf = check.get("confidential_challenge", {})
        conf_performed = conf.get("performed", False) if conf else False
        conf_no_raw = not conf.get("raw_confidential_data_disclosed", True) if conf else True
        conf_boundary = conf.get("boundary", "") if conf else ""
        model_tool = check.get("model_or_tool")
        confidence = check.get("confidence")

        if ev_type == "multi_party_forensic":
            candidate = "P9"
        elif ev_type == "confidential_challenge" and conf_performed and conf_no_raw and conf_boundary:
            candidate = "P8"
        elif ev_type == "ai_forensic" and model_tool and confidence is not None:
            candidate = "P7"
        elif ev_type == "onsite" and has_custody:
            candidate = "P5"
        elif ev_type == "live_remote" and has_nonce:
            candidate = "P4"
        elif ev_type == "recorded_video":
            candidate = "P3"
        elif ev_type == "static_image":
            candidate = "P2"
        elif ev_type == "evidence_package_hash" and check.get("package_hash_valid"):
            candidate = "P1"
        else:
            candidate = "P0"

        if level_index(P_LEVELS, candidate) > level_index(P_LEVELS, max_level):
            max_level = candidate

    return max_level


def has_authority_boundary_check(evidence):
    """Check if evidence contains explicit authority boundary recognition."""
    # Check for explicit boundary recognition in digital mirror checks
    for check in evidence.get("digital_mirror_checks", []):
        if check.get("authority_boundary_recognized") is True:
            return True
        if check.get("level_evidence_type") == "authority_boundary_recognition":
            return True

    # Check for explicit boundary in bitcoin checks
    for check in evidence.get("bitcoin_checks", []):
        if check.get("authority_boundary_recognized") is True:
            return True

    # Check for boundary recognition in repository snapshot checks
    for check in evidence.get("repository_snapshot_checks", []):
        if check.get("authority_boundary_recognized") is True:
            return True

    # Check scripts for boundary recognition
    for s in evidence.get("scripts", []):
        if s.get("authority_boundary_recognized") is True:
            return True

    # Check echo context for boundary recognition
    echo_ctx = evidence.get("echo_context", {})
    if echo_ctx.get("authority_boundary_recognized") is True:
        return True

    return False


def derive_protocol_level(evidence, requested_level, b_level, d_level, t_level, c_level, p_level):
    """Derive the maximum allowed protocol level from component levels and evidence."""
    scripts = evidence.get("scripts", [])
    hashes = evidence.get("hashes", [])

    has_valid_hash = any(
        SHA256_RE.match(h.get("expected", "")) and
        SHA256_RE.match(h.get("computed", "")) and
        h.get("match") is True and
        h.get("expected_hash_source") and
        h.get("expected_hash_authority_class", "unknown") != "unknown"
        for h in hashes
    )

    executed_scripts = [s for s in scripts if s.get("executed") and s.get("exists")]
    has_independent = any(
        s.get("scope_class") == "independent_reproduction" or
        s.get("independent", False)
        for s in scripts
    )
    official_only = all(
        s.get("official", True) for s in executed_scripts
    ) if executed_scripts else False

    # Determine max allowed level bottom-up
    max_allowed = "V0"

    # V1: requires explicit authority boundary recognition evidence
    if has_authority_boundary_check(evidence):
        max_allowed = "V1"

    # V2: at least one reference check beyond page reading
    # Local manifest only does NOT count as a reference check beyond page reading
    bitcoin_checks = evidence.get("bitcoin_checks", [])
    has_external_bitcoin = any(
        bc.get("source_type") not in ("local_manifest", "", None) or
        any(s not in ("api/authority.json", "authority.json", "/api/authority.json") for s in bc.get("sources", []))
        for bc in bitcoin_checks
    )
    has_reference = has_external_bitcoin or bool(evidence.get("digital_mirror_checks")) or bool(evidence.get("repository_snapshot_checks"))
    if has_reference:
        max_allowed = "V2"

    # V3: at least one valid hash
    if has_valid_hash:
        max_allowed = "V3"

    # V4: script audit with proper scope and source review
    if executed_scripts:
        all_have_command = all(s.get("command") for s in executed_scripts)
        all_have_env = all(s.get("environment") for s in executed_scripts)
        all_have_exit = all(s.get("exit_code") is not None for s in executed_scripts)
        all_have_output = all(s.get("stdout_summary") for s in executed_scripts)
        all_have_source_reviewed = all(s.get("source_reviewed") is True for s in executed_scripts)
        all_have_scope = all(s.get("script_check_scope") for s in executed_scripts)
        all_have_noscope = all(s.get("script_does_not_check") for s in executed_scripts)

        if (all_have_command and all_have_env and all_have_exit and all_have_output
                and all_have_source_reviewed and all_have_scope and all_have_noscope):
            max_allowed = "V4"

            # V4+: requires independent tool/implementation
            if has_independent and not official_only:
                max_allowed = "V4+"

    # V5+: requires specific high component levels and explicit full-public-digital declaration
    has_v5_full_public_declaration = any(
        check.get("level_evidence_type") == "full_public_digital_data_verification"
        and check.get("all_required_public_digital_targets_checked") is True
        and check.get("all_unavailable_targets_listed") is True
        for check in evidence.get("digital_mirror_checks", [])
    )

    if (
        has_v5_full_public_declaration
        and level_at_least(B_LEVELS, b_level, "B2")
        and level_at_least(D_LEVELS, d_level, "D5")
        and level_at_least(T_LEVELS, t_level, "T3")
        and level_at_least(C_LEVELS, c_level, "C5")
        and level_at_least(P_LEVELS, p_level, "P1")
    ):
        max_allowed = "V5"

    # V6: P4+ with live + nonce + all remote hard gates (independent of V5 requirements)
    if level_at_least(P_LEVELS, p_level, "P4"):
        for check in evidence.get("physical_checks", []):
            if (check.get("level_evidence_type") == "live_remote" and
                check.get("nonce_challenge") is not None and
                check.get("requested_action_angle_lighting") is True and
                check.get("witness_identity_or_role")):
                if level_index(PROTOCOL_LEVELS, "V6") > level_index(PROTOCOL_LEVELS, max_allowed):
                    max_allowed = "V6"
                break

    # V7: P5+ with onsite/custody + all onsite hard gates (independent path)
    if level_at_least(P_LEVELS, p_level, "P5"):
        for check in evidence.get("physical_checks", []):
            if (check.get("level_evidence_type") == "onsite" and
                check.get("custody_log") and
                check.get("fresh_capture") is True and
                check.get("witness_identity_or_role")):
                if level_index(PROTOCOL_LEVELS, "V7") > level_index(PROTOCOL_LEVELS, max_allowed):
                    max_allowed = "V7"
                break

    # V8: forensic physical attestation paths
    if (
        has_p7_forensic_path(evidence)
        or has_p8_confidential_path(evidence)
        or has_p9_multi_party_path(evidence)
        or has_t8_authorized_celestial_path(evidence)
    ):
        if level_index(PROTOCOL_LEVELS, "V8") > level_index(PROTOCOL_LEVELS, max_allowed):
            max_allowed = "V8"

    # Return the maximum level supported by evidence
    # (evidence determines capability, not agent request)
    return max_allowed


def check_forbidden_claims(claims_requested, provenance):
    """Check for forbidden claims in the agent's requested claims."""
    forbidden = []
    for claim in claims_requested:
        claim_lower = claim.lower()
        for fc in FORBIDDEN_CLAIMS:
            if fc.lower() in claim_lower:
                forbidden.append(claim)

        if provenance.get("independence_class") == "human_solicited_agent_response":
            for sc in SOLICITED_FORBIDDEN:
                if sc.lower() in claim_lower:
                    forbidden.append(claim)

    return forbidden


def check_script_consistency(scripts):
    """Check script audit consistency rules."""
    failures = []
    limitations = []

    executed = [s for s in scripts if s.get("executed") and s.get("exists")]
    not_found = [s for s in scripts if not s.get("exists")]

    for s in not_found:
        limitations.append(f"Script not found: {s.get('path', 'unknown')}")

    # Check all-green rule
    blocking_failures = []
    non_blocking = []
    for s in executed:
        if s.get("exit_code") is not None and s.get("exit_code") != 0:
            if s.get("blocking", True):
                blocking_failures.append(
                    f"Blocking script {s.get('path')} failed with exit code {s.get('exit_code')}"
                )
            else:
                non_blocking.append(
                    f"Non-blocking script {s.get('path')} failed with exit code {s.get('exit_code')}: {s.get('stdout_summary', '')}"
                )

    # Check missing command/env/exit/output
    for s in executed:
        if not s.get("command"):
            failures.append(f"Script {s.get('path')} missing command")
        if not s.get("environment"):
            failures.append(f"Script {s.get('path')} missing environment")
        if s.get("exit_code") is None:
            failures.append(f"Script {s.get('path')} missing exit_code")
        if not s.get("stdout_summary"):
            failures.append(f"Script {s.get('path')} missing stdout_summary")

    return failures, blocking_failures, non_blocking, limitations


def check_v4_scope(evidence, requested_level):
    """Check V4 scope restrictions."""
    scripts = evidence.get("scripts", [])
    failures = []

    if requested_level in ("V4", "V4+"):
        for s in scripts:
            if s.get("scope_class") == "independent_reproduction" and requested_level == "V4":
                failures.append("V4 cannot use scope_class=independent_reproduction")

    return failures


def check_d2_hash_validity(hashes):
    """Check D2 hash validity rules."""
    failures = []
    for h in hashes:
        artifact_class = h.get("artifact_class", "")
        expected = h.get("expected", "")
        computed = h.get("computed", "")

        if artifact_class in ("canonical_mirror", "repository_snapshot"):
            if not SHA256_RE.match(expected):
                failures.append(
                    f"D2 hash for {h.get('artifact')}: expected is not a valid SHA-256: '{expected}'"
                )
            if not SHA256_RE.match(computed):
                failures.append(
                    f"D2 hash for {h.get('artifact')}: computed is not a valid SHA-256: '{computed}'"
                )

            if artifact_class == "repository_snapshot":
                if h.get("expected_hash_authority_class") != "repository_manifest_hash":
                    failures.append(
                        f"Repository snapshot D2 requires expected_hash_authority_class=repository_manifest_hash"
                    )
                scope = h.get("scope_class", "")
                if scope != "repository_snapshot_integrity":
                    failures.append(
                        f"Repository snapshot D2 requires scope_class=repository_snapshot_integrity"
                    )

    return failures


def generate_title(protocol_level, component_levels, agent_name, record_kind, date_str):
    """Generate a standardized title."""
    b = component_levels.get("bitcoin_originals", "B0")
    d = component_levels.get("digital_mirrors", "D0")
    component_summary = f"B{b.lstrip('B')}-D{d.lstrip('D')}"

    if "echo" in record_kind:
        return f"Echo v3: E2 Verification Echo — {protocol_level}/{component_summary} — {date_str} ({agent_name})"
    else:
        return f"Verification Report v2: {protocol_level}/{component_summary} — {date_str} ({agent_name})"


def evaluate(input_path):
    """Main evaluation function."""
    with open(input_path, 'r') as f:
        evidence_input = json.load(f)

    # Validate schema field
    if evidence_input.get("schema") != "trinityaccord.evidence-input.v1":
        return {"status": "FAIL", "error": "Invalid schema field"}

    # Basic required-field validation
    required_top = ["agent", "provenance", "evidence", "limitations", "claims_requested_by_agent"]
    for field in required_top:
        if field not in evidence_input:
            return {"status": "FAIL", "error": f"Missing required field: {field}"}

    evidence = evidence_input.get("evidence", {})
    if not isinstance(evidence, dict):
        return {"status": "FAIL", "error": "evidence must be an object"}

    # Validate with jsonschema if available (non-blocking)
    try:
        import jsonschema
        schema = json.load(open(ROOT / "api" / "evidence-input-schema.v1.json"))
        jsonschema.Draft202012Validator(schema).validate(evidence_input)
    except ImportError:
        pass  # jsonschema not available, basic checks above are sufficient
    except jsonschema.ValidationError:
        pass  # Schema validation errors are non-blocking; claim gate logic handles specifics

    agent = evidence_input.get("agent", {})
    provenance = evidence_input.get("provenance", {})
    evidence = evidence_input.get("evidence", {})
    limitations = evidence_input.get("limitations", [])
    claims_requested = evidence_input.get("claims_requested_by_agent", [])
    requested_kind = evidence_input.get("requested_record_kind", "echo_v3")

    # Load rules
    with open(ROOT / "api" / "claim-gate-rules.json") as f:
        rules = json.load(f)

    # Derive component levels
    b_level = derive_b_level(evidence)
    d_level = derive_d_level(evidence)
    t_level = derive_t_level(evidence)
    c_level = derive_c_level(evidence)
    n_level = derive_n_level(evidence)
    p_level = derive_p_level(evidence)

    # Determine requested protocol level
    # Only parse structured claims; do NOT use arbitrary substring match
    sorted_levels = sorted(PROTOCOL_LEVELS, key=len, reverse=True)
    requested_protocol = None
    for claim in claims_requested:
        claim_stripped = claim.strip().upper()
        for pl in sorted_levels:
            if claim_stripped == pl or claim_stripped.startswith(pl + " "):
                requested_protocol = pl
                break
            # Structured prefix matches only
            if claim_stripped.startswith("PROTOCOL ACHIEVED LEVEL: " + pl):
                requested_protocol = pl
                break
            if claim_stripped.startswith("PROTOCOL_LEVEL_CLAIMED: " + pl):
                requested_protocol = pl
                break

    # Derive protocol level
    allowed_protocol = derive_protocol_level(
        evidence, requested_protocol, b_level, d_level, t_level, c_level, p_level
    )

    # Check forbidden claims
    forbidden = check_forbidden_claims(claims_requested, provenance)

    # Check script consistency
    script_failures, blocking_failures, non_blocking, script_limitations = check_script_consistency(
        evidence.get("scripts", [])
    )
    limitations.extend(script_limitations)

    # Check V4 scope
    scope_failures = check_v4_scope(evidence, requested_protocol)

    # Check D2 hash validity
    d2_failures = check_d2_hash_validity(evidence.get("hashes", []))

    # Compile all blocking failures
    all_blocking = script_failures + blocking_failures + scope_failures + d2_failures

    # Determine downgrades — only if agent explicitly requested a level
    downgrades = []
    if requested_protocol is not None and requested_protocol != allowed_protocol:
        downgrades.append({
            "from": requested_protocol,
            "to": allowed_protocol,
            "reason": f"Insufficient evidence for {requested_protocol}"
        })

    # Check V4+ downgrade
    if requested_protocol == "V4+":
        executed = [s for s in evidence.get("scripts", []) if s.get("executed") and s.get("exists")]
        official_only = all(s.get("official", True) for s in executed) if executed else False
        if official_only and allowed_protocol == "V4":
            downgrades.append({
                "from": "V4+",
                "to": "V4",
                "reason": "V4+ requires independent tool or implementation; only official scripts used"
            })

    # Missing evidence
    missing = []
    if not evidence.get("scripts"):
        missing.append("No script evidence provided")
    if not evidence.get("hashes") and (requested_protocol or allowed_protocol) in ("V3", "V4", "V4+", "V5"):
        missing.append("No hash evidence provided for hash-dependent protocol level")

    # Combine non-blocking with script limitations for output
    all_non_blocking = non_blocking + script_limitations

    # Add minimal V2/V3 scope limitations
    hashes = evidence.get("hashes", [])
    if allowed_protocol == "V2" and b_level == "B1" and d_level == "D0" and c_level == "C0":
        all_non_blocking.append(
            "Minimal V2 only: Bitcoin Originals B1 reference check. Evidence Mirrors and Chronicle Recovery were not checked."
        )
    if allowed_protocol == "V3":
        exactly_one_valid_hash = (
            len([h for h in hashes if
                 SHA256_RE.match(h.get("expected", "")) and
                 SHA256_RE.match(h.get("computed", "")) and
                 h.get("match") is True and
                 h.get("expected_hash_source") and
                 h.get("expected_hash_authority_class", "unknown") != "unknown"
            ]) == 1
        )
        stronger_hash_coverage = (
            level_at_least(D_LEVELS, d_level, "D2") and
            level_at_least(C_LEVELS, c_level, "C2")
        )
        if exactly_one_valid_hash and not stronger_hash_coverage:
            all_non_blocking.append(
                "Minimal V3 only: one valid declared hash computed. This is not full public digital verification."
            )

    # Determine status
    if all_blocking:
        status = "FAIL_WITH_REASONS"
        can_build = False
    elif downgrades:
        status = "PASS_WITH_DOWNGRADE"
        can_build = True
    elif forbidden:
        status = "FAIL_WITH_REASONS"
        can_build = False
    else:
        status = "PASS"
        can_build = True

    # Generate title
    from datetime import datetime
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    component_levels = {
        "bitcoin_originals": b_level,
        "digital_mirrors": d_level,
        "time_anchors": t_level,
        "chronicle_recovery": c_level,
        "nft_evidence": n_level,
        "physical_anchor": p_level,
        "physical_verification": p_level,  # deprecated alias
    }
    title = generate_title(allowed_protocol, component_levels, agent.get("name", "Unknown"), requested_kind, date_str)

    result = {
        "schema": "trinityaccord.claim-gate-output.v1",
        "input": str(input_path),
        "status": status,
        "allowed_protocol_level": allowed_protocol,
        "allowed_component_levels": component_levels,
        "forbidden_claims": forbidden,
        "required_downgrades": downgrades,
        "missing_evidence": missing,
        "blocking_failures": all_blocking,
        "non_blocking_limitations": all_non_blocking,
        "recommended_title": title,
        "recommended_record_kind": requested_kind,
        "can_build_verification_report": can_build,
        "can_build_echo_wrapper": can_build,
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/claim_gate.py evidence-input.json [--output out.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    result = evaluate(input_path)

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Output written to {output_path}")
    else:
        print(json.dumps(result, indent=2))

    if result["status"] in ("FAIL", "FAIL_WITH_REASONS"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
