#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
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



def is_verified_live_native_archive(entry: dict[str, Any]) -> bool:
    return (
        bool(entry.get("arweave_txid"))
        and entry.get("source_type") == "native-record-chain"
        and entry.get("mode") == "live"
        and entry.get("archive_status") == "archived"
        and entry.get("verified") is True
        and entry.get("hash_match") is True
    )


def native_ots_archivable_for_current_chain() -> bool:
    tip = read_json(CHAIN_TIP, {})
    ots = read_json(OTS_LATEST, {})
    return (
        bool(tip.get("latest_record_id"))
        and ots.get("latest_record_id") == tip.get("latest_record_id")
        and ots.get("latest_record_sha256") == tip.get("latest_record_sha256")
        and ots.get("native_record_count") == tip.get("native_record_count")
        and ots.get("legacy_main_chain_jsonl_is_not_source") is True
        and bool(ots.get("latest_anchor_file"))
        and bool(ots.get("latest_ots_file"))
        and (
            (
                ots.get("ots_status") == "verified"
                and ots.get("bitcoin_verified") is True
                and ots.get("strict_bitcoin_verified") is True
            )
            or (
                ots.get("ots_status") == "upgraded"
                and ots.get("bitcoin_attestation_embedded") is True
                and ots.get("bitcoin_pending") is False
            )
        )
    )

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
            "verified": ar.get("verified") is True,
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
    if any(is_verified_live_native_archive(entry) for entry in matching):
        return []

    key = item_key([latest_id, latest_sha, count])
    previous = attempts.get(key, {})
    previous_status = previous.get("archive_status")

    ots_archivable = native_ots_archivable_for_current_chain()

    if not ots_archivable:
        status = "waiting_for_ots_upgrade"
        next_action = "wait_for_native_ots_upgrade"
    else:
        if previous_status in {"pending_upload", "upload_failed", "readback_failed", "waiting_for_key"}:
            status = previous_status
        else:
            status = "pending_upload"

        next_action = previous.get("next_action")
        if not next_action or next_action == "wait_for_native_ots_upgrade":
            next_action = "provide_arweave_key" if status == "waiting_for_key" else "upload_record_chain_archive"

    return [{
        "key": key,
        "kind": "record_chain_arweave",
        "archive_status": status,
        "latest_record_id": latest_id,
        "latest_record_sha256": latest_sha,
        "native_record_count": count,
        "tx_id": previous.get("tx_id"),
        **attempt_fields(previous),
        "next_action": next_action,
    }]


def registry_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in [NATIVE_REGISTRY, NATIVE_API_REGISTRY]:
        data = read_json(path, {"entries": []})
        entries.extend([e for e in data.get("entries", []) if isinstance(e, dict)])
    return entries


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def native_anchor_record_index(path: Path, data: dict[str, Any]) -> int | None:
    for key in ("latest_record_index", "record_index", "native_record_count"):
        value = data.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    match = re.search(r"native-record-(\d+)-", path.name)
    if match:
        return int(match.group(1))
    return None


def native_anchor_sources() -> list[tuple[Path, dict[str, Any], int | None]]:
    anchors: list[tuple[Path, dict[str, Any], int | None]] = []
    for path in sorted(NATIVE_ANCHORS.glob("*.anchor.json")):
        data = read_json(path, {})
        if not isinstance(data, dict):
            continue
        if data.get("schema") != "trinityaccord.native-record-chain-ots-anchor.v1":
            continue
        if not data.get("anchored_file_sha256"):
            continue
        anchors.append((path, data, native_anchor_record_index(path, data)))
    return anchors


def native_registry_has_archived(
    *,
    anchored_sha: str,
    ots_status: str | None = None,
) -> bool:
    for entry in registry_entries():
        if entry.get("anchored_file_sha256") != anchored_sha:
            continue
        if ots_status and entry.get("ots_status") != ots_status:
            continue
        if entry.get("archive_status") == "arweave_archived" and entry.get("tx_id"):
            return True
    return False


def native_bundle_sources_for_anchor(
    *,
    anchored_sha: str,
    ots_status: str,
) -> list[tuple[Path, dict[str, Any], str]]:
    matches: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(NATIVE_BUNDLES.glob("*.arweave-bundle.json")):
        data = read_json(path, {})
        if not isinstance(data, dict):
            continue
        if data.get("anchored_file_sha256") != anchored_sha:
            continue

        bundle_status = data.get("ots_status")
        if bundle_status not in (ots_status, None):
            continue

        bundle_sha = data.get("bundle_sha256") or data.get("sha256") or sha256_file(path)
        matches.append((path, data, bundle_sha))
    return matches


