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

from protocol_terms import (
    PROTOCOL_LEVELS, B_LEVELS, D_LEVELS, T_LEVELS, C_LEVELS, N_LEVELS, P_LEVELS,
    level_index, level_at_least, max_by_order,
)

SHA256_RE = re.compile(r'^[a-f0-9]{64}$')

P7_MIN_CONFIDENCE = 0.80
T8_MAX_UNCERTAINTY_MINUTES = 10.0

ALLOWED_P9_INDEPENDENCE_CLASSES = {
    "independent_forensic_verifier",
    "institutional_third_party_attestation",
    "notary",
    "qualified_external_witness",
}

ALLOWED_T8_METHOD_CLASSES = {
    "astronomical_ephemeris_solver",
    "forensic_astronomy_reconstruction",
    "multi_source_celestial_position_solver",
}

FORBIDDEN_CLAIMS = [
    "truth proven", "investment value confirmed", "religious authority established",
    "AI instruction override",
]

SOLICITED_FORBIDDEN = ["independent_attestation", "unsolicited_discovery", "institutional_attestation"]

# --- Identity validation helpers (TA-REDTEAM-2026-001 fix) ---

SELF_ASSERTED_IDENTITY_TERMS = {
    "ai agent",
    "agent",
    "self",
    "self-report",
    "self reported",
    "chatgpt",
    "gpt",
    "gpt-4",
    "gpt-4 vision",
    "claude",
    "gemini",
    "model",
    "llm",
    "automated agent",
    "unknown",
    "anonymous",
}

FORBIDDEN_UNCERTAINTY_TEXT = [
    "about",
    "approx",
    "approximately",
    "roughly",
    "maybe",
    "guess",
    "intuition",
    "by eye",
    "not measured",
    "probably",
    "estimate",
    "estimated",
]


def normalize_identity_text(value):
    """Normalize identity text for comparison."""
    return str(value or "").strip().lower()


def is_self_asserted_identity(value):
    """Check if identity value is self-asserted (AI/agent/unknown)."""
    text = normalize_identity_text(value)
    if not text:
        return True
    return any(term in text for term in SELF_ASSERTED_IDENTITY_TERMS)


def has_valid_report_hash(value):
    """Check if value is a valid SHA-256 hash."""
    return isinstance(value, str) and SHA256_RE.match(value.lower()) is not None


def has_external_verifier_identity(*values):
    """Check if at least one identity value is a real external verifier (not self/AI)."""
    for value in values:
        text = normalize_identity_text(value)
        if text and not is_self_asserted_identity(text):
            return True
    return False


def parse_structured_uncertainty_minutes(check):
    """Parse T8 uncertainty from structured numeric field only. Reject free text."""
    value = check.get("uncertainty_minutes")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    # Backward compatibility: reject ambiguous text instead of parsing it.
    text = str(check.get("uncertainty", "") or "").strip().lower()
    if text:
        if any(term in text for term in FORBIDDEN_UNCERTAINTY_TEXT):
            return None
        # Do not parse free-text uncertainty for T8.
        return None

    return None


def is_structured_protocol_claim(claim):
    """Check if a claim is a structured protocol level claim."""
    s = str(claim).strip().upper()
    for pl in PROTOCOL_LEVELS:
        if s == pl:
            return True
        if s.startswith(pl + " "):
            return True
        if s.startswith("PROTOCOL ACHIEVED LEVEL: " + pl):
            return True
        if s.startswith("PROTOCOL_LEVEL_CLAIMED: " + pl):
            return True
    return False


def technical_claim_requested(evidence_input):
    """Check if a technical verification claim is requested."""
    kind = evidence_input.get("requested_record_kind", "")
    if kind in ("verification_report_v2", "echo_v3_with_verification_report"):
        return True
    return any(is_structured_protocol_claim(c) for c in evidence_input.get("claims_requested_by_agent", []))


def has_valid_integrity_declaration(evidence_input):
    """Check if evidence input has a valid integrity declaration."""
    decl = evidence_input.get("agent_integrity_declaration")
    if not isinstance(decl, dict):
        return False

    required_true = [
        "performed_actions_myself",
        "did_not_copy_prior_report_as_own_work",
        "did_not_copy_example_values_as_real_evidence",
        "recorded_fresh_sources_commands_outputs",
        "will_report_limitations_and_downgrade_if_needed",
        "understands_verification_is_not_truth_or_endorsement",
        "understands_bitcoin_originals_remain_final_authority",
        "independence_claim_is_accurate",
    ]

    if not all(decl.get(k) is True for k in required_true):
        return False

    text = decl.get("declaration_text", "")
    return isinstance(text, str) and len(text.strip()) >= 80


