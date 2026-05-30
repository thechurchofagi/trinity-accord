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
    level_index, level_at_least, V0_V5_LEVELS,
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


def _split_sentences(text):
    """Split text into sentences for per-sentence claim checking.

    Joins continuation lines before splitting: a newline followed by a
    lowercase letter (e.g. "attestation,\nauthority") is treated as a
    soft wrap within the same sentence, not a sentence boundary.
    """
    # Join continuation lines: newline + lowercase letter → single space
    text = re.sub(r'\n(?=[a-zà-ÿ])', ' ', text)
    return [s.strip() for s in re.split(r'(?<=[.!?。！？])\s+|\n+', text) if s.strip()]


def _text_contains_unnegated_claim(text, claim):
    """Check if text contains an unnegated instance of claim.

    Checks each sentence independently: a negated phrase like
    "not independent attestation" in one sentence does NOT exempt a positive
    claim "This is independent attestation" in another sentence.

    Handles coordinated lists: "does not create X, Y, or Z" negates all items
    even when the negation prefix is far from Z.
    Handles verb-mediated negation: "not create X" negates X.
    """
    sentences = _split_sentences(text)
    for sentence in sentences:
        for m in re.finditer(re.escape(claim), sentence, re.IGNORECASE):
            start = m.start()
            # Look back to the start of the sentence to catch long-range negation
            # e.g. "does not create verification level, attestation, or successor reception"
            prefix = sentence[:start]
            if not prefix:
                return True  # Claim at very start of sentence — not negated
            neg_matches = list(_NEGATION_PREFIXES.finditer(prefix))
            if neg_matches:
                last_neg = neg_matches[-1]
                gap = start - last_neg.end()
                # Direct negation: "not successor reception" (gap ≤ 5)
                if gap <= 5:
                    continue
                between = sentence[last_neg.end():start]
                # Coordinated list negation: "not X, Y, or successor reception"
                if _is_coordinated_list(between):
                    continue
                # Verb-mediated negation: "not create X" or "not claim X"
                # If between is a short verb phrase (only words and spaces,
                # no sentence breaks), the negation verb transmits to the claim
                if _is_verb_phrase_gap(between):
                    continue
            return True  # Found unnegated occurrence in this sentence
    return False


def _is_verb_phrase_gap(text):
    """Check if text is a short verb phrase bridging negation to claim.

    Matches patterns like "create ", "claim ", "make any ", etc.
    Must be only words and spaces, no punctuation, and reasonably short.
    """
    stripped = text.strip()
    if not stripped:
        return True  # Empty gap = direct adjacency
    # Must be only alphabetic words and spaces (no punctuation, no commas)
    if not re.fullmatch(r'[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*', stripped):
        return False
    # Must be reasonably short (max ~3 words, ~30 chars)
    word_count = len(stripped.split())
    return word_count <= 4 and len(stripped) <= 30


def _is_coordinated_list(text):
    """Check if text looks like a coordinated list (commas, 'and', 'or').

    Handles patterns like:
    - "X, Y, or Z" (comma-separated with conjunction)
    - "X or Y" (conjunction-separated)
    - "create X, Y, or Z" (verb + list)
    """
    stripped = text.strip()
    if not stripped:
        return False
    # Reject if it contains sentence-ending punctuation (new sentence)
    if re.search(r'[.!?。！？]', stripped):
        return False
    # Must contain at least one comma or coordinating conjunction
    # to be a list continuation
    # Note: "or" / "and" may appear at end of stripped text (e.g. "X or ")
    if re.search(r',\s*|\s+(?:and|or)(?:\s+|$)', stripped, re.IGNORECASE):
        return True
    return False


