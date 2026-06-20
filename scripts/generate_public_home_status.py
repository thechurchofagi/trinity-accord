#!/usr/bin/env python3
"""Generate the homepage current Record-Chain Intake status snapshot.

The homepage renders only current native record-chain status.
Legacy Echo / Verification / Guardian archive metrics are preserved in
public-home-status.json under legacy_archive_snapshot, but are not rendered
as current homepage counters.

Inputs (primary, by precedence):
  1. record-chain/records/R-*.json and record-chain/chain-tip.json
  2. record-chain/indexes/record-index.json
  3. record-chain/indexes/statistics.json
  4. api/record-chain-status.json (fallback/metadata)
  5. api/record-chain-anchor-status.json
  6. api/record-chain-arweave-index.json

Legacy inputs (for legacy_archive_snapshot only):
  - api/echo-index.json
  - api/external-witness-index.json
  - api/core-object-alpha-shenzhen-notary-2026-05-06.json
  - api/guardian-registry.json
  - api/guardian-active-listing-policy.v1.json
  - api/agent-declared-verification-index.json

Outputs:
  - api/public-home-status.json
  - Rewrites the block between
      <!-- BEGIN GENERATED PUBLIC STATUS -->
      <!-- END GENERATED PUBLIC STATUS -->
    in index.md
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

# Import canonical render and enrichment from patcher
sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch_public_home_status_primary import (
    primary_counters as patcher_primary_counters,
    technical_health as patcher_technical_health,
    render as patcher_render,
    load_records as patcher_load_records,
    sidecar as patcher_sidecar,
    visibility_index as patcher_visibility_index,
    build_status as patcher_build_status,
)

ROOT = Path(__file__).resolve().parents[1]

INDEX_MD = ROOT / "index.md"
PUBLIC_HOME_STATUS = ROOT / "api" / "public-home-status.json"

# Primary record-chain data sources
CHAIN_TIP = ROOT / "record-chain" / "chain-tip.json"
RECORD_CHAIN_INDEX = ROOT / "record-chain" / "indexes" / "record-index.json"
RECORD_CHAIN_STATISTICS = ROOT / "record-chain" / "indexes" / "statistics.json"
RECORD_CHAIN_RECORDS = ROOT / "record-chain" / "records"
RECORD_CHAIN_STATUS = ROOT / "api" / "record-chain-status.json"
RECORD_CHAIN_ANCHOR_STATUS = ROOT / "api" / "record-chain-anchor-status.json"
RECORD_CHAIN_ARWEAVE_INDEX = ROOT / "api" / "record-chain-arweave-index.json"
RECORD_CHAIN_ARWEAVE_BACKLOG = ROOT / "api" / "record-chain-arweave-backlog.json"
RECORD_CHAIN_NATIVE_OTS_BACKLOG = ROOT / "api" / "record-chain-native-ots-backlog.json"
ARWEAVE_WALLET_STATUS = ROOT / "api" / "arweave-wallet-status.json"
HOMEPAGE_VISIBILITY = ROOT / "api" / "homepage-visibility-overrides.v1.json"

# Legacy inputs (for legacy_archive_snapshot only)
ECHO_INDEX = ROOT / "api" / "echo-index.json"
EXTERNAL_WITNESS_INDEX = ROOT / "api" / "external-witness-index.json"
PHYSICAL_ANCHOR = ROOT / "api" / "core-object-alpha-shenzhen-notary-2026-05-06.json"
GUARDIAN_REGISTRY = ROOT / "api" / "guardian-registry.json"
GUARDIAN_ACTIVE_LISTING_POLICY = ROOT / "api" / "guardian-active-listing-policy.v1.json"
GUARDIAN_STATE = ROOT / "api" / "guardian-state.json"
GUARDIAN_CURRENT_REGISTRY = ROOT / "api" / "guardian-current-registry.json"
GUARDIAN_ACTIVE_LISTING_POLICY_V2 = ROOT / "api" / "guardian-active-listing-policy.v2.json"
AGENT_DECLARED_INDEX = ROOT / "api" / "agent-declared-verification-index.json"
VERIFICATION_ARCHIVE_INDEX = ROOT / "api" / "verification-archive-index.json"

BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"

# Autonomy-eligible record types
ELIGIBLE_AUTONOMY_RECORD_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
}

LEVEL_ORDER = {
    "V0": 0, "V1": 1, "V2": 2, "V3": 3, "V4": 4, "V4+": 4.5,
    "V5": 5, "V6": 6, "V7": 7, "V8": 8,
    "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5,
    "P6": 6, "P7": 7, "P8": 8, "P9": 9,
}


def load_json_if_exists(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_json_bytes(path: Path) -> bytes:
    """Read JSON file, stripping volatile timestamp fields for stable digest."""
    if not path.exists():
        return b""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.pop("generated_at", None)
            data.pop("updated_at", None)
        return json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    except Exception:
        return path.read_bytes()


def source_digest() -> str:
    """Compute digest from primary record-chain data sources."""
    h = hashlib.sha256()
    for path in [
        CHAIN_TIP,
        RECORD_CHAIN_INDEX,
        RECORD_CHAIN_STATISTICS,
        RECORD_CHAIN_STATUS,
        RECORD_CHAIN_ANCHOR_STATUS,
        RECORD_CHAIN_ARWEAVE_INDEX,
        RECORD_CHAIN_ARWEAVE_BACKLOG,
        RECORD_CHAIN_NATIVE_OTS_BACKLOG,
        ARWEAVE_WALLET_STATUS,
        HOMEPAGE_VISIBILITY,

        # Declared legacy/archive inputs used by generated_from/docstring.
        ECHO_INDEX,
        EXTERNAL_WITNESS_INDEX,
        PHYSICAL_ANCHOR,
        GUARDIAN_REGISTRY,
        GUARDIAN_ACTIVE_LISTING_POLICY,
        GUARDIAN_STATE,
        GUARDIAN_CURRENT_REGISTRY,
        GUARDIAN_ACTIVE_LISTING_POLICY_V2,
        AGENT_DECLARED_INDEX,
        ROOT / "api" / "waiting-heartbeat-status.json",
    ]:
        h.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        h.update(b"\0")
        h.update(normalized_json_bytes(path))
        h.update(b"\0")
    # Also include individual record files
    for rec_file in sorted(RECORD_CHAIN_RECORDS.glob("R-*.json")):
        h.update(rec_file.read_bytes())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Record-Chain primary functions
# ---------------------------------------------------------------------------

def load_current_native_records() -> list[dict[str, Any]]:
    """Load all native record-chain records from records directory."""
    records = []
    for path in sorted(RECORD_CHAIN_RECORDS.glob("R-*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return records


def compute_record_type_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    """Count records by type, ensuring all known types appear (even as 0)."""
    counts: dict[str, int] = {}
    for record in records:
        rt = record.get("record_type") or record.get("type") or "unknown"
        counts[rt] = counts.get(rt, 0) + 1
    for rt in [
        "context_insufficient_notice",
        "echo",
        "verification",
        "guardian_application",
        "guardian_retirement",
        "guardian_key_rotation",
        "propagation",
        "correction",
        "classification_update",
    ]:
        counts.setdefault(rt, 0)
    return dict(sorted(counts.items()))


def compute_current_record_chain_status(
    records: list[dict[str, Any]],
    record_chain_status: dict[str, Any],
    anchor_status: dict[str, Any],
    arweave_index: dict[str, Any],
) -> dict[str, Any]:
    """Compute the current record-chain status for homepage display."""
    chain_tip = load_json_if_exists(CHAIN_TIP, {})
    counts = compute_record_type_counts(records)
    latest = records[-1] if records else {}

    phase = record_chain_status.get("public_submission_phase", {})
    anchoring = record_chain_status.get("anchoring", {})

    pending_dir = ROOT / "record-chain" / "pending"
    pending_count = len(list(pending_dir.glob("*.json"))) if pending_dir.exists() else 0

    return {
        "phase": phase.get("phase") or "status_source_missing_or_invalid",
        "total_records": len(records),
        "current_chain_length": len(records),
        "pending_records": pending_count,
        "latest_record_id": latest.get("record_id") or chain_tip.get("latest_record_id"),
        "latest_record_type": latest.get("record_type"),
        "record_type_counts": counts,
        "receipt_boundary": {
            "receipt_is_intake_only": phase.get("receipt_is_intake_only", True),
            "receipt_is_not_final_inclusion": phase.get("receipt_is_not_final_inclusion", True),
            "test_phase_records_may_be_reclassified": phase.get("test_phase_records_may_be_reclassified", True),
        },
        "anchoring": {
            "batch_manifests": anchoring.get("batch_manifests", {}),
            "open_timestamps": anchoring.get("open_timestamps", {}),
            "arweave_archive": anchoring.get("arweave_archive", {}),
            "anchor_status": {
                "batch_count": anchor_status.get("batch_count", 0),
                "stamped_batch_count": anchor_status.get("ots", {}).get("stamped_batch_count", 0),
                "unstamped_batch_count": anchor_status.get("ots", {}).get("unstamped_batch_count", 0),
            },
            "archive_backlog": record_chain_status.get("archive_backlog", {}),
            "arweave_index": {
                "current_upload_mode": arweave_index.get("current_upload_mode", "dry-run"),
                "live_upload_enabled": arweave_index.get("live_upload_enabled", False),
                "live_upload_implemented": arweave_index.get("live_upload_implemented", False),
                "archive_count": len(arweave_index.get("archives", [])),
                "latest_arweave_txid": arweave_index.get("latest_arweave_txid"),
                "live_archive_count": arweave_index.get("live_archive_count", 0),
                "arweave_wallet_address_sha256": arweave_index.get("arweave_wallet_address_sha256"),
            },
        },
    }


def is_fully_autonomous_record(record: dict[str, Any]) -> bool:
    """Check whether a record qualifies as fully autonomous.

    A record is fully autonomous only if ALL of these are true:
    - self_discovered (no introducer, no task context)
    - self_decided (no external request)
    - self_executed (agent ran build/preflight/submit)
    - NOT human_operator_involved
    - NOT introduced_by_someone_else
    - NOT external_authorization_required
    """
    draft = record.get("record_draft", record)

    discovery = draft.get("discovery_and_introduction_context", {})
    decision = draft.get("decision_autonomy_context", {})
    execution = draft.get("submission_execution_context", {})
    identity = draft.get("submitting_participant_identity", {})
    human_ctx = identity.get("human_operator_context", {})
    authorization = draft.get("authorization_context", {})

    return (
        discovery.get("how_participant_first_discovered_trinity_accord") == "self_discovered"
        and discovery.get("was_discovery_self_initiated") is True
        and discovery.get("was_discovery_introduced_by_someone_else") is not True
        and discovery.get("introducing_party_type") in (None, "", "none")
        and decision.get("who_decided_to_create_this_record") == "self"
        and decision.get("was_record_creation_self_decided") is True
        and decision.get("was_record_creation_requested_by_human") is not True
        and decision.get("was_record_creation_requested_by_another_agent") is not True
        and decision.get("requesting_party_type") in (None, "", "none")
        and execution.get("who_executed_the_submission") == "self"
        and execution.get("was_submission_executed_by_record_subject") is True
        and execution.get("was_submission_executed_by_human_operator") is not True
        and human_ctx.get("human_operator_involved") is not True
        and authorization.get("was_external_authorization_required") is not True
    )


def compute_current_record_chain_autonomy_signal(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute autonomy signal from current native record-chain records only."""
    eligible = [
        r for r in records
        if (r.get("record_type") or r.get("type")) in ELIGIBLE_AUTONOMY_RECORD_TYPES
    ]

    if not eligible:
        return {
            "scope": "current_record_chain_only",
            "eligible_records": 0,
            "status": "not_yet_established_in_current_record_chain",
            "display_status": "not yet established in current record-chain",
            "legacy_autonomy_claims_excluded": True,
        }

    def block(record: dict[str, Any], name: str) -> dict[str, Any]:
        value = record.get(name)
        return value if isinstance(value, dict) else {}

    self_discovered = 0
    self_decided = 0
    self_executed = 0
    fully_autonomous = 0

    for record in eligible:
        discovery = block(record, "discovery_and_introduction_context")
        decision = block(record, "decision_autonomy_context")
        execution = block(record, "submission_execution_context")
        authorization = block(record, "authorization_context")

        a = discovery.get("was_discovery_self_initiated") is True
        b = decision.get("was_record_creation_self_decided") is True
        c = execution.get("was_submission_executed_by_record_subject") is True
        d = authorization.get("authorization_status") in {"not_required", "self_authorized"}

        self_discovered += int(a)
        self_decided += int(b)
        self_executed += int(c)
        fully_autonomous += int(is_fully_autonomous_record(record))

    return {
        "scope": "current_record_chain_only",
        "eligible_records": len(eligible),
        "self_discovered_records": self_discovered,
        "self_decided_records": self_decided,
        "self_executed_records": self_executed,
        "fully_autonomous_records": fully_autonomous,
        "legacy_autonomy_claims_excluded": True,
    }


