#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from archive_backlog_lib import (
    API_OTS_BACKLOG,
    API_RC_BACKLOG,
    OTS_BACKLOG,
    RC_BACKLOG,
    attempt_fields,
    dump_json,
    item_key,
    native_ots_backlog_doc,
    read_json,
    record_chain_backlog_doc,
    write_json_if_changed,
)

ROOT = Path(__file__).resolve().parents[1]
CHAIN_TIP = ROOT / "record-chain/chain-tip.json"
OTS_LATEST = ROOT / "api/record-chain-native-ots-latest.json"
ARWEAVE_INDEX = ROOT / "api/record-chain-arweave-index.json"
ARCHIVE_MANIFESTS = ROOT / "record-chain/arweave-archives"
NATIVE_ANCHORS = ROOT / "record-chain/ots/native-anchors"
NATIVE_BUNDLES = ROOT / "record-chain/ots/native-arweave-bundles"
NATIVE_REGISTRY = ROOT / "record-chain/ots/native-arweave-registry.json"
NATIVE_API_REGISTRY = ROOT / "api/record-chain-native-ots-arweave-registry.json"


def stable_updated_at() -> str:
    tip = read_json(CHAIN_TIP, {})
    ots = read_json(OTS_LATEST, {})
    return ots.get("updated_at") or tip.get("updated_at") or "2026-06-10T00:00:00Z"


def native_archive_sources() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    index = read_json(ARWEAVE_INDEX, {"archives": []})
    for entry in index.get("archives", []):
        if entry.get("source_type") == "native-record-chain" and entry.get("mode") == "live":
            entries.append(entry)
    for path in sorted(ARCHIVE_MANIFESTS.glob("*/manifest.json")):
        mf = read_json(path, {})
        source = mf.get("source", {})
        native = source.get("native_chain", {})
        ar = mf.get("arweave", {})
        if source.get("source_type") != "native-record-chain" or mf.get("mode") != "live":
            continue
        entries.append({
            "archive_id": mf.get("archive_id"),
            "manifest_path": str(path.relative_to(ROOT)),
            "mode": mf.get("mode"),
            "source_type": source.get("source_type"),
            "native_latest_record_id": native.get("latest_record_id"),
            "native_latest_record_sha256": native.get("latest_record_sha256"),
            "native_record_count": native.get("native_record_count"),
            "arweave_txid": ar.get("txid") or ar.get("tx_id"),
            "archive_status": ar.get("archive_status"),
            "hash_match": ar.get("hash_match"),
        })
    return entries


def record_chain_items() -> list[dict[str, Any]]:
    tip = read_json(CHAIN_TIP, {})
    prev = read_json(RC_BACKLOG, {"items": []})
    attempts = {i.get("key", ""): i for i in prev.get("items", []) if isinstance(i, dict)}
    latest_id = tip.get("latest_record_id")
    latest_sha = tip.get("latest_record_sha256")
    count = tip.get("native_record_count")
    if not latest_id or not latest_sha or not count:
        return []

    matching = [
        entry for entry in native_archive_sources()
        if entry.get("native_latest_record_id") == latest_id
        and entry.get("native_latest_record_sha256") == latest_sha
        and entry.get("native_record_count") == count
    ]
    if any(entry.get("arweave_txid") for entry in matching):
        return []

    key = item_key([latest_id, latest_sha, count])
    previous = attempts.get(key, {})
    status = previous.get("archive_status") or "pending_upload"
    return [{
        "key": key,
        "kind": "record_chain_arweave",
        "archive_status": status,
        "latest_record_id": latest_id,
        "latest_record_sha256": latest_sha,
        "native_record_count": count,
        "tx_id": previous.get("tx_id"),
        **attempt_fields(previous),
        "next_action": previous.get("next_action") or ("provide_arweave_key" if status == "waiting_for_key" else "upload_record_chain_archive"),
    }]


def registry_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in [NATIVE_REGISTRY, NATIVE_API_REGISTRY]:
        data = read_json(path, {"entries": []})
        entries.extend([e for e in data.get("entries", []) if isinstance(e, dict)])
    return entries


