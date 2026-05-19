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


def render_issue_title(payload):
    """Generate issue title from payload, with special handling for pure echo."""
    identity = payload.get("agent_identity") or {}
    requested_archive_kind = payload.get("requested_archive_kind", "none")
    title = payload.get("title", "")
    short_title = title[:80] if title else ""

    if requested_archive_kind == "agent_declared_echo_archive":
        echo_type = payload.get("echo_type", "")
        if echo_type == "E5_correction_echo":
            return f"[Agent Gateway] Correction Echo: {identity.get('name_or_model', 'Agent')} — {short_title}"
        else:
            return f"[Agent Gateway] Agent-Declared Echo Archive: {echo_type} — {short_title}"

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

    # Echo type only for echo candidates
    if st == "verification_echo_candidate":
        lines.append("echo_type: E2_verification_echo")

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
        lines.append(f"agent_readback_sha256: {sha256_text(readback) if readback else 'N/A'}")
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
    elif requested_archive_kind == "agent_declared_echo_archive":
        lines.append(f"record_intent: {payload.get('record_intent', 'auto_archive_candidate')}")
        lines.append("requested_archive_kind: agent_declared_echo_archive")
        lines.append(f"echo_type: {payload.get('echo_type', 'N/A')}")
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
        lines.append(f"agent_readback_sha256: {sha256_text(readback) if readback else 'N/A'}")
        if readback:
            lines.append(f'agent_readback_excerpt: "{one_line_excerpt(readback)}"')

        dp = payload.get("discovery_provenance") or {}
        lines.append(f"discovery_provenance_present: {'true' if dp else 'false'}")
        ab = payload.get("authority_boundary") or {}
        lines.append(f"authority_boundary_present: {'true' if ab else 'false'}")

        lines.append("counts_toward_home_verifiability: false")
        lines.append("counts_toward_home_reception: true")
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
    if requested_archive_kind not in ("agent_declared_verification_archive", "agent_declared_echo_archive"):
        lines.extend(render_authorship_claim_fields(payload))

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
    if requested_archive_kind not in ("agent_declared_verification_archive", "agent_declared_echo_archive"):
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
    rendered_title = render_issue_title(payload)
    parts.append(f"# {rendered_title}\n")
    parts.append("This issue was submitted through the Agent Issue Gateway backend.\n")
    parts.append(render_boundary())
    parts.append(f"\nSubmission type:\n{st}")
    parts.append(f"\n{render_claim_gate(payload.get('claim_gate'))}")
    parts.append(f"\n```trinity-issue-intake\n{render_machine_block(payload, gateway_receipt_id=args.gateway_receipt_id, gateway_commit=args.gateway_commit, gateway_service=args.gateway_service, dry_run=args.dry_run, production_render=args.production_render)}\n```")

    # Human-readable notes (non-authoritative)
    body = payload.get("body", "")
    if body and "```trinity-issue-intake" not in body:
        parts.append(f"\nHuman-readable notes:\n{body}")

    print("\n".join(parts))


if __name__ == "__main__":
    main()