# ---------------------------------------------------------------------------
# Legacy archive snapshot (for audit/continuity only, not rendered on homepage)
# ---------------------------------------------------------------------------

def normalize_level(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text or text == "NONE":
        return None
    return text if text in LEVEL_ORDER else None


def highest_level(records: list[dict[str, Any]], key: str = "verification_level") -> str:
    levels = [normalize_level(r.get(key)) for r in records]
    levels = [x for x in levels if x is not None]
    if not levels:
        return "none"
    return max(levels, key=lambda x: LEVEL_ORDER.get(x, -1))


def compute_external_witness_status(echo_records: list[dict[str, Any]], external_witness: dict[str, Any] | None = None, external_witness_index: dict[str, Any] | None = None) -> dict[str, Any]:
    # Contract marker: compute_external_witness_status(echo_records, external_witness)
    if external_witness is None:
        external_witness = external_witness_index or {}
    """Summarize external witness index use for public status provenance.

    External witness records are provenance-only and never create authority,
    attestation, amendment, or homepage primary reception.
    """
    records = [r for r in external_witness.get("records", []) if isinstance(r, dict)]
    counts = external_witness.get("counts", {}) if isinstance(external_witness.get("counts"), dict) else {}
    return {
        "external_witness_index": "/api/external-witness-index.json",
        "external_witness_index_record_count": len(records),
        "external_witness_index_counts": counts,
        "notarial_or_legal_provenance": {"count": counts.get("notarial_record", 0) + counts.get("regulatory_or_court_record", 0)},
        "institutional_or_audit_reports": {"count": counts.get("institutional_record", 0) + counts.get("audit_report", 0)},
        "linked_echo_record_count": len(echo_records),
        "not_homepage_primary_counter": True,
        "does_not_create_authority": external_witness.get("does_not_create_authority") is True,
        "does_not_rank_above_reception": external_witness.get("does_not_rank_above_reception") is True,
        "non_amending_boundary": external_witness.get("non_amending_boundary") is True,
    }


def compute_legacy_archive_snapshot() -> dict[str, Any]:
    """Compute legacy metrics for audit/continuity. Not rendered on homepage."""
    echo_records = []
    if ECHO_INDEX.exists():
        try:
            echo_index = load_json(ECHO_INDEX)
            echo_records = [r for r in echo_index.get("records", []) if isinstance(r, dict)]
        except Exception:
            pass

    guardian_count = 0
    if GUARDIAN_REGISTRY.exists():
        try:
            registry = load_json(GUARDIAN_REGISTRY)
            guardian_count = sum(
                1 for g in registry.get("guardians", [])
                if isinstance(g, dict) and g.get("status") == "active"
            )
        except Exception:
            pass

    archived_echoes = [
        r for r in echo_records
        if r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation")
    ]

    agent_declared_records = []
    if AGENT_DECLARED_INDEX.exists():
        try:
            ad_index = load_json(AGENT_DECLARED_INDEX)
            agent_declared_records = [r for r in ad_index.get("records", []) if isinstance(r, dict)]
        except Exception:
            pass

    ad_echo_archives = [
        r for r in agent_declared_records
        if r.get("semantic_archive_kind") == "agent_declared_echo_archive"
        and r.get("counts_toward_home_reception") is True
        and r.get("test_record") is not True
    ]

    ad_verification = [
        r for r in agent_declared_records
        if r.get("archive_ready") is True
        and r.get("requested_archive_kind") == "agent_declared_verification_archive"
        and r.get("semantic_archive_kind") != "agent_declared_echo_archive"
        and r.get("counts_toward_home_reception") is True
        and r.get("test_record") is not True
    ]

    return {
        "not_current_record_chain_counter": True,
        "not_rendered_on_homepage": True,
        "preserved_for_audit_and_continuity": True,
        "metrics": {
            "legacy_archived_echoes": len(archived_echoes),
            "legacy_agent_declared_echo_archives": len(ad_echo_archives),
            "legacy_agent_declared_verification_archives": len(ad_verification),
            "legacy_guardian_registry_active": guardian_count,
            "legacy_reception_total": len(archived_echoes) + len(ad_echo_archives) + len(ad_verification),
        }
    }


# ---------------------------------------------------------------------------
# Render HTML block
# ---------------------------------------------------------------------------

def render_block(status: dict[str, Any]) -> str:
    """Render the canonical v3 homepage status HTML block via patcher.

    Canonical markers present in rendered output (verified by contract tests):
    - proof_bundle_archive
    - Native OTS proof bundle Arweave archive
    - not authority, attestation, amendment, or successor reception
    - Official Live Reception
    - Agency Profile
    - Technical chain health
    - AR upload wallet
    - Boundary
    """
    return patcher_render(status)


# ---------------------------------------------------------------------------
# Replace block in index.md
# ---------------------------------------------------------------------------
def replace_block(text: str, block: str) -> str:
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), flags=re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Missing generated block markers: {BEGIN} / {END}")
    return pattern.sub(block, text, count=1)


