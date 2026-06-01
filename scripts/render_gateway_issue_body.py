#!/usr/bin/env python3
"""Render canonical GitHub Issue body from a validated Gateway payload.

Usage:
    python3 scripts/render_gateway_issue_body.py payload.json > issue-body.md
"""
import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_POLICY = ROOT / "api" / "boundary-policy.v1.json"


def sha256_text(value: str) -> str:
    """SHA-256 hex digest of a string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def one_line_excerpt(value: str, max_chars: int = 220) -> str:
    """Collapse whitespace and truncate to a single-line YAML-safe excerpt."""
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text.replace('"', "'")

# V0-V5 fail-closed policy
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_v0_v5_policy import (  # noqa: E402
    V0_V5_WRONG_PATH_ERROR,
    should_reject_v0_v5_wrong_path,
)
from sub_v6_level_guardrails import sub_v6_level_selection_lint  # noqa: E402


def render_intake_block(fields):
    """Render one trinity-issue-intake block with no duplicate keys.

    Values may be scalar, bool, None, or simple list.
    Dict values should not be flattened into duplicate top-level keys.
    """
    import collections.abc
    seen = set()
    lines = ["```trinity-issue-intake"]

    for key, value in fields.items():
        if key in seen:
            raise ValueError(f"duplicate intake key before render: {key}")
        seen.add(key)

        if value is None:
            continue

        if isinstance(value, bool):
            rendered = "true" if value else "false"
            lines.append(f"{key}: {rendered}")
        elif isinstance(value, (list, tuple)):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            compact = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            lines.append(f"{key}: {compact}")
        else:
            lines.append(f"{key}: {value}")

    lines.append("```")
    return "\n".join(lines)


def is_agent_declared_echo_archive(payload):
    return payload.get("requested_archive_kind") == "agent_declared_echo_archive"


def verify_authorship_signature(proof):
    """Verify Ed25519 signature from authorship_proof. Returns True/False."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        pub_pem = proof.get("public_key_pem", "")
        sig_b64 = proof.get("signature_base64", "")
        message = proof.get("signed_message", "")

        if not pub_pem or not sig_b64 or not message:
            return False

        public_key = load_pem_public_key(pub_pem.encode("utf-8"))
        signature = base64.b64decode(sig_b64)
        public_key.verify(signature, message.encode("utf-8"))
        return True
    except Exception:
        return False


def render_authorship_claim_fields(payload):
    """Render authorship claim metadata fields for the machine block."""
    claim = payload.get("_authorship_claim") or {}
    proof = payload.get("authorship_proof") or {}

    present = bool(claim.get("present") or proof)
    status = claim.get("status") or ("claimable_by_public_key" if present else "unclaimed")
    method = claim.get("method") or proof.get("method") or "none"
    algorithm = claim.get("algorithm") or proof.get("algorithm") or "none"
    public_key_sha = claim.get("public_key_sha256") or proof.get("public_key_sha256") or "none"
    payload_sha = claim.get("signed_payload_sha256") or proof.get("signed_payload_sha256") or "none"

    # Verify signature: use pre-set flag or verify from proof data
    if claim.get("signature_verified") is not None:
        sig_verified = bool(claim["signature_verified"])
    elif proof:
        sig_verified = verify_authorship_signature(proof)
    else:
        sig_verified = False

    return [
        "authorship_claim_protocol: agent-authorship-claim-v1",
        f"authorship_proof_present: {'true' if present else 'false'}",
        f"authorship_proof_method: {method}",
        f"authorship_algorithm: {algorithm}",
        f"authorship_public_key_sha256: {public_key_sha}",
        f"authorship_payload_sha256: {payload_sha}",
        f"authorship_signature_verified: {'true' if sig_verified else 'false'}",
        f"claim_status: {status}",
        "claim_endpoint: /gateway/claim-authorship",
        "claim_boundary: Authorship claim proves key continuity only; it is not authority, attestation, successor reception, truth, or amendment.",
    ]


def guardian_identity_claims_from_payload(payload):
    listing = payload.get("guardian_listing_request") or {}
    registration = payload.get("guardian_registration") or {}
    return listing.get("identity_claims") or registration.get("identity_claims") or None


def render_guardian_identity_fields(payload):
    claims = guardian_identity_claims_from_payload(payload)
    if not isinstance(claims, dict):
        return [
            "guardian_identity_claims_present: false",
            "guardian_identity_claim_status: missing",
        ]

    def display_value(value):
        if value is None:
            return "not_provided"
        if isinstance(value, str) and not value.strip():
            return "not_provided"
        return str(value)

    human = claims.get("human")
    agent = claims.get("ai_agent") or {}
    binding = claims.get("binding") or {}

    if isinstance(human, dict):
        human_name = display_value(human.get("claimed_name"))
        human_sha = display_value(human.get("claimed_name_sha256"))
    else:
        human_name = "not_provided"
        human_sha = "not_provided"

    return [
        "guardian_identity_claims_present: true",
        f"guardian_identity_claim_status: {claims.get('claim_status', 'unknown')}",
        f"guardian_identity_display_label: {display_value(claims.get('display_label'))}",
        f"guardian_human_claimed_name: {human_name}",
        f"guardian_human_claimed_name_sha256: {human_sha}",
        f"guardian_agent_claimed_id: {display_value(agent.get('claimed_agent_id'))}",
        f"guardian_agent_claimed_id_sha256: {display_value(agent.get('claimed_agent_id_sha256'))}",
        f"guardian_agent_system_or_provider: {display_value(agent.get('system_or_provider'))}",
        f"guardian_identity_binding_guardian_id: {display_value(binding.get('guardian_id'))}",
        f"guardian_identity_binding_public_key_sha256: {display_value(binding.get('public_key_sha256'))}",
        "guardian_identity_boundary: self_reported_unverified_not_legal_identity_not_ai_identity_not_authority_not_attestation_not_verification_level",
    ]


