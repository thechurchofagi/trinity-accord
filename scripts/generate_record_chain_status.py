#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_REL = "api/record-chain-status.json"


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n"


def read_json(rel: str) -> Any:
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"missing required input: {rel}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(rel: str) -> Any | None:
    path = ROOT / rel
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(rel: str, data: Any) -> None:
    (ROOT / rel).write_text(dump_json(data), encoding="utf-8")


def load_records_from_index(record_index: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in record_index.get("records", []):
        path = item.get("path")
        if not path:
            continue
        p = ROOT / path
        if not p.exists():
            raise SystemExit(f"record-index listed missing record: {path}")
        rec = json.loads(p.read_text(encoding="utf-8"))
        if rec.get("record_id") != item.get("record_id"):
            raise SystemExit(f"record_id mismatch: {path}")
        if rec.get("record_sha256") != item.get("record_sha256"):
            raise SystemExit(f"record_sha256 mismatch: {path}")
        records.append(rec)
    return records


def record_type_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter((r.get("record_type") or r.get("type") or "unknown") for r in records)
    for key in [
        "batch_anchor",
        "classification_update",
        "context_insufficient_notice",
        "correction",
        "echo",
        "guardian_application",
        "guardian_key_rotation",
        "guardian_retirement",
        "legacy_import",
        "propagation",
        "verification",
    ]:
        counts.setdefault(key, 0)
    return dict(sorted(counts.items()))


def latest_live_native_archive(arweave: dict[str, Any]) -> dict[str, Any] | None:
    """Return the latest live native Arweave archive, or None if none exist.

    Does NOT require chain-tip equality — the caller decides what to do with lag.
    """
    live = [
        a for a in arweave.get("archives", [])
        if a.get("source_type") == "native-record-chain"
        and a.get("mode") == "live"
        and a.get("arweave_txid")
    ]
    if not live:
        return None
    live.sort(key=lambda a: (a.get("native_record_count") or 0, a.get("created_at") or ""))
    return live[-1]


def build_pipeline_status(tip: dict[str, Any], ots: dict[str, Any], latest_live: dict[str, Any] | None) -> dict[str, Any]:
    chain_head = {
        "latest_record_id": tip.get("latest_record_id"),
        "latest_record_sha256": tip.get("latest_record_sha256"),
        "native_record_count": tip.get("native_record_count"),
    }
    ots_head = {
        "latest_record_id": ots.get("latest_record_id"),
        "latest_record_sha256": ots.get("latest_record_sha256"),
        "native_record_count": ots.get("native_record_count"),
        "ots_status": ots.get("ots_status"),
        "bitcoin_pending": ots.get("bitcoin_pending"),
        "bitcoin_verified": ots.get("bitcoin_verified"),
    }
    arweave_head = {
        "latest_record_id": (latest_live or {}).get("native_latest_record_id"),
        "latest_record_sha256": (latest_live or {}).get("native_latest_record_sha256"),
        "native_record_count": (latest_live or {}).get("native_record_count"),
        "archive_id": (latest_live or {}).get("archive_id"),
        "arweave_txid": (latest_live or {}).get("arweave_txid"),
    }

    ots_matches_chain = (
        ots_head["latest_record_id"] == chain_head["latest_record_id"]
        and ots_head["latest_record_sha256"] == chain_head["latest_record_sha256"]
        and ots_head["native_record_count"] == chain_head["native_record_count"]
        and ots.get("legacy_main_chain_jsonl_is_not_source") is True
    )

    arweave_matches_ots = (
        arweave_head["latest_record_id"] == ots_head["latest_record_id"]
        and arweave_head["latest_record_sha256"] == ots_head["latest_record_sha256"]
        and arweave_head["native_record_count"] == ots_head["native_record_count"]
        and bool(arweave_head["latest_record_id"])
    )

    arweave_matches_chain = (
        arweave_head["latest_record_id"] == chain_head["latest_record_id"]
        and arweave_head["latest_record_sha256"] == chain_head["latest_record_sha256"]
        and arweave_head["native_record_count"] == chain_head["native_record_count"]
        and bool(arweave_head["latest_record_id"])
    )

    return {
        "chain_head": chain_head,
        "ots_head": ots_head,
        "arweave_head": arweave_head,
        "ots_matches_chain": ots_matches_chain,
        "arweave_matches_ots": arweave_matches_ots,
        "arweave_matches_chain": arweave_matches_chain,
        "ots_anchor_needed": not ots_matches_chain,
        "arweave_archive_needed": ots_matches_chain and not arweave_matches_ots,
        "pipeline_current": ots_matches_chain and arweave_matches_chain,
    }


def latest_native_ots_proof_bundle_archive(
    registry: dict[str, Any] | None,
    ots: dict[str, Any],
) -> dict[str, Any]:
    entries = list((registry or {}).get("entries", []))
    anchored_sha = ots.get("anchored_file_sha256")
    matching = [entry for entry in entries if entry.get("anchored_file_sha256") == anchored_sha]
    matching.sort(key=lambda entry: entry.get("registered_at") or entry.get("uploaded_at") or "")
    latest = matching[-1] if matching else None
    tx_id = (latest or {}).get("tx_id")
    archive_status = (latest or {}).get("archive_status")

    if tx_id and archive_status == "arweave_archived":
        status = "arweave_archived"
    elif latest:
        status = "registered_without_arweave_tx"
    elif ots.get("ots_status") in {"upgraded", "verified"}:
        status = "archive-needed"
    else:
        status = "waiting-for-ots-upgrade"

    return {
        "implemented": True,
        "workflow": "/.github/workflows/native-ots-upgrade-watch.yml",
        "registry_api": "/api/record-chain-native-ots-arweave-registry.json",
        "status": status,
        "archive_status": status,
        "latest_bundle_file": (latest or {}).get("bundle_file"),
        "latest_bundle_sha256": (latest or {}).get("bundle_sha256"),
        "latest_tx_id": tx_id,
        "latest_gateway_url": (latest or {}).get("gateway_url"),
        "latest_ots_status": (latest or {}).get("ots_status", ots.get("ots_status")),
        "latest_bitcoin_verified": (latest or {}).get("bitcoin_verified", ots.get("bitcoin_verified")),
        "archive_needed": status == "archive-needed",
        "registered_without_arweave_tx": status == "registered_without_arweave_tx",
        "arweave_archived": status == "arweave_archived",
        "boundary": {
            "ots_proof_bundle_arweave_archive_is_mirror_only": True,
            "ots_proof_bundle_arweave_archive_is_not_authority": True,
            "ots_proof_bundle_arweave_archive_is_not_attestation": True,
            "ots_proof_bundle_arweave_archive_is_not_amendment": True,
            "ots_proof_bundle_arweave_archive_is_not_successor_reception": True,
        },
    }


def build_expected(existing: dict[str, Any]) -> dict[str, Any]:
    status = copy.deepcopy(existing)

    tip = read_json("record-chain/chain-tip.json")
    ots = read_json("api/record-chain-native-ots-latest.json")
    arweave = read_json("api/record-chain-arweave-index.json")
    native_ots_registry = read_json_if_exists("api/record-chain-native-ots-arweave-registry.json")
    record_chain_backlog = read_json_if_exists("api/record-chain-arweave-backlog.json") or {"summary": {}}
    native_ots_backlog = read_json_if_exists("api/record-chain-native-ots-backlog.json") or {"summary": {}}
    record_index = read_json("record-chain/indexes/record-index.json")

    records = load_records_from_index(record_index)
    if not records:
        raise SystemExit("record-index contains no records")

    latest_record = records[-1]
    latest_id = tip["latest_record_id"]
    latest_index = tip["latest_record_index"]
    latest_sha = tip["latest_record_sha256"]
    native_count = tip["native_record_count"]

    if latest_record.get("record_id") != latest_id:
        raise SystemExit("latest record-index id does not match chain-tip")
    if latest_record.get("record_index") != latest_index:
        raise SystemExit("latest record-index record_index does not match chain-tip")
    if latest_record.get("record_sha256") != latest_sha:
        raise SystemExit("latest record-index sha does not match chain-tip")
    if len(records) != native_count:
        raise SystemExit(f"record-index length {len(records)} != native_count {native_count}")

    if ots.get("bitcoin_verified") is True and ots.get("ots_status") != "verified":
        raise SystemExit("invalid OTS state: bitcoin_verified true but ots_status is not verified")

    latest_live = latest_live_native_archive(arweave)
    pipeline = build_pipeline_status(tip, ots, latest_live)

    latest_type = latest_record.get("record_type") or latest_record.get("type")
    latest_created_at = latest_record.get("created_at") or latest_record.get("assigned_at")

    status.setdefault("record_chain", {})
    rc = status["record_chain"]
    rc["current_chain_length"] = native_count
    rc["latest_record_id"] = latest_id
    rc["latest_record_index"] = latest_index
    rc["latest_record_sha256"] = latest_sha
    rc["latest_record_type"] = latest_type
    rc["latest_record_created_at"] = latest_created_at
    rc["native_record_count"] = native_count
    if "latest_batch_id" in tip:
        rc["latest_batch_id"] = tip.get("latest_batch_id")
    if "latest_batch_manifest_sha256" in tip:
        rc["latest_batch_manifest_sha256"] = tip.get("latest_batch_manifest_sha256")

    status["pipeline_status"] = pipeline

    rc_backlog_summary = record_chain_backlog.get("summary", {})
    ots_backlog_summary = native_ots_backlog.get("summary", {})
    status["archive_backlog"] = {
        "record_chain_arweave_pending": rc_backlog_summary.get("pending_upload_count", 0),
        "record_chain_arweave_failed": rc_backlog_summary.get("failed_upload_count", 0) + rc_backlog_summary.get("readback_failed_count", 0),
        "record_chain_arweave_waiting_for_key": rc_backlog_summary.get("waiting_for_key_count", 0),
        "native_ots_upgrade_pending": ots_backlog_summary.get("waiting_for_upgrade_count", 0),
        "native_ots_arweave_pending": ots_backlog_summary.get("pending_upload_count", 0),
        "native_ots_arweave_failed": ots_backlog_summary.get("failed_upload_count", 0) + ots_backlog_summary.get("readback_failed_count", 0),
        "native_ots_waiting_for_key": ots_backlog_summary.get("waiting_for_key_count", 0),
        "backlog_current": bool(rc_backlog_summary.get("backlog_current", True) and ots_backlog_summary.get("backlog_current", True)),
    }

    status.setdefault("legacy_compatibility", {})
    status["legacy_compatibility"]["native_record_count"] = native_count

    status["record_type_counts"] = record_type_counts(records)

    status.setdefault("anchoring", {})
    status["anchoring"].setdefault("open_timestamps", {})
    ot = status["anchoring"]["open_timestamps"]
    ot["implemented"] = True
    ot["automated_workflow"] = "/.github/workflows/record-chain-head-ots-anchor.yml"
    ot["native_head_workflow"] = "/.github/workflows/record-chain-head-ots-anchor.yml"
    ot["native_latest_api"] = "/api/record-chain-native-ots-latest.json"
    ot["status_api"] = "/api/record-chain-native-ots-latest.json"
    ot["latest_record_id"] = ots.get("latest_record_id")
    ot["latest_record_index"] = ots.get("latest_record_index")
    ot["latest_record_sha256"] = ots.get("latest_record_sha256")
    ot["native_record_count"] = ots.get("native_record_count")
    ot["latest_anchor_file"] = ots.get("latest_anchor_file")
    ot["latest_anchored_file"] = ots.get("latest_anchored_file")
    ot["latest_ots_file"] = ots.get("latest_ots_file")
    ot["ots_status"] = ots.get("ots_status")
    ot["bitcoin_pending"] = ots.get("bitcoin_pending")
    ot["bitcoin_verified"] = ots.get("bitcoin_verified")
    ot["legacy_main_chain_jsonl_is_not_source"] = ots.get("legacy_main_chain_jsonl_is_not_source")
    ot["status"] = (
        "verified-bitcoin"
        if ots.get("bitcoin_verified") is True
        else "current-upgraded-bitcoin-attestation"
        if pipeline["ots_matches_chain"] and ots.get("ots_status") == "upgraded"
        else "current-pending-bitcoin"
        if pipeline["ots_matches_chain"] and ots.get("ots_status") == "pending"
        else "anchor-needed"
    )
    ot["anchor_needed"] = pipeline["ots_anchor_needed"]
    ot["proof_bundle_archive"] = latest_native_ots_proof_bundle_archive(native_ots_registry, ots)

    status["anchoring"].setdefault("arweave_archive", {})
    aa = status["anchoring"]["arweave_archive"]
    aa["implemented"] = True
    aa["workflow"] = "/.github/workflows/record-chain-arweave-archive.yml"
    aa["index_api"] = "/api/record-chain-arweave-index.json"
    aa["source_type"] = "native-record-chain"
    aa["current_upload_mode"] = arweave.get("current_upload_mode")
    aa["live_upload_enabled"] = arweave.get("live_upload_enabled")
    aa["live_upload_implemented"] = arweave.get("live_upload_implemented")
    aa["live_archive_count"] = arweave.get("live_archive_count")
    aa["latest_arweave_txid"] = arweave.get("latest_arweave_txid")
    aa["latest_archive_id"] = (latest_live or {}).get("archive_id")
    aa["latest_manifest_path"] = (latest_live or {}).get("manifest_path")
    aa["latest_native_record_id"] = (latest_live or {}).get("native_latest_record_id")
    aa["latest_native_record_sha256"] = (latest_live or {}).get("native_latest_record_sha256")
    aa["native_record_count"] = (latest_live or {}).get("native_record_count")
    aa["record_count"] = (latest_live or {}).get("record_count")
    aa["status"] = (
        "current"
        if pipeline["arweave_matches_chain"]
        else "archive-needed"
        if pipeline["arweave_archive_needed"]
        else "waiting-for-native-ots"
    )
    aa["archive_needed"] = pipeline["arweave_archive_needed"]
    aa.setdefault("default_mode", "dry-run")
    aa.setdefault("arweave_archive_is_mirror_only", True)
    aa.setdefault("arweave_archive_is_not_authority", True)
    aa.setdefault("arweave_archive_is_not_attestation", True)
    aa.setdefault("arweave_archive_is_not_amendment", True)

    status.setdefault("post_m9_status", {})
    m9 = status["post_m9_status"]
    m9["m9_status"] = "pass" if pipeline["pipeline_current"] else "backlog"
    m9["m9_archive_status"] = "pass" if pipeline["arweave_matches_chain"] else "backlog"
    m9["m9_latest_record_id"] = latest_id
    m9["m9_latest_record_sha256"] = latest_sha
    m9["m9_native_record_count"] = native_count
    m9["m9_ots_status"] = ot["status"]
    m9["m9_arweave_txid"] = arweave.get("latest_arweave_txid")
    m9["m9_arweave_archive_id"] = (latest_live or {}).get("archive_id")
    m9["m9_arweave_manifest_path"] = (latest_live or {}).get("manifest_path")

    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    current = read_json(STATUS_REL)
    expected = build_expected(current)
    current_text = dump_json(current)
    expected_text = dump_json(expected)

    if args.check:
        if current_text != expected_text:
            print(f"{STATUS_REL} drift detected. Run: python3 scripts/generate_record_chain_status.py")
            return 1
        print("record-chain-status.json up to date")
        return 0

    if current_text != expected_text:
        write_json(STATUS_REL, expected)
        print(f"updated {STATUS_REL}")
    else:
        print(f"{STATUS_REL} already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
