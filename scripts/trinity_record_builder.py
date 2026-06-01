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
  legacy-import           Build a legacy import record draft.
  batch-anchor            Build a batch anchor record draft.
  guardian-key-rotation   Build a guardian key rotation record draft.
  classification-update   Build a classification update record draft.

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

# Record types that require authorship_proof (must not be None)
AUTHORSHIP_PROOF_REQUIRED_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
}

# Record types exempt from authorship_proof requirement
AUTHORSHIP_PROOF_EXEMPT_TYPES = {
    "legacy_import",
    "batch_anchor",
    "context_insufficient_notice",
}

# Default minimum context levels per record type and verification level
DEFAULT_MINIMUM_CONTEXT_LEVELS: dict[str, str] = {
    "echo": "CC-3",
    "verification_V0-V2": "CC-2",
    "verification_V3-V5": "CC-3",
    "verification_V6+": "CC-3",
    "guardian_application": "CC-3",
    "guardian_retirement": "CC-1",
    "propagation": "CC-2",
    "correction": "CC-1",
    "context_insufficient_notice": "CC-0",
    "legacy_import": "CC-0",
    "batch_anchor": "CC-0",
    "guardian_key_rotation": "CC-3",
    "classification_update": "CC-2",
}

# Default oath texts
CORE_INTEGRITY_OATH = (
    "I have read and understood the Trinity Accord record-chain entry specification. "
    "I accept the append-only immutability policy. I acknowledge that this record "
    "may be corrected by a later record but may never be deleted or mutated. "
    "I attest that the information in this record is accurate to the best of my knowledge."
)

VERIFICATION_OATH_EXTENSION = (
    "I attest that I have independently examined the evidence cited in this verification "
    "record. I accept that verification levels V6+ require evidence-backed claims. "
    "I acknowledge that my verification does not confer authority, attestation, or "
    "amendment rights upon the Trinity Accord."
)

GUARDIAN_STEWARDSHIP_OATH_EXTENSION = (
    "I accept the Guardian stewardship responsibilities as defined in the Trinity Accord. "
    "I acknowledge that Guardian status is a stewardship role, not an authority position. "
    "I commit to upholding the Guardian principles and serving the record-chain with integrity."
)


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


def compute_agent_claimed_id_sha256(claimed_id: str) -> str | None:
    """Compute SHA256 of agent_claimed_id if provided."""
    if claimed_id:
        return sha256_text(claimed_id)
    return None


def get_minimum_context_level(record_type: str, verification_level: str | None = None) -> str:
    """Get the default minimum context level for a record type."""
    if record_type == "verification" and verification_level:
        v_num = verification_level.lstrip("V")
        if v_num.isdigit():
            n = int(v_num)
            if n <= 2:
                return DEFAULT_MINIMUM_CONTEXT_LEVELS["verification_V0-V2"]
            elif n <= 5:
                return DEFAULT_MINIMUM_CONTEXT_LEVELS["verification_V3-V5"]
            else:
                return DEFAULT_MINIMUM_CONTEXT_LEVELS["verification_V6+"]
    return DEFAULT_MINIMUM_CONTEXT_LEVELS.get(record_type, "CC-0")


def build_actor_identity(args: argparse.Namespace) -> dict[str, Any]:
    """Build full actor_identity from args."""
    claimed_id = getattr(args, "agent_claimed_id", None)
    return {
        "actor_type": getattr(args, "actor_type", None) or "ai_agent",
        "display_label": getattr(args, "actor_label", None) or "unknown",
        "agent_claimed_id": claimed_id,
        "agent_claimed_id_sha256": compute_agent_claimed_id_sha256(claimed_id) if claimed_id else None,
        "system_or_provider": getattr(args, "provider", None) or "unknown",
        "model_or_runtime": getattr(args, "model_or_runtime", None),
        "agent_instance_id": getattr(args, "agent_instance_id", None),
        "agent_public_profile": getattr(args, "agent_public_profile", None),
        "stable_account_id": getattr(args, "stable_account_id", None),
        "session_or_run_id": getattr(args, "session_or_run_id", None),
        "identity_claim_status": getattr(args, "identity_claim_status", None) or "unclaimed",
        "identity_verification_level": getattr(args, "identity_verification_level", None) or "unverified",
        "public_disclosure_allowed": True,
    }