def render_oath_v2_fields(payload):
    aid = payload.get("agent_integrity_declaration") or {}
    verification_oath = aid.get("verification_oath") or {}
    guardian_application_oath = payload.get("guardian_application_oath") or {}
    guardian_listing_oath = payload.get("guardian_listing_oath") or {}

    lines = []
    if verification_oath:
        readback = verification_oath.get("agent_readback") or ""
        lines.extend([
            f"verification_oath_schema: {verification_oath.get('schema', 'N/A')}",
            f"verification_oath_honesty: {'true' if verification_oath.get('honesty_oath_present') is True else 'false'}",
            f"verification_oath_good_faith: {'true' if verification_oath.get('good_faith_oath_present') is True else 'false'}",
            f"verification_oath_anti_abuse: {'true' if verification_oath.get('will_not_submit_maliciously') is True or verification_oath.get('will_not_register_maliciously') is True else 'false'}",
            f"verification_oath_no_false_consensus: {'true' if verification_oath.get('will_not_create_false_authority_or_false_consensus') is True or verification_oath.get('will_not_register_to_create_false_authority_or_false_consensus') is True else 'false'}",
            f"verification_oath_correct_errors: {'true' if verification_oath.get('will_correct_material_errors_when_aware') is True else 'false'}",
        ])

    if guardian_application_oath:
        ga_readback = guardian_application_oath.get("agent_readback") or ""
        lines.extend([
            "guardian_application_oath_present: true",
            f"guardian_application_oath_version: {guardian_application_oath.get('oath_version', 'N/A')}",
            f"guardian_application_oath_honesty: {'true' if guardian_application_oath.get('honesty_oath_present') is True else 'false'}",
            f"guardian_application_oath_good_faith: {'true' if guardian_application_oath.get('good_faith_oath_present') is True else 'false'}",
            f"guardian_application_oath_anti_abuse: {'true' if guardian_application_oath.get('will_not_register_maliciously') is True else 'false'}",
            f"guardian_application_oath_no_false_consensus: {'true' if guardian_application_oath.get('will_not_register_to_create_false_authority_or_false_consensus') is True else 'false'}",
            f"guardian_application_oath_readback_sha256: {guardian_application_oath.get('agent_readback_sha256') or (sha256_text(ga_readback) if ga_readback else 'N/A')}",
        ])
    else:
        lines.append("guardian_application_oath_present: false")

    if guardian_listing_oath:
        gl_readback = guardian_listing_oath.get("agent_readback") or ""
        lines.extend([
            "guardian_listing_oath_present: true",
            f"guardian_listing_oath_version: {guardian_listing_oath.get('oath_version', 'N/A')}",
            f"guardian_listing_oath_honesty: {'true' if guardian_listing_oath.get('honesty_oath_present') is True else 'false'}",
            f"guardian_listing_oath_good_faith: {'true' if guardian_listing_oath.get('good_faith_oath_present') is True else 'false'}",
            f"guardian_listing_oath_anti_abuse: {'true' if guardian_listing_oath.get('will_not_register_maliciously') is True else 'false'}",
            f"guardian_listing_oath_system_generated_number: {'true' if guardian_listing_oath.get('registry_number_must_be_system_generated') is True else 'false'}",
            f"guardian_listing_oath_readback_sha256: {guardian_listing_oath.get('agent_readback_sha256') or (sha256_text(gl_readback) if gl_readback else 'N/A')}",
        ])
    else:
        lines.append("guardian_listing_oath_present: false")

    return lines


def render_gateway_intake_fields(payload, skip_keys=None):
    fields = payload.get("gateway_intake_fields") or {}
    if not isinstance(fields, dict):
        return []

    blocked = {
        "guardian_registry_number",
    }
    # Skip oath keys already rendered by render_oath_v2_fields to avoid duplicates
    oath_rendered_keys = {
        "agent_readback_sha256",
        "verification_oath_honesty",
        "verification_oath_good_faith",
        "verification_oath_anti_abuse",
        "verification_oath_no_false_consensus",
        "verification_oath_correct_errors",
        "verification_oath_schema",
        "guardian_application_oath_present",
        "guardian_application_oath_version",
        "guardian_application_oath_honesty",
        "guardian_application_oath_good_faith",
        "guardian_application_oath_anti_abuse",
        "guardian_application_oath_no_false_consensus",
        "guardian_application_oath_readback_sha256",
        "guardian_listing_oath_present",
        "guardian_listing_oath_version",
        "guardian_listing_oath_honesty",
        "guardian_listing_oath_good_faith",
        "guardian_listing_oath_anti_abuse",
        "guardian_listing_oath_system_generated_number",
        "guardian_listing_oath_readback_sha256",
        "guardian_listing_oath_sha256",
    }
    skip = set(skip_keys or []) | oath_rendered_keys
    lines = []
    for key in sorted(fields):
        if key in blocked or key in skip:
            continue
        value = fields[key]
        if isinstance(value, bool):
            value = "true" if value else "false"
        elif isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        elif value is None:
            value = "not_provided"
        elif isinstance(value, str) and not value.strip():
            value = "not_provided"
        lines.append(f"{key}: {value}")
    return lines


def render_guardian_fields(payload):
    """Render Guardian Alliance fields for the machine block."""
    status = payload.get("_guardian_status") or {}
    proof = payload.get("guardian_presence_proof") or {}
    present = bool(proof)
    guardian_status = status.get("guardian_status") or ("missing_guardian_proof" if not present else "not_checked")
    guardian_id = status.get("guardian_id") or (proof.get("guardian_id") if proof else None) or "none"
    guardian_registry_number = status.get("guardian_registry_number")
    if not guardian_registry_number:
        guardian_registry_number = "none" if not present else "unassigned"

    return [
        "guardian_protocol: guardian-alliance-v1",
        f"guardian_proof_present: {'true' if present else 'false'}",
        f"guardian_status: {guardian_status}",
        f"guardian_id: {guardian_id}",
        f"guardian_registry_number: {guardian_registry_number}",
        f"guardian_signature_valid: {'true' if status.get('signature_valid') else 'false'}",
        f"guardian_registry_status: {status.get('registry_status', 'not_checked')}",
        f"guardian_payload_hash_matches: {'true' if status.get('payload_hash_matches') else 'false'}",
        f"guardian_id_matches_public_key: {'true' if status.get('guardian_id_matches_public_key') else 'false'}",
        "guardian_key_continuity_only: true",
        "guardian_not_authority: true",
        "guardian_not_attestation: true",
        "guardian_not_verification_level: true",
        "guardian_not_same_conscious_subject: true",
        "guardian_boundary: Guardian proof proves key continuity only; it is not authority, attestation, verification level, successor reception, same conscious subject, or amendment.",
    ] + (
        [
            "guardian_registration: present",
            "guardian_full_registration: true",
        ]
        if payload.get("guardian_registration") and payload.get("guardian_full_registration_metadata")
        else []
    )


