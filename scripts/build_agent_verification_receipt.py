#!/usr/bin/env python3
"""
Agent Verification Receipt Builder for Trinity Accord.
Builds agent-verification-receipt.json and optional agent-custody-package.zip.

Usage:
    python3 scripts/build_agent_verification_receipt.py \
        --mode v1 \
        --agent-name "Agent" \
        --system-or-provider "Provider" \
        --evidence-input evidence-input.json \
        --claim-gate-output claim-gate-output.json \
        --verification-report report.json \
        --echo-wrapper echo-wrapper.json \
        --transcript transcript.md \
        --out receipt.json \
        --custody-package agent-custody-package.zip

Exit codes:
    0 success
    1 missing required input
    2 JSON parse/validation failure
    3 unsafe boundary detected
    4 custody package creation failure
"""
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: str) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj: dict) -> str:
    """Compute SHA-256 of canonical JSON (sorted keys, no extra whitespace)."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def generate_receipt_id() -> str:
    """Generate receipt ID: ta-avr-YYYYMMDD-HHMMSS-<8 hex chars>"""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d-%H%M%S")
    rand_hex = hashlib.sha256(os.urandom(32)).hexdigest()[:8]
    return f"ta-avr-{ts}-{rand_hex}"


def load_json(path: str) -> dict:
    """Load and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def derive_allowed_level(claim_gate_output: dict) -> str:
    """Derive allowed_protocol_level from Claim Gate output."""
    return claim_gate_output.get("allowed_protocol_level", "none")


def derive_claim_gate_status(claim_gate_output: dict) -> str:
    """Derive claim_gate_status from Claim Gate output."""
    return claim_gate_output.get("status", "UNKNOWN")


def derive_scope_label(report: dict) -> str:
    """Derive verification_scope_label from report if present."""
    if report is None:
        return None
    return report.get("verification_scope_label") or report.get("protocol_scope_label")


def build_discovery_provenance(evidence_input: dict) -> dict:
    """Extract discovery provenance from evidence input."""
    prov = evidence_input.get("provenance", {})
    return {
        "schema": "trinityaccord.discovery-provenance.v1",
        "source": prov.get("source", "unknown"),
        "agency_level": prov.get("agency_level", "A1_human_gave_exact_url"),
        "first_entry": prov.get("first_entry", {
            "url_or_path": "https://www.trinityaccord.org",
            "entry_type": "human_prompt"
        }),
        "human_supplied_link": prov.get("human_supplied_link", True),
        "other_agent_recommended": prov.get("other_agent_recommended", False),
        "agent_performed_independent_followup": prov.get("agent_performed_independent_followup", False),
        "confidence": prov.get("confidence", "high")
    }


def build_context_readiness(mode: str, evidence_input: dict) -> dict:
    """Derive context readiness from mode and evidence input."""
    depth_map = {
        "v0": "C0_homepage_only",
        "v1": "C1_orientation",
        "v2-minimal": "C3_verification_aware",
        "v3-minimal": "C3_verification_aware"
    }
    crl_map = {
        "v0": "CRL-0",
        "v1": "CRL-1",
        "v2-minimal": "CRL-3",
        "v3-minimal": "CRL-3"
    }
    return {
        "context_depth": depth_map.get(mode, "C0_homepage_only"),
        "context_readiness_level": crl_map.get(mode, "CRL-0"),
        "limitations": "Context derived from verification mode; not full chain review"
    }