def native_ots_items() -> list[dict[str, Any]]:
    latest = read_json(OTS_LATEST, {})
    prev = read_json(OTS_BACKLOG, {"items": []})
    attempts = {i.get("key", ""): i for i in prev.get("items", []) if isinstance(i, dict)}
    anchored_sha = latest.get("anchored_file_sha256")
    ots_status = latest.get("ots_status")
    anchor_file = latest.get("latest_anchor_file")
    if not anchored_sha or not ots_status:
        return []

    for entry in registry_entries():
        if (
            entry.get("anchored_file_sha256") == anchored_sha
            and entry.get("archive_status") == "arweave_archived"
            and entry.get("tx_id")
        ):
            return []

    bundle_entries = []
    for path in sorted(NATIVE_BUNDLES.glob("*.arweave-bundle.json")):
        data = read_json(path, {})
        if data.get("anchored_file_sha256") == anchored_sha:
            bundle_entries.append((path, data))

    if ots_status not in {"upgraded", "verified"} and not bundle_entries:
        key = item_key([anchored_sha, ots_status, anchor_file])
        previous = attempts.get(key, {})
        return [{
            "key": key,
            "kind": "native_ots_bundle",
            "archive_status": previous.get("archive_status") or "waiting_for_upgrade",
            "anchored_file_sha256": anchored_sha,
            "ots_status": ots_status,
            "anchor_file": anchor_file,
            "bundle_file": None,
            "bundle_sha256": None,
            "tx_id": previous.get("tx_id"),
            **attempt_fields(previous),
            "next_action": previous.get("next_action") or "wait_for_ots_upgrade",
        }]

    items: list[dict[str, Any]] = []
    if bundle_entries:
        for path, data in bundle_entries:
            bundle_sha = data.get("bundle_sha256") or data.get("sha256")
            key = item_key([anchored_sha, ots_status, bundle_sha or str(path.relative_to(ROOT))])
            previous = attempts.get(key, {})
            items.append({
                "key": key,
                "kind": "native_ots_bundle",
                "archive_status": previous.get("archive_status") or "pending_upload",
                "anchored_file_sha256": anchored_sha,
                "ots_status": ots_status,
                "anchor_file": anchor_file,
                "bundle_file": str(path.relative_to(ROOT)),
                "bundle_sha256": bundle_sha,
                "tx_id": previous.get("tx_id"),
                **attempt_fields(previous),
                "next_action": previous.get("next_action") or "upload_native_ots_bundle",
            })
    elif ots_status in {"upgraded", "verified"}:
        key = item_key([anchored_sha, ots_status, anchor_file])
        previous = attempts.get(key, {})
        items.append({
            "key": key,
            "kind": "native_ots_bundle",
            "archive_status": previous.get("archive_status") or "pending_upload",
            "anchored_file_sha256": anchored_sha,
            "ots_status": ots_status,
            "anchor_file": anchor_file,
            "bundle_file": None,
            "bundle_sha256": None,
            "tx_id": previous.get("tx_id"),
            **attempt_fields(previous),
            "next_action": previous.get("next_action") or "build_and_upload_native_ots_bundle",
        })
    return items


def build_docs() -> tuple[dict[str, Any], dict[str, Any]]:
    updated = stable_updated_at()
    return record_chain_backlog_doc(record_chain_items(), updated), native_ots_backlog_doc(native_ots_items(), updated)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect lightweight Arweave/native OTS archive backlog")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()

    rc_doc, ots_doc = build_docs()
    if args.write:
        for path, doc in [(RC_BACKLOG, rc_doc), (API_RC_BACKLOG, rc_doc), (OTS_BACKLOG, ots_doc), (API_OTS_BACKLOG, ots_doc)]:
            write_json_if_changed(path, doc)

    rc_sum = rc_doc["summary"]
    ots_sum = ots_doc["summary"]
    output = {
        "record_chain_arweave_pending": str(rc_sum["pending_upload_count"] > 0).lower(),
        "record_chain_arweave_failed": str((rc_sum["failed_upload_count"] + rc_sum["readback_failed_count"] + rc_sum["waiting_for_key_count"]) > 0).lower(),
        "native_ots_pending": str((ots_sum["waiting_for_upgrade_count"] + ots_sum["pending_upload_count"]) > 0).lower(),
        "native_ots_failed": str((ots_sum["failed_upload_count"] + ots_sum["readback_failed_count"] + ots_sum["waiting_for_key_count"]) > 0).lower(),
        "record_chain_pending_count": str(rc_sum["pending_upload_count"]),
        "native_ots_pending_count": str(ots_sum["waiting_for_upgrade_count"] + ots_sum["pending_upload_count"]),
        "backlog_current": str(rc_sum["backlog_current"] and ots_sum["backlog_current"]).lower(),
    }
    if args.github_output:
        for key, value in output.items():
            print(f"{key}={value}")
    else:
        print(dump_json({"record_chain_arweave": rc_doc, "native_ots": ots_doc}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
