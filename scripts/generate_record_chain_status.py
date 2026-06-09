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


def latest_live_native_archive(arweave: dict[str, Any], tip: dict[str, Any]) -> dict[str, Any]:
    live = [
        a for a in arweave.get("archives", [])
        if a.get("source_type") == "native-record-chain"
        and a.get("mode") == "live"
        and a.get("arweave_txid")
    ]
    if not live:
        raise SystemExit("no live native Arweave archive found")
    live.sort(key=lambda a: (a.get("native_record_count") or 0, a.get("created_at") or ""))
    latest = live[-1]
    if latest.get("native_latest_record_id") != tip.get("latest_record_id"):
        raise SystemExit("latest live native Arweave record id does not match chain-tip")
    if latest.get("native_latest_record_sha256") != tip.get("latest_record_sha256"):
        raise SystemExit("latest live native Arweave sha does not match chain-tip")
    if latest.get("native_record_count") != tip.get("native_record_count"):
        raise SystemExit("latest live native Arweave count does not match chain-tip")
    return latest


def build_expected(existing: dict[str, Any]) -> dict[str, Any]:
    status = copy.deepcopy(existing)

    tip = read_json("record-chain/chain-tip.json")
    ots = read_json("api/record-chain-native-ots-latest.json")
    arweave = read_json("api/record-chain-arweave-index.json")
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

    if ots.get("latest_record_id") != latest_id:
        raise SystemExit("native OTS latest id does not match chain-tip")
    if ots.get("latest_record_sha256") != latest_sha:
        raise SystemExit("native OTS latest sha does not match chain-tip")
    if ots.get("native_record_count") != native_count:
        raise SystemExit("native OTS count does not match chain-tip")
    if ots.get("bitcoin_verified") is True and ots.get("ots_status") != "verified":
        raise SystemExit("invalid OTS state: bitcoin_verified true but ots_status is not verified")

    latest_live = latest_live_native_archive(arweave, tip)

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
    ot["status"] = "verified-bitcoin" if ots.get("bitcoin_verified") is True else "pending-bitcoin"

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
    aa["latest_archive_id"] = latest_live.get("archive_id")
    aa["latest_manifest_path"] = latest_live.get("manifest_path")
    aa["latest_native_record_id"] = latest_live.get("native_latest_record_id")
    aa["latest_native_record_sha256"] = latest_live.get("native_latest_record_sha256")
    aa["native_record_count"] = latest_live.get("native_record_count")
    aa["record_count"] = latest_live.get("record_count")
    aa.setdefault("default_mode", "dry-run")
    aa.setdefault("arweave_archive_is_mirror_only", True)
    aa.setdefault("arweave_archive_is_not_authority", True)
    aa.setdefault("arweave_archive_is_not_attestation", True)
    aa.setdefault("arweave_archive_is_not_amendment", True)

    status.setdefault("post_m9_status", {})
    m9 = status["post_m9_status"]
    m9["m9_status"] = "pass"
    m9["m9_archive_status"] = "pass"
    m9["m9_latest_record_id"] = latest_id
    m9["m9_latest_record_sha256"] = latest_sha
    m9["m9_native_record_count"] = native_count
    m9["m9_ots_status"] = ot["status"]
    m9["m9_arweave_txid"] = arweave.get("latest_arweave_txid")
    m9["m9_arweave_archive_id"] = latest_live.get("archive_id")
    m9["m9_arweave_manifest_path"] = latest_live.get("manifest_path")

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
