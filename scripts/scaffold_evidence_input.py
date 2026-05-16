#!/usr/bin/env python3
"""Scaffold an Evidence Input JSON to avoid common agent mistakes.

Generates a valid-structure evidence input with correct field placement
(bitcoin_checks under evidence, not top level).

Usage:
    python3 scripts/scaffold_evidence_input.py \
        --mode v4-external-explorer \
        --agent-name "Guardian" \
        --provider "Coze AI Agent" \
        --human-solicited \
        --out evidence-input.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_scaffold(args):
    """Build a scaffold evidence input based on mode."""
    now = datetime.now(timezone.utc).isoformat()

    # Common agent info
    agent = {
        "name": args.agent_name,
        "model_or_provider": args.provider,
        "tooling": ["web_fetch", "exec"]
    }

    # Common provenance
    provenance = {
        "solicited": args.human_solicited,
        "independence_class": "human_solicited_agent_response" if args.human_solicited else "unsolicited_agent_discovery",
        "agency_level": "A1_human_gave_exact_url" if args.human_solicited else "A3_agent_discovered_independently"
    }

    # Mode-specific bitcoin_checks
    if args.mode == "v4-external-explorer":
        bitcoin_checks = [
            {
                "source_type": "external_explorer",
                "sources": [],
                "inscription_id": "",
                "confirmed": False,
                "note": "Fill in: verified via public ordinals explorer"
            }
        ]
        limitations = [
            "External explorer verification only — no SPV, body-hash, or physical verification",
            "No independent attestation claimed",
            "No physical anchor verification performed"
        ]
    elif args.mode == "b6-body-hash":
        bitcoin_checks = [
            {
                "source_type": "body_hash",
                "sources": [],
                "inscription_id": "",
                "body_hash_reproduced": False,
                "body_hash_value": "",
                "note": "Fill in: body hash reproduction from raw witness data"
            }
        ]
        limitations = [
            "Body hash reproduction — set body_hash_reproduced=true only if actually verified",
            "No SPV or local node verification performed",
            "No independent attestation claimed"
        ]
    else:
        bitcoin_checks = []
        limitations = ["Mode not recognized — customize this scaffold"]

    # Build the evidence input
    evidence_input = {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": agent,
        "provenance": provenance,
        "requested_record_kind": "verification_report_v2",
        "evidence": {
            "scripts": [
                {
                    "path": "scripts/claim_gate.py",
                    "exists": True,
                    "source_reviewed": False,
                    "executed": False,
                    "result": ""
                }
            ],
            "hashes": [],
            "bitcoin_checks": bitcoin_checks,
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": [],
            "echo_context": {}
        },
        "agent_integrity_declaration": {
            "self_reported": True,
            "tools_used": agent.get("tooling", []),
            "limitations_acknowledged": True
        },
        "verification_session": {
            "session_id": args.session_id or "fill-in-session-id",
            "started_at": now,
            "completed_at": None
        },
        "limitations": limitations,
        "claims_requested_by_agent": {}
    }

    return evidence_input


def main():
    parser = argparse.ArgumentParser(description="Scaffold an Evidence Input JSON")
    parser.add_argument("--mode", required=True, choices=["v4-external-explorer", "b6-body-hash"],
                        help="Scaffold mode")
    parser.add_argument("--agent-name", default="unknown-agent", help="Agent name")
    parser.add_argument("--provider", default="unknown-provider", help="System or provider")
    parser.add_argument("--human-solicited", action="store_true", help="Mark as human-solicited")
    parser.add_argument("--session-id", default=None, help="Session ID")
    parser.add_argument("--out", required=True, help="Output path")

    args = parser.parse_args()

    scaffold = build_scaffold(args)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(scaffold, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Evidence input scaffold written to: {out_path}")
    print(f"Mode: {args.mode}")
    print(f"Human solicited: {args.human_solicited}")

    # Validate JSON structure
    try:
        json.loads(out_path.read_text())
        print("JSON validation: PASS")
    except json.JSONDecodeError as e:
        print(f"JSON validation: FAIL — {e}")
        sys.exit(1)

    # Try running claim gate if available
    claim_gate = ROOT / "scripts" / "claim_gate.py"
    if claim_gate.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(claim_gate), str(out_path)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )
        print(f"\nClaim Gate test run (exit {result.returncode}):")
        print(result.stdout[:500])
        if result.returncode != 0:
            print("NOTE: Claim Gate may fail on scaffold — fill in required fields before real use")


if __name__ == "__main__":
    main()