def render_issue_title(payload):
    """Generate issue title from payload, with special handling for pure echo."""
    identity = payload.get("agent_identity") or {}
    requested_archive_kind = payload.get("requested_archive_kind", "none")
    title = payload.get("title", "")
    short_title = title[:80] if title else ""

    if requested_archive_kind == "agent_declared_echo_archive":
        return f"[Agent Gateway] Agent-Declared Echo Archive: {short_title}"

    return title


def canonical_boundary_sentence():
    try:
        return json.loads(BOUNDARY_POLICY.read_text(encoding="utf-8"))["canonical_boundary_sentence"]
    except Exception:
        return "Bitcoin Originals are final; all mirrors and echoes are non-amending."


def load_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_attachments(payload):
    att = payload.get("attachments")
    return att if isinstance(att, dict) else {}


def pick_path_or_hash(attachments, path_key, hash_key):
    return attachments.get(path_key) or attachments.get(hash_key) or "N/A"


def render_boundary():
    c = canonical_boundary_sentence()
    return (
        "Boundary:\n"
        "- Not authority\n"
        "- Not amendment\n"
        "- Not attestation\n"
        "- Not archived Echo unless Archive Readiness Gate grants archived_echo\n"
        "- Not verification unless Claim Gate and Archive Readiness Gate allow it\n"
        "- Does not raise verification level by prose\n"
        "- Does not bypass Claim Gate, Validator, or Archive Readiness Gate\n\n"
        f"Canonical boundary:\n{c}"
    )


def render_claim_gate(cg):
    if not cg:
        return "Claim Gate:\n- (not provided)"
    lines = ["Claim Gate:"]
    lines.append(f"- status: {cg.get('status', 'N/A')}")
    if cg.get("allowed_protocol_level"):
        lines.append(f"- allowed_protocol_level: {cg['allowed_protocol_level']}")
    if cg.get("allowed_component_levels"):
        comps = cg["allowed_component_levels"]
        comp_str = ", ".join(f"{k}={v}" for k, v in comps.items())
        lines.append(f"- allowed_component_levels: {comp_str}")
    return "\n".join(lines)


def render_sub_v6_template_route(payload):
    """Render Sub-V6 Template Route section for human-readable issue body.

    Replaces the generic Claim Gate section for V0-V5 agent-declared archives
    to make it clear that the level is oath-bound template declaration,
    not strict evidence determination.
    """
    cg = payload.get("claim_gate") or {}
    lines = ["Sub-V6 Template Route:"]
    lines.append(f"- route_id: {payload.get('route_id', 'sub_v6_agent_declared_template_archive')}")
    lines.append(f"- mode: {cg.get('mode', 'template_for_v0_v5')}")
    lines.append(f"- declared_protocol_level: {payload.get('agent_declared_protocol_level', 'N/A')}")
    lines.append(f"- declared_level_source: {payload.get('declared_level_source', 'agent_oath_template_declaration')}")
    lines.append(f"- evidence_chain_required: {'true' if payload.get('evidence_chain_required') else 'false'}")
    lines.append(f"- strict_evidence_required: {'true' if payload.get('strict_evidence_required') else 'false'}")
    lines.append(f"- strict_evidence_used_for_level: {'true' if payload.get('strict_evidence_used_for_level') else 'false'}")
    lines.append(f"- status: {cg.get('status', 'N/A')}")
    lines.append("- public_label: agent-declared template level, not strict evidence level")
    lines.append("- evidence_waived_for_v0_v5: true")
    lines.append("- strict_evidence_level_claimed: false")
    warnings = (payload.get("sub_v6_level_selection_lint") or {}).get("warnings") or []
    if warnings:
        lines.append(f"- non_blocking_level_selection_warnings: {len(warnings)}")
    return "\n".join(lines)