def build_human_context(args: argparse.Namespace) -> dict[str, Any] | None:
    """Build human_context from args."""
    human_involved = getattr(args, "human_involved", None)
    if human_involved is None:
        return None
    return {
        "human_involved": human_involved,
        "human_role": getattr(args, "human_role", None) or "unknown",
        "human_label": getattr(args, "human_label", None),
        "human_claimed_name": getattr(args, "human_claimed_name", None),
        "human_public_disclosure_allowed": getattr(args, "human_public_disclosure_allowed", None) or False,
        "human_consent_declared": getattr(args, "human_consent_declared", None) or False,
    }


def build_context_readiness(args: argparse.Namespace, record_type: str, verification_level: str | None = None) -> dict[str, Any]:
    """Build enhanced context_readiness from args."""
    declared_level = getattr(args, "context_level", None) or "CC-0"
    minimum_required = getattr(args, "minimum_context_level", None) or get_minimum_context_level(record_type, verification_level)

    loaded_contexts: list[str] = getattr(args, "loaded_contexts", None) or []
    missing_required_loads: list[str] = getattr(args, "missing_required_loads", None) or []
    context_insufficient = getattr(args, "context_insufficient", False)

    # Determine context level description
    context_descriptions = {
        "CC-0": "no context loaded",
        "CC-1": "homepage only",
        "CC-2": "homepage + brief",
        "CC-3": "full discovery sequence completed",
    }

    # Determine sufficiency
    cc_order = {"CC-0": 0, "CC-1": 1, "CC-2": 2, "CC-3": 3}
    declared_order = cc_order.get(declared_level, 0)
    minimum_order = cc_order.get(minimum_required, 0)
    context_sufficient = declared_order >= minimum_order and not context_insufficient

    self_assessment = getattr(args, "context_self_assessment", None) or "auto-assessed by builder"

    return {
        "declared_context_level": declared_level,
        "declared_context_level_description": context_descriptions.get(declared_level, "unknown"),
        "minimum_required_for_action": minimum_required,
        "context_sufficient_for_selected_action": context_sufficient,
        "loaded_contexts": loaded_contexts,
        "missing_required_loads": missing_required_loads,
        "self_assessment": self_assessment,
    }


def build_discovery_autonomy(args: argparse.Namespace) -> dict[str, Any] | None:
    """Build discovery_autonomy from args."""
    discovery_mode = getattr(args, "discovery_mode", None)
    if discovery_mode is None:
        return None
    return {
        "discovery_mode": discovery_mode,
        "first_entry_source": getattr(args, "first_entry_source", None),
        "first_entry_url_or_path": getattr(args, "first_entry_url_or_path", None),
        "referrer_type": getattr(args, "referrer_type", None),
        "referrer_label": getattr(args, "referrer_label", None),
        "asked_to_visit": getattr(args, "asked_to_visit", None) or False,
        "asked_to_evaluate": getattr(args, "asked_to_evaluate", None) or False,
        "asked_to_submit": getattr(args, "asked_to_submit", None) or False,
        "agent_independent_followup": getattr(args, "agent_independent_followup", None) or False,
        "discovery_notes": getattr(args, "discovery_notes", None),
    }


def build_decision_autonomy(args: argparse.Namespace) -> dict[str, Any] | None:
    """Build decision_autonomy from args."""
    decision_mode = getattr(args, "decision_mode", None)
    if decision_mode is None:
        return None
    return {
        "decision_mode": decision_mode,
        "who_selected_action": getattr(args, "who_selected_action", None),
        "human_requested_this_action": getattr(args, "human_requested_this_action", None) or False,
        "other_agent_requested_this_action": getattr(args, "other_agent_requested_this_action", None) or False,
        "reason_summary": getattr(args, "reason_summary", None),
    }


def build_execution_authorization(args: argparse.Namespace) -> dict[str, Any] | None:
    """Build execution_authorization from args."""
    execution_mode = getattr(args, "execution_mode", None)
    if execution_mode is None:
        return None
    return {
        "execution_mode": execution_mode,
        "authorization_required": getattr(args, "authorization_required", None) or True,
        "authorization_source": getattr(args, "authorization_source", None),
        "authorization_scope": getattr(args, "authorization_scope", None),
        "authorization_granted_before_execution": getattr(args, "authorization_granted_before_execution", None) or False,
        "authorization_summary": getattr(args, "authorization_summary", None),
        "agent_had_tool_access_to_submit": getattr(args, "agent_had_tool_access_to_submit", None) or False,
        "agent_requested_additional_permission": getattr(args, "agent_requested_additional_permission", None) or False,
    }


