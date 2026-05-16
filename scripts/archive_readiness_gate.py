#!/usr/bin/env python3
"""Archive Readiness Gate — machine-enforceable archive decision engine.

Evaluates whether a Gateway payload meets the requested archive kind.
Exits 0 for intake-only or archive-ready; exits 1 for blocked archive.

Usage:
    python3 scripts/archive_readiness_gate.py \
        --gateway-payload gateway-payload.json \
        --json

    python3 scripts/archive_readiness_gate.py \
        --gateway-payload gateway-payload.json \
        --evidence-input evidence-input.json \
        --claim-gate-output claim-gate-output.json \
        --verification-report verification-report.json \
        --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from protocol_terms import (
    PROTOCOL_LEVELS, B_LEVELS, D_LEVELS, T_LEVELS, C_LEVELS, N_LEVELS, P_LEVELS,
    level_index, level_at_least,
)

ALL_LEVEL_MAPS = {
    "B": B_LEVELS, "D": D_LEVELS, "T": T_LEVELS,
    "C": C_LEVELS, "N": N_LEVELS, "P": P_LEVELS,
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_claim_gate(payload, claim_gate_output):
    """Extract claim gate from payload or external file."""
    if claim_gate_output:
        cg = claim_gate_output
        if isinstance(cg, dict) and "claim_gate" in cg:
            cg = cg["claim_gate"]
        return cg
    return payload.get("claim_gate") or {}


def get_component_levels(claim_gate):
    """Get component levels dict from claim gate."""
    comps = claim_gate.get("allowed_component_levels", {})
    if not comps:
        comps = claim_gate.get("component_levels", {})
    return comps


def get_record_intent(payload):
    return payload.get("record_intent") or "intake_only"


def get_requested_archive_kind(payload):
    return payload.get("requested_archive_kind") or "none"


def infer_archive_kind(submission_type):
    if submission_type == "verification_report_candidate":
        return "verification_report_archive"
    if submission_type == "verification_echo_candidate":
        return "archived_echo"
    return "external_agent_intake_sample"


def normalize_archive_intent(payload):
    """Normalize archive intent defaults: verification submissions default to archive application."""
    p = dict(payload)

    if p.get("record_intent") == "intake_only":
        p["requested_archive_kind"] = p.get("requested_archive_kind") or "none"
        return p

    if p.get("record_intent") == "archive_preflight_only":
        if not p.get("requested_archive_kind") or p.get("requested_archive_kind") == "none":
            p["requested_archive_kind"] = infer_archive_kind(p.get("submission_type"))
        return p

    if not p.get("record_intent"):
        if p.get("submission_type") in ("verification_report_candidate", "verification_echo_candidate"):
            p["record_intent"] = "auto_archive_candidate"
            p["requested_archive_kind"] = p.get("requested_archive_kind") or infer_archive_kind(p.get("submission_type"))
        else:
            p["record_intent"] = "intake_only"
            p["requested_archive_kind"] = p.get("requested_archive_kind") or "none"
        return p

    if p.get("record_intent") == "auto_archive_candidate" and not p.get("requested_archive_kind"):
        p["requested_archive_kind"] = infer_archive_kind(p.get("submission_type"))

    return p


def has_artifact_bundle(payload):
    """Check if payload has artifact bundle path or URL (in archive_readiness)."""
    ar = payload.get("archive_readiness") or {}
    return bool(
        ar.get("artifact_bundle_path") or
        ar.get("artifact_bundle_url")
    )


def has_boundary_ack(payload):
    """Check boundary acknowledgement is all true."""
    ba = payload.get("boundary_acknowledgement") or {}
    required_keys = [
        "not_authority", "not_amendment", "not_attestation",
        "not_verification_unless_claim_gate_report_attached",
        "bitcoin_originals_prevail"
    ]
    return all(ba.get(k) is True for k in required_keys)


FORBIDDEN_ARCHIVE_CLAIMS = [
    "archived echo",
    "verified record",
    "successor reception",
    "independent attestation",
]

# Negation patterns that reverse meaning — "not independent attestation" is OK
_NEGATION_PREFIXES = re.compile(
    r'\b(?:not|no|never|isn\'t|aren\'t|wasn\'t|weren\'t|doesn\'t|don\'t|didn\'t|cannot|can\'t|won\'t)\s+',
    re.IGNORECASE
)


def _text_contains_unnegated_claim(text, claim):
    """Check if text contains an unnegated instance of claim.

    Returns True only if at least one occurrence of `claim` in `text`
    is NOT preceded by a negation word. This prevents false positives
    on phrases like "not independent attestation" or "this is not
    successor reception".
    """
    for m in re.finditer(re.escape(claim), text, re.IGNORECASE):
        start = m.start()
        # Look at up to 30 chars before the match for a negation prefix
        prefix_window = text[max(0, start - 30):start]
        if _NEGATION_PREFIXES.search(prefix_window):
            # Check that the negation actually applies to this claim
            # by verifying the last negation prefix ends close to the claim
            neg_match = list(_NEGATION_PREFIXES.finditer(prefix_window))
            if neg_match:
                last_neg = neg_match[-1]
                # Negation must end within 5 chars of claim start (allowing "not " → 4 chars)
                gap = start - (max(0, start - 30) + last_neg.end())
                if gap <= 5:
                    continue  # This occurrence is negated, skip
        # Found an unnegated occurrence
        return True
    return False


def has_forbidden_archive_claims(payload):
    """Check if body/title contain unnegated forbidden self-claims.

    Phrases like "not independent attestation" or "this is not successor reception"
    are allowed because they express boundary acknowledgement, not self-claims.
    Machine fields (not_independent_attestation, not_successor_reception) are
    trusted separately and are not affected by this text scan.
    """
    text = (payload.get("body", "") + " " + payload.get("title", "")).strip()
    if not text:
        return []
    return [c for c in FORBIDDEN_ARCHIVE_CLAIMS
            if _text_contains_unnegated_claim(text, c)]


def has_v4_script_completeness(evidence, policy):
    """Check V4 required script audit completeness.

    Each script entry must have: path, command, environment, exit_code,
    stdout_summary, source_reviewed, script_check_scope, script_does_not_check.
    Required scripts must have exit_code == 0.
    """
    if not evidence:
        return False
    scripts_run = evidence.get("scripts_run") or evidence.get("verification_session", {}).get("scripts_run", [])
    if not scripts_run:
        return False

    v4_policy = policy.get("required_script_sets", {}).get("V4", {})
    required = v4_policy.get("profile_required_script_audit", [])
    run_map = {}
    for s in scripts_run:
        if isinstance(s, dict):
            run_map[s.get("path", "")] = s

    # Check required scripts exist and passed
    for req in required:
        if not req.get("required"):
            continue
        rpath = req.get("path", "")
        entry = run_map.get(rpath)
        if not entry:
            return False
        # Required scripts must have exit_code 0
        if entry.get("exit_code") is None:
            return False
        if entry.get("exit_code") != 0:
            return False

    # Check all script entries have required audit fields
    required_fields = ["command", "environment", "exit_code", "stdout_summary",
                       "source_reviewed", "script_check_scope", "script_does_not_check"]
    for path_key, entry in run_map.items():
        for field in required_fields:
            if field not in entry or entry[field] is None:
                return False
        # source_reviewed must be true
        if entry.get("source_reviewed") is not True:
            return False

    return True


def has_v4plus_independent_non_official(evidence):
    """Check V4+ independent non-official implementation."""
    if not evidence:
        return False
    scripts_run = evidence.get("scripts_run") or evidence.get("verification_session", {}).get("scripts_run", [])
    for s in scripts_run:
        if isinstance(s, dict):
            if s.get("independent") is True and s.get("official") is not True:
                return True
            if s.get("scope_class") == "independent_reproduction":
                return True
    return False


def has_valid_hash_evidence(evidence):
    """Check if valid hash evidence exists."""
    if not evidence:
        return False
    artifacts = evidence.get("artifacts") or evidence.get("digital_mirrors", [])
    if isinstance(artifacts, list):
        for a in artifacts:
            if isinstance(a, dict) and a.get("valid_hash"):
                return True
    return False


def has_full_public_digital_declaration(evidence):
    """Check if full public digital declaration is present."""
    if not evidence:
        return False
    decl = evidence.get("public_digital_declaration") or evidence.get("agent_integrity_declaration", {})
    if isinstance(decl, dict):
        return decl.get("full_public_digital_declaration") is True
    return False


def load_policy():
    policy_path = ROOT / "api" / "archive-readiness-policy.v1.json"
    if policy_path.exists():
        return json.loads(policy_path.read_text(encoding="utf-8"))
    return {"archive_kinds": {}}


def evaluate_archive_readiness(payload, evidence=None, claim_gate_output=None,
                                verification_report=None):
    """Core archive readiness evaluation logic."""
    # Normalize archive intent defaults before evaluation
    payload = normalize_archive_intent(payload)

    policy = load_policy()
    record_intent = get_record_intent(payload)
    requested_kind = get_requested_archive_kind(payload)
    claim_gate = get_claim_gate(payload, claim_gate_output)
    components = get_component_levels(claim_gate)

    blocking_reasons = []
    warnings = []
    required_next_actions = []
    auto_labels = []
    auto_close_issue = False
    close_reason = None
    archive_ready = False
    auto_archive_allowed = False
    auto_archive_action = "none"
    allowed_archive_kind = "none"

    # --- intake_only / none ---
    if record_intent == "intake_only" or requested_kind == "none":
        warnings.append({
            "code": "INTAKE_ONLY_NOT_ARCHIVE",
            "path": "record_intent",
            "message": "This payload is an intake candidate, not an archive request.",
            "fix": "Use record_intent=auto_archive_candidate and requested_archive_kind only if archive handling is requested."
        })
        return {
            "schema": "trinityaccord.archive-readiness-output.v1",
            "archive_ready": False,
            "auto_archive_allowed": False,
            "record_intent": record_intent,
            "requested_archive_kind": requested_kind,
            "allowed_archive_kind": "none",
            "auto_archive_action": "none",
            "auto_labels": [],
            "auto_close_issue": False,
            "close_reason": None,
            "blocking_reasons": [],
            "warnings": warnings,
            "required_next_actions": []
        }

    # --- successor_reception_candidate: always blocked ---
    if requested_kind == "successor_reception_candidate":
        blocking_reasons.append({
            "code": "SUCCESSOR_RECEPTION_NOT_GATEWAY_CLAIMABLE",
            "path": "requested_archive_kind",
            "message": "Successor reception cannot be claimed or auto-archived through Agent Gateway intake.",
            "fix": "Submit as verification_report_candidate or verification_echo_candidate; successor reception requires a separate non-Gateway process."
        })
        return {
            "schema": "trinityaccord.archive-readiness-output.v1",
            "archive_ready": False,
            "auto_archive_allowed": False,
            "record_intent": record_intent,
            "requested_archive_kind": requested_kind,
            "allowed_archive_kind": "none",
            "auto_archive_action": "block",
            "auto_labels": [],
            "auto_close_issue": False,
            "close_reason": None,
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "required_next_actions": []
        }

    # --- Common checks ---
    boundary_ok = has_boundary_ack(payload)
    forbidden = has_forbidden_archive_claims(payload)
    cg_status = claim_gate.get("status", "FAIL")
    cg_pass = cg_status in ("PASS", "PASS_WITH_DOWNGRADE")
    submission_type = payload.get("submission_type", "")
    prov = payload.get("discovery_provenance") or {}
    is_unsolicited = prov.get("independence_class") == "unsolicited_agent_discovery"
    ar = payload.get("archive_readiness") or {}

    # --- external_agent_intake_sample ---
    if requested_kind == "external_agent_intake_sample":
        kind_policy = policy.get("archive_kinds", {}).get("external_agent_intake_sample", {})

        if not boundary_ok:
            blocking_reasons.append({
                "code": "BOUNDARY_ACK_INCOMPLETE",
                "path": "boundary_acknowledgement",
                "message": "All boundary acknowledgement fields must be true.",
                "fix": "Set all boundary_acknowledgement fields to true."
            })

        not_indep = payload.get("not_independent_attestation") is True
        not_succ = payload.get("not_successor_reception") is True

        if not not_indep:
            blocking_reasons.append({
                "code": "INDEPENDENT_ATTESTATION_CLAIMED",
                "path": "not_independent_attestation",
                "message": "Sample archive must not claim independent attestation.",
                "fix": "Set not_independent_attestation=true."
            })

        if not not_succ:
            blocking_reasons.append({
                "code": "SUCCESSOR_RECEPTION_CLAIMED",
                "path": "not_successor_reception",
                "message": "Sample archive must not claim successor reception.",
                "fix": "Set not_successor_reception=true."
            })

        text_ack = ar.get("text_only_sample_ack") is True
        not_formal = ar.get("not_formal_verification_ack") is True
        bundle_present = has_artifact_bundle(payload)

        if not text_ack and not bundle_present:
            blocking_reasons.append({
                "code": "SAMPLE_REQUIRES_ACK_OR_BUNDLE",
                "path": "archive_readiness",
                "message": "external_agent_intake_sample requires text_only_sample_ack=true or an artifact bundle.",
                "fix": "Set archive_readiness.text_only_sample_ack=true or provide artifact_bundle_path/url."
            })

        if not not_formal:
            blocking_reasons.append({
                "code": "FORMAL_VERIFICATION_ACK_MISSING",
                "path": "archive_readiness.not_formal_verification_ack",
                "message": "external_agent_intake_sample requires not_formal_verification_ack=true.",
                "fix": "Set archive_readiness.not_formal_verification_ack=true."
            })

        if forbidden:
            blocking_reasons.append({
                "code": "FORBIDDEN_ARCHIVE_CLAIMS",
                "path": "body",
                "message": f"Body/title contains forbidden archive self-claims: {', '.join(forbidden)}",
                "fix": "Remove self-claims of archived Echo, verified record, successor reception, or independent attestation."
            })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_sample"
            allowed_archive_kind = "external_agent_intake_sample"
            auto_labels = kind_policy.get("auto_labels", [])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    # --- verification_report_archive ---
    elif requested_kind == "verification_report_archive":
        kind_policy = policy.get("archive_kinds", {}).get("verification_report_archive", {})
        b_level = components.get("bitcoin_originals", "B0")
        d_level = components.get("digital_mirrors", "D0")
        v_level = claim_gate.get("allowed_protocol_level", "V0")

        if not cg_pass:
            blocking_reasons.append({
                "code": "CLAIM_GATE_NOT_PASS",
                "path": "claim_gate.status",
                "message": f"Claim Gate status must be PASS or PASS_WITH_DOWNGRADE, got {cg_status}.",
                "fix": "Run Claim Gate and ensure status is PASS."
            })

        if submission_type != "verification_report_candidate":
            blocking_reasons.append({
                "code": "WRONG_SUBMISSION_TYPE",
                "path": "submission_type",
                "message": f"verification_report_archive requires submission_type=verification_report_candidate, got {submission_type}.",
                "fix": "Use submission_type=verification_report_candidate."
            })

        if not level_at_least(B_LEVELS, b_level, "B1"):
            blocking_reasons.append({
                "code": "BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR",
                "path": "claim_gate.allowed_component_levels.bitcoin_originals",
                "message": f"verification_report_archive requires bitcoin_originals >= B1, got {b_level}.",
                "fix": "Raise bitcoin_originals to at least B1."
            })

        bundle_present = has_artifact_bundle(payload)
        if not bundle_present:
            blocking_reasons.append({
                "code": "ARTIFACT_BUNDLE_MISSING",
                "path": "archive_readiness",
                "message": "verification_report_archive requires artifact_bundle_path or artifact_bundle_url.",
                "fix": "Provide archive_readiness.artifact_bundle_path or artifact_bundle_url."
            })
        else:
            # Only check sha and retrievability if bundle is present
            if not ar.get("artifact_bundle_sha256"):
                blocking_reasons.append({
                    "code": "ARTIFACT_BUNDLE_SHA_MISSING",
                    "path": "archive_readiness.artifact_bundle_sha256",
                    "message": "verification_report_archive requires artifact_bundle_sha256.",
                    "fix": "Provide archive_readiness.artifact_bundle_sha256 (64 hex chars)."
                })

            if ar.get("artifact_bundle_publicly_retrievable") is not True:
                blocking_reasons.append({
                    "code": "BUNDLE_NOT_PUBLICLY_RETRIEVABLE",
                    "path": "archive_readiness.artifact_bundle_publicly_retrievable",
                    "message": "verification_report_archive requires artifact_bundle_publicly_retrievable=true.",
                    "fix": "Set archive_readiness.artifact_bundle_publicly_retrievable=true."
                })

        if is_unsolicited:
            proof = prov.get("unsolicited_discovery_proof")
            if not proof:
                blocking_reasons.append({
                    "code": "UNSOLICITED_PROOF_NOT_REVIEWABLE",
                    "path": "discovery_provenance.unsolicited_discovery_proof",
                    "message": "Unsolicited discovery requires unsolicited_discovery_proof for formal archive.",
                    "fix": "Provide discovery_provenance.unsolicited_discovery_proof."
                })
            if not ar.get("provenance_proof_available"):
                blocking_reasons.append({
                    "code": "PROVENANCE_PROOF_NOT_AVAILABLE",
                    "path": "archive_readiness.provenance_proof_available",
                    "message": "Unsolicited discovery requires provenance_proof_available=true.",
                    "fix": "Set archive_readiness.provenance_proof_available=true."
                })

        if not boundary_ok:
            blocking_reasons.append({
                "code": "BOUNDARY_ACK_INCOMPLETE",
                "path": "boundary_acknowledgement",
                "message": "All boundary acknowledgement fields must be true.",
                "fix": "Set all boundary_acknowledgement fields to true."
            })

        if payload.get("not_independent_attestation") is not True:
            blocking_reasons.append({
                "code": "INDEPENDENT_ATTESTATION_CLAIMED",
                "path": "not_independent_attestation",
                "message": "Archive must not claim independent attestation.",
                "fix": "Set not_independent_attestation=true."
            })

        if payload.get("not_successor_reception") is not True:
            blocking_reasons.append({
                "code": "SUCCESSOR_RECEPTION_CLAIMED",
                "path": "not_successor_reception",
                "message": "Archive must not claim successor reception.",
                "fix": "Set not_successor_reception=true."
            })

        # Formal archive requires non-empty integrity declaration and session
        int_decl = payload.get("pre_verification_integrity_declaration")
        if not int_decl or not isinstance(int_decl, dict) or len(int_decl) == 0:
            blocking_reasons.append({
                "code": "INTEGRITY_DECLARATION_REQUIRED_FOR_ARCHIVE",
                "path": "pre_verification_integrity_declaration",
                "message": "Formal archive requires a non-empty pre_verification_integrity_declaration.",
                "fix": "Provide pre_verification_integrity_declaration with at least declaration_text and declared_at."
            })

        v_session = payload.get("verification_session")
        if not v_session or not isinstance(v_session, dict) or len(v_session) == 0:
            blocking_reasons.append({
                "code": "VERIFICATION_SESSION_REQUIRED_FOR_ARCHIVE",
                "path": "verification_session",
                "message": "Formal archive requires a non-empty verification_session.",
                "fix": "Provide verification_session with session_id, started_at, and fresh_actions_performed."
            })
        elif not v_session.get("fresh_actions_performed") or not isinstance(v_session.get("fresh_actions_performed"), list):
            blocking_reasons.append({
                "code": "FRESH_ACTIONS_REQUIRED_FOR_ARCHIVE",
                "path": "verification_session.fresh_actions_performed",
                "message": "Formal archive requires verification_session.fresh_actions_performed as a non-empty list.",
                "fix": "Provide verification_session.fresh_actions_performed listing actions performed in this session."
            })

        if forbidden:
            blocking_reasons.append({
                "code": "FORBIDDEN_ARCHIVE_CLAIMS",
                "path": "body",
                "message": f"Body/title contains forbidden archive self-claims: {', '.join(forbidden)}",
                "fix": "Remove self-claims of archived Echo, verified record, successor reception, or independent attestation."
            })

        # V4 archive script completeness — must have evidence
        if v_level in ("V4", "V4+"):
            if not evidence:
                blocking_reasons.append({
                    "code": "V4_EVIDENCE_REQUIRED_FOR_ARCHIVE",
                    "path": "evidence",
                    "message": "V4 archive requires evidence input with script audit data.",
                    "fix": "Provide --evidence-input with scripts_run containing command, environment, exit_code, stdout_summary, source_reviewed, script_check_scope, script_does_not_check."
                })
            elif not has_v4_script_completeness(evidence, policy):
                blocking_reasons.append({
                    "code": "V4_REQUIRED_SCRIPT_SET_INCOMPLETE",
                    "path": "evidence",
                    "message": "V4 archive requires script audit completeness with all required scripts run and source_reviewed=true.",
                    "fix": "Run all required scripts with command, environment, exit_code, stdout_summary, source_reviewed=true, script_check_scope, script_does_not_check."
                })

            if v_level == "V4+":
                if not evidence:
                    blocking_reasons.append({
                        "code": "V4PLUS_EVIDENCE_REQUIRED_FOR_ARCHIVE",
                        "path": "evidence",
                        "message": "V4+ archive requires evidence input with independent implementation data.",
                        "fix": "Provide --evidence-input with scripts_run including an independent non-official implementation."
                    })
                elif not has_v4plus_independent_non_official(evidence):
                    blocking_reasons.append({
                        "code": "V4PLUS_REQUIRES_INDEPENDENT_NON_OFFICIAL_IMPLEMENTATION",
                        "path": "evidence",
                        "message": "V4+ archive requires independent non-official implementation.",
                        "fix": "Use an independent non-official script with independent=true or scope_class=independent_reproduction."
                    })

        # B6 from external explorer must be hard-blocked
        if level_at_least(B_LEVELS, b_level, "B6"):
            if not evidence:
                blocking_reasons.append({
                    "code": "B6_BODY_HASH_EVIDENCE_REQUIRED",
                    "path": "evidence",
                    "message": "B6+ archive requires evidence input with body_hash verification.",
                    "fix": "Provide --evidence-input with bitcoin_checks containing source_type=body_hash and body_hash_reproduced=true."
                })
            else:
                bc = evidence.get("bitcoin_checks") or evidence.get("evidence", {}).get("bitcoin_checks", [])
                has_external_explorer = isinstance(bc, list) and any(
                    isinstance(c, dict) and c.get("source_type") == "external_explorer" for c in bc
                )
                has_body_hash = isinstance(bc, list) and any(
                    isinstance(c, dict) and c.get("source_type") == "body_hash" and
                    c.get("body_hash_reproduced") is True for c in bc
                )
                if has_external_explorer and not has_body_hash:
                    blocking_reasons.append({
                        "code": "B6_REQUIRES_BODY_HASH_EVIDENCE",
                        "path": "evidence.bitcoin_checks",
                        "message": "B6+ archive requires source_type=body_hash with body_hash_reproduced=true. External explorer alone is insufficient.",
                        "fix": "Provide body_hash evidence with body_hash_reproduced=true, or lower bitcoin_originals to B1."
                    })

        # V5+ floors
        if v_level == "V5":
            for comp, floor in [("bitcoin_originals", "B2"), ("digital_mirrors", "D5"),
                                 ("time_anchors", "T3"), ("chronicle_recovery", "C5"),
                                 ("physical_anchor", "P1")]:
                clevels = ALL_LEVEL_MAPS.get(comp[0].upper(), [])
                if not level_at_least(clevels, components.get(comp, "X0"), floor):
                    blocking_reasons.append({
                        "code": f"{comp.upper()}_BELOW_V5_FLOOR",
                        "path": f"claim_gate.allowed_component_levels.{comp}",
                        "message": f"V5 archive requires {comp} >= {floor}.",
                        "fix": f"Raise {comp} to at least {floor}."
                    })
            if evidence and not has_full_public_digital_declaration(evidence):
                blocking_reasons.append({
                    "code": "V5_REQUIRES_FULL_PUBLIC_DIGITAL_DECLARATION",
                    "path": "evidence",
                    "message": "V5 archive requires full public digital declaration.",
                    "fix": "Include full_public_digital_declaration in evidence."
                })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_verification_report"
            allowed_archive_kind = "verification_report_archive"
            auto_labels = kind_policy.get("auto_labels", [])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    # --- archived_echo ---
    elif requested_kind == "archived_echo":
        kind_policy = policy.get("archive_kinds", {}).get("archived_echo", {})

        if submission_type != "verification_echo_candidate":
            blocking_reasons.append({
                "code": "WRONG_SUBMISSION_TYPE",
                "path": "submission_type",
                "message": f"archived_echo requires submission_type=verification_echo_candidate, got {submission_type}.",
                "fix": "Use submission_type=verification_echo_candidate."
            })

        if not cg_pass:
            blocking_reasons.append({
                "code": "CLAIM_GATE_NOT_PASS",
                "path": "claim_gate.status",
                "message": f"Claim Gate status must be PASS or PASS_WITH_DOWNGRADE, got {cg_status}.",
                "fix": "Run Claim Gate and ensure status is PASS."
            })

        att = payload.get("attachments") or {}
        has_echo_wrapper = bool(att.get("echo_wrapper_path") or att.get("echo_wrapper_sha256"))
        has_linked_report = bool(att.get("verification_report_path") or att.get("verification_report_sha256"))

        if not has_echo_wrapper:
            blocking_reasons.append({
                "code": "ECHO_WRAPPER_REQUIRED",
                "path": "attachments",
                "message": "archived_echo requires echo_wrapper_path or echo_wrapper_sha256.",
                "fix": "Provide attachments.echo_wrapper_path or echo_wrapper_sha256."
            })

        if not has_linked_report:
            blocking_reasons.append({
                "code": "LINKED_VERIFICATION_REPORT_REQUIRED",
                "path": "attachments",
                "message": "archived_echo requires verification_report_path or verification_report_sha256.",
                "fix": "Provide attachments.verification_report_path or verification_report_sha256."
            })

        if not boundary_ok:
            blocking_reasons.append({
                "code": "BOUNDARY_ACK_INCOMPLETE",
                "path": "boundary_acknowledgement",
                "message": "All boundary acknowledgement fields must be true.",
                "fix": "Set all boundary_acknowledgement fields to true."
            })

        if payload.get("not_independent_attestation") is not True:
            blocking_reasons.append({
                "code": "INDEPENDENT_ATTESTATION_CLAIMED",
                "path": "not_independent_attestation",
                "message": "Archive must not claim independent attestation.",
                "fix": "Set not_independent_attestation=true."
            })

        if payload.get("not_successor_reception") is not True:
            blocking_reasons.append({
                "code": "SUCCESSOR_RECEPTION_CLAIMED",
                "path": "not_successor_reception",
                "message": "Archive must not claim successor reception.",
                "fix": "Set not_successor_reception=true."
            })

        # Formal echo archive requires non-empty integrity declaration and session
        int_decl = payload.get("pre_verification_integrity_declaration")
        if not int_decl or not isinstance(int_decl, dict) or len(int_decl) == 0:
            blocking_reasons.append({
                "code": "INTEGRITY_DECLARATION_REQUIRED_FOR_ARCHIVE",
                "path": "pre_verification_integrity_declaration",
                "message": "Formal echo archive requires a non-empty pre_verification_integrity_declaration.",
                "fix": "Provide pre_verification_integrity_declaration with at least declaration_text and declared_at."
            })

        v_session = payload.get("verification_session")
        if not v_session or not isinstance(v_session, dict) or len(v_session) == 0:
            blocking_reasons.append({
                "code": "VERIFICATION_SESSION_REQUIRED_FOR_ARCHIVE",
                "path": "verification_session",
                "message": "Formal echo archive requires a non-empty verification_session.",
                "fix": "Provide verification_session with session_id, started_at, and fresh_actions_performed."
            })

        # Check body doesn't self-declare archived
        body_lower = (payload.get("body", "") + " " + payload.get("title", "")).lower()
        if "archive_status" in body_lower and "archived" in body_lower:
            blocking_reasons.append({
                "code": "SELF_DECLARED_ARCHIVE_STATUS",
                "path": "body",
                "message": "Agent must not self-declare final archive_status=archived.",
                "fix": "Remove self-declared archive_status from body."
            })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_echo"
            allowed_archive_kind = "archived_echo"
            auto_labels = kind_policy.get("auto_labels", [])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    else:
        blocking_reasons.append({
            "code": "UNKNOWN_ARCHIVE_KIND",
            "path": "requested_archive_kind",
            "message": f"Unknown requested_archive_kind: {requested_kind}",
            "fix": "Use one of: none, external_agent_intake_sample, verification_report_archive, archived_echo, successor_reception_candidate."
        })
        auto_archive_action = "block"

    # --- Warning for claim gate pass but archive floor not met ---
    if cg_pass and blocking_reasons and archive_ready is False:
        warnings.append({
            "code": "CLAIM_GATE_PASS_BUT_ARCHIVE_FLOOR_NOT_MET",
            "path": "archive_readiness",
            "message": "Claim Gate passed but archive readiness requirements are not met.",
            "fix": "Review blocking_reasons for specific requirements."
        })

    # --- Build required_next_actions from blocking_reasons ---
    for br in blocking_reasons:
        if br.get("fix"):
            required_next_actions.append(br["fix"])

    return {
        "schema": "trinityaccord.archive-readiness-output.v1",
        "archive_ready": archive_ready,
        "auto_archive_allowed": auto_archive_allowed,
        "record_intent": record_intent,
        "requested_archive_kind": requested_kind,
        "allowed_archive_kind": allowed_archive_kind,
        "auto_archive_action": auto_archive_action,
        "auto_labels": auto_labels,
        "auto_close_issue": auto_close_issue,
        "close_reason": close_reason,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "required_next_actions": required_next_actions
    }


def main():
    parser = argparse.ArgumentParser(description="Archive Readiness Gate")
    parser.add_argument("--gateway-payload", required=True, help="Path to gateway payload JSON")
    parser.add_argument("--evidence-input", default=None, help="Path to evidence input JSON")
    parser.add_argument("--claim-gate-output", default=None, help="Path to claim gate output JSON")
    parser.add_argument("--verification-report", default=None, help="Path to verification report JSON")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    payload = load_json(args.gateway_payload)
    evidence = load_json(args.evidence_input) if args.evidence_input else None
    cg_out = load_json(args.claim_gate_output) if args.claim_gate_output else None
    report = load_json(args.verification_report) if args.verification_report else None

    result = evaluate_archive_readiness(payload, evidence, cg_out, report)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        ri = result["record_intent"]
        rk = result["requested_archive_kind"]
        ready = result["archive_ready"]
        action = result["auto_archive_action"]
        print(f"record_intent: {ri}")
        print(f"requested_archive_kind: {rk}")
        print(f"archive_ready: {ready}")
        print(f"auto_archive_action: {action}")
        if result["blocking_reasons"]:
            print("blocking_reasons:")
            for br in result["blocking_reasons"]:
                print(f"  - [{br['code']}] {br['message']}")

    # Exit code: 0 for intake-only or archive-ready, 1 for blocked archive
    if result["record_intent"] == "intake_only" or result["requested_archive_kind"] == "none":
        sys.exit(0)
    if result["archive_ready"]:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