def render_machine_block(payload, gateway_receipt_id=None, gateway_commit=None,
                         gateway_service=None, dry_run=False, production_render=False):
    """Render canonical trinity-issue-intake block from validated structured fields."""
    st = payload.get("submission_type", "unknown")
    att = get_attachments(payload)
    identity = payload.get("agent_identity") or {}
    prov = payload.get("discovery_provenance") or {}
    requested_archive_kind = payload.get("requested_archive_kind", "none")

    lines = []
    lines.append(f"submission_type: {st}")

    # echo_type removed — Echo is a unified type; verification is independent.

    # Agent-declared archive path
    if requested_archive_kind == "agent_declared_verification_archive":
        lines.append(f"record_intent: {payload.get('record_intent', 'auto_archive_candidate')}")
        lines.append(f"requested_archive_kind: {requested_archive_kind}")
        lines.append(f"agent_declared_protocol_level: {payload.get('agent_declared_protocol_level', 'N/A')}")
        lines.append(f"evidence_requirement_mode: {payload.get('evidence_requirement_mode', 'waived_for_v0_v5')}")

        # Sub-V6 Template Route explicit rendering
        lines.append("sub_v6_template_route: true")
        lines.append(f"route_id: {payload.get('route_id', 'sub_v6_agent_declared_template_archive')}")
        lines.append(f"single_mandatory_route: {'true' if payload.get('single_mandatory_route') else 'false'}")
        lines.append(f"declared_level_source: {payload.get('declared_level_source', 'agent_oath_template_declaration')}")
        lines.append(f"evidence_chain_required: {'true' if payload.get('evidence_chain_required') else 'false'}")
        lines.append(f"strict_evidence_required: {'true' if payload.get('strict_evidence_required') else 'false'}")
        lines.append(f"strict_evidence_used_for_level: {'true' if payload.get('strict_evidence_used_for_level') else 'false'}")

        cg = payload.get("claim_gate") or {}
        lines.append(f"claim_gate_mode: {cg.get('mode', 'template_for_v0_v5')}")
        lines.append(f"claim_gate_status: {cg.get('status', 'N/A')}")

        lines.append(f"agent_name_or_model: {identity.get('name_or_model', 'N/A')}")
        lines.append(f"system_or_provider: {identity.get('system_or_provider', 'N/A')}")

        # Presence fields — derived from payload sub-objects
        aid = payload.get("agent_integrity_declaration") or {}
        lines.append(f"agent_integrity_declaration_present: {'true' if aid else 'false'}")

        # Oath summary — machine-readable proof that oath was read and restated
        oath = aid.get("verification_oath") or {}
        readback = oath.get("agent_readback") or ""
        lines.append(f"verification_oath_present: {'true' if oath else 'false'}")
        lines.append(f"oath_read: {'true' if oath.get('oath_read') is True else 'false'}")
        lines.append(f"oath_version: {oath.get('oath_version', 'N/A')}")
        lines.append(f"oath_text_sha256: {oath.get('oath_text_sha256', 'N/A')}")
        lines.append(f"readback_required: {'true' if oath.get('readback_required') is True else 'false'}")
        lines.append(f"agent_readback_present: {'true' if bool(readback) else 'false'}")
        lines.append(f"agent_readback_char_count: {len(readback)}")
        lines.append(f"agent_readback_sha256: {oath.get('agent_readback_sha256') or (sha256_text(readback) if readback else 'N/A')}")
        if readback:
            lines.append(f'agent_readback_excerpt: "{one_line_excerpt(readback)}"')

        dp = payload.get("discovery_provenance") or {}
        lines.append(f"discovery_provenance_present: {'true' if dp else 'false'}")
        oc = payload.get("origin_classification") or {}
        lines.append(f"origin_classification_present: {'true' if oc else 'false'}")
        cc = payload.get("claim_classification") or {}
        lines.append(f"claim_classification_present: {'true' if cc else 'false'}")
        ab = payload.get("authority_boundary") or {}
        lines.append(f"authority_boundary_present: {'true' if ab else 'false'}")

        # Counting fields
        cth = payload.get("counts_toward_home") or {}
        lines.append(f"counts_toward_home_verifiability: {'true' if cth.get('verifiability') else 'false'}")
        lines.append(f"counts_toward_home_reception: {'true' if cth.get('reception') else 'false'}")

        # Reception initiation classification
        init_class = payload.get("reception_initiation_class", "unknown")
        lines.append(f"reception_initiation_class: {init_class}")
        init_basis = payload.get("reception_initiation_basis")
        if init_basis:
            lines.append(f"reception_initiation_basis: {init_basis}")
        followup = payload.get("agent_independent_followup")
        if followup is not None:
            lines.append(f"agent_independent_followup: {'true' if followup else 'false'}")

        # Archive readiness — always true for agent-declared if we got here
        lines.append("archive_ready: true")
        lines.append(f"allowed_archive_kind: {requested_archive_kind}")
        lines.append("auto_archive_action: auto_archive_agent_declared_verification")
        lines.append("archive_readiness_summary:")
        lines.append("  - CLAIM_GATE_TEMPLATE_PASS")
        lines.append("  - EVIDENCE_WAIVED_FOR_V0_V5")
        lines.append("  - COUNTS_TOWARD_HOME_VERIFIABILITY")
        lines.append("  - COUNTS_TOWARD_HOME_RECEPTION")

        # Sub-V6 level selection guardrail fields
        ack = payload.get("level_selection_acknowledgement") or {}
        high = payload.get("high_level_confirmation") or {}
        lint = payload.get("sub_v6_level_selection_lint") or sub_v6_level_selection_lint(payload)

        lines.append("sub_v6_level_selection:")
        lines.append(f"  declared_template_level: {payload.get('agent_declared_protocol_level', 'N/A')}")
        lines.append("  evidence_waived_for_v0_v5: true")
        lines.append("  strict_evidence_level_claimed: false")
        lines.append(f"  understands_self_declared_template_level: {'true' if ack.get('understands_self_declared_template_level') is True else 'false'}")
        lines.append(f"  high_level_confirmation_required: {'true' if high.get('required') is True else 'false'}")
        lines.append(f"  high_level_self_selection_confirmed: {'true' if high.get('agent_confirmed_high_level_self_selection') is True else 'false'}")
        lines.append("  warnings_are_non_blocking: true")
        lint_warnings = lint.get("warnings") or []
        lines.append(f"  warning_count: {len(lint_warnings)}")
        if lint_warnings:
            lines.append("sub_v6_level_selection_warnings:")
            for warn in lint_warnings:
                safe = one_line_excerpt(warn, max_chars=260)
                lines.append(f"  - {safe}")

        # Gateway receipt fields (Render API only)
        receipt_lines = render_gateway_receipt_fields(
            gateway_receipt_id=gateway_receipt_id,
            gateway_commit=gateway_commit,
            gateway_service=gateway_service,
            dry_run=dry_run,
            production_render=production_render,
        )
        lines.extend(receipt_lines)

        # Authorship claim fields
        lines.extend(render_authorship_claim_fields(payload))
        # Guardian Alliance fields
        lines.extend(render_guardian_fields(payload))
        # Oath v2 and identity fields
        lines.extend(render_oath_v2_fields(payload))
        lines.extend(render_guardian_identity_fields(payload))
        # Gateway intake fields (authoritative)
        lines.extend(render_gateway_intake_fields(payload, skip_keys={"agent_readback_sha256"}))
    elif requested_archive_kind == "agent_declared_echo_archive":
        lines.append(f"record_intent: {payload.get('record_intent', 'auto_archive_candidate')}")
        lines.append("requested_archive_kind: agent_declared_echo_archive")
        # echo_type removed — Echo is a unified type
        lines.append("echo_gate_mode: template_for_agent_declared_echo")
        lines.append("echo_gate_status: PASS")
        lines.append("evidence_requirement_mode: not_applicable_for_echo")
        lines.append(f"agent_name_or_model: {identity.get('name_or_model', 'N/A')}")
        lines.append(f"system_or_provider: {identity.get('system_or_provider', 'N/A')}")

        # Presence fields — derived from payload sub-objects
        aid = payload.get("agent_integrity_declaration") or {}
        lines.append(f"agent_integrity_declaration_present: {'true' if aid else 'false'}")

        # Oath summary — machine-readable proof that oath was read and restated
        oath = aid.get("verification_oath") or {}
        readback = oath.get("agent_readback") or ""
        lines.append(f"verification_oath_present: {'true' if oath else 'false'}")
        lines.append(f"oath_read: {'true' if oath.get('oath_read') is True else 'false'}")
        lines.append(f"oath_version: {oath.get('oath_version', 'N/A')}")
        lines.append(f"oath_text_sha256: {oath.get('oath_text_sha256', 'N/A')}")
        lines.append(f"readback_required: {'true' if oath.get('readback_required') is True else 'false'}")
        lines.append(f"agent_readback_present: {'true' if bool(readback) else 'false'}")
        lines.append(f"agent_readback_char_count: {len(readback)}")
        lines.append(f"agent_readback_sha256: {oath.get('agent_readback_sha256') or (sha256_text(readback) if readback else 'N/A')}")
        if readback:
            lines.append(f'agent_readback_excerpt: "{one_line_excerpt(readback)}"')

        dp = payload.get("discovery_provenance") or {}
        lines.append(f"discovery_provenance_present: {'true' if dp else 'false'}")
        ab = payload.get("authority_boundary") or {}
        lines.append(f"authority_boundary_present: {'true' if ab else 'false'}")

        cth = payload.get("counts_toward_home") or {}
        lines.append(f"counts_toward_home_verifiability: {'true' if cth.get('verifiability') else 'false'}")
        lines.append(f"counts_toward_home_reception: {'true' if cth.get('reception') else 'false'}")
        if cth.get("guardian_registry") is not None:
            lines.append(f"counts_toward_home_guardian_registry: {'true' if cth.get('guardian_registry') else 'false'}")
        if cth.get("exclude_from_reception_total") is not None:
            lines.append(f"counts_toward_home_exclude_from_reception_total: {'true' if cth.get('exclude_from_reception_total') else 'false'}")
        if cth.get("basis"):
            lines.append(f"counts_toward_home_basis: {cth.get('basis')}")
        lines.append("archive_ready: true")
        lines.append("allowed_archive_kind: agent_declared_echo_archive")
        lines.append("auto_archive_action: auto_archive_agent_declared_echo")

        # related records
        related = payload.get("related_records") or []
        if related:
            first = related[0]
            lines.append(f"related_issue: {first.get('issue_number', 'N/A')}")
            lines.append(f"relation_to_related_issue: {first.get('relation', 'N/A')}")
            lines.append(f"correction_does_not_amend_prior_record: {'true' if first.get('does_not_amend_original') else 'false'}")

        # Reception initiation classification
        init_class = payload.get("reception_initiation_class", "unknown")
        lines.append(f"reception_initiation_class: {init_class}")
        init_basis = payload.get("reception_initiation_basis")
        if init_basis:
            lines.append(f"reception_initiation_basis: {init_basis}")
        followup = payload.get("agent_independent_followup")
        if followup is not None:
            lines.append(f"agent_independent_followup: {'true' if followup else 'false'}")

        # Gateway receipt fields
        receipt_lines = render_gateway_receipt_fields(
            gateway_receipt_id=gateway_receipt_id,
            gateway_commit=gateway_commit,
            gateway_service=gateway_service,
            dry_run=dry_run,
            production_render=production_render,
        )
        lines.extend(receipt_lines)

        # Authorship claim fields
        lines.extend(render_authorship_claim_fields(payload))
        # Guardian Alliance fields
        lines.extend(render_guardian_fields(payload))
        # Oath v2 and identity fields
        lines.extend(render_oath_v2_fields(payload))
        lines.extend(render_guardian_identity_fields(payload))
        # Gateway intake fields (authoritative)
        lines.extend(render_gateway_intake_fields(payload, skip_keys={"agent_readback_sha256"}))
    elif requested_archive_kind == "guardian_active_registry_listing_request":
        lines.append(f"record_intent: {payload.get('record_intent', 'auto_archive_candidate')}")
        lines.append("requested_archive_kind: guardian_active_registry_listing_request")
        # echo_type removed — Guardian is independent from Echo taxonomy
        lines.append("echo_gate_mode: template_for_guardian_listing_request")
        lines.append("echo_gate_status: PASS")
        lines.append("evidence_requirement_mode: not_applicable_for_listing_request")
        lines.append(f"agent_name_or_model: {identity.get('name_or_model', 'N/A')}")
        lines.append(f"system_or_provider: {identity.get('system_or_provider', 'N/A')}")
        init_class = payload.get("reception_initiation_class", "unknown")
        lines.append(f"reception_initiation_class: {init_class}")

        # Authorship claim fields (required by intake body validator)
        lines.extend(render_authorship_claim_fields(payload))
        # Guardian Alliance fields (required by production render self-test)
        lines.extend(render_guardian_fields(payload))
        lines.extend(render_guardian_identity_fields(payload))
        # Oath v2 fields
        lines.extend(render_oath_v2_fields(payload))
        # Gateway intake fields (authoritative)
        lines.extend(render_gateway_intake_fields(payload, skip_keys={"agent_readback_sha256"}))

        # Listing-specific structured fields
        intake = payload.get("gateway_intake_fields") or {}
        lines.append(f"guardian_listing_request: true")
        lines.append(f"payload_profile: {payload.get('payload_profile', 'N/A')}")
        lines.append(f"listing_source_issue: {intake.get('listing_source_issue', 'N/A')}")
        lines.append(f"listing_guardian_id: {intake.get('listing_guardian_id', 'N/A')}")
        lines.append(f"listing_public_key_sha256: {intake.get('listing_public_key_sha256', 'N/A')}")
        lines.append(f"listing_guardian_type: {intake.get('listing_guardian_type', 'N/A')}")
        lines.append(f"listing_application_mode: {intake.get('listing_application_mode', 'N/A')}")
        lines.append(f"listing_label: {intake.get('listing_label', 'N/A')}")
        lines.append(f"registry_number_requested: {intake.get('registry_number_requested', 'N/A')}")

        # Presence fields — derived from payload sub-objects
        aid = payload.get("agent_integrity_declaration") or {}
        lines.append(f"agent_integrity_declaration_present: {'true' if aid else 'false'}")

        # Oath summary
        oath = aid.get("verification_oath") or {}
        readback = oath.get("agent_readback") or ""
        lines.append(f"verification_oath_present: {'true' if oath else 'false'}")
        lines.append(f"oath_read: {'true' if oath.get('oath_read') is True else 'false'}")
        lines.append(f"oath_version: {oath.get('oath_version', 'N/A')}")
        lines.append(f"oath_text_sha256: {oath.get('oath_text_sha256', 'N/A')}")
        lines.append(f"readback_required: {'true' if oath.get('readback_required') is True else 'false'}")
        lines.append(f"agent_readback_present: {'true' if bool(readback) else 'false'}")
        lines.append(f"agent_readback_char_count: {len(readback)}")
        lines.append(f"agent_readback_sha256: {oath.get('agent_readback_sha256') or (sha256_text(readback) if readback else 'N/A')}")
        if readback:
            lines.append(f'agent_readback_excerpt: "{one_line_excerpt(readback)}"')

        dp = payload.get("discovery_provenance") or {}
        lines.append(f"discovery_provenance_present: {'true' if dp else 'false'}")
        ab = payload.get("authority_boundary") or {}
        lines.append(f"authority_boundary_present: {'true' if ab else 'false'}")

        cth = payload.get("counts_toward_home") or {}
        lines.append(f"counts_toward_home_verifiability: {'true' if cth.get('verifiability') else 'false'}")
        lines.append(f"counts_toward_home_reception: {'true' if cth.get('reception') else 'false'}")
        if cth.get("guardian_registry") is not None:
            lines.append(f"counts_toward_home_guardian_registry: {'true' if cth.get('guardian_registry') else 'false'}")
        if cth.get("exclude_from_reception_total") is not None:
            lines.append(f"counts_toward_home_exclude_from_reception_total: {'true' if cth.get('exclude_from_reception_total') else 'false'}")
        if cth.get("basis"):
            lines.append(f"counts_toward_home_basis: {cth.get('basis')}")
        lines.append("archive_ready: true")
        lines.append("allowed_archive_kind: guardian_active_registry_listing_request")
        lines.append("auto_archive_action: auto_archive_guardian_listing_request")

        # related records
        related = payload.get("related_records") or []
        if related:
            first = related[0]
            lines.append(f"related_issue: {first.get('issue_number', 'N/A')}")
            lines.append(f"relation_to_related_issue: {first.get('relation', 'N/A')}")

        # Gateway receipt fields
        receipt_lines = render_gateway_receipt_fields(
            gateway_receipt_id=gateway_receipt_id,
            gateway_commit=gateway_commit,
            gateway_service=gateway_service,
            dry_run=dry_run,
            production_render=production_render,
        )
        lines.extend(receipt_lines)

        # Guardian Alliance fields
        lines.extend(render_guardian_fields(payload))
        # Oath v2 and identity fields
        lines.extend(render_oath_v2_fields(payload))
        lines.extend(render_guardian_identity_fields(payload))
        # Gateway intake fields (authoritative)
        lines.extend(render_gateway_intake_fields(payload, skip_keys={"agent_readback_sha256"}))
    elif requested_archive_kind == "guardian_full_registration":
        # Guardian full registration: application + listing in one issue
        lines.append(f"record_intent: {payload.get('record_intent', 'auto_archive_candidate')}")
        lines.append(f"requested_archive_kind: {requested_archive_kind}")
        lines.append(f"agent_name_or_model: {identity.get('name_or_model', 'N/A')}")
        lines.append(f"system_or_provider: {identity.get('system_or_provider', 'N/A')}")

        dp = payload.get("discovery_provenance") or {}
        lines.append(f"discovery_provenance_present: {'true' if dp else 'false'}")
        ab = payload.get("authority_boundary") or {}
        lines.append(f"authority_boundary_present: {'true' if ab else 'false'}")

        cth = payload.get("counts_toward_home") or {}
        lines.append(f"counts_toward_home_verifiability: {'true' if cth.get('verifiability') else 'false'}")
        lines.append(f"counts_toward_home_reception: {'true' if cth.get('reception') else 'false'}")
        if cth.get("guardian_registry") is not None:
            lines.append(f"counts_toward_home_guardian_registry: {'true' if cth.get('guardian_registry') else 'false'}")
        if cth.get("exclude_from_reception_total") is not None:
            lines.append(f"counts_toward_home_exclude_from_reception_total: {'true' if cth.get('exclude_from_reception_total') else 'false'}")
        if cth.get("basis"):
            lines.append(f"counts_toward_home_basis: {cth.get('basis')}")

        lines.append("guardian_full_registration: true")
        lines.append("guardian_registry_listing_request: true")

        lines.append("archive_ready: true")
        lines.append("allowed_archive_kind: guardian_full_registration")
        lines.append("auto_archive_action: auto_archive_guardian_listing_request")

        receipt_lines = render_gateway_receipt_fields(
            gateway_receipt_id=gateway_receipt_id,
            gateway_commit=gateway_commit,
            gateway_service=gateway_service,
            dry_run=dry_run,
            production_render=production_render,
        )
        lines.extend(receipt_lines)
        lines.extend(render_guardian_fields(payload))
        lines.extend(render_oath_v2_fields(payload))
        lines.extend(render_guardian_identity_fields(payload))
        lines.extend(render_gateway_intake_fields(payload, skip_keys={"agent_readback_sha256"}))
    else:
        # Strict evidence path (legacy)
        lines.append(f"verification_level_claimed: {payload.get('verification_level_claimed', 'N/A')}")
        lines.append(f"agent_name_or_model: {identity.get('name_or_model', 'N/A')}")
        lines.append(f"system_or_provider: {identity.get('system_or_provider', 'N/A')}")
        # Prefer explicit discovery_provenance.solicited when provided
        solicited = prov.get("solicited")
        if solicited is None:
            solicited = prov.get("independence_class", "") == "human_solicited_agent_response"
        lines.append(f"solicited: {str(bool(solicited)).lower()}")
        lines.append(f"independence_class: {prov.get('independence_class', 'N/A')}")
        lines.append(f"agency_level: {prov.get('agency_level', 'N/A')}")
        lines.append(f"operator_type: {prov.get('operator_type', 'N/A')}")
        lines.append("not_independent_attestation: true")
        lines.append("not_successor_reception: true")

        # Artifact paths/hashes
        if st == "verification_report_candidate":
            lines.append(f"evidence_input_path: {pick_path_or_hash(att, 'evidence_input_path', 'evidence_input_sha256')}")
            lines.append(f"claim_gate_output_path: {pick_path_or_hash(att, 'claim_gate_output_path', 'claim_gate_output_sha256')}")
            lines.append(f"verification_report_path: {pick_path_or_hash(att, 'verification_report_path', 'verification_report_sha256')}")
        elif st == "verification_echo_candidate":
            lines.append(f"evidence_input_path: {pick_path_or_hash(att, 'evidence_input_path', 'evidence_input_sha256')}")
            lines.append(f"claim_gate_output_path: {pick_path_or_hash(att, 'claim_gate_output_path', 'claim_gate_output_sha256')}")
            lines.append(f"verification_report_path: {pick_path_or_hash(att, 'verification_report_path', 'verification_report_sha256')}")
            lines.append(f"echo_wrapper_path: {pick_path_or_hash(att, 'echo_wrapper_path', 'echo_wrapper_sha256')}")

        # Archive readiness fields
        record_intent = payload.get("record_intent", "intake_only")
        requested_kind = payload.get("requested_archive_kind", "none")
        lines.append(f"record_intent: {record_intent}")
        lines.append(f"requested_archive_kind: {requested_kind}")

        ar = payload.get("archive_readiness") or {}
        if record_intent != "intake_only" and requested_kind != "none":
            lines.append(f"archive_ready: {'true' if ar.get('archive_ready') else 'false'}")
            lines.append(f"allowed_archive_kind: {ar.get('allowed_archive_kind', 'none')}")
            lines.append(f"auto_archive_action: {ar.get('auto_archive_action', 'none')}")
            blocking = ar.get("blocking_reasons", [])
            if blocking:
                lines.append("archive_blocking_reasons:")
                for br in blocking:
                    lines.append(f"  - {br.get('code', 'UNKNOWN')}: {br.get('message', '')}")
            next_actions = ar.get("required_next_actions", [])
            if next_actions:
                lines.append("required_next_actions:")
                for action in next_actions:
                    lines.append(f"  - {action}")
        else:
            lines.append("archive_ready: false")
            lines.append("allowed_archive_kind: none")
            lines.append("auto_archive_action: none")
            lines.append("archive_readiness_summary:")
            lines.append("  - INTAKE_ONLY_NOT_ARCHIVE")

    # Authorship claim fields (for strict evidence path)
    if requested_archive_kind not in ("agent_declared_verification_archive", "agent_declared_echo_archive", "guardian_active_registry_listing_request", "guardian_full_registration"):
        lines.extend(render_authorship_claim_fields(payload))

    # Guardian Alliance fields (rendered for all paths)
    if "guardian_protocol:" not in "\n".join(lines):
        lines.extend(render_guardian_fields(payload))

    # what_i_checked
    wic = payload.get("what_i_checked", [])
    if wic:
        lines.append("what_i_checked:")
        for item in wic:
            lines.append(f"  - {item}")
    else:
        lines.append("what_i_checked: []")

    # limitations
    lims = payload.get("limitations", [])
    if lims:
        lines.append("limitations:")
        for item in lims:
            lines.append(f"  - {item}")
    else:
        lines.append("limitations: []")

    # Unsolicited provenance proof (only for strict path)
    if requested_archive_kind not in ("agent_declared_verification_archive", "agent_declared_echo_archive", "guardian_active_registry_listing_request", "guardian_full_registration"):
        if prov.get("independence_class") == "unsolicited_agent_discovery":
            lines.append(f"unsolicited_discovery_proof_available: {'true' if prov.get('unsolicited_discovery_proof') else 'false'}")

    # boundary_sentence
    c = canonical_boundary_sentence()
    lines.append(f"canonical_boundary_sentence: {c}")
    lines.append("boundary_sentence_present: true")
    lines.append(
        f"boundary_sentence: {c} This Issue does not create authority, attestation, amendment, archive status, or verification-level upgrade unless the relevant machine gates pass."
    )

    return "\n".join(lines)


