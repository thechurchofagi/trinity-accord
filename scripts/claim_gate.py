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
B_LEVELS = ["B0", "B1", "B2", "B3", "B4", "B5", "B6"]
D_LEVELS = ["D0", "D1", "D2", "D4", "D5"]
T_LEVELS = ["T0", "T1", "T2", "T3", "T5", "T8"]
C_LEVELS = ["C0", "C2", "C3", "C3R", "C5"]
N_LEVELS = ["N0", "N2", "N4", "N7"]
P_LEVELS = ["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8", "P9"]

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

    has_valid_hash = False
    for h in hashes:
        if (SHA256_RE.match(h.get("expected", "")) and
            SHA256_RE.match(h.get("computed", "")) and
            h.get("match") is True and
            h.get("expected_hash_source") and
            h.get("expected_hash_authority_class", "unknown") != "unknown"):
            has_valid_hash = True
            break

    if has_valid_hash:
        return "D2"
    if digital_checks or repo_checks:
        return "D1"
    return "D0"


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

        if full_recovery and samples_recovered >= 175:
            candidate = "C5"
        elif samples_recovered >= 2:
            candidate = "C3"
        elif has_package_hash:
            candidate = "C2"
        else:
            candidate = "C0"

        if level_index(C_LEVELS, candidate) > level_index(C_LEVELS, max_level):
            max_level = candidate

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
        else:
            candidate = "P0"

        if level_index(P_LEVELS, candidate) > level_index(P_LEVELS, max_level):
            max_level = candidate

    return max_level


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

    # V1: authority boundary preserved
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

    # V4: script audit with proper scope
    if executed_scripts:
        all_have_command = all(s.get("command") for s in executed_scripts)
        all_have_env = all(s.get("environment") for s in executed_scripts)
        all_have_exit = all(s.get("exit_code") is not None for s in executed_scripts)
        all_have_output = all(s.get("stdout_summary") for s in executed_scripts)

        if all_have_command and all_have_env and all_have_exit and all_have_output:
            max_allowed = "V4"

            # V4+: requires independent tool/implementation
            if has_independent and not official_only:
                max_allowed = "V4+"

    # V5+: requires specific high component levels
    if (level_at_least(B_LEVELS, b_level, "B2") and
        level_at_least(D_LEVELS, d_level, "D5") and
        level_at_least(T_LEVELS, t_level, "T3") and
        level_at_least(C_LEVELS, c_level, "C5") and
        level_at_least(P_LEVELS, p_level, "P1")):
        max_allowed = "V5"

    # V6: P4+ with live + nonce (independent of V5 requirements)
    if level_at_least(P_LEVELS, p_level, "P4"):
        for check in evidence.get("physical_checks", []):
            if (check.get("level_evidence_type") == "live_remote" and
                check.get("nonce_challenge") is not None):
                if level_index(PROTOCOL_LEVELS, "V6") > level_index(PROTOCOL_LEVELS, max_allowed):
                    max_allowed = "V6"
                break

    # V7: P5+ with onsite/custody (independent path)
    if level_at_least(P_LEVELS, p_level, "P5"):
        for check in evidence.get("physical_checks", []):
            if check.get("level_evidence_type") == "onsite" and check.get("custody_log"):
                if level_index(PROTOCOL_LEVELS, "V7") > level_index(PROTOCOL_LEVELS, max_allowed):
                    max_allowed = "V7"
                break

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
    p_level = derive_p_level(evidence)

    # Determine requested protocol level
    # Default to None (no specific level requested); only set if agent explicitly claims one
    sorted_levels = sorted(PROTOCOL_LEVELS, key=len, reverse=True)
    requested_protocol = None
    for claim in claims_requested:
        claim_stripped = claim.strip().upper()
        for pl in sorted_levels:
            if claim_stripped == pl or claim_stripped.startswith(pl + " ") or claim_stripped == pl.upper():
                requested_protocol = pl
                break
            # Fallback: case-insensitive substring match
            if pl.lower() in claim.lower():
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
        "physical_verification": p_level,
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
