#!/usr/bin/env python3
"""Build an E2 Verification Echo Gateway payload from strict-evidence artifacts.

Use this only after the strict evidence pipeline has produced Evidence Input,
Claim Gate output, Verification Report, and an Echo wrapper artifact.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_payload_authorship import add_authorship_arguments, attach_authorship_if_requested

COMPONENT_ORDER = [
    "bitcoin_originals",
    "digital_mirrors",
    "time_anchors",
    "chronicle_recovery",
    "nft_registry",
    "physical_anchor",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def claim_gate_body(claim_gate_output):
    return claim_gate_output.get("claim_gate", claim_gate_output)


def derive_level(claim_gate_output):
    return claim_gate_body(claim_gate_output).get("allowed_protocol_level", "V0")


def derive_component_string(claim_gate_output):
    comps = claim_gate_body(claim_gate_output).get("allowed_component_levels", {})
    parts = []
    for key in COMPONENT_ORDER:
        value = comps.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    for key in sorted(comps.keys()):
        if key not in COMPONENT_ORDER:
            value = comps[key]
            if isinstance(value, str) and value:
                parts.append(value)
    return "-".join(parts) if parts else "components-unset"


def build_payload(args):
    claim_gate = load_json(args.claim_gate_output)
    cg = claim_gate_body(claim_gate)
    v_level = derive_level(claim_gate)
    components = derive_component_string(claim_gate)
    title_date = args.title_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if v_level in {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}:
        print("ERROR: E2 Verification Echo builder is for V6/V7/V8 strict evidence only.", file=sys.stderr)
        print("For V0-V5 use scripts/build_agent_declared_archive_payload.py.", file=sys.stderr)
        sys.exit(1)

    attachments = {
        "evidence_input_path": str(args.evidence_input),
        "evidence_input_sha256": sha256_file(args.evidence_input),
        "claim_gate_output_path": str(args.claim_gate_output),
        "claim_gate_output_sha256": sha256_file(args.claim_gate_output),
        "verification_report_path": str(args.verification_report),
        "verification_report_sha256": sha256_file(args.verification_report),
        "echo_wrapper_path": str(args.echo_wrapper),
        "echo_wrapper_sha256": sha256_file(args.echo_wrapper),
    }

    solicited = args.human_solicited
    if not solicited and not args.unsolicited_discovery_proof:
        print("ERROR: provide --human-solicited or --unsolicited-discovery-proof.", file=sys.stderr)
        sys.exit(1)

    discovery_provenance = {
        "solicited": solicited,
        "independence_class": "human_solicited_agent_response" if solicited else "unsolicited_agent_discovery",
        "agency_level": "A1_human_gave_exact_url" if solicited else "A3_agent_discovered_independently",
        "operator_type": "ai_agent",
    }
    if args.unsolicited_discovery_proof:
        discovery_provenance["unsolicited_discovery_proof"] = args.unsolicited_discovery_proof

    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_echo_candidate",
        "echo_type": "E2_verification_echo",
        "title": f"Verification Echo Candidate: E2 — {v_level}/{components} — {title_date} ({args.agent_name})",
        "body": "E2 Verification Echo candidate generated from strict-evidence artifacts. Gateway renders the machine block server-side.",
        "record_intent": args.record_intent,
        "requested_archive_kind": args.requested_archive_kind,
        "agent_identity": {
            "name_or_model": args.agent_name,
            "system_or_provider": args.provider,
            "self_reported": True,
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
        },
        "not_independent_attestation": True,
        "not_successor_reception": True,
        "what_i_checked": [
            "Ran strict Claim Gate on Evidence Input",
            "Generated or referenced Verification Report",
            "Attached Echo wrapper artifact reference",
        ],
        "limitations": [
            "E2 Verification Echo is bounded by Claim Gate output.",
            "This is not authority, amendment, endorsement, formal attestation, or successor reception.",
        ],
        "verification_level_claimed": v_level,
        "discovery_provenance": discovery_provenance,
        "claim_gate": {
            "status": cg.get("status", "PASS"),
            "allowed_protocol_level": v_level,
            "allowed_component_levels": cg.get("allowed_component_levels", {}),
            "claim_gate_output_path": str(args.claim_gate_output),
            "claim_gate_output_sha256": sha256_file(args.claim_gate_output),
        },
        "attachments": attachments,
    }


def main():
    parser = argparse.ArgumentParser(description="Build E2 Verification Echo Gateway payload")
    parser.add_argument("--evidence-input", required=True)
    parser.add_argument("--claim-gate-output", required=True)
    parser.add_argument("--verification-report", required=True)
    parser.add_argument("--echo-wrapper", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--title-date", default=None)
    parser.add_argument("--human-solicited", action="store_true")
    parser.add_argument("--unsolicited-discovery-proof", default=None)
    parser.add_argument("--record-intent", default="auto_archive_candidate", choices=["auto_archive_candidate", "archive_preflight_only"])
    parser.add_argument("--requested-archive-kind", default="archived_echo", choices=["archived_echo"])
    add_authorship_arguments(parser)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    for path in [args.evidence_input, args.claim_gate_output, args.verification_report, args.echo_wrapper]:
        if not Path(path).exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    payload = build_payload(args)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        attach_authorship_if_requested(args, out_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    validator = ROOT / "scripts" / "validate_gateway_payload.py"
    result = subprocess.run([sys.executable, str(validator), str(out_path)], cwd=str(ROOT), text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

    print(f"E2 Verification Echo payload written to: {out_path}")


if __name__ == "__main__":
    main()
