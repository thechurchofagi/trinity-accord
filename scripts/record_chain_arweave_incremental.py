#!/usr/bin/env python3
"""Incremental payload builder for weekly native Record-Chain archives.

Archive manifests continue to describe and verify the complete native chain
snapshot. The paid payload contains only records added after the latest
successfully archived snapshot, plus an immutable link to that previous
transaction. It also carries a compact Waiting Heartbeat period summary and the
latest mature Native OTS proof files covering the current chain head.

The first archive remains a complete snapshot. Every later archive is a delta,
so ``base snapshot + ordered deltas`` reconstructs the complete chain without
re-uploading historical record bytes.
"""
from __future__ import annotations

import base64
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import build_record_chain_arweave_archive as builder

OTS_LATEST = builder.ROOT / "api" / "record-chain-native-ots-latest.json"


def record_ordinal(record_id: object) -> int | None:
    if not isinstance(record_id, str) or not record_id.startswith("R-"):
        return None
    suffix = record_id[2:]
    return int(suffix) if suffix.isdigit() else None


def _latest_archived_snapshot(exclude_archive_id: str) -> dict[str, Any] | None:
    candidates: list[tuple[int, str, dict[str, Any], Path]] = []
    for manifest_path in builder.ARCHIVES.glob("*/manifest.json"):
        try:
            manifest = builder.read_json(manifest_path)
            payload = builder.read_json(manifest_path.parent / "payload.json")
        except Exception:
            continue
        if manifest.get("archive_id") == exclude_archive_id:
            continue
        arweave = manifest.get("arweave", {})
        if (
            manifest.get("mode") != "live"
            or arweave.get("archive_status") != "archived"
            or arweave.get("verified") is not True
            or arweave.get("hash_match") is not True
            or not (arweave.get("txid") or arweave.get("tx_id"))
            or payload.get("schema") != "trinityaccord.record-chain-arweave-delta.v1"
            or payload.get("archive_cadence") != "weekly"
            or not isinstance(payload.get("continuity_bundle"), dict)
            or payload["continuity_bundle"].get("schema")
            != "trinityaccord.weekly-continuity-bundle.v1"
        ):
            continue
        native = manifest.get("source", {}).get("native_chain", {})
        count = native.get("native_record_count")
        latest_id = native.get("latest_record_id")
        if not isinstance(count, int) or count < 1 or record_ordinal(latest_id) != count:
            continue
        candidates.append((count, str(manifest.get("created_at") or ""), manifest, manifest_path))

    if not candidates:
        return None
    _count, _created, manifest, manifest_path = sorted(candidates, key=lambda item: (item[0], item[1]))[-1]
    return {"manifest": manifest, "manifest_path": manifest_path}


def _encoded_file(relative_path: str) -> dict[str, Any]:
    path = builder.ROOT / relative_path
    if not path.is_file():
        raise SystemExit(f"weekly continuity artifact missing: {path}")
    raw = path.read_bytes()
    return {
        "path": relative_path,
        "sha256": builder.sha256_bytes(raw),
        "bytes": len(raw),
        "content_base64": base64.b64encode(raw).decode("ascii"),
    }


def _record_payload(record_ref: dict[str, Any]) -> dict[str, Any]:
    rec_path = builder.ROOT / str(record_ref.get("path") or "")
    if not rec_path.exists():
        raise SystemExit(f"incremental Arweave payload record missing: {rec_path}")
    raw = rec_path.read_bytes()
    actual_raw_sha = builder.sha256_bytes(raw)
    expected_raw_sha = record_ref.get("raw_file_sha256")
    if expected_raw_sha and expected_raw_sha != actual_raw_sha:
        raise SystemExit(
            f"incremental Arweave payload raw SHA mismatch for {record_ref.get('record_id')}"
        )
    return {
        "record_id": record_ref.get("record_id"),
        "path": record_ref.get("path"),
        "record_sha256": record_ref.get("record_sha256"),
        "raw_file_sha256": actual_raw_sha,
        "bytes": len(raw),
        "content_base64": base64.b64encode(raw).decode("ascii"),
    }