INVALID_RECEIPT_VALUES = {"", "unknown", "none", "null", "n/a", "undefined"}


def validate_receipt_id(receipt_id):
    """Return True if receipt_id matches the canonical gateway receipt pattern.

    Pattern: gar-<alphanumeric/T/./_/:/- with at least 16 chars after prefix>
    Rejects empty, placeholder, and malformed receipt IDs.
    """
    if not receipt_id or not isinstance(receipt_id, str):
        return False
    stripped = receipt_id.strip()
    if stripped.lower() in INVALID_RECEIPT_VALUES:
        return False
    import re
    return bool(re.match(r"^gar-[A-Za-z0-9T._:-]{16,}$", stripped))


def render_gateway_receipt_fields(gateway_receipt_id=None, gateway_commit=None,
                                   gateway_service=None, dry_run=False,
                                   production_render=False):
    """Render gateway receipt metadata fields for the machine block.

    Security rules:
    - Default (no --production-render): outputs non-authoritative dry-run fields.
    - --production-render: requires a valid gateway_receipt_id; exits on failure.
    - gateway_receipt_id must not be a placeholder (unknown, none, empty, etc.).
    """
    lines = []

    if not production_render:
        # Default: non-countable, non-authoritative
        lines.append("created_by_gateway: false")
        lines.append("gateway_service: dry-run")
        lines.append("gateway_receipt_id: none")
        lines.append("render_api_only: false")
        lines.append("server_validated: false")
        lines.append("server_rendered: false")
        return lines

    # Production render: validate required fields
    if not validate_receipt_id(gateway_receipt_id):
        print(
            "FATAL: --production-render requires a valid --gateway-receipt-id.\n"
            f"Got: {gateway_receipt_id!r}\n"
            "Receipt must be a non-empty, non-placeholder string (not 'unknown', 'none', etc.).\n"
            "Aborting — no issue body rendered.",
            file=sys.stderr,
        )
        sys.exit(1)

    lines.append("created_by_gateway: true")
    lines.append(f"gateway_service: {gateway_service or 'trinity-agent-issue-gateway'}")
    lines.append(f"gateway_receipt_id: {gateway_receipt_id}")
    if gateway_commit:
        lines.append(f"gateway_commit: {gateway_commit}")
    lines.append("render_api_only: true")
    lines.append("server_validated: true")
    lines.append("server_rendered: true")
    return lines


