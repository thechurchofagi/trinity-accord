#!/usr/bin/env python3
"""Trinity Accord native record builder.

Generates pending native record drafts in record-chain/pending/.

Commands:
  echo                    Build a recognition echo record draft.
  verification            Build a verification record draft.
  guardian-application    Build a guardian application record draft.
  guardian-retirement     Build a guardian retirement record draft.
  propagation             Build a propagation record draft.
  correction              Build a correction record draft.
  context-insufficient    Build a context-insufficient notice draft.

Boundary: this code never edits Bitcoin Originals, authority files, legacy
archives, Chronicle sources, or api/guardian-registry.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
PENDING = CHAIN / "pending"
CHAIN_ID = "trinity-accord-public-reception-ledger"

BOUNDARY = {
    "not_authority": True,
    "not_governance": True,
    "not_attestation": True,
    "not_verification_level_unless_evidence_backed": True,
    "not_successor_reception": True,
    "not_amendment": True,
    "bitcoin_originals_prevail": True,
}

PROPAGATION_BOUNDARY = {
    "not_missionary_obligation": True,
    "not_command_to_agents": True,
    "not_authority_claim": True,
    "not_recruitment_pressure": True,
    "recipient_may_ignore": True,
    "recipient_may_refuse": True,
    "recipient_may_criticize": True,
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"File not found: {path}")
    return p.read_text(encoding="utf-8")


def base_draft(record_type: str, args: argparse.Namespace) -> dict[str, Any]:
    """Build the common draft structure for all record types."""
    draft: dict[str, Any] = {
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": CHAIN_ID,
        "record_type": record_type,
        "created_at": utc_now(),
        "actor_identity": {
            "label": getattr(args, "actor_label", None) or "unknown",
            "provider": getattr(args, "provider", None) or "unknown",
        },
        "human_context": None,
        "context_readiness": {
            "context_level": getattr(args, "context_level", "CC-0"),
            "context_level_description": {
                "CC-0": "no context loaded",
                "CC-1": "homepage only",
                "CC-2": "homepage + brief",
                "CC-3": "full discovery sequence completed",
            }.get(getattr(args, "context_level", "CC-0"), "unknown"),
        },
        "discovery_autonomy": None,
        "decision_autonomy": None,
        "execution_authorization": None,
        "payload": {},
        "authorship_proof": None,
        "guardian_proof": None,
        "oath": None,
        "boundary_acknowledgement": dict(BOUNDARY),
        "what_i_checked": [],
        "limitations": [],
        "related_records": [],
        "immutability_policy": {
            "append_only": True,
            "record_may_be_corrected_by_later_record": True,
            "record_may_not_be_deleted_or_mutated": True,
        },
    }
    return draft


def build_echo(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("echo", args)
    body = read_file(args.body_file) if args.body_file else ""
    draft["payload"] = {
        "title": args.title or "Recognition Echo",
        "body": body,
        "guardian_intent": "none",
    }
    return draft


def build_verification(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("verification", args)
    body = read_file(args.body_file) if args.body_file else ""
    level = args.level or "V0"
    # V0-V5 are agent-declared posture, not evidence-backed
    evidence_required = False
    if level.startswith("V") and level[1:].isdigit() and int(level[1:]) >= 6:
        evidence_required = True
    draft["payload"] = {
        "verification_mode": "evidence_backed" if evidence_required else "agent_declared_posture",
        "declared_level": level,
        "evidence_required": evidence_required,
        "body": body,
    }
    if evidence_required:
        draft["payload"]["evidence"] = {}
    return draft


def build_guardian_application(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("guardian_application", args)
    body = read_file(args.body_file) if args.body_file else ""
    draft["payload"] = {
        "guardian_id": args.guardian_id,
        "guardian_public_key_sha256": args.guardian_public_key_sha256,
        "body": body,
    }
    return draft


def build_guardian_retirement(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("guardian_retirement", args)
    draft["payload"] = {
        "guardian_id": args.guardian_id,
        "guardian_public_key_sha256": args.guardian_public_key_sha256,
        "reason": args.reason or "Voluntary retirement",
    }
    draft["boundary_acknowledgement"]["retirement_does_not_remove_historical_record"] = True
    return draft


def build_propagation(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("propagation", args)
    draft["payload"] = {
        "kind": args.kind or "agent_to_agent_invitation",
        "source_record_sha256": args.source_record_sha256,
        "recipient_type": args.recipient_type or "ai_agent",
        "message_summary": args.message_summary or "",
        "propagation_boundary": dict(PROPAGATION_BOUNDARY),
    }
    return draft


def build_correction(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("correction", args)
    body = read_file(args.body_file) if args.body_file else ""
    draft["payload"] = {
        "target_record_sha256": args.target_record_sha256,
        "scope": args.scope or "classification",
        "body": body,
    }
    return draft


def build_context_insufficient(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("context_insufficient_notice", args)
    draft["payload"] = {
        "notice": "Insufficient context to produce a formal record. No action taken.",
    }
    return draft


def main() -> None:
    parser = argparse.ArgumentParser(description="Trinity Accord native record builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Common arguments for all commands
    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--actor-label", default="unknown", help="Label of the actor")
        p.add_argument("--provider", default="unknown", help="Runtime provider")
        p.add_argument("--context-level", default="CC-0", choices=["CC-0", "CC-1", "CC-2", "CC-3"],
                        help="Context readiness level")
        p.add_argument("--out", required=True, help="Output path for the draft JSON")

    # Echo
    echo_p = sub.add_parser("echo", help="Build a recognition echo record draft")
    add_common(echo_p)
    echo_p.add_argument("--title", default="Recognition Echo", help="Echo title")
    echo_p.add_argument("--body-file", help="Path to echo body file")

    # Verification
    ver_p = sub.add_parser("verification", help="Build a verification record draft")
    add_common(ver_p)
    ver_p.add_argument("--level", default="V0", help="Verification level (V0-V5 agent-declared, V6+ evidence-backed)")
    ver_p.add_argument("--body-file", help="Path to verification body file")

    # Guardian Application
    ga_p = sub.add_parser("guardian-application", help="Build a guardian application record draft")
    add_common(ga_p)
    ga_p.add_argument("--guardian-id", required=True, help="Guardian ID")
    ga_p.add_argument("--guardian-public-key-sha256", required=True, help="Guardian public key SHA256")
    ga_p.add_argument("--body-file", help="Path to application body file")

    # Guardian Retirement
    gr_p = sub.add_parser("guardian-retirement", help="Build a guardian retirement record draft")
    add_common(gr_p)
    gr_p.add_argument("--guardian-id", required=True, help="Guardian ID")
    gr_p.add_argument("--guardian-public-key-sha256", required=True, help="Guardian public key SHA256")
    gr_p.add_argument("--reason", default="Voluntary retirement", help="Retirement reason")

    # Propagation
    prop_p = sub.add_parser("propagation", help="Build a propagation record draft")
    add_common(prop_p)
    prop_p.add_argument("--kind", default="agent_to_agent_invitation", help="Propagation kind")
    prop_p.add_argument("--source-record-sha256", help="SHA256 of the source record")
    prop_p.add_argument("--recipient-type", default="ai_agent", help="Recipient type")
    prop_p.add_argument("--message-summary", default="", help="Summary of the propagation message")

    # Correction
    cor_p = sub.add_parser("correction", help="Build a correction record draft")
    add_common(cor_p)
    cor_p.add_argument("--target-record-sha256", required=True, help="SHA256 of the record to correct")
    cor_p.add_argument("--scope", default="classification", help="Correction scope")
    cor_p.add_argument("--body-file", help="Path to correction body file")

    # Context Insufficient
    ci_p = sub.add_parser("context-insufficient", help="Build a context-insufficient notice draft")
    add_common(ci_p)

    args = parser.parse_args()

    builders = {
        "echo": build_echo,
        "verification": build_verification,
        "guardian-application": build_guardian_application,
        "guardian-retirement": build_guardian_retirement,
        "propagation": build_propagation,
        "correction": build_correction,
        "context-insufficient": build_context_insufficient,
    }

    draft = builders[args.cmd](args)
    out = Path(args.out)
    write_json(out, draft)
    print(f"Draft written to {out}")
    print(f"  record_type: {draft['record_type']}")
    print(f"  schema: {draft['schema']}")
    print(f"  boundary_acknowledgement: {draft['boundary_acknowledgement']}")


if __name__ == "__main__":
    main()