def _heartbeat_summary(selected: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    observed: set[date] = set()
    for record_ref in selected:
        path = builder.ROOT / str(record_ref.get("path") or "")
        record = builder.read_json(path)
        heartbeat = record.get("system_waiting_heartbeat")
        if not isinstance(heartbeat, dict):
            continue
        heartbeat_id = heartbeat.get("heartbeat_id")
        heartbeat_date = heartbeat.get("heartbeat_date")
        parsed: date | None = None
        if isinstance(heartbeat_date, str):
            try:
                parsed = date.fromisoformat(heartbeat_date)
            except ValueError:
                parsed = None
        if parsed is not None:
            observed.add(parsed)
        entries.append(
            {
                "heartbeat_id": heartbeat_id,
                "heartbeat_date": heartbeat_date,
                "record_id": record_ref.get("record_id"),
                "record_sha256": record_ref.get("record_sha256"),
                "record_path": record_ref.get("path"),
                "semantic_agent_arrived": heartbeat.get("semantic_agent_arrived") is True,
                "not_echo": heartbeat.get("not_echo") is True,
                "not_verification": heartbeat.get("not_verification") is True,
                "not_guardian_application": heartbeat.get("not_guardian_application") is True,
            }
        )

    missing: list[str] = []
    period_start = min(observed) if observed else None
    period_end = max(observed) if observed else None
    if period_start is not None and period_end is not None:
        current = period_start
        while current <= period_end:
            if current not in observed:
                missing.append(current.isoformat())
            current += timedelta(days=1)

    return {
        "schema": "trinityaccord.weekly-heartbeat-summary.v1",
        "period_start": period_start.isoformat() if period_start else None,
        "period_end": period_end.isoformat() if period_end else None,
        "expected_days_within_observed_span": (
            (period_end - period_start).days + 1
            if period_start is not None and period_end is not None
            else 0
        ),
        "present_days": len(observed),
        "missing_days": missing,
        "heartbeat_count": len(entries),
        "heartbeats": entries,
        "summary_is_non_authoritative_index": True,
        "native_record_files_remain_source": True,
    }


def _latest_native_ots(
    *,
    current_count: int,
    current_latest_id: str,
    current_latest_sha: str,
) -> dict[str, Any]:
    if not OTS_LATEST.is_file():
        raise SystemExit("weekly continuity payload requires api/record-chain-native-ots-latest.json")
    latest = builder.read_json(OTS_LATEST)
    if (
        latest.get("native_record_count") != current_count
        or latest.get("latest_record_id") != current_latest_id
        or latest.get("latest_record_sha256") != current_latest_sha
    ):
        raise SystemExit("latest Native OTS metadata does not cover the current chain head")
    if latest.get("ots_status") not in {"upgraded", "verified"}:
        raise SystemExit("latest Native OTS proof is not mature enough for weekly continuity archival")

    artifact_paths = [
        latest.get("latest_anchor_file"),
        latest.get("latest_anchored_file"),
        latest.get("latest_ots_file"),
    ]
    if not all(isinstance(path, str) and path for path in artifact_paths):
        raise SystemExit("latest Native OTS metadata is missing required proof paths")

    return {
        "schema": "trinityaccord.weekly-native-ots-evidence.v1",
        "metadata": latest,
        "artifacts": [_encoded_file(path) for path in artifact_paths],
        "covers_current_chain_head": True,
        "proof_files_embedded_in_this_payload": True,
    }


def build_incremental_payload_json(manifest: dict[str, Any], archive_dir: Path) -> Path:
    archive_id = str(manifest.get("archive_id") or "")
    current_native = manifest.get("source", {}).get("native_chain", {})
    current_count = current_native.get("native_record_count")
    current_latest_id = current_native.get("latest_record_id")
    current_latest_sha = current_native.get("latest_record_sha256")
    all_records = manifest.get("included_records", [])

    if not isinstance(current_count, int) or current_count < 1:
        raise SystemExit("incremental Arweave payload requires native_record_count >= 1")
    if record_ordinal(current_latest_id) != current_count:
        raise SystemExit("incremental Arweave payload latest_record_id/count mismatch")
    if not isinstance(current_latest_sha, str) or not current_latest_sha:
        raise SystemExit("incremental Arweave payload requires latest_record_sha256")
    if not isinstance(all_records, list) or len(all_records) != current_count:
        raise SystemExit("incremental Arweave payload requires a complete manifest record index")

    previous_info = _latest_archived_snapshot(archive_id)
    previous_count = 0
    previous_manifest: dict[str, Any] | None = None
    previous_path: Path | None = None
    if previous_info is not None:
        previous_manifest = previous_info["manifest"]
        previous_path = previous_info["manifest_path"]
        previous_native = previous_manifest.get("source", {}).get("native_chain", {})
        previous_count = int(previous_native.get("native_record_count") or 0)
        if previous_count >= current_count:
            raise SystemExit(
                "latest archived snapshot is not behind the current chain; refusing an empty or backwards delta"
            )
        previous_latest_id = previous_native.get("latest_record_id")
        previous_latest_sha = previous_native.get("latest_record_sha256")
        if not isinstance(previous_latest_id, str) or not isinstance(previous_latest_sha, str):
            raise SystemExit("latest archived snapshot is missing its immutable prefix identity")
        prefix_ref = all_records[previous_count - 1]
        if (
            prefix_ref.get("record_id") != previous_latest_id
            or prefix_ref.get("record_sha256") != previous_latest_sha
        ):
            raise SystemExit(
                "latest archived snapshot does not match the current chain prefix; refusing to attach a delta to a divergent base"
            )

    selected: list[dict[str, Any]] = []
    expected_next = previous_count + 1
    for record_ref in all_records:
        ordinal = record_ordinal(record_ref.get("record_id"))
        if ordinal is None:
            raise SystemExit(f"invalid record id in manifest: {record_ref.get('record_id')}")
        if ordinal <= previous_count:
            continue
        if ordinal != expected_next:
            raise SystemExit(
                f"incremental payload record sequence gap: expected R-{expected_next:09d}, got {record_ref.get('record_id')}"
            )
        selected.append(record_ref)
        expected_next += 1

    expected_delta_count = current_count - previous_count
    if len(selected) != expected_delta_count:
        raise SystemExit(
            f"incremental payload count mismatch: selected={len(selected)} expected={expected_delta_count}"
        )

    previous_arweave = previous_manifest.get("arweave", {}) if previous_manifest else {}
    previous_native = previous_manifest.get("source", {}).get("native_chain", {}) if previous_manifest else {}
    previous_txid = previous_arweave.get("txid") or previous_arweave.get("tx_id")
    previous_manifest_sha = previous_manifest.get("archive_manifest_sha256") if previous_manifest else None
    first_id = selected[0].get("record_id")
    last_id = selected[-1].get("record_id")

    overlapping_batches = []
    for batch in manifest.get("included_batches", []):
        last_index = batch.get("last_record_index")
        if not isinstance(last_index, int) or last_index >= previous_count + 1:
            overlapping_batches.append(
                {
                    "batch_id": batch.get("batch_id"),
                    "batch_manifest_sha256": batch.get("batch_manifest_sha256"),
                    "first_record_index": batch.get("first_record_index"),
                    "last_record_index": batch.get("last_record_index"),
                }
            )

    mode = "full_snapshot" if previous_manifest is None else "incremental_delta"
    heartbeat_summary = _heartbeat_summary(selected)
    native_ots = _latest_native_ots(
        current_count=current_count,
        current_latest_id=current_latest_id,
        current_latest_sha=current_latest_sha,
    )
    payload = {
        "schema": "trinityaccord.record-chain-arweave-delta.v1",
        "archive_id": archive_id,
        "created_at": manifest.get("created_at"),
        "chain_id": builder.CHAIN_ID,
        "archive_mode": mode,
        "archive_cadence": "weekly",
        "coverage": {
            "previous_native_record_count": previous_count,
            "first_record_id": first_id,
            "last_record_id": last_id,
            "delta_record_count": len(selected),
            "current_native_record_count": current_count,
            "current_latest_record_id": current_latest_id,
            "current_latest_record_sha256": current_latest_sha,
        },
        "previous_archive": None
        if previous_manifest is None
        else {
            "archive_id": previous_manifest.get("archive_id"),
            "manifest_path": str(previous_path.relative_to(builder.ROOT)) if previous_path else None,
            "archive_manifest_sha256": previous_manifest_sha,
            "arweave_txid": previous_txid,
            "latest_record_id": previous_native.get("latest_record_id"),
            "latest_record_sha256": previous_native.get("latest_record_sha256"),
            "native_record_count": previous_count,
        },
        "included_batches": overlapping_batches,
        "included_records": [_record_payload(record_ref) for record_ref in selected],
        "continuity_bundle": {
            "schema": "trinityaccord.weekly-continuity-bundle.v1",
            "heartbeat_summary": heartbeat_summary,
            "latest_native_ots": native_ots,
            "daily_heartbeat_capsules_are_not_required": True,
            "single_paid_payload_covers_records_heartbeats_and_ots": True,
        },
        "source": manifest.get("source", {}),
        "reconstruction": {
            "rule": "Start with the earliest full_snapshot payload, then apply incremental_delta payloads in ascending record order.",
            "previous_archive_txid_required_for_delta": previous_manifest is not None,
            "record_hash_chain_remains_authoritative": True,
        },
        "boundary": {
            "arweave_archive_is_mirror_only": True,
            "arweave_archive_is_not_authority": True,
            "arweave_archive_is_not_attestation": True,
            "arweave_archive_is_not_amendment": True,
            "arweave_archive_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }

    if previous_manifest is not None and not previous_txid:
        raise SystemExit("incremental payload previous archive is missing a verified Arweave transaction id")

    manifest["payload_mode"] = mode
    manifest["payload_delta"] = {
        "previous_archive_txid": previous_txid,
        "previous_native_record_count": previous_count,
        "first_record_id": first_id,
        "last_record_id": last_id,
        "delta_record_count": len(selected),
        "current_native_record_count": current_count,
    }
    manifest["weekly_continuity"] = {
        "heartbeat_count": heartbeat_summary["heartbeat_count"],
        "heartbeat_period_start": heartbeat_summary["period_start"],
        "heartbeat_period_end": heartbeat_summary["period_end"],
        "missing_heartbeat_days": heartbeat_summary["missing_days"],
        "native_ots_record_id": current_latest_id,
        "native_ots_record_sha256": current_latest_sha,
        "native_ots_embedded": True,
    }

    payload_path = archive_dir / "payload.json"
    builder.write_json(payload_path, payload)
    return payload_path