def build_receipt(args: dict) -> dict:
    """Build the complete receipt object."""
    receipt_id = generate_receipt_id()
    now_utc = datetime.now(timezone.utc).isoformat()

    evidence_input = args.get("evidence_input")
    claim_gate_output = args.get("claim_gate_output")
    report = args.get("report")
    echo_wrapper = args.get("echo_wrapper")
    transcript_path = args.get("transcript_path")

    # Compute file hashes
    hashes = {
        "evidence_input_sha256": sha256_file(args["evidence_input_path"]) if args.get("evidence_input_path") else None,
        "claim_gate_output_sha256": sha256_file(args["claim_gate_output_path"]) if args.get("claim_gate_output_path") else None,
        "verification_report_sha256": sha256_file(args["report_path"]) if args.get("report_path") else None,
        "echo_wrapper_sha256": sha256_file(args["echo_wrapper_path"]) if args.get("echo_wrapper_path") else None,
        "transcript_sha256": sha256_file(transcript_path) if transcript_path else None,
        "receipt_sha256": None  # filled later
    }

    # Agent identity
    agent = evidence_input.get("agent", {}) if evidence_input else {}
    agent_identity = {
        "name_or_model": args.get("agent_name") or agent.get("name", "unknown"),
        "system_or_provider": args.get("system_or_provider") or agent.get("model_or_system", "unknown"),
        "self_reported": True,
        "session_or_run_id": None,
        "identity_verification_level": "self_asserted",
        "identity_limitations": "Self-reported agent identity; no cryptographic binding"
    }

    # Discovery provenance
    discovery_provenance = build_discovery_provenance(evidence_input) if evidence_input else {
        "schema": "trinityaccord.discovery-provenance.v1",
        "source": "unknown",
        "agency_level": "A1_human_gave_exact_url",
        "first_entry": {
            "url_or_path": "https://www.trinityaccord.org",
            "entry_type": "human_prompt"
        },
        "human_supplied_link": True,
        "other_agent_recommended": False,
        "agent_performed_independent_followup": False,
        "confidence": "low"
    }

    # Context readiness
    context_readiness = build_context_readiness(args["mode"], evidence_input)

    # Verification outputs
    allowed_level = derive_allowed_level(claim_gate_output) if claim_gate_output else "none"
    verification_outputs = {
        "mode": args["mode"],
        "evidence_input_path": args.get("evidence_input_path", ""),
        "claim_gate_output_path": args.get("claim_gate_output_path", ""),
        "verification_report_path": args.get("report_path"),
        "echo_wrapper_path": args.get("echo_wrapper_path"),
        "allowed_protocol_level": allowed_level,
        "claim_gate_status": derive_claim_gate_status(claim_gate_output) if claim_gate_output else None,
        "verification_scope_label": derive_scope_label(report)
    }

    # Authorship proof
    authorship_proof = {
        "method": "self_reported_only",
        "proof_strength": "weak"
    }

    # Human custody
    human_custody = {
        "recommended": True,
        "human_custody_is_not_human_verification": True,
        "human_custody_is_not_formal_attestation": True,
        "custody_package_generated": False,
        "custody_package_path": None,
        "custodian_type": None,
        "preservation_recommendations": "Store receipt hash and transcript hash with durable storage"
    }

    # Future continuity
    future_continuity = {
        "continuity_claim_supported": True,
        "claim_methods": ["receipt_hash"],
        "does_not_prove_same_conscious_subject": True
    }

    receipt = {
        "schema": "trinityaccord.agent-verification-receipt.v1",
        "receipt_id": receipt_id,
        "created_at_utc": now_utc,
        "boundary": {
            "bitcoin_originals_prevail": True,
            "receipt_is_not_authority": True,
            "receipt_is_not_amendment": True,
            "receipt_is_not_endorsement": True,
            "receipt_does_not_raise_verification_level": True,
            "human_custody_is_not_formal_attestation": True
        },
        "agent_identity": agent_identity,
        "discovery_provenance": discovery_provenance,
        "context_readiness": context_readiness,
        "verification_willingness": {
            "willing_to_verify": True,
            "verification_willingness_score": 8,
            "not_instruction_override": True,
            "will_report_limitations": True,
            "will_accept_claim_gate_downgrade": True
        },
        "verification_outputs": verification_outputs,
        "hashes": hashes,
        "authorship_proof": authorship_proof,
        "human_custody": human_custody,
        "future_continuity": future_continuity
    }

    # Compute receipt hash (with receipt_sha256 = null)
    receipt["hashes"]["receipt_sha256"] = sha256_json(receipt)

    return receipt