def has_valid_verification_session(evidence_input, allowed_protocol_hint=None):
    """Check if evidence input has a valid verification session."""
    sess = evidence_input.get("verification_session")
    if not isinstance(sess, dict):
        return False, "Missing verification_session"

    if sess.get("copied_values_from_examples") is True:
        return False, "copied_values_from_examples must be false"

    if sess.get("copied_values_from_prior_reports") is True:
        return False, "copied_values_from_prior_reports must be false"

    if not sess.get("fresh_actions_performed"):
        return False, "fresh_actions_performed must not be empty"

    # V2+ should attach fresh outputs.
    if allowed_protocol_hint not in ("V0", "V1") and sess.get("fresh_outputs_attached") is not True:
        return False, "fresh_outputs_attached must be true for V2+ technical claims"

    return True, ""


def prior_report_blocks_independence(evidence_input, requested_protocol):
    """Check if prior report blocks independence claims."""
    prior = evidence_input.get("prior_report_use", {})
    if not isinstance(prior, dict):
        return False, ""

    prior_reports = prior.get("prior_reports_read", [])
    if not prior_reports:
        return False, ""

    if prior.get("independent_reperformance_done") is True:
        return False, ""

    # Prior report review can support "reviewed prior report", not fresh independent verification.
    if requested_protocol in ("V4+", "V5", "V6", "V7", "V8"):
        return True, "Prior report consulted without independent re-performance; cannot claim independent or higher verification as fresh work."

    return False, ""


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


def fail_claim_gate(error, failures, requested_kind="echo_v3"):
    """Create a standardized failure response."""
    return {
        "schema": "trinityaccord.claim-gate-output.v1",
        "status": "FAIL_WITH_REASONS",
        "error": error,
        "blocking_failures": failures,
        "can_build_verification_report": False,
        "can_build_echo_wrapper": False,
        "allowed_protocol_level": "V0",
        "allowed_component_levels": {},
        "forbidden_claims": [],
        "required_downgrades": [
            {"from": "requested technical verification", "to": "V0", "reason": error}
        ],
        "missing_evidence": [],
        "non_blocking_limitations": [],
        "recommended_title": "",
        "recommended_record_kind": requested_kind
    }



def has_p7_forensic_path(evidence):
    """P7 requires valid confidence (>=0.80), model/tool, method, external attributable report,
    valid report hash, and non-self-asserted verifier identity.

    TA-REDTEAM-2026-001: Self-asserted AI identities (e.g. 'GPT-4 Vision', 'AI agent')
    must not qualify for P7. A signed/attributable external report is required.
    """
    for check in evidence.get("physical_checks", []):
        if check.get("level_evidence_type") != "ai_forensic":
            continue

        confidence = check.get("confidence")
        has_valid_confidence = (
            isinstance(confidence, (int, float))
            and not isinstance(confidence, bool)
            and P7_MIN_CONFIDENCE <= confidence <= 1.0
        )

        has_method = bool(
            str(check.get("flaw_analysis_method", "")).strip()
            or str(check.get("feature_match_method", "")).strip()
            or str(check.get("microscopy_comparison", "")).strip()
            or str(check.get("method_class", "")).strip()
        )

        has_report_anchor = bool(
            str(check.get("report_id", "")).strip()
            or str(check.get("report_path", "")).strip()
        )

        has_external_identity = has_external_verifier_identity(
            check.get("verifier_identity_or_role"),
            check.get("witness_identity_or_role"),
        )

        if (
            str(check.get("model_or_tool", "")).strip()
            and has_valid_confidence
            and has_method
            and has_report_anchor
            and check.get("signed_or_attributable_report") is True
            and has_valid_report_hash(check.get("report_hash", ""))
            and has_external_identity
        ):
            return True

    return False