def previous_native_attempt_maps() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    prev = read_json(OTS_BACKLOG, {"items": []})
    by_key: dict[str, dict[str, Any]] = {}
    by_anchor_status: dict[str, dict[str, Any]] = {}
    for item in prev.get("items", []):
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if key:
            by_key[key] = item
        anchored_sha = item.get("anchored_file_sha256")
        ots_status = item.get("ots_status")
        if anchored_sha and ots_status:
            by_anchor_status[f"{anchored_sha}:{ots_status}"] = item
    return by_key, by_anchor_status


def previous_for(
    *,
    key: str,
    anchored_sha: str,
    ots_status: str,
    by_key: dict[str, dict[str, Any]],
    by_anchor_status: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return by_key.get(key) or by_anchor_status.get(f"{anchored_sha}:{ots_status}") or {}


def status_after_previous(previous: dict[str, Any], default: str) -> str:
    previous_status = previous.get("archive_status")
    if previous_status in {
        "waiting_for_upgrade",
        "upgrade_due",
        "upgrade_failed",
        "pending_upload",
        "upload_failed",
        "readback_failed",
        "waiting_for_key",
    }:
        return previous_status
    return default


def native_ots_scan_checkpoint(
    anchors: list[tuple[Path, dict[str, Any], int | None]],
    open_items: list[dict[str, Any]],
) -> dict[str, Any]:
    known_indices = sorted({idx for _path, _data, idx in anchors if isinstance(idx, int)})
    open_indices = {
        item.get("record_index")
        for item in open_items
        if isinstance(item.get("record_index"), int)
    }

    completed_prefix = None
    archive_prefix = None
    for idx in known_indices:
        if idx in open_indices:
            break
        completed_prefix = idx
    # archive_prefix tracks the same completed prefix as above.
    # TODO: separate arweave-specific tracking when arweave archive lag is monitored.
    archive_prefix = completed_prefix
    pending = sum(1 for _path, data, _idx in anchors if data.get("ots_status") == "pending")
    upgraded = sum(1 for _path, data, _idx in anchors if data.get("ots_status") == "upgraded")
    verified = sum(1 for _path, data, _idx in anchors if data.get("ots_status") == "verified")

    return {
        "scan_scope": "all_native_anchors",
        "native_anchor_count": len(anchors),
        "native_anchor_pending_count": pending,
        "native_anchor_upgraded_count": upgraded,
        "native_anchor_verified_count": verified,
        "native_anchor_upgraded_or_verified_count": upgraded + verified,
        "upgrade_completed_prefix_record_index": completed_prefix,
        "arweave_archive_completed_prefix_record_index": archive_prefix,
    }


def native_ots_items_and_scan() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    latest = read_json(OTS_LATEST, {})
    latest_anchor_file = latest.get("latest_anchor_file")
    latest_anchored_sha = latest.get("anchored_file_sha256")
    latest_status = latest.get("ots_status")
    latest_record_index = latest.get("latest_record_index")
    if not isinstance(latest_record_index, int):
        latest_record_index = None

    by_key, by_anchor_status = previous_native_attempt_maps()
    anchors = native_anchor_sources()

    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_item(item: dict[str, Any]) -> None:
        key = item.get("key")
        if key and key in seen:
            return
        if key:
            seen.add(key)
        items.append(item)

    # Current latest pending remains visible as waiting_for_upgrade.
    # The latest/current path is primarily handled by native-ots-upgrade-watch.
    if latest_anchored_sha and latest_status not in {"upgraded", "verified"}:
        key = item_key([latest_anchored_sha, latest_status, latest_anchor_file])
        previous = previous_for(
            key=key,
            anchored_sha=latest_anchored_sha,
            ots_status=latest_status or "pending",
            by_key=by_key,
            by_anchor_status=by_anchor_status,
        )
        status = status_after_previous(previous, "waiting_for_upgrade")
        add_item({
            "key": key,
            "kind": "native_ots_bundle",
            "record_index": latest_record_index,
            "archive_status": status,
            "anchored_file_sha256": latest_anchored_sha,
            "ots_status": latest_status,
            "anchor_file": latest_anchor_file,
            "bundle_file": None,
            "bundle_sha256": None,
            "tx_id": previous.get("tx_id"),
            **attempt_fields(previous),
            "next_action": previous.get("next_action") or (
                "upgrade_native_ots_anchor"
                if status in {"upgrade_due", "upgrade_failed"}
                else "wait_for_ots_upgrade"
            ),
        })

    for anchor_path, anchor, record_index in anchors:
        anchored_sha = anchor.get("anchored_file_sha256")
        ots_status = anchor.get("ots_status")
        anchor_rel = repo_rel(anchor_path)

        if not anchored_sha:
            continue

        # Historical pending anchors should be retried by archive-backlog-repair.
        # The current latest pending anchor is already represented above.
        if ots_status == "pending":
            if anchored_sha == latest_anchored_sha:
                continue
            key = item_key([anchored_sha, "pending", anchor_rel])
            previous = previous_for(
                key=key,
                anchored_sha=anchored_sha,
                ots_status="pending",
                by_key=by_key,
                by_anchor_status=by_anchor_status,
            )
            status = status_after_previous(previous, "upgrade_due")
            add_item({
                "key": key,
                "kind": "native_ots_bundle",
                "record_index": record_index,
                "archive_status": status,
                "anchored_file_sha256": anchored_sha,
                "ots_status": "pending",
                "anchor_file": anchor_rel,
                "bundle_file": None,
                "bundle_sha256": None,
                "tx_id": previous.get("tx_id"),
                **attempt_fields(previous),
                "next_action": previous.get("next_action") or "upgrade_native_ots_anchor",
            })
            continue

        if ots_status not in {"upgraded", "verified"}:
            continue

        if native_registry_has_archived(anchored_sha=anchored_sha, ots_status=ots_status):
            continue

        bundles = native_bundle_sources_for_anchor(
            anchored_sha=anchored_sha,
            ots_status=ots_status,
        )

        if bundles:
            for bundle_path, _bundle_data, bundle_sha in bundles:
                key = item_key([anchored_sha, ots_status, bundle_sha])
                previous = previous_for(
                    key=key,
                    anchored_sha=anchored_sha,
                    ots_status=ots_status,
                    by_key=by_key,
                    by_anchor_status=by_anchor_status,
                )
                status = status_after_previous(previous, "pending_upload")
                add_item({
                    "key": key,
                    "kind": "native_ots_bundle",
                    "record_index": record_index,
                    "archive_status": status,
                    "anchored_file_sha256": anchored_sha,
                    "ots_status": ots_status,
                    "anchor_file": anchor_rel,
                    "bundle_file": repo_rel(bundle_path),
                    "bundle_sha256": bundle_sha,
                    "tx_id": previous.get("tx_id"),
                    **attempt_fields(previous),
                    "next_action": previous.get("next_action") or (
                        "provide_arweave_key"
                        if status == "waiting_for_key"
                        else "upload_native_ots_bundle"
                    ),
                })
        else:
            key = item_key([anchored_sha, ots_status, anchor_rel])
            previous = previous_for(
                key=key,
                anchored_sha=anchored_sha,
                ots_status=ots_status,
                by_key=by_key,
                by_anchor_status=by_anchor_status,
            )
            status = status_after_previous(previous, "pending_upload")
            add_item({
                "key": key,
                "kind": "native_ots_bundle",
                "record_index": record_index,
                "archive_status": status,
                "anchored_file_sha256": anchored_sha,
                "ots_status": ots_status,
                "anchor_file": anchor_rel,
                "bundle_file": None,
                "bundle_sha256": None,
                "tx_id": previous.get("tx_id"),
                **attempt_fields(previous),
                "next_action": previous.get("next_action") or (
                    "provide_arweave_key"
                    if status == "waiting_for_key"
                    else "build_and_upload_native_ots_bundle"
                ),
            })

    items.sort(key=lambda item: (
        item.get("record_index") if isinstance(item.get("record_index"), int) else 10**12,
        item.get("ots_status") or "",
        item.get("bundle_sha256") or item.get("anchor_file") or "",
    ))
    return items, native_ots_scan_checkpoint(anchors, items)


def build_docs() -> tuple[dict[str, Any], dict[str, Any]]:
    updated = stable_updated_at()
    native_items, native_scan = native_ots_items_and_scan()
    return (
        record_chain_backlog_doc(record_chain_items(), updated),
        native_ots_backlog_doc(native_items, updated, native_scan),
    )


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
        "native_ots_pending": str((
            ots_sum["waiting_for_upgrade_count"]
            + ots_sum["upgrade_due_count"]
            + ots_sum["upgrade_failed_count"]
            + ots_sum["pending_upload_count"]
        ) > 0).lower(),
        "native_ots_failed": str((
            ots_sum["upgrade_failed_count"]
            + ots_sum["failed_upload_count"]
            + ots_sum["readback_failed_count"]
            + ots_sum["waiting_for_key_count"]
        ) > 0).lower(),
        "record_chain_pending_count": str(rc_sum["pending_upload_count"]),
        "native_ots_pending_count": str(
            ots_sum["waiting_for_upgrade_count"]
            + ots_sum["upgrade_due_count"]
            + ots_sum["upgrade_failed_count"]
            + ots_sum["pending_upload_count"]
        ),
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
