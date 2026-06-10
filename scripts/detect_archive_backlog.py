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
    for path in sorted(ARCHIVE_MANIFESTS.glob("*/manifest.json")):
        mf = read_json(path, {})
        source = mf.get("source", {})
        native = source.get("native_chain", {})
        ar = mf.get("arweave", {})
        if source.get("source_type") != "native-record-chain" or mf.get("mode") != "live":
            continue
        upload_result_path = path.parent / "upload-result.json"
        upload = read_json(upload_result_path, {}) if upload_result_path.exists() else {}
        entries.append({
            "archive_id": mf.get("archive_id"),
            "manifest_path": str(path.relative_to(ROOT)),
            "mode": mf.get("mode"),
            "source_type": source.get("source_type"),
            "native_latest_record_id": native.get("latest_record_id"),
            "native_latest_record_sha256": native.get("latest_record_sha256"),
            "native_record_count": native.get("native_record_count"),
            "arweave_txid": ar.get("txid") or ar.get("tx_id") or upload.get("txid") or upload.get("tx_id"),
            "archive_status": ar.get("archive_status"),
            "hash_match": ar.get("hash_match") if "hash_match" in ar else upload.get("hash_match"),
            "readback_sha256": ar.get("readback_sha256") or upload.get("readback_sha256"),
            "last_error": ar.get("last_error"),
        })
    return entries


def record_chain_entry_is_archived(entry: dict[str, Any]) -> bool:
    return bool(
        entry.get("arweave_txid")
        and (entry.get("archive_status") == "archived" or entry.get("hash_match") is True)
    )


def record_chain_entry_status(entry: dict[str, Any]) -> str:
    if not entry.get("arweave_txid"):
        return entry.get("archive_status") or "pending_upload"
    if record_chain_entry_is_archived(entry):
        return "archived"
    return entry.get("archive_status") or "readback_failed"


def record_chain_items() -> list[dict[str, Any]]:
    tip = read_json(CHAIN_TIP, {})
    prev = read_json(RC_BACKLOG, {"items": []})
    attempts = {i.get("key", ""): i for i in prev.get("items", []) if isinstance(i, dict)}
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for entry in native_archive_sources():
        latest_id = entry.get("native_latest_record_id")
        latest_sha = entry.get("native_latest_record_sha256")
        count = entry.get("native_record_count")
        if not latest_id or not latest_sha or not count:
            continue
        key = item_key([latest_id, latest_sha, count])
        seen.add(key)
        if record_chain_entry_is_archived(entry):
            continue
        previous = attempts.get(key, {})
        status = previous.get("archive_status") or record_chain_entry_status(entry)
        tx_id = previous.get("tx_id") or entry.get("arweave_txid")
        items.append({
            "key": key,
            "kind": "record_chain_arweave",
            "archive_status": status,
            "latest_record_id": latest_id,
            "latest_record_sha256": latest_sha,
            "native_record_count": count,
            "manifest_path": entry.get("manifest_path"),
            "tx_id": tx_id,
            **attempt_fields(previous),
            "last_error": previous.get("last_error") or entry.get("last_error"),
            "next_action": previous.get("next_action") or ("retry_readback_or_upload" if tx_id else "upload_record_chain_archive"),
        })

    latest_id = tip.get("latest_record_id")
    latest_sha = tip.get("latest_record_sha256")
    count = tip.get("native_record_count")
    if latest_id and latest_sha and count:
        key = item_key([latest_id, latest_sha, count])
        if key not in seen:
            previous = attempts.get(key, {})
            status = previous.get("archive_status") or "pending_upload"
            items.append({
                "key": key,
                "kind": "record_chain_arweave",
                "archive_status": status,
                "latest_record_id": latest_id,
                "latest_record_sha256": latest_sha,
                "native_record_count": count,
                "manifest_path": previous.get("manifest_path"),
                "tx_id": previous.get("tx_id"),
                **attempt_fields(previous),
                "next_action": previous.get("next_action") or ("provide_arweave_key" if status == "waiting_for_key" else "upload_record_chain_archive"),
            })
    return sorted(items, key=lambda item: (item.get("native_record_count") or 0, item.get("latest_record_id") or ""))