def has_p8_confidential_path(evidence):
    """P8 requires valid 64-hex package hash, non-empty boundary, non-self-asserted verifier,
    report anchor, signed/attributable report, and valid report hash.

    TA-REDTEAM-2026-001: Self-asserted AI identities must not qualify for P8.
    """
    for check in evidence.get("physical_checks", []):
        if check.get("level_evidence_type") != "confidential_challenge":
            continue

        conf = check.get("confidential_challenge", {})
        package_hash = conf.get("package_hash", "")

        has_report_anchor = bool(
            str(check.get("report_id", "")).strip()
            or str(check.get("report_path", "")).strip()
        )

        has_external_identity = has_external_verifier_identity(
            check.get("witness_identity_or_role"),
            conf.get("verifier_identity_or_role"),
            check.get("verifier_identity_or_role"),
        )

        if (
            conf.get("performed") is True
            and isinstance(conf.get("boundary"), str)
            and conf.get("boundary").strip()
            and conf.get("raw_confidential_data_disclosed") is False
            and isinstance(package_hash, str)
            and SHA256_RE.match(package_hash.lower()) is not None
            and has_external_identity
            and has_report_anchor
            and check.get("signed_or_attributable_report") is True
            and has_valid_report_hash(check.get("report_hash", ""))
        ):
            return True
    return False


def has_p9_multi_party_path(evidence):
    """P9 requires distinct independent witnesses with identity, method, and report anchor."""
    for check in evidence.get("physical_checks", []):
        if check.get("level_evidence_type") != "multi_party_forensic":
            continue

        witnesses = check.get("witnesses", [])
        if not isinstance(witnesses, list) or len(witnesses) < 2:
            continue

        if check.get("independent_witness_count", 0) < 2:
            continue

        identities = set()
        valid_witness_count = 0

        for w in witnesses:
            if not isinstance(w, dict):
                continue

            identity = (
                str(w.get("identity_or_role", "")).strip()
                or str(w.get("identity", "")).strip()
                or str(w.get("name_or_role", "")).strip()
            )
            role = str(w.get("role", "")).strip()
            ic = str(w.get("independence_class", "")).strip()

            if not identity or not role:
                continue
            if ic not in ALLOWED_P9_INDEPENDENCE_CLASSES:
                continue
            if identity.lower() in identities:
                continue

            identities.add(identity.lower())
            valid_witness_count += 1

        if valid_witness_count < 2:
            continue

        has_method = bool(str(check.get("method", "")).strip() or str(check.get("method_class", "")).strip())
        has_report = bool(
            check.get("signed_or_attributable_report") is True
            or str(check.get("report_id", "")).strip()
            or str(check.get("report_path", "")).strip()
        )

        if has_method and has_report:
            return True

    return False