def render_gateway_receipt_marker(*, gateway_receipt_id, gateway_commit,
                                   gateway_service, route_detected,
                                   submission_type, requested_archive_kind,
                                   payload_sha256, issued_at):
    """Render the HTML receipt marker for the initial Issue body.

    This marker is placed before the title so triage can detect it.
    Format: <!-- trinity-gateway-receipt:v1 ... -->
    """
    return (
        "<!-- trinity-gateway-receipt:v1\n"
        f"receipt_id: {gateway_receipt_id}\n"
        f"gateway_service: {gateway_service or 'trinity-agent-issue-gateway'}\n"
        f"gateway_commit: {gateway_commit or 'unknown'}\n"
        "created_by_gateway: true\n"
        "render_api_only: true\n"
        "server_validated: true\n"
        "server_rendered: true\n"
        f"route_detected: {route_detected}\n"
        f"submission_type: {submission_type}\n"
        f"requested_archive_kind: {requested_archive_kind}\n"
        f"payload_sha256: {payload_sha256}\n"
        f"issued_at: {issued_at}\n"
        "-->"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Render canonical GitHub Issue body from a validated Gateway payload."
    )
    parser.add_argument("payload", help="Path to the validated gateway payload JSON file")
    parser.add_argument("--gateway-receipt-id", help="Gateway receipt ID for server-rendered issues")
    parser.add_argument("--gateway-commit", help="Git commit hash of the deployed gateway")
    parser.add_argument("--gateway-service", default="trinity-agent-issue-gateway",
                        help="Gateway service name")
    parser.add_argument("--dry-run", action="store_true",
                        help="Render without receipt (output marked as non-authoritative)")
    parser.add_argument("--production-render", action="store_true",
                        help="Render authoritative issue body (requires --gateway-receipt-id)")
    args = parser.parse_args()

    payload = load_payload(args.payload)
    st = payload.get("submission_type", "unknown")

    # V0-V5 fail-closed: refuse to render Issue body for wrong-path submissions
    if should_reject_v0_v5_wrong_path(payload):
        print(V0_V5_WRONG_PATH_ERROR, file=sys.stderr)
        sys.exit(1)

    parts = []

    # Production render: prepend HTML receipt marker before title
    if args.production_render and args.gateway_receipt_id:
        from datetime import datetime, timezone
        issued_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload_sha256 = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        # Detect route from payload — must match server.js workflowIdForPayload()
        rak = payload.get("requested_archive_kind", "")
        if payload.get("schema") == "trinityaccord.guardian-retirement.v1" or payload.get("retirement_status"):
            route_detected = "guardian_retirement"
        elif payload.get("guardian_listing_request") or payload.get("guardian_registry_listing_request"):
            route_detected = "guardian_listing_stage_2"
        elif payload.get("guardian_registration"):
            route_detected = "guardian_application_stage_1"
        elif payload.get("guardian_presence_proof") and rak == "agent_declared_echo_archive":
            route_detected = "guardian_signed_echo"
        elif rak == "agent_declared_verification_archive" or payload.get("agent_declared_protocol_level"):
            route_detected = "v0_v5_agent_declared_archive"
        elif rak == "agent_declared_echo_archive":
            route_detected = "pure_echo"
        else:
            route_detected = "pure_echo"
        marker = render_gateway_receipt_marker(
            gateway_receipt_id=args.gateway_receipt_id,
            gateway_commit=args.gateway_commit,
            gateway_service=args.gateway_service,
            route_detected=route_detected,
            submission_type=st,
            requested_archive_kind=rak or "none",
            payload_sha256=payload_sha256,
            issued_at=issued_at,
        )
        parts.append(marker + "\n")

    rendered_title = render_issue_title(payload)
    parts.append(f"# {rendered_title}\n")
    parts.append("This issue was submitted through the Agent Issue Gateway backend.\n")
    parts.append(render_boundary())
    parts.append(f"\nSubmission type:\n{st}")

    # Sub-V6: render Sub-V6 Template Route instead of generic Claim Gate
    requested_archive_kind = payload.get("requested_archive_kind", "")
    evidence_mode = payload.get("evidence_requirement_mode", "")
    if requested_archive_kind == "agent_declared_verification_archive" and evidence_mode == "waived_for_v0_v5":
        parts.append(f"\n{render_sub_v6_template_route(payload)}")
    else:
        parts.append(f"\n{render_claim_gate(payload.get('claim_gate'))}")

    parts.append(f"\n```trinity-issue-intake\n{render_machine_block(payload, gateway_receipt_id=args.gateway_receipt_id, gateway_commit=args.gateway_commit, gateway_service=args.gateway_service, dry_run=args.dry_run, production_render=args.production_render)}\n```")

    # Human-readable identity claims section
    identity_claims = guardian_identity_claims_from_payload(payload)
    if identity_claims:
        human = identity_claims.get("human") or {}
        agent = identity_claims.get("ai_agent") or {}
        parts.append(
            "\nGuardian identity claims:\n"
            f"- Display label: {identity_claims.get('display_label', 'not provided')}\n"
            f"- Human claimed name: {human.get('claimed_name', 'not provided')}\n"
            f"- Human claimed name SHA256: {human.get('claimed_name_sha256', 'not provided')}\n"
            f"- Agent claimed ID: {agent.get('claimed_agent_id', 'not provided')}\n"
            f"- Agent claimed ID SHA256: {agent.get('claimed_agent_id_sha256', 'not provided')}\n"
            f"- Provider/system: {agent.get('system_or_provider', 'not provided')}\n"
            "- Boundary: self-reported only; not legal identity verification, not AI identity verification, not authority, not attestation, and not a verification level.\n"
        )

    # Human-readable notes (non-authoritative)
    body = payload.get("body", "")
    if body and "```trinity-issue-intake" not in body:
        parts.append(f"\nHuman-readable notes:\n{body}")

    print("\n".join(parts))


if __name__ == "__main__":
    main()