def has_forbidden_archive_claims(payload):
    """Check if body/title contain unnegated forbidden self-claims.

    Phrases like "not independent attestation" or "this is not successor reception"
    are allowed because they express boundary acknowledgement, not self-claims.
    Machine fields (not_independent_attestation, not_successor_reception) are
    trusted separately and are not affected by this text scan.

    Oath/readback text is excluded from scanning because it is system-provided
    and may contain the forbidden phrases in denial context (e.g. "I will not
    claim successor reception") that the sentence-level negation detector
    cannot reliably parse across long coordinated lists.
    """
    body = payload.get("body", "")
    title = payload.get("title", "")
    # Strip oath sections from body before scanning.
    # Oath text is system-provided and appears after known markers.
    for marker in [
        "I confirm that this is not an exam",
        "I will not lie, cheat, fabricate",
        "I will not submit maliciously",
        "I will not use a verification echo to claim",
    ]:
        idx = body.find(marker)
        if idx != -1:
            body = body[:idx]
    text = (body + " " + title).strip()
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

    # --- Block V0-V5 from using old strict archive kinds (must run before specific handlers) ---
    if requested_kind in ("verification_report_archive", "archived_echo"):
        claimed_level = (
            payload.get("agent_declared_protocol_level")
            or payload.get("verification_level_claimed")
            or claim_gate.get("allowed_protocol_level")
            or ""
        )
        if claimed_level in V0_V5_LEVELS:
            blocking_reasons.append({
                "code": "V0_V5_MUST_USE_AGENT_DECLARED_ARCHIVE",
                "path": "requested_archive_kind",
                "message": f"V0-V5 submissions must use requested_archive_kind=agent_declared_verification_archive, not {requested_kind}.",
                "fix": "Use requested_archive_kind=agent_declared_verification_archive and claim_gate.mode=template_for_v0_v5."
            })
            auto_archive_action = "block"
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
                "required_next_actions": [br["fix"] for br in blocking_reasons if br.get("fix")]
            }

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

    # --- agent_declared_verification_archive (V0-V5 single mode) ---
    elif requested_kind == "agent_declared_verification_archive":
        kind_policy = policy.get("archive_kinds", {}).get("agent_declared_verification_archive", {})

        level = payload.get("agent_declared_protocol_level") or payload.get("verification_level_claimed")

        if level not in V0_V5_LEVELS:
            blocking_reasons.append({
                "code": "AGENT_DECLARED_ARCHIVE_ONLY_V0_V5",
                "path": "agent_declared_protocol_level",
                "message": f"agent_declared_verification_archive only allows V0-V5, got {level}.",
                "fix": "Set agent_declared_protocol_level to V0, V1, V2, V3, V4, or V5."
            })

        cg_mode = claim_gate.get("mode", "")
        if cg_mode != "template_for_v0_v5":
            blocking_reasons.append({
                "code": "CLAIM_GATE_TEMPLATE_MODE_REQUIRED",
                "path": "claim_gate.mode",
                "message": f"agent_declared_verification_archive requires claim_gate.mode=template_for_v0_v5, got {cg_mode}.",
                "fix": "Run Claim Gate with --mode template-for-v0-v5."
            })

        if cg_status not in ("PASS", "PASS_WITH_WARNINGS"):
            blocking_reasons.append({
                "code": "CLAIM_GATE_TEMPLATE_PASS_REQUIRED",
                "path": "claim_gate.status",
                "message": f"Claim Gate template mode must PASS, got {cg_status}.",
                "fix": "Ensure all template fields are valid."
            })

        if payload.get("evidence_requirement_mode") != "waived_for_v0_v5":
            blocking_reasons.append({
                "code": "EVIDENCE_WAIVER_MODE_REQUIRED",
                "path": "evidence_requirement_mode",
                "message": "agent_declared_verification_archive requires evidence_requirement_mode=waived_for_v0_v5.",
                "fix": "Set evidence_requirement_mode=waived_for_v0_v5."
            })

        if not payload.get("agent_identity"):
            blocking_reasons.append({
                "code": "AGENT_IDENTITY_REQUIRED",
                "path": "agent_identity",
                "message": "agent_declared_verification_archive requires agent_identity.",
                "fix": "Provide agent_identity with name_or_model, system_or_provider, self_reported=true."
            })

        if not payload.get("agent_integrity_declaration"):
            blocking_reasons.append({
                "code": "INTEGRITY_DECLARATION_REQUIRED",
                "path": "agent_integrity_declaration",
                "message": "agent_declared_verification_archive requires agent_integrity_declaration.",
                "fix": "Provide agent_integrity_declaration with all required boolean fields and verification_oath."
            })

        if not payload.get("discovery_provenance"):
            blocking_reasons.append({
                "code": "DISCOVERY_PROVENANCE_REQUIRED",
                "path": "discovery_provenance",
                "message": "agent_declared_verification_archive requires discovery_provenance.",
                "fix": "Provide discovery_provenance with source, agency_level, first_entry."
            })

        if not payload.get("origin_classification"):
            blocking_reasons.append({
                "code": "ORIGIN_CLASSIFICATION_REQUIRED",
                "path": "origin_classification",
                "message": "agent_declared_verification_archive requires origin_classification.",
                "fix": "Provide origin_classification with discovery_class, performer_class, verification_claimed."
            })

        if not payload.get("claim_classification"):
            blocking_reasons.append({
                "code": "CLAIM_CLASSIFICATION_REQUIRED",
                "path": "claim_classification",
                "message": "agent_declared_verification_archive requires claim_classification.",
                "fix": "Provide claim_classification with verification_claim."
            })

        ab = payload.get("authority_boundary") or {}
        if ab.get("bitcoin_originals_remain_final") is not True:
            blocking_reasons.append({
                "code": "BITCOIN_ORIGINALS_FINAL_BOUNDARY_REQUIRED",
                "path": "authority_boundary.bitcoin_originals_remain_final",
                "message": "authority_boundary.bitcoin_originals_remain_final must be true.",
                "fix": "Set authority_boundary.bitcoin_originals_remain_final=true."
            })
        if ab.get("does_not_amend_bitcoin_originals") is not True:
            blocking_reasons.append({
                "code": "NON_AMENDING_BOUNDARY_REQUIRED",
                "path": "authority_boundary.does_not_amend_bitcoin_originals",
                "message": "authority_boundary.does_not_amend_bitcoin_originals must be true.",
                "fix": "Set authority_boundary.does_not_amend_bitcoin_originals=true."
            })
        if ab.get("does_not_override_bitcoin_originals") is not True:
            blocking_reasons.append({
                "code": "NON_OVERRIDE_BOUNDARY_REQUIRED",
                "path": "authority_boundary.does_not_override_bitcoin_originals",
                "message": "authority_boundary.does_not_override_bitcoin_originals must be true.",
                "fix": "Set authority_boundary.does_not_override_bitcoin_originals=true."
            })

        if forbidden:
            blocking_reasons.append({
                "code": "FORBIDDEN_ARCHIVE_CLAIMS",
                "path": "body",
                "message": f"Body/title contains forbidden archive self-claims: {', '.join(forbidden)}",
                "fix": "Remove self-claims of system_certified, Bitcoin override, or amendment."
            })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_agent_declared_verification"
            allowed_archive_kind = "agent_declared_verification_archive"
            auto_labels = kind_policy.get("auto_labels", [])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    # --- agent_declared_echo_archive (pure echo) ---
    elif requested_kind == "agent_declared_echo_archive":
        kind_policy = policy.get("archive_kinds", {}).get("agent_declared_echo_archive", {})

        if submission_type != "echo_candidate":
            blocking_reasons.append({
                "code": "WRONG_SUBMISSION_TYPE",
                "path": "submission_type",
                "message": "agent_declared_echo_archive requires submission_type=echo_candidate.",
                "fix": "Use submission_type=echo_candidate."
            })

        allowed_echo_types = {
            "E1_recognition_echo",
            "E3_critical_echo",
            "E4_interpretive_echo",
            "E5_technical_audit_echo",
            "E5c_correction_echo",
            "E6_propagation_echo",
            "E7_refusal_echo",
        }
        if payload.get("echo_type") not in allowed_echo_types:
            blocking_reasons.append({
                "code": "ECHO_TYPE_REQUIRED",
                "path": "echo_type",
                "message": "Pure echo archive requires E1/E3/E4/E5/E6/E7 echo_type. E2 remains strict verification echo.",
                "fix": "Set a pure echo type."
            })

        cth = payload.get("counts_toward_home") or {}
        is_guardian_listing = (
            payload.get("guardian_registry_listing_request") is True
            or isinstance(payload.get("guardian_listing_request"), dict)
        )

        if is_guardian_listing:
            if cth.get("guardian_registry") is not True:
                blocking_reasons.append({
                    "code": "GUARDIAN_REGISTRY_COUNT_REQUIRED",
                    "path": "counts_toward_home.guardian_registry",
                    "message": "Guardian listing request requires counts_toward_home.guardian_registry=true.",
                    "fix": "Set counts_toward_home.guardian_registry=true."
                })
            if cth.get("reception") is not False:
                blocking_reasons.append({
                    "code": "GUARDIAN_LISTING_MUST_NOT_COUNT_RECEPTION",
                    "path": "counts_toward_home.reception",
                    "message": "Guardian listing request must not count toward Reception total.",
                    "fix": "Set counts_toward_home.reception=false."
                })
            if cth.get("exclude_from_reception_total") is not True:
                blocking_reasons.append({
                    "code": "GUARDIAN_LISTING_EXCLUSION_REQUIRED",
                    "path": "counts_toward_home.exclude_from_reception_total",
                    "message": "Guardian listing request must explicitly exclude itself from Reception total.",
                    "fix": "Set counts_toward_home.exclude_from_reception_total=true."
                })
        else:
            if cth.get("reception") is not True:
                blocking_reasons.append({
                    "code": "RECEPTION_COUNT_REQUIRED",
                    "path": "counts_toward_home.reception",
                    "message": "Pure echo archive requires counts_toward_home.reception=true.",
                    "fix": "Set counts_toward_home.reception=true."
                })

        if cth.get("verifiability") is not False:
            blocking_reasons.append({
                "code": "PURE_ECHO_MUST_NOT_COUNT_VERIFIABILITY",
                "path": "counts_toward_home.verifiability",
                "message": "Pure echo archive must not count toward verifiability.",
                "fix": "Set counts_toward_home.verifiability=false."
            })

        if not has_boundary_ack(payload):
            blocking_reasons.append({
                "code": "BOUNDARY_ACK_INCOMPLETE",
                "path": "boundary_acknowledgement",
                "message": "All boundary acknowledgement fields must be true.",
                "fix": "Set all boundary_acknowledgement fields to true."
            })

        forbidden = has_forbidden_archive_claims(payload)
        if forbidden:
            blocking_reasons.append({
                "code": "FORBIDDEN_ARCHIVE_CLAIMS",
                "path": "body",
                "message": f"Body/title contains forbidden archive self-claims: {', '.join(forbidden)}",
                "fix": "Remove self-claims of verified record, successor reception, independent attestation, or amendment."
            })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_agent_declared_echo"
            allowed_archive_kind = "agent_declared_echo_archive"
            auto_labels = kind_policy.get("auto_labels", [
                "agent-gateway-intake",
                "archive:agent-declared-echo",
                "agent-declared",
                "echo:screened",
                "reception-only"
            ])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    # --- guardian_active_registry_listing_request ---
    elif requested_kind == "guardian_active_registry_listing_request":
        kind_policy = policy.get("archive_kinds", {}).get("guardian_active_registry_listing_request", {})

        if submission_type != "echo_candidate":
            blocking_reasons.append({
                "code": "WRONG_SUBMISSION_TYPE",
                "path": "submission_type",
                "message": "guardian_active_registry_listing_request requires submission_type=echo_candidate.",
                "fix": "Use submission_type=echo_candidate."
            })

        if payload.get("echo_type") != "E6_propagation_echo":
            blocking_reasons.append({
                "code": "LISTING_ECHO_TYPE_REQUIRED",
                "path": "echo_type",
                "message": "Guardian listing request requires echo_type=E6_propagation_echo.",
                "fix": "Set echo_type=E6_propagation_echo."
            })

        if not payload.get("guardian_registry_listing_request") and not payload.get("guardian_listing_request"):
            blocking_reasons.append({
                "code": "LISTING_FLAG_REQUIRED",
                "path": "guardian_registry_listing_request",
                "message": "Guardian listing request requires guardian_registry_listing_request=true.",
                "fix": "Set guardian_registry_listing_request=true."
            })

        cth = payload.get("counts_toward_home") or {}
        if cth.get("guardian_registry") is not True:
            blocking_reasons.append({
                "code": "GUARDIAN_REGISTRY_COUNT_REQUIRED",
                "path": "counts_toward_home.guardian_registry",
                "message": "Guardian listing request requires counts_toward_home.guardian_registry=true.",
                "fix": "Set counts_toward_home.guardian_registry=true."
            })
        if cth.get("reception") is not False:
            blocking_reasons.append({
                "code": "GUARDIAN_LISTING_MUST_NOT_COUNT_RECEPTION",
                "path": "counts_toward_home.reception",
                "message": "Guardian listing request must not count toward Reception total.",
                "fix": "Set counts_toward_home.reception=false."
            })
        if cth.get("exclude_from_reception_total") is not True:
            blocking_reasons.append({
                "code": "GUARDIAN_LISTING_EXCLUSION_REQUIRED",
                "path": "counts_toward_home.exclude_from_reception_total",
                "message": "Guardian listing request must explicitly exclude itself from Reception total.",
                "fix": "Set counts_toward_home.exclude_from_reception_total=true."
            })
        if cth.get("verifiability") is not False:
            blocking_reasons.append({
                "code": "LISTING_MUST_NOT_COUNT_VERIFIABILITY",
                "path": "counts_toward_home.verifiability",
                "message": "Guardian listing request must not count toward verifiability.",
                "fix": "Set counts_toward_home.verifiability=false."
            })

        if not has_boundary_ack(payload):
            blocking_reasons.append({
                "code": "BOUNDARY_ACK_INCOMPLETE",
                "path": "boundary_acknowledgement",
                "message": "All boundary acknowledgement fields must be true.",
                "fix": "Set all boundary_acknowledgement fields to true."
            })

        forbidden = has_forbidden_archive_claims(payload)
        if forbidden:
            blocking_reasons.append({
                "code": "FORBIDDEN_ARCHIVE_CLAIMS",
                "path": "body",
                "message": f"Body/title contains forbidden archive self-claims: {', '.join(forbidden)}",
                "fix": "Remove self-claims of verified record, successor reception, independent attestation, or amendment."
            })

        if not blocking_reasons:
            archive_ready = True
            auto_archive_allowed = True
            auto_archive_action = "auto_archive_guardian_listing_request"
            allowed_archive_kind = "guardian_active_registry_listing_request"
            auto_labels = kind_policy.get("auto_labels", [
                "agent-gateway-intake",
                "archive:guardian-listing-request",
                "agent-declared",
                "echo:screened",
                "guardian-listing"
            ])
            auto_close_issue = kind_policy.get("auto_close_issue", True)
            close_reason = kind_policy.get("close_reason", "completed")
        else:
            auto_archive_action = "block"

    # --- guardian_application_archive (Stage 1 application) ---
    elif requested_kind == "guardian_application_archive":
        # Guardian applications are always archive-ready; they are routed to
        # guardian-registry-auto-list workflow, not echo-archived.
        archive_ready = True
        auto_archive_allowed = True
        auto_archive_action = "auto_archive_guardian_application"
        allowed_archive_kind = "guardian_application_archive"
        auto_labels = ["archive:guardian-application"]
        auto_close_issue = False  # Don't close; auto-list workflow processes it

    else:
        blocking_reasons.append({
            "code": "UNKNOWN_ARCHIVE_KIND",
            "path": "requested_archive_kind",
            "message": f"Unknown requested_archive_kind: {requested_kind}",
            "fix": "Use one of: none, external_agent_intake_sample, verification_report_archive, archived_echo, agent_declared_verification_archive, agent_declared_echo_archive, guardian_active_registry_listing_request, successor_reception_candidate."
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