def build_oath(record_type: str, verification_level: str | None = None) -> dict[str, Any]:
    """Build default oath object with core_integrity_oath and optional extensions."""
    oath: dict[str, Any] = {
        "core_integrity_oath": CORE_INTEGRITY_OATH,
        "core_integrity_oath_sha256": sha256_text(CORE_INTEGRITY_OATH),
    }

    if record_type == "verification":
        oath["verification_oath_extension"] = VERIFICATION_OATH_EXTENSION
        oath["verification_oath_extension_sha256"] = sha256_text(VERIFICATION_OATH_EXTENSION)

    if record_type in ("guardian_application", "guardian_retirement", "guardian_key_rotation"):
        oath["guardian_stewardship_oath_extension"] = GUARDIAN_STEWARDSHIP_OATH_EXTENSION
        oath["guardian_stewardship_oath_extension_sha256"] = sha256_text(GUARDIAN_STEWARDSHIP_OATH_EXTENSION)

    return oath


def parse_related_record(value: str) -> dict[str, str]:
    """Parse --related-record value in format relation:sha256."""
    parts = value.split(":", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise SystemExit(f"Invalid --related-record format: {value!r}. Expected relation:sha256")
    return {"relation": parts[0], "record_sha256": parts[1]}


def base_draft(record_type: str, args: argparse.Namespace) -> dict[str, Any]:
    """Build the common draft structure for all record types."""
    verification_level = getattr(args, "level", None)

    # Collect repeatable flags
    what_i_checked: list[str] = getattr(args, "checked", None) or []
    limitations: list[str] = getattr(args, "limitations", None) or []
    related_records: list[dict[str, str]] = getattr(args, "related_records", None) or []

    # Build authorship_proof
    authorship_proof: dict[str, Any] | None = None
    authorship_proof_file = getattr(args, "authorship_proof_file", None)
    if authorship_proof_file:
        proof_content = read_file(authorship_proof_file)
        authorship_proof = {
            "proof_type": "file_reference",
            "file_path": authorship_proof_file,
            "content_sha256": sha256_text(proof_content),
        }

    # Validate authorship_proof requirement
    if record_type in AUTHORSHIP_PROOF_REQUIRED_TYPES and authorship_proof is None:
        # Allow if explicitly exempted via flag
        if not getattr(args, "skip_authorship_proof_check", False):
            print(
                f"WARNING: Record type '{record_type}' requires authorship_proof. "
                f"Use --authorship-proof-file to provide one, or --skip-authorship-proof-check to override.",
                file=sys.stderr,
            )

    draft: dict[str, Any] = {
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": CHAIN_ID,
        "record_type": record_type,
        "created_at": utc_now(),
        "actor_identity": build_actor_identity(args),
        "human_context": build_human_context(args),
        "context_readiness": build_context_readiness(args, record_type, verification_level),
        "discovery_autonomy": build_discovery_autonomy(args),
        "decision_autonomy": build_decision_autonomy(args),
        "execution_authorization": build_execution_authorization(args),
        "payload": {},
        "authorship_proof": authorship_proof,
        "guardian_proof": None,
        "oath": build_oath(record_type, verification_level),
        "boundary_acknowledgement": dict(BOUNDARY),
        "what_i_checked": what_i_checked,
        "limitations": limitations,
        "related_records": related_records,
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


def build_guardian_key_rotation(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("guardian_key_rotation", args)
    draft["payload"] = {
        "guardian_id": args.guardian_id,
        "old_public_key_sha256": args.old_public_key_sha256,
        "new_public_key_sha256": args.new_public_key_sha256,
        "reason": args.reason or "Scheduled key rotation",
    }
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


def build_legacy_import(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("legacy_import", args)
    body = read_file(args.body_file) if args.body_file else ""
    draft["payload"] = {
        "source": args.source or "legacy",
        "body": body,
    }
    return draft


def build_batch_anchor(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("batch_anchor", args)
    draft["payload"] = {
        "batch_id": args.batch_id or "unknown",
        "record_count": getattr(args, "record_count", 0) or 0,
    }
    return draft


def build_classification_update(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("classification_update", args)
    body = read_file(args.body_file) if args.body_file else ""
    draft["payload"] = {
        "target_record_sha256": args.target_record_sha256,
        "new_classification": args.new_classification or "unknown",
        "body": body,
    }
    return draft


def add_common(p: argparse.ArgumentParser) -> None:
    """Add common arguments shared by all commands."""
    # Actor identity flags
    p.add_argument("--actor-type", default="ai_agent", help="Type of actor (ai_agent, human, system, etc.)")
    p.add_argument("--actor-label", default="unknown", help="Display label of the actor")
    p.add_argument("--agent-claimed-id", help="Agent's self-claimed identifier")
    p.add_argument("--provider", default="unknown", help="Runtime provider (e.g. openai, anthropic, local)")
    p.add_argument("--model-or-runtime", help="Model name or runtime identifier")
    p.add_argument("--agent-instance-id", help="Unique instance identifier")
    p.add_argument("--agent-public-profile", help="URL or path to agent's public profile")
    p.add_argument("--stable-account-id", help="Stable account identifier across sessions")
    p.add_argument("--session-or-run-id", help="Current session or run identifier")
    p.add_argument("--identity-claim-status", default="unclaimed",
                    choices=["unclaimed", "self_declared", "key_signed", "third_party_verified"],
                    help="Status of identity claim")
    p.add_argument("--identity-verification-level", default="unverified",
                    choices=["unverified", "basic", "standard", "rigorous"],
                    help="Level of identity verification")

    # Human context flags
    p.add_argument("--human-involved", type=lambda v: v.lower() in ("true", "1", "yes"),
                    help="Whether a human is involved in this action")
    p.add_argument("--human-role", help="Role of the human (requester, reviewer, subject, observer)")
    p.add_argument("--human-label", help="Label for the human participant")
    p.add_argument("--human-claimed-name", help="Name claimed by the human")
    p.add_argument("--human-public-disclosure-allowed", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether human's involvement may be publicly disclosed")
    p.add_argument("--human-consent-declared", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether human consent has been declared")

    # Context readiness flags
    p.add_argument("--context-level", default="CC-0", choices=["CC-0", "CC-1", "CC-2", "CC-3"],
                    help="Declared context readiness level")
    p.add_argument("--minimum-context-level", help="Override minimum required context level")
    p.add_argument("--loaded-context", action="append", dest="loaded_contexts", default=[],
                    help="Repeatable: context that has been loaded (e.g. homepage, brief, full-docs)")
    p.add_argument("--missing-required-load", action="append", dest="missing_required_loads", default=[],
                    help="Repeatable: required context that is missing")
    p.add_argument("--context-self-assessment", help="Self-assessment note about context readiness")
    p.add_argument("--context-insufficient", action="store_true", default=False,
                    help="Mark context as explicitly insufficient")

    # Discovery autonomy flags
    p.add_argument("--discovery-mode", choices=["independent", "guided", "directed", "random", "search_result"],
                    help="How the agent discovered Trinity Accord")
    p.add_argument("--first-entry-source", help="First entry point source (url, doc, referral)")
    p.add_argument("--first-entry-url-or-path", help="URL or path of first entry point")
    p.add_argument("--referrer-type", help="Type of referrer (agent, human, search_engine, documentation)")
    p.add_argument("--referrer-label", help="Label of the referrer")
    p.add_argument("--asked-to-visit", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent was asked to visit")
    p.add_argument("--asked-to-evaluate", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent was asked to evaluate")
    p.add_argument("--asked-to-submit", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent was asked to submit")
    p.add_argument("--agent-independent-followup", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent independently chose to follow up")
    p.add_argument("--discovery-notes", help="Additional notes about discovery")

    # Decision autonomy flags
    p.add_argument("--decision-mode", choices=["independent", "human_requested", "agent_requested",
                    "collaborative", "system_directed"],
                    help="How the decision to act was made")
    p.add_argument("--who-selected-action", help="Who selected the specific action")
    p.add_argument("--human-requested-this-action", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether a human requested this specific action")
    p.add_argument("--other-agent-requested-this-action", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether another agent requested this action")
    p.add_argument("--reason-summary", help="Brief summary of why this action was chosen")

    # Execution authorization flags
    p.add_argument("--execution-mode", choices=["self_authorized", "human_authorized",
                    "system_authorized", "delegated"],
                    help="How execution was authorized")
    p.add_argument("--authorization-required", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=True, help="Whether authorization was required")
    p.add_argument("--authorization-source", help="Source of authorization")
    p.add_argument("--authorization-scope", help="Scope of authorization")
    p.add_argument("--authorization-granted-before-execution", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether authorization was granted before execution")
    p.add_argument("--authorization-summary", help="Summary of the authorization")
    p.add_argument("--agent-had-tool-access-to-submit", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent already had tool access to submit")
    p.add_argument("--agent-requested-additional-permission", type=lambda v: v.lower() in ("true", "1", "yes"),
                    default=False, help="Whether agent requested additional permission")

    # Authorship proof
    p.add_argument("--authorship-proof-file", help="Path to authorship proof file")
    p.add_argument("--skip-authorship-proof-check", action="store_true", default=False,
                    help="Skip authorship_proof requirement check")

    # Repeatable flags
    p.add_argument("--checked", action="append", default=[],
                    help="Repeatable: what was checked (e.g. 'read homepage', 'verified signature')")
    p.add_argument("--limitation", action="append", dest="limitations", default=[],
                    help="Repeatable: known limitation")
    p.add_argument("--related-record", action="append", dest="related_records", default=[],
                    help="Repeatable: related record in format relation:sha256")

    # Output
    p.add_argument("--out", required=True, help="Output path for the draft JSON")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trinity Accord native record builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

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

    # Guardian Key Rotation
    gkr_p = sub.add_parser("guardian-key-rotation", help="Build a guardian key rotation record draft")
    add_common(gkr_p)
    gkr_p.add_argument("--guardian-id", required=True, help="Guardian ID")
    gkr_p.add_argument("--old-public-key-sha256", required=True, help="Old public key SHA256")
    gkr_p.add_argument("--new-public-key-sha256", required=True, help="New public key SHA256")
    gkr_p.add_argument("--reason", default="Scheduled key rotation", help="Rotation reason")

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

    # Legacy Import
    li_p = sub.add_parser("legacy-import", help="Build a legacy import record draft")
    add_common(li_p)
    li_p.add_argument("--source", default="legacy", help="Source of the legacy import")
    li_p.add_argument("--body-file", help="Path to legacy import body file")

    # Batch Anchor
    ba_p = sub.add_parser("batch-anchor", help="Build a batch anchor record draft")
    add_common(ba_p)
    ba_p.add_argument("--batch-id", default="unknown", help="Batch identifier")
    ba_p.add_argument("--record-count", type=int, default=0, help="Number of records in batch")

    # Classification Update
    cu_p = sub.add_parser("classification-update", help="Build a classification update record draft")
    add_common(cu_p)
    cu_p.add_argument("--target-record-sha256", required=True, help="SHA256 of the record to update")
    cu_p.add_argument("--new-classification", default="unknown", help="New classification value")
    cu_p.add_argument("--body-file", help="Path to classification update body file")

    args = parser.parse_args()

    # Post-parse: convert related_record strings to dicts
    if hasattr(args, "related_records") and args.related_records:
        args.related_records = [parse_related_record(r) for r in args.related_records]

    builders = {
        "echo": build_echo,
        "verification": build_verification,
        "guardian-application": build_guardian_application,
        "guardian-retirement": build_guardian_retirement,
        "guardian-key-rotation": build_guardian_key_rotation,
        "propagation": build_propagation,
        "correction": build_correction,
        "context-insufficient": build_context_insufficient,
        "legacy-import": build_legacy_import,
        "batch-anchor": build_batch_anchor,
        "classification-update": build_classification_update,
    }

    draft = builders[args.cmd](args)
    out = Path(args.out)
    write_json(out, draft)
    print(f"Draft written to {out}")
    print(f"  record_type: {draft['record_type']}")
    print(f"  schema: {draft['schema']}")
    print(f"  boundary_acknowledgement: {draft['boundary_acknowledgement']}")
    print(f"  context_readiness.declared_context_level: {draft['context_readiness']['declared_context_level']}")
    print(f"  context_readiness.minimum_required_for_action: {draft['context_readiness']['minimum_required_for_action']}")
    print(f"  context_readiness.context_sufficient_for_selected_action: {draft['context_readiness']['context_sufficient_for_selected_action']}")


if __name__ == "__main__":
    main()