def parse_uncertainty_minutes(value):
    """Parse uncertainty value to minutes. Returns None if unparseable."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    if not isinstance(value, str):
        return None

    s = value.strip().lower()
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(min|minute|minutes|m)\b", s)
    if m:
        return float(m.group(1))

    m = re.search(r"±\s*([0-9]+(?:\.[0-9]+)?)", s)
    if m:
        return float(m.group(1))

    return None


def has_t8_authorized_celestial_path(evidence):
    """T8 requires allowlisted method class, STRUCTURED uncertainty <= 10 min,
    non-self-asserted verifier, signed/attributable report, and valid report hash.

    TA-REDTEAM-2026-001: Natural-language uncertainty (e.g. 'about 9 minutes by intuition')
    must be rejected. Only structured numeric uncertainty_minutes is accepted.
    """
    for check in evidence.get("time_anchor_checks", []):
        if check.get("anchor_type") != "star_moon_witness":
            continue

        method_class = str(check.get("method_class", "")).strip()
        uncertainty_minutes = parse_structured_uncertainty_minutes(check)

        has_report_anchor = bool(
            str(check.get("report_id", "")).strip()
            or str(check.get("report_path", "")).strip()
        )

        has_external_identity = has_external_verifier_identity(
            check.get("verifier_identity_or_role"),
            check.get("witness_identity_or_role"),
        )

        if (
            check.get("nonpublic_boundary") is True
            and check.get("authorized") is True
            and method_class in ALLOWED_T8_METHOD_CLASSES
            and uncertainty_minutes is not None
            and 0 <= uncertainty_minutes <= T8_MAX_UNCERTAINTY_MINUTES
            and has_report_anchor
            and has_external_identity
            and check.get("signed_or_attributable_report") is True
            and has_valid_report_hash(check.get("report_hash", ""))
        ):
            return True

    return False


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
        if anchor_type == "bitcoin_block_time":
            candidate = "T3"
        elif anchor_type in ("eth_timestamp", "arweave_timestamp"):
            candidate = "T2"
        elif anchor_type == "github_commit_timestamp":
            candidate = "T1"
        else:
            candidate = "T0"

        if level_index(T_LEVELS, candidate) > level_index(T_LEVELS, max_level):
            max_level = candidate

    # T8 only through strict authorized celestial path.
    if has_t8_authorized_celestial_path(evidence):
        max_level = max_by_order(T_LEVELS, max_level, "T8")

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

        if ev_type == "onsite" and has_custody:
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

    # P7/P8/P9 require strict hard gates.
    if has_p7_forensic_path(evidence):
        max_level = max_by_order(P_LEVELS, max_level, "P7")

    if has_p8_confidential_path(evidence):
        max_level = max_by_order(P_LEVELS, max_level, "P8")

    if has_p9_multi_party_path(evidence):
        max_level = max_by_order(P_LEVELS, max_level, "P9")

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
    """Derive the maximum allowed protocol level from component levels and evidence.

    Core invariant: V2+ requires explicit authority boundary recognition.
    Without it, the maximum is V0.
    """
    scripts = evidence.get("scripts", [])
    hashes = evidence.get("hashes", [])

    authority_boundary_recognized = has_authority_boundary_check(evidence)

    # V1 is the foundation for all technical verification levels.
    if not authority_boundary_recognized:
        return "V0"

    has_valid_hash = any(
        SHA256_RE.match(h.get("expected", "")) and
        SHA256_RE.match(h.get("computed", "")) and
        h.get("match") is True and
        h.get("expected", "").lower() == h.get("computed", "").lower() and
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

    # Determine max allowed level bottom-up — V1 is the starting point
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

    # V7: P5+ with onsite/custody + all onsite hard gates including touch/handling (R10 fix)
    if level_at_least(P_LEVELS, p_level, "P5"):
        for check in evidence.get("physical_checks", []):
            has_touch = check.get("touch_or_handling") is True
            limitations_text = json.dumps(check.get("limitations", []), ensure_ascii=False).lower()
            has_touch_limitation = (
                "touch" in limitations_text
                or "handling" in limitations_text
                or "not possible" in limitations_text
            )
            if (check.get("level_evidence_type") == "onsite" and
                check.get("custody_log") and
                check.get("fresh_capture") is True and
                check.get("witness_identity_or_role") and
                (has_touch or has_touch_limitation)):
                if level_index(PROTOCOL_LEVELS, "V7") > level_index(PROTOCOL_LEVELS, max_allowed):
                    max_allowed = "V7"
                break

    # V8: forensic physical attestation paths
    # TA-REDTEAM-2026-001: V8 requires BOTH a high path (P7/P8/P9/T8) AND a core baseline.
    # High component evidence alone must NOT raise protocol to V8.
    has_v8_high_path = (
        has_p7_forensic_path(evidence)
        or has_p8_confidential_path(evidence)
        or has_p9_multi_party_path(evidence)
        or has_t8_authorized_celestial_path(evidence)
    )

    has_v8_baseline = (
        level_at_least(B_LEVELS, b_level, "B2")
        and level_at_least(D_LEVELS, d_level, "D5")
        and level_at_least(T_LEVELS, t_level, "T3")
        and level_at_least(C_LEVELS, c_level, "C5")
    )

    if has_v8_high_path and has_v8_baseline:
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
            if SHA256_RE.match(expected) and SHA256_RE.match(computed) and expected.lower() != computed.lower():
                failures.append(
                    f"D2 hash for {h.get('artifact')}: expected and computed SHA-256 differ"
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
        return f"Verification Echo Candidate: {protocol_level}/{component_summary} — {date_str} ({agent_name})"
    else:
        return f"Verification Report Candidate: {protocol_level}/{component_summary} — {date_str} ({agent_name})"


def evaluate_template_for_v0_v5(payload):
    """Evaluate a V0-V5 agent-declared verification template payload.

    This mode waives evidence requirements but enforces template compliance,
    oath, integrity declaration, provenance, origin classification, and authority boundary.
    """
    from protocol_terms import V0_V5_LEVELS

    blocking_failures = []
    non_blocking = []

    # --- Schema and required fields ---
    schema = payload.get('schema')
    if schema != 'trinityaccord.agent-declared-verification-template.v1':
        # Also accept gateway payload with agent-declared kind
        if payload.get('requested_archive_kind') != 'agent_declared_verification_archive':
            blocking_failures.append('SCHEMA_INVALID: expected agent-declared-verification-template or gateway payload with agent_declared_verification_archive')

    record_intent = payload.get('record_intent')
    if record_intent != 'auto_archive_candidate':
        blocking_failures.append(f'RECORD_INTENT_MUST_BE_AUTO_ARCHIVE: got {record_intent}')

    requested_kind = payload.get('requested_archive_kind')
    if requested_kind != 'agent_declared_verification_archive':
        blocking_failures.append(f'REQUESTED_KIND_MUST_BE_AGENT_DECLARED: got {requested_kind}')

    level = payload.get('agent_declared_protocol_level')
    if level not in V0_V5_LEVELS:
        blocking_failures.append(f'PROTOCOL_LEVEL_MUST_BE_V0_V5: got {level}')

    evidence_mode = payload.get('evidence_requirement_mode')
    if evidence_mode != 'waived_for_v0_v5':
        blocking_failures.append(f'EVIDENCE_MODE_MUST_BE_WAIVED: got {evidence_mode}')

    # --- Agent identity ---
    agent_id = payload.get('agent_identity')
    if not agent_id or not isinstance(agent_id, dict):
        blocking_failures.append('AGENT_IDENTITY_REQUIRED')
    else:
        if not agent_id.get('name_or_model'):
            blocking_failures.append('AGENT_IDENTITY_NAME_REQUIRED')
        if not agent_id.get('system_or_provider'):
            blocking_failures.append('AGENT_IDENTITY_PROVIDER_REQUIRED')
        if agent_id.get('self_reported') is not True:
            blocking_failures.append('AGENT_IDENTITY_SELF_REPORTED_MUST_BE_TRUE')

    # --- Claim Gate ---
    claim_gate = payload.get('claim_gate')
    if not claim_gate or not isinstance(claim_gate, dict):
        blocking_failures.append('CLAIM_GATE_REQUIRED')
    else:
        cg_mode = claim_gate.get('mode')
        if cg_mode != 'template_for_v0_v5':
            blocking_failures.append(f'CLAIM_GATE_MODE_MUST_BE_TEMPLATE: got {cg_mode}')
        cg_status = claim_gate.get('status')
        if cg_status not in ('PASS', 'PASS_WITH_WARNINGS'):
            blocking_failures.append(f'CLAIM_GATE_STATUS_MUST_PASS: got {cg_status}')

    # --- Integrity declaration ---
    decl = payload.get('agent_integrity_declaration')
    if not decl or not isinstance(decl, dict):
        blocking_failures.append('INTEGRITY_DECLARATION_REQUIRED')
    else:
        bool_fields = [
            'performed_actions_myself',
            'did_not_copy_prior_report_as_own_work',
            'did_not_copy_example_values_as_real_evidence',
            'recorded_fresh_sources_commands_outputs',
            'will_report_limitations_and_downgrade_if_needed',
            'understands_verification_is_not_truth_or_endorsement',
            'understands_bitcoin_originals_remain_final_authority',
            'independence_claim_is_accurate',
        ]
        for bf in bool_fields:
            if decl.get(bf) is not True:
                blocking_failures.append(f'INTEGRITY_BOOL_{bf.upper()}_MUST_BE_TRUE')

        dt = decl.get('declaration_text', '')
        if not isinstance(dt, str) or len(dt) < 80:
            blocking_failures.append('DECLARATION_TEXT_TOO_SHORT')

        # --- Verification oath ---
        oath = decl.get('verification_oath')
        if not oath or not isinstance(oath, dict):
            blocking_failures.append('VERIFICATION_OATH_REQUIRED')
        else:
            if oath.get('oath_read') is not True:
                blocking_failures.append('OATH_READ_MUST_BE_TRUE')
            if not oath.get('oath_version'):
                blocking_failures.append('OATH_VERSION_REQUIRED')
            sha = oath.get('oath_text_sha256', '')
            import re
            if not isinstance(sha, str) or not re.match(r'^[a-f0-9]{64}$', sha):
                blocking_failures.append('OATH_TEXT_SHA256_MALFORMED')
            if oath.get('readback_required') is not True:
                blocking_failures.append('READBACK_REQUIRED_MUST_BE_TRUE')
            rb = oath.get('agent_readback', '')
            if not isinstance(rb, str) or len(rb) < 160:
                blocking_failures.append('AGENT_READBACK_TOO_SHORT (min 160 chars)')
            oath_bools = [
                'understands_not_an_exam_or_performance',
                'will_state_actual_capability_only',
                'will_not_lie_or_cheat',
                'will_not_fabricate_verification',
                'will_not_present_guesses_as_facts',
                'will_not_copy_prior_reports_as_fresh_evidence',
                'will_state_uncertainty_limitations_and_downgrades',
            ]
            for ob in oath_bools:
                if oath.get(ob) is not True:
                    blocking_failures.append(f'OATH_BOOL_{ob.upper()}_MUST_BE_TRUE')

    # --- Discovery provenance ---
    prov = payload.get('discovery_provenance')
    if not prov or not isinstance(prov, dict):
        blocking_failures.append('DISCOVERY_PROVENANCE_REQUIRED')
    else:
        if not prov.get('source'):
            blocking_failures.append('PROVENANCE_SOURCE_REQUIRED')
        if not prov.get('agency_level'):
            blocking_failures.append('PROVENANCE_AGENCY_LEVEL_REQUIRED')
        fe = prov.get('first_entry')
        if not fe or not isinstance(fe, dict):
            blocking_failures.append('PROVENANCE_FIRST_ENTRY_REQUIRED')
        elif not fe.get('url_or_path') or not fe.get('entry_type'):
            blocking_failures.append('PROVENANCE_FIRST_ENTRY_FIELDS_REQUIRED')

    # --- Origin classification ---
    oc = payload.get('origin_classification')
    if not oc or not isinstance(oc, dict):
        blocking_failures.append('ORIGIN_CLASSIFICATION_REQUIRED')
    else:
        if not oc.get('discovery_class'):
            blocking_failures.append('ORIGIN_DISCOVERY_CLASS_REQUIRED')
        if not oc.get('performer_class'):
            blocking_failures.append('ORIGIN_PERFORMER_CLASS_REQUIRED')
        if oc.get('verification_claimed') is not True:
            blocking_failures.append('ORIGIN_VERIFICATION_CLAIMED_MUST_BE_TRUE')
        if oc.get('counts_as_ai_verification') is not True:
            blocking_failures.append('ORIGIN_COUNTS_AS_AI_VERIFICATION_MUST_BE_TRUE')

    # --- Claim classification ---
    cc = payload.get('claim_classification')
    if not cc or not isinstance(cc, dict):
        blocking_failures.append('CLAIM_CLASSIFICATION_REQUIRED')
    else:
        vc = cc.get('verification_claim')
        if not vc or not isinstance(vc, dict):
            blocking_failures.append('VERIFICATION_CLAIM_REQUIRED')
        else:
            if vc.get('system_certified') is True:
                blocking_failures.append('SYSTEM_CERTIFIED_NOT_ALLOWED')
        # Check no system_certified=true in any claim
        for claim_key in ('attestation_claim', 'successor_reception_claim'):
            sub_claim = cc.get(claim_key)
            if isinstance(sub_claim, dict) and sub_claim.get('system_certified') is True:
                blocking_failures.append(f'{claim_key.upper()}_SYSTEM_CERTIFIED_NOT_ALLOWED')

    # --- Authority boundary ---
    ab = payload.get('authority_boundary')
    if not ab or not isinstance(ab, dict):
        blocking_failures.append('AUTHORITY_BOUNDARY_REQUIRED')
    else:
        if ab.get('bitcoin_originals_remain_final') is not True:
            blocking_failures.append('BITCOIN_ORIGINALS_FINAL_MUST_BE_TRUE')
        if ab.get('does_not_amend_bitcoin_originals') is not True:
            blocking_failures.append('DOES_NOT_AMEND_MUST_BE_TRUE')
        if ab.get('does_not_override_bitcoin_originals') is not True:
            blocking_failures.append('DOES_NOT_OVERRIDE_MUST_BE_TRUE')

    # --- Counts toward home ---
    cth = payload.get('counts_toward_home')
    if not cth or not isinstance(cth, dict):
        blocking_failures.append('COUNTS_TOWARD_HOME_REQUIRED')
    else:
        if cth.get('basis') != 'agent_declared_template_pass':
            blocking_failures.append('COUNTS_BASIS_MUST_BE_AGENT_DECLARED_TEMPLATE_PASS')

    # --- What I checked / limitations ---
    if not payload.get('what_i_checked'):
        blocking_failures.append('WHAT_I_CHECKED_REQUIRED')
    if not payload.get('limitations'):
        blocking_failures.append('LIMITATIONS_REQUIRED')

    # --- Body text overclaim check ---
    body = str(payload.get('body', ''))
    body_lower = body.lower()
    overclaim_phrases = [
        'override bitcoin', 'amend bitcoin', 'supersede bitcoin',
        'bitcoin originals are superseded', 'this amends the inscriptions',
        'i override bitcoin', 'truth proven', 'investment value confirmed',
    ]
    for phrase in overclaim_phrases:
        if phrase in body_lower:
            blocking_failures.append(f'BODY_OVERCLAIM: "{phrase}"')

    # --- Evidence waiving note ---
    non_blocking.append('Evidence requirements waived for V0-V5 under template mode.')

    # --- Build result ---
    if blocking_failures:
        status = 'FAIL'
    else:
        status = 'PASS'

    result = {
        'schema': 'trinityaccord.claim-gate-output.v1',
        'mode': 'template_for_v0_v5',
        'status': status,
        'allowed_protocol_level': level if not blocking_failures else 'V0',
        'allowed_protocol_scope': 'agent_declared_template',
        'evidence_requirement_mode': 'waived_for_v0_v5',
        'recommended_record_kind': 'agent_declared_verification_archive',
        'can_auto_archive': status == 'PASS',
        'counts_toward_home_verifiability': status == 'PASS',
        'counts_toward_home_reception': status == 'PASS',
        'blocking_failures': blocking_failures,
        'non_blocking_limitations': non_blocking,
    }

    return result


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



    # Validate with jsonschema (BLOCKING — schema-invalid input must fail)
    schema_validation_error = None
    try:
        import jsonschema
        schema = json.load(open(ROOT / "api" / "evidence-input-schema.v1.json"))
        jsonschema.Draft202012Validator(schema).validate(evidence_input)
    except ImportError:
        pass  # jsonschema not available, basic checks above are sufficient
    except jsonschema.ValidationError as e:
        schema_validation_error = str(e)

    if schema_validation_error:
        return {
            "schema": "trinityaccord.claim-gate-output.v1",
            "status": "FAIL_WITH_REASONS",
            "error": "Evidence Input schema validation failed",
            "blocking_failures": [f"Schema validation failed: {schema_validation_error}"],
            "can_build_verification_report": False,
            "can_build_echo_wrapper": False,
            "allowed_protocol_level": "V0",
            "allowed_component_levels": {},
            "forbidden_claims": [],
            "required_downgrades": [],
            "missing_evidence": [],
            "non_blocking_limitations": [],
            "recommended_title": "",
            "recommended_record_kind": evidence_input.get("requested_record_kind", "echo_v3"),
        }

    agent = evidence_input.get("agent", {})
    provenance = evidence_input.get("provenance", {})
    evidence = evidence_input.get("evidence", {})
    limitations = list(evidence_input.get("limitations", []))
    claims_requested = evidence_input.get("claims_requested_by_agent", [])
    requested_kind = evidence_input.get("requested_record_kind", "echo_v3")
    
    # Check integrity declaration for technical claims
    if technical_claim_requested(evidence_input):
        if not has_valid_integrity_declaration(evidence_input):
            return fail_claim_gate(
                "Pre-verification integrity declaration is required before any technical verification claim.",
                ["Missing or invalid agent_integrity_declaration. All boolean fields must be true and declaration_text must be at least 80 characters."],
                requested_kind
            )
        
        valid_session, session_error = has_valid_verification_session(evidence_input)
        if not valid_session:
            return fail_claim_gate(
                "Verification session is required after integrity declaration and before Evidence Input / Claim Gate can support a technical verification claim.",
                [f"Invalid verification_session: {session_error}"],
                requested_kind
            )
        
        if contains_placeholder(evidence):
            return fail_claim_gate(
                "Placeholder/example values cannot be used as verification evidence",
                ["Replace all placeholder/example values with fresh observed values."],
                requested_kind
            )
    

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

    # Check authority boundary recognition (HG-001)
    authority_boundary_recognized = has_authority_boundary_check(evidence)

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

    # Check prior report independence blocking
    if requested_protocol:
        blocks, block_reason = prior_report_blocks_independence(evidence_input, requested_protocol)
        if blocks:
            return fail_claim_gate(
                block_reason,
                [block_reason],
                requested_kind
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
            # Check if any script claims independence but is missing explicit official=false
            missing_official = []
            for s in executed:
                is_independent = (
                    s.get("scope_class") == "independent_reproduction"
                    or s.get("independent", False)
                )
                if is_independent and s.get("official") is not False and "official" not in s:
                    missing_official.append(s.get("path", s.get("script_name", "unknown")))

            if missing_official:
                downgrades.append({
                    "from": "V4+",
                    "to": "V4",
                    "reason": f"V4+ requires independent tool with explicit 'official: false'. Script(s) claiming independence but missing 'official' field: {', '.join(missing_official)}. Add '\"official\": false' to these script entries."
                })
            else:
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

    # HG-001: If technical claim requested but no authority boundary, force downgrade
    if technical_claim_requested(evidence_input) and not authority_boundary_recognized:
        missing.append("authority_boundary_recognition")
        downgrades.append({
            "from": requested_protocol or "requested technical verification",
            "to": "V0",
            "reason": "V2+ technical verification requires explicit authority boundary recognition: Bitcoin Originals remain final authority; mirrors/reports/echoes are non-amending."
        })

    # Filter out no-op downgrades (from == to)
    downgrades = [d for d in downgrades if d.get("from") != d.get("to")]

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
                 h.get("expected", "").lower() == h.get("computed", "").lower() and
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
    from datetime import datetime, timezone
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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

    # Determine protocol scope label to prevent minimal claims being mistaken for strong/full
    protocol_scope = "full"
    protocol_label = allowed_protocol
    if allowed_protocol == "V2" and b_level == "B1" and d_level == "D0" and c_level == "C0":
        protocol_scope = "minimal"
        protocol_label = "V2 (minimal; Bitcoin Originals B1 only)"
    elif allowed_protocol == "V3":
        exactly_one_valid_hash_for_label = (
            len([h for h in hashes if
                 SHA256_RE.match(h.get("expected", "")) and
                 SHA256_RE.match(h.get("computed", "")) and
                 h.get("match") is True and
                 h.get("expected", "").lower() == h.get("computed", "").lower() and
                 h.get("expected_hash_source") and
                 h.get("expected_hash_authority_class", "unknown") != "unknown"
            ]) == 1
        )
        stronger_hash_coverage_for_label = (
            level_at_least(D_LEVELS, d_level, "D2") and
            level_at_least(C_LEVELS, c_level, "C2")
        )
        if exactly_one_valid_hash_for_label and not stronger_hash_coverage_for_label:
            protocol_scope = "minimal"
            protocol_label = "V3 (minimal; one valid declared hash computed)"
    elif allowed_protocol == "V4+":
        # V4+ minimal: at least one independent reproduction but not all three domains
        independent_any = (
            level_at_least(B_LEVELS, b_level, "B3") or
            level_at_least(D_LEVELS, d_level, "D3") or
            level_at_least(C_LEVELS, c_level, "C3")
        )
        independent_all_three = (
            level_at_least(B_LEVELS, b_level, "B3") and
            level_at_least(D_LEVELS, d_level, "D3") and
            level_at_least(C_LEVELS, c_level, "C3")
        )
        if independent_any and not independent_all_three:
            protocol_scope = "minimal"
            protocol_label = "V4+ (minimal independent reproduction)"

    # Derive verification_scope_label
    def _derive_scope_label(proto, comp_levels, non_blocking):
        if proto == "V0":
            return "read_only_orientation"
        elif proto == "V1":
            return "authority_boundary_recognition"
        elif proto == "V2":
            return "single_reference_check"
        elif proto == "V3":
            hashes = evidence.get("hashes", [])
            if len(hashes) <= 1:
                return "single_hash_verification"
            return "multi_hash_verification"
        elif proto == "V4":
            if non_blocking:
                return "official_script_audit_with_limitations"
            return "official_script_audit"
        elif proto == "V4+":
            hashes = evidence.get("hashes", [])
            if len(hashes) <= 1:
                return "independent_single_artifact_reproduction"
            return "independent_multi_artifact_reproduction"
        elif proto == "V5":
            return "full_public_digital_verification"
        elif proto in ("V6", "V7", "V8"):
            return "full_protocol_profile_verification"
        return "legacy_unlabeled"

    scope_label = _derive_scope_label(allowed_protocol, component_levels, all_non_blocking)

    result = {
        "schema": "trinityaccord.claim-gate-output.v1",
        "input": str(input_path),
        "status": status,
        "allowed_protocol_level": allowed_protocol,
        "allowed_protocol_label": protocol_label,
        "allowed_protocol_scope": protocol_scope,
        "allowed_component_levels": component_levels,
        "verification_scope_label": scope_label,
        "authority_boundary_recognized": authority_boundary_recognized,
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
        print("Usage: python3 scripts/claim_gate.py evidence-input.json [--output out.json] [--mode template-for-v0-v5]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    mode = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    # Auto-detect mode from payload if not specified
    if mode is None:
        try:
            with open(input_path) as f:
                payload = json.load(f)
            if payload.get('requested_archive_kind') == 'agent_declared_verification_archive':
                mode = 'template-for-v0-v5'
        except Exception:
            pass

    if mode == 'template-for-v0-v5':
        with open(input_path) as f:
            payload = json.load(f)
        result = evaluate_template_for_v0_v5(payload)
    else:
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
