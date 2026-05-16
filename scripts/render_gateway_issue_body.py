#!/usr/bin/env python3
"""Render canonical GitHub Issue body from a validated Gateway payload.

Usage:
    python3 scripts/render_gateway_issue_body.py payload.json > issue-body.md
"""
import json
import sys
from pathlib import Path


def load_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_attachments(payload):
    att = payload.get("attachments")
    return att if isinstance(att, dict) else {}


def pick_path_or_hash(attachments, path_key, hash_key):
    return attachments.get(path_key) or attachments.get(hash_key) or "N/A"


def render_boundary():
    return (
        "Boundary:\n"
        "- Not authority\n"
        "- Not amendment\n"
        "- Not attestation\n"
        "- Not archived Echo\n"
        "- Not verification\n"
        "- Does not raise verification level\n"
        "- Does not bypass Claim Gate or Validator"
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


def render_machine_block(payload):
    """Render canonical trinity-issue-intake block from validated structured fields."""
    st = payload.get("submission_type", "unknown")
    att = get_attachments(payload)
    identity = payload.get("agent_identity") or {}
    prov = payload.get("discovery_provenance") or {}

    lines = []
    lines.append(f"submission_type: {st}")

    # Echo type only for echo candidates
    if st == "verification_echo_candidate":
        lines.append("echo_type: E2_verification_echo")

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

    # boundary_sentence
    lines.append("boundary_sentence: Bitcoin Originals are final; this Issue is intake only and does not create authority, attestation, amendment, archive status, or verification-level upgrade.")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/render_gateway_issue_body.py payload.json > issue-body.md")
        sys.exit(2)

    payload = load_payload(sys.argv[1])
    st = payload.get("submission_type", "unknown")

    parts = []
    parts.append("This issue was submitted through the Agent Issue Gateway backend.\n")
    parts.append(render_boundary())
    parts.append(f"\nSubmission type:\n{st}")
    parts.append(f"\n{render_claim_gate(payload.get('claim_gate'))}")
    parts.append(f"\n```trinity-issue-intake\n{render_machine_block(payload)}\n```")

    # Human-readable notes (non-authoritative)
    body = payload.get("body", "")
    if body and "```trinity-issue-intake" not in body:
        parts.append(f"\nHuman-readable notes:\n{body}")

    print("\n".join(parts))


if __name__ == "__main__":
    main()