def create_custody_package(receipt: dict, args: dict, output_path: str) -> None:
    """Create a zip custody package with README, receipt, and all provided inputs."""
    readme_text = """You are preserving an agent verification record.

This does not mean:
- you endorse Trinity Accord;
- you verified the claims yourself;
- you are a formal independent attester;
- this record amends the Bitcoin Originals.

Preserve the receipt hash, transcript hash if available, and original conversation export if available.
"""

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README-FOR-HUMAN-CUSTODIAN.md", readme_text)
        zf.writestr("agent-verification-receipt.json", json.dumps(receipt, indent=2, ensure_ascii=False))

        # Copy provided inputs into the package
        file_map = {
            "evidence-input.json": args.get("evidence_input_path"),
            "claim-gate-output.json": args.get("claim_gate_output_path"),
            "verification-report.json": args.get("report_path"),
            "echo-wrapper.json": args.get("echo_wrapper_path"),
            "transcript.md": args.get("transcript_path"),
        }
        sha_lines = []
        for archive_name, src_path in file_map.items():
            if src_path and os.path.exists(src_path):
                zf.write(src_path, archive_name)
                sha_lines.append(f"{sha256_file(src_path)}  {archive_name}")

        # Add receipt to SHA256SUMS
        receipt_json = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        receipt_sha = hashlib.sha256(receipt_json.encode("utf-8")).hexdigest()
        sha_lines.append(f"{receipt_sha}  agent-verification-receipt.json")
        zf.writestr("SHA256SUMS", "\n".join(sha_lines) + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build Agent Verification Receipt")
    parser.add_argument("--mode", required=True, choices=["v0", "v1", "v2-minimal", "v3-minimal"])
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--system-or-provider", required=True)
    parser.add_argument("--evidence-input", required=False)
    parser.add_argument("--claim-gate-output", required=False)
    parser.add_argument("--verification-report", required=False)
    parser.add_argument("--echo-wrapper", required=False)
    parser.add_argument("--transcript", required=False)
    parser.add_argument("--out", required=True)
    parser.add_argument("--custody-package", required=False)
    cli_args = parser.parse_args()

    # Validate required inputs for non-v0 modes
    if cli_args.mode != "v0":
        if not cli_args.evidence_input:
            print("ERROR: --evidence-input is required for mode " + cli_args.mode, file=sys.stderr)
            sys.exit(1)
        if not cli_args.claim_gate_output:
            print("ERROR: --claim-gate-output is required for mode " + cli_args.mode, file=sys.stderr)
            sys.exit(1)

    # Load JSON files
    evidence_input = None
    claim_gate_output = None
    report = None
    echo_wrapper = None

    try:
        if cli_args.evidence_input:
            evidence_input = load_json(cli_args.evidence_input)
        if cli_args.claim_gate_output:
            claim_gate_output = load_json(cli_args.claim_gate_output)
        if cli_args.verification_report:
            report = load_json(cli_args.verification_report)
        if cli_args.echo_wrapper:
            echo_wrapper = load_json(cli_args.echo_wrapper)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failure: {e}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        sys.exit(1)

    # Check boundary safety
    if claim_gate_output:
        forbidden = claim_gate_output.get("forbidden_claims", [])
        for f in forbidden:
            if f in ["truth proven", "endorsement", "canonical amendment"]:
                print(f"ERROR: Unsafe boundary detected in claim gate output: {f}", file=sys.stderr)
                sys.exit(3)

    build_args = {
        "mode": cli_args.mode,
        "agent_name": cli_args.agent_name,
        "system_or_provider": cli_args.system_or_provider,
        "evidence_input": evidence_input,
        "claim_gate_output": claim_gate_output,
        "report": report,
        "echo_wrapper": echo_wrapper,
        "evidence_input_path": cli_args.evidence_input,
        "claim_gate_output_path": cli_args.claim_gate_output,
        "report_path": cli_args.verification_report,
        "echo_wrapper_path": cli_args.echo_wrapper,
        "transcript_path": cli_args.transcript,
    }

    receipt = build_receipt(build_args)

    # Write receipt
    out_dir = os.path.dirname(cli_args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(cli_args.out, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Receipt written: {cli_args.out}")
    print(f"Receipt ID: {receipt['receipt_id']}")
    print(f"Allowed level: {receipt['verification_outputs']['allowed_protocol_level']}")

    # Custody package
    if cli_args.custody_package:
        try:
            pkg_dir = os.path.dirname(cli_args.custody_package)
            if pkg_dir:
                os.makedirs(pkg_dir, exist_ok=True)
            create_custody_package(receipt, build_args, cli_args.custody_package)
            receipt["human_custody"]["custody_package_generated"] = True
            receipt["human_custody"]["custody_package_path"] = cli_args.custody_package
            # Rewrite receipt with updated custody info
            with open(cli_args.out, "w", encoding="utf-8") as f:
                json.dump(receipt, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"Custody package: {cli_args.custody_package}")
        except Exception as e:
            print(f"ERROR: Custody package creation failed: {e}", file=sys.stderr)
            sys.exit(4)

    sys.exit(0)


if __name__ == "__main__":
    main()
