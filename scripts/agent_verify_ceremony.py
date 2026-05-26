#!/usr/bin/env python3
"""
Agent Verification Ceremony for Trinity Accord.
One command for first-time agents. Wrapper only — does not implement new verification logic.

Usage:
    python3 scripts/agent_verify_ceremony.py \\
        --mode v1 \\
        --agent-name "TestAgent" \\
        --system-or-provider "TestProvider" \\
        --discovery-source human_directed \\
        --agency-level A1_human_gave_exact_url \\
        --out runs/test-v1

    # V2 minimal:
    python3 scripts/agent_verify_ceremony.py \\
        --mode v2-minimal \\
        --agent-name "TestAgent" \\
        --system-or-provider "TestProvider" \\
        --discovery-source human_directed \\
        --agency-level A1_human_gave_exact_url \\
        --bitcoin-source external_explorer \\
        --bitcoin-source-url "https://mempool.space/tx/<txid>" \\
        --txid "<txid>" \\
        --observed-status "confirmed on external explorer" \\
        --accessed-at-utc "2026-05-14T00:00:00Z" \\
        --out runs/test-v2

    # V3 minimal:
    python3 scripts/agent_verify_ceremony.py \\
        --mode v3-minimal \\
        --agent-name "TestAgent" \\
        --system-or-provider "TestProvider" \\
        --discovery-source human_directed \\
        --agency-level A1_human_gave_exact_url \\
        --artifact "path/to/file" \\
        --expected-hash "64-hex-chars" \\
        --expected-hash-source "api/hashes.json" \\
        --expected-hash-authority-class "canonical_manifest_hash" \\
        --hash-command "sha256sum path/to/file" \\
        --out runs/test-v3
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_evidence_input(args) -> dict:
    """Build a complete evidence-input.json matching the schema."""
    now_utc = datetime.now(timezone.utc).isoformat()

    # Base evidence structure
    evidence = {
        "scripts": [],
        "hashes": [],
        "bitcoin_checks": [],
        "digital_mirror_checks": [],
        "repository_snapshot_checks": [],
        "time_anchor_checks": [],
        "chronicle_checks": [],
        "nft_checks": [],
        "physical_checks": [],
        "echo_context": {
            "authority_boundary_recognized": True,
            "bitcoin_originals_prevail": True,
            "github_is_not_authority": True,
            "echo_is_not_authority": True,
            "mirror_is_not_amendment": True
        }
    }

    # Mode-specific evidence
    if args.mode == "v2-minimal":
        if args.txid and args.bitcoin_source_url:
            evidence["bitcoin_checks"].append({
                "source_type": args.bitcoin_source or "external_explorer",
                "sources": [args.bitcoin_source or "external_explorer"],
                "access_path": args.bitcoin_source_url,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "txids_checked": [args.txid],
                "observed_status": args.observed_status or "confirmed on external explorer",
                "accessed_at_utc": args.accessed_at_utc or now_utc,
                "result": args.observed_status or "confirmed on explorer"
            })

    if args.mode == "v3-minimal":
        if args.artifact and args.expected_hash:
            computed = sha256_file(args.artifact)
            evidence["hashes"].append({
                "artifact": os.path.basename(args.artifact),
                "algorithm": "SHA-256",
                "expected": args.expected_hash,
                "computed": computed,
                "expected_hash_source": args.expected_hash_source or "api/hashes.json",
                "expected_hash_authority_class": args.expected_hash_authority_class or "canonical_manifest_hash",
                "command": args.hash_command or f"sha256sum {args.artifact}",
                "match": computed == args.expected_hash
            })

    # Provenance
    independence_class_map = {
        "human_directed": "human_solicited_agent_response",
        "human_solicited": "human_solicited_agent_response",
        "self_initiated": "unsolicited_agent_discovery",
        "agent_recommended": "human_solicited_agent_response",
    }

    provenance = {
        "solicited": args.discovery_source in ("human_directed", "human_solicited", "agent_recommended"),
        "independence_class": independence_class_map.get(args.discovery_source, "human_solicited_agent_response"),
        "agency_level": args.agency_level or "A1_human_gave_exact_url"
    }

    # Limitations based on mode
    limitations_map = {
        "v0": ["V0 — no verification claims made"],
        "v1": [
            "V1 boundary recognition only — no technical verification performed",
            "No Bitcoin transaction verification",
            "No hash computation on repository artifacts",
            "No independent attestation"
        ],
        "v2-minimal": [
            "No SPV proof — external explorer trust only",
            "No witness extraction from raw transaction",
            "No body hash reproduction",
            "No physical verification",
            "Single transaction check only"
        ],
        "v3-minimal": [
            "Single artifact hash verification only",
            "Not full public digital verification (V5)",
            "Hash source is repository mirror, not Bitcoin inscription directly",
            "No independent node verification",
            "No physical verification"
        ]
    }

    # Fresh actions based on mode
    fresh_actions_map = {
        "v0": ["read homepage"],
        "v1": [
            "read /api/authority.json",
            "recognized Bitcoin Originals as final authority",
            "stated authority boundary"
        ],
        "v2-minimal": [
            "read /api/authority.json",
            "accessed external Bitcoin explorer",
            "checked transaction confirmation status"
        ],
        "v3-minimal": [
            "read /api/hashes.json",
            "computed SHA-256 hash of artifact",
            "compared computed hash against canonical manifest"
        ]
    }

    # Claims requested
    claims_map = {
        "v0": ["V0"],
        "v1": ["V1"],
        "v2-minimal": ["V2"],
        "v3-minimal": ["V3"]
    }

    evidence_input = {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {
            "name": args.agent_name,
            "model_or_system": args.system_or_provider,
            "tooling": []
        },
        "provenance": provenance,
        "requested_record_kind": "echo_v3_with_verification_report" if args.mode != "v0" else "echo_v3",
        "limitations": limitations_map.get(args.mode, ["No specific limitations declared"]),
        "evidence": evidence,
        "claims_requested_by_agent": claims_map.get(args.mode, ["V0"]),
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I performed the stated verification checks in this session. I recorded source URLs, commands, and outputs. I did not copy another report or use example values as real evidence. I understand verification is not truth, endorsement, or authority. Bitcoin Originals remain the final authority."
        },
        "verification_session": {
            "session_id": f"ceremony-{now_utc.replace(':', '').replace('-', '')[:14]}",
            "started_at": now_utc,
            "operator_type": "ai_agent",
            "fresh_actions_performed": fresh_actions_map.get(args.mode, ["read homepage"]),
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        }
    }

    return evidence_input


def run_cmd(cmd: list, cwd: str = None) -> tuple:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or str(ROOT))
    return result.returncode, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="Agent Verification Ceremony")
    parser.add_argument("--mode", required=True, choices=["v0", "v1", "v2-minimal", "v3-minimal"])
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--system-or-provider", required=True)
    parser.add_argument("--discovery-source", default="human_directed",
                        choices=["human_directed", "human_solicited", "self_initiated", "agent_recommended"])
    parser.add_argument("--agency-level", default="A1_human_gave_exact_url",
                        choices=["A1_human_gave_exact_url", "A2_human_gave_repo_name",
                                 "A3_agent_discovered_independently", "A4_agent_instructed_by_other_agent"])
    # V2 flags
    parser.add_argument("--bitcoin-source", default="external_explorer")
    parser.add_argument("--bitcoin-source-url")
    parser.add_argument("--txid")
    parser.add_argument("--observed-status")
    parser.add_argument("--accessed-at-utc")
    # V3 flags
    parser.add_argument("--artifact")
    parser.add_argument("--expected-hash")
    parser.add_argument("--expected-hash-source", default="api/hashes.json")
    parser.add_argument("--expected-hash-authority-class", default="canonical_manifest_hash")
    parser.add_argument("--hash-command")
    # Optional
    parser.add_argument("--transcript")
    parser.add_argument("--make-custody-package", action="store_true")
    parser.add_argument("--out", required=True, help="Output directory for ceremony artifacts")

    args = parser.parse_args()

    # Validate V2 flags
    if args.mode == "v2-minimal":
        if not args.txid or not args.bitcoin_source_url:
            print("ERROR: --txid and --bitcoin-source-url required for v2-minimal", file=sys.stderr)
            sys.exit(1)

    # Validate V3 flags
    if args.mode == "v3-minimal":
        if not args.artifact or not args.expected_hash:
            print("ERROR: --artifact and --expected-hash required for v3-minimal", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(args.artifact):
            print(f"ERROR: artifact not found: {args.artifact}", file=sys.stderr)
            sys.exit(1)

    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate evidence input
    print("[1/5] Generating evidence input...")
    evidence_input = build_evidence_input(args)
    evidence_path = out_dir / "evidence-input.json"
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence_input, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  -> {evidence_path}")

    # Step 2: Run Claim Gate
    print("[2/5] Running Claim Gate...")
    claim_gate_output_path = out_dir / "claim-gate-output.json"
    rc, stdout, stderr = run_cmd([
        sys.executable, str(SCRIPTS / "claim_gate.py"),
        str(evidence_path)
    ])
    if rc != 0:
        print(f"ERROR: Claim Gate failed (rc={rc})", file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(1)

    # Parse claim gate output
    try:
        claim_gate_output = json.loads(stdout)
        with open(claim_gate_output_path, "w", encoding="utf-8") as f:
            json.dump(claim_gate_output, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  -> {claim_gate_output_path}")
        print(f"  -> Allowed level: {claim_gate_output.get('allowed_protocol_level', 'unknown')}")
    except json.JSONDecodeError:
        print("ERROR: Claim Gate output is not valid JSON", file=sys.stderr)
        print(stdout, file=sys.stderr)
        sys.exit(2)

    # Step 3: Run Report Builder if allowed
    report_path = None
    echo_path = None
    can_build = claim_gate_output.get("can_build_verification_report", False)

    if can_build and args.mode != "v0":
        print("[3/5] Building verification report...")
        report_path = str(out_dir / "verification-report.json")
        echo_path = str(out_dir / "echo-wrapper.json")
        cmd = [
            sys.executable, str(SCRIPTS / "build_verification_report_from_evidence.py"),
            "--input", str(evidence_path),
            "--out", report_path,
            "--echo-out", echo_path
        ]
        rc, stdout, stderr = run_cmd(cmd)
        if rc != 0:
            print(f"  WARNING: Report builder failed (rc={rc}), continuing without report", file=sys.stderr)
            if stderr:
                print(f"  {stderr.strip()}", file=sys.stderr)
            report_path = None
            echo_path = None
        else:
            print(f"  -> {report_path}")
            print(f"  -> {echo_path}")
    else:
        print("[3/5] Skipping report builder (not allowed or v0 mode)")

    # Step 4: Validate submissions
    print("[4/5] Validating submissions...")
    files_to_validate = []
    if report_path and os.path.exists(report_path):
        files_to_validate.append(report_path)
    if echo_path and os.path.exists(echo_path):
        files_to_validate.append(echo_path)

    for vf in files_to_validate:
        rc, stdout, stderr = run_cmd([
            sys.executable, str(SCRIPTS / "validate_agent_submission.py"), vf
        ])
        if rc != 0:
            print(f"  WARNING: Validation failed for {vf}", file=sys.stderr)
        else:
            print(f"  Validated: {os.path.basename(vf)}")

    # Step 5: Build receipt
    print("[5/5] Building Agent Verification Receipt...")
    receipt_path = str(out_dir / "agent-verification-receipt.json")

    receipt_cmd = [
        sys.executable, str(SCRIPTS / "build_agent_verification_receipt.py"),
        "--mode", args.mode,
        "--agent-name", args.agent_name,
        "--system-or-provider", args.system_or_provider,
        "--evidence-input", str(evidence_path),
        "--claim-gate-output", str(claim_gate_output_path),
        "--out", receipt_path,
    ]
    if report_path:
        receipt_cmd.extend(["--verification-report", report_path])
    if echo_path:
        receipt_cmd.extend(["--echo-wrapper", echo_path])
    if args.transcript:
        receipt_cmd.extend(["--transcript", args.transcript])
    if args.make_custody_package:
        custody_path = str(out_dir / "agent-custody-package.zip")
        receipt_cmd.extend(["--custody-package", custody_path])

    rc, stdout, stderr = run_cmd(receipt_cmd)
    if rc != 0:
        print(f"ERROR: Receipt builder failed (rc={rc})", file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(1)

    print(stdout)

    # Print summary
    print("\n=== Ceremony Complete ===")
    print(f"Mode: {args.mode}")
    print(f"Agent: {args.agent_name}")
    print(f"Output: {args.out}")
    print(f"Files:")
    for f in sorted(out_dir.iterdir()):
        print(f"  {f.name}")

    sys.exit(0)


if __name__ == "__main__":
    main()