def registry_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in [NATIVE_REGISTRY, NATIVE_API_REGISTRY]:
        data = read_json(path, {"entries": []})
        entries.extend([e for e in data.get("entries", []) if isinstance(e, dict)])
    return entries


def bundle_sha_for(path: Path, data: dict[str, Any]) -> str | None:
    return data.get("bundle_sha256") or data.get("sha256")


def registry_archived_by_anchor() -> set[str]:
    archived: set[str] = set()
    for entry in registry_entries():
        if entry.get("archive_status") == "arweave_archived" and entry.get("tx_id") and entry.get("anchored_file_sha256"):
            archived.add(str(entry["anchored_file_sha256"]))
    return archived


def native_ots_items() -> list[dict[str, Any]]:
    latest = read_json(OTS_LATEST, {})
    prev = read_json(OTS_BACKLOG, {"items": []})
    attempts = {i.get("key", ""): i for i in prev.get("items", []) if isinstance(i, dict)}
    archived_anchors = registry_archived_by_anchor()
    bundles_by_anchor: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path in sorted(NATIVE_BUNDLES.glob("*.arweave-bundle.json")):
        data = read_json(path, {})
        anchored_sha = data.get("anchored_file_sha256")
        if anchored_sha:
            bundles_by_anchor.setdefault(str(anchored_sha), []).append((path, data))

    anchor_entries: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(NATIVE_ANCHORS.glob("*.anchor.json")):
        data = read_json(path, {})
        if data.get("anchored_file_sha256"):
            anchor_entries.append((str(path.relative_to(ROOT)), data))

    latest_anchor = latest.get("latest_anchor_file")
    if latest_anchor and not any(rel == latest_anchor for rel, _ in anchor_entries):
        anchor_entries.append((latest_anchor, latest))

    items: list[dict[str, Any]] = []
    for anchor_rel, anchor in anchor_entries:
        anchored_sha = anchor.get("anchored_file_sha256")
        ots_status = anchor.get("ots_status") or latest.get("ots_status")
        if not anchored_sha or not ots_status or anchored_sha in archived_anchors:
            continue
        bundle_entries = bundles_by_anchor.get(str(anchored_sha), [])
        if bundle_entries:
            for bundle_path, bundle in bundle_entries:
                bundle_sha = bundle_sha_for(bundle_path, bundle)
                key = item_key([anchored_sha, ots_status, bundle_sha or str(bundle_path.relative_to(ROOT))])
                previous = attempts.get(key, {})
                items.append({
                    "key": key,
                    "kind": "native_ots_bundle",
                    "archive_status": previous.get("archive_status") or "pending_upload",
                    "anchored_file_sha256": anchored_sha,
                    "ots_status": ots_status,
                    "anchor_file": anchor_rel,
                    "bundle_file": str(bundle_path.relative_to(ROOT)),
                    "bundle_sha256": bundle_sha,
                    "tx_id": previous.get("tx_id"),
                    **attempt_fields(previous),
                    "next_action": previous.get("next_action") or "upload_native_ots_bundle",
                })
            continue

        if ots_status in {"upgraded", "verified"}:
            status = "pending_upload"
            action = "build_and_upload_native_ots_bundle"
        else:
            status = "waiting_for_upgrade"
            action = "wait_for_ots_upgrade"
        key = item_key([anchored_sha, ots_status, anchor_rel])
        previous = attempts.get(key, {})
        items.append({
            "key": key,
            "kind": "native_ots_bundle",
            "archive_status": previous.get("archive_status") or status,
            "anchored_file_sha256": anchored_sha,
            "ots_status": ots_status,
            "anchor_file": anchor_rel,
            "bundle_file": None,
            "bundle_sha256": None,
            "tx_id": previous.get("tx_id"),
            **attempt_fields(previous),
            "next_action": previous.get("next_action") or action,
        })
    return sorted(items, key=lambda item: item.get("anchor_file") or "")


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