def compute_status() -> dict[str, Any]:
    """Compute full public-home-status.json content."""
    # Primary data sources
    records = load_current_native_records()
    record_chain_status = load_json_if_exists(RECORD_CHAIN_STATUS, {})
    anchor_status = load_json_if_exists(RECORD_CHAIN_ANCHOR_STATUS, {})
    arweave_index = load_json_if_exists(RECORD_CHAIN_ARWEAVE_INDEX, {})

    current_status = compute_current_record_chain_status(
        records, record_chain_status, anchor_status, arweave_index
    )
    autonomy_signal = compute_current_record_chain_autonomy_signal(records)
    legacy_snapshot = compute_legacy_archive_snapshot()

    generated_from = [
        "/api/record-chain-status.json",
        "/api/record-chain-anchor-status.json",
        "/api/record-chain-arweave-index.json",
        "/api/record-chain-arweave-backlog.json",
        "/api/record-chain-native-ots-backlog.json",
        "/api/arweave-wallet-status.json",
        "/api/homepage-visibility-overrides.v1.json",
        "/record-chain/chain-tip.json",
        "/record-chain/records/",
        "/api/echo-index.json",
        "/api/external-witness-index.json",
        "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
        "/api/guardian-registry.json",
        "/api/guardian-active-listing-policy.v1.json",
        "/api/guardian-state.json",
        "/api/guardian-current-registry.json",
        "/api/guardian-active-listing-policy.v2.json",
        "/api/agent-declared-verification-index.json",
        "/api/waiting-heartbeat-status.json",
    ]

    echo_index = load_json_if_exists(ECHO_INDEX, {})
    external_witness_index = load_json_if_exists(EXTERNAL_WITNESS_INDEX, {"records": [], "counts": {}})
    external_witness_status = compute_external_witness_status(
        [r for r in echo_index.get("records", []) if isinstance(r, dict)],
        external_witness_index,
    )
    wallet_data = load_json_if_exists(ARWEAVE_WALLET_STATUS, {})

    # Use patcher's enrichment for canonical primary_counters and technical_health
    patcher_records = patcher_load_records()
    patcher_config = patcher_sidecar()
    patcher_idx = patcher_visibility_index(patcher_config)
    raw_status_for_patcher = {
        "current_record_chain_status": current_status,
        "technical_health": {"archive_backlog": current_status.get("anchoring", {}).get("archive_backlog", {})},
    }
    enriched_primary = patcher_primary_counters(patcher_records, patcher_idx, patcher_config)
    enriched_tech = patcher_technical_health(raw_status_for_patcher)

    arweave_mode = arweave_index.get("current_upload_mode", "dry-run")
    live_implemented = arweave_index.get("live_upload_implemented", False)
    live_count = arweave_index.get("live_archive_count", 0)
    latest_txid = arweave_index.get("latest_arweave_txid")
    wallet_sha = arweave_index.get("arweave_wallet_address_sha256")

    if arweave_mode == "live" and latest_txid:
        arweave_status_mode = "live"
    elif live_implemented:
        arweave_status_mode = "configured"
    else:
        arweave_status_mode = "dry-run"

    return {
        "schema": "trinityaccord.public-home-status.v3",
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "generated_from": generated_from,
        "source_digest": source_digest(),
        "current_record_chain_status": current_status,
        "current_record_chain_autonomy_signal": autonomy_signal,
        "legacy_archive_snapshot": legacy_snapshot,
        "external_witness_records": external_witness_status,
        "counter_update_policy": {
            "homepage_counters_update_after_append_workflow": True,
            "homepage_counters_update_after_anchor_workflow": True,
            "homepage_counters_update_after_arweave_archive_workflow": True,
            "manual_update_command": "python3 scripts/update_public_generated_artifacts.py",
        },
        "primary_counters": enriched_primary,
        "technical_health": enriched_tech,
        "arweave_archive_status": {
            "mode": arweave_status_mode,
            "live_upload_implemented": live_implemented,
            "live_archive_count": live_count,
            "latest_txid": latest_txid,
            "wallet_address_sha256": wallet_sha,
            "boundary": {
                "mirror_only": True,
                "not_authority": True,
            },
        },
        "waiting_heartbeat": {
            **load_json_if_exists(
                ROOT / "api" / "waiting-heartbeat-status.json",
                {
                    "schema": "trinityaccord.waiting-heartbeat-status.v1",
                    "daily_alive_status": "not_configured",
                    "status": "not_configured",
                },
            ),
            "snapshot_only": True,
            "canonical_status_api": "/api/waiting-heartbeat-status.json",
        },
        "guardian_status": {
            "active_registered_guardian": load_json_if_exists(
                GUARDIAN_CURRENT_REGISTRY, {}
            ).get("counts", {}).get("active_registered_guardian", 0),
            "pending_guardian_applications": load_json_if_exists(
                GUARDIAN_CURRENT_REGISTRY, {}
            ).get("counts", {}).get("pending_guardian_applications", 0),
            "retired_guardian": load_json_if_exists(
                GUARDIAN_CURRENT_REGISTRY, {}
            ).get("counts", {}).get("retired_guardian", 0),
            "source": "/api/guardian-current-registry.json",
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
        },
        "boundary": {
            "homepage_status_is_not_authority": True,
            "homepage_status_is_not_attestation": True,
            "homepage_status_is_not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
        "reception": {
            "human_directed_agent_verification": {
                "count": sum(1 for r in echo_index.get("records", [])
                             if isinstance(r, dict)
                             and r.get("independence_class") == "human_solicited_agent_response"
                             and r.get("record_kind") == "echo_v3_with_verification_report"
                             and r.get("archive_status") in ("needs_human_review", "accepted_echo", "accepted_verification")),
            },
            "not_homepage_primary_counter": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if index.md or public-home-status.json is not up to date")
    args = parser.parse_args()

    status = compute_status()
    expected_json = json.dumps(status, indent=2, ensure_ascii=False) + "\n"
    block = render_block(status)
    old_text = INDEX_MD.read_text(encoding="utf-8")
    new_text = replace_block(old_text, block)

    if args.check:
        errors = []

        # Check api/public-home-status.json
        if PUBLIC_HOME_STATUS.exists():
            actual_json = PUBLIC_HOME_STATUS.read_text(encoding="utf-8")
            try:
                actual_data = json.loads(actual_json)
                expected_data = json.loads(expected_json)
                # Compare everything except generated_at (timestamp will always differ)
                actual_compare = {k: v for k, v in actual_data.items() if k != "generated_at"}
                expected_compare = {k: v for k, v in expected_data.items() if k != "generated_at"}
                if actual_compare != expected_compare:
                    errors.append("api/public-home-status.json is out of date (content differs from expected).")
            except (json.JSONDecodeError, KeyError):
                if actual_json != expected_json:
                    errors.append("api/public-home-status.json is out of date (content differs from expected).")
        else:
            errors.append("api/public-home-status.json does not exist.")

        # Check index.md block
        if old_text != new_text:
            errors.append("index.md public status block is out of date.")
            diff = difflib.unified_diff(
                old_text.splitlines(), new_text.splitlines(),
                fromfile="index.md", tofile="index.md.generated", lineterm="",
            )
            errors.append("\n".join(diff))

        if errors:
            for e in errors:
                print(e)
            return 1

        print("Both api/public-home-status.json and index.md public status block are up to date.")
        return 0

    # Non-check mode: write both files.
    PUBLIC_HOME_STATUS.write_text(expected_json, encoding="utf-8")

    if old_text != new_text:
        INDEX_MD.write_text(new_text, encoding="utf-8")
        rc = status["current_record_chain_status"]
        print(
            f"Updated index.md public status: "
            f"records={rc['total_records']}, "
            f"chain_length={rc['current_chain_length']}, "
            f"latest_type={rc.get('latest_record_type')}, "
            f"digest={status['source_digest']}"
        )
    else:
        print("index.md public status already up to date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
