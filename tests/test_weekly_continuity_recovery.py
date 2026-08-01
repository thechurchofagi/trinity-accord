from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import restore_weekly_continuity_archive as recovery  # noqa: E402
import trinity_record_chain as chain  # noqa: E402


def encoded(path: str, raw: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "content_base64": base64.b64encode(raw).decode("ascii"),
    }


def native_record(index: int, previous_sha: str | None) -> tuple[dict[str, Any], bytes]:
    record_id = f"R-{index:09d}"
    record: dict[str, Any] = {
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": chain.CHAIN_ID,
        "record_type": "context_insufficient_notice",
        "record_id": record_id,
        "record_index": index,
        "assigned_at": f"2026-08-{index:02d}T00:00:00Z",
        "previous_record_sha256": previous_sha,
        "context_insufficient_notice": {"reason": f"test-{index}"},
    }
    record["content_sha256"] = chain.content_hash(record)
    record["record_sha256"] = chain.record_hash(record)
    raw = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return record, raw


def build_records(count: int) -> list[tuple[dict[str, Any], bytes]]:
    result: list[tuple[dict[str, Any], bytes]] = []
    previous_sha: str | None = None
    for index in range(1, count + 1):
        record, raw = native_record(index, previous_sha)
        result.append((record, raw))
        previous_sha = str(record["record_sha256"])
    return result


def source(
    records: list[tuple[dict[str, Any], bytes]],
    *,
    archive_id: str,
    first_index: int,
    txid: str,
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    selected = records[first_index - 1 :]
    latest = records[-1][0]
    included = []
    for record, raw in selected:
        item = encoded(f"record-chain/records/{record['record_id']}.json", raw)
        item.update(
            {
                "record_id": record["record_id"],
                "record_sha256": record["record_sha256"],
                "raw_file_sha256": item.pop("sha256"),
            }
        )
        included.append(item)
    artifacts = [
        encoded(f"record-chain/ots/test-{archive_id}.{suffix}", raw)
        for suffix, raw in (
            ("anchor.json", b"anchor"),
            ("commitment.json", b"commitment"),
            ("commitment.json.ots", b"ots-proof"),
        )
    ]
    payload = {
        "schema": "trinityaccord.record-chain-arweave-delta.v1",
        "archive_id": archive_id,
        "created_at": "2026-08-01T00:00:00Z",
        "chain_id": chain.CHAIN_ID,
        "archive_mode": "full_snapshot" if previous is None else "incremental_delta",
        "archive_cadence": "weekly",
        "coverage": {
            "previous_native_record_count": first_index - 1,
            "delta_record_count": len(selected),
            "current_native_record_count": len(records),
            "current_latest_record_id": latest["record_id"],
            "current_latest_record_sha256": latest["record_sha256"],
        },
        "previous_archive": previous,
        "included_records": included,
        "continuity_bundle": {
            "schema": "trinityaccord.weekly-continuity-bundle.v1",
            "latest_native_ots": {
                "metadata": {
                    "native_record_count": len(records),
                    "latest_record_id": latest["record_id"],
                    "latest_record_sha256": latest["record_sha256"],
                },
                "artifacts": artifacts,
                "covers_current_chain_head": True,
            },
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "label": archive_id,
        "payload": payload,
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "package_identity_sha256": None,
        "txid": txid,
        "source_type": "test_verified_transport",
    }


def complete_series() -> tuple[list[dict[str, Any]], list[tuple[dict[str, Any], bytes]]]:
    first_records = build_records(2)
    all_records = build_records(3)
    baseline_txid = "A" * 43
    baseline = source(
        first_records,
        archive_id="weekly-baseline",
        first_index=1,
        txid=baseline_txid,
        previous=None,
    )
    previous = {
        "archive_id": "weekly-baseline",
        "arweave_txid": baseline_txid,
        "native_record_count": 2,
        "latest_record_id": first_records[-1][0]["record_id"],
        "latest_record_sha256": first_records[-1][0]["record_sha256"],
    }
    delta = source(
        all_records,
        archive_id="weekly-delta",
        first_index=3,
        txid="B" * 43,
        previous=previous,
    )
    return [delta, baseline], all_records


def test_recovery_rebuilds_native_records_and_checks_archive_link(tmp_path):
    sources, records = complete_series()
    output = tmp_path / "restore"
    report = recovery.recover(sources, output)

    assert report["recovery_status"] == "full_recovery"
    assert report["native_record_count"] == 3
    assert report["latest_record_id"] == "R-000000003"
    assert report["arweave_transaction_links_verified"] == 1
    for record, raw in records:
        restored = output / "record-chain" / "records" / f"{record['record_id']}.json"
        assert restored.read_bytes() == raw
    assert json.loads((output / "recovery-report.json").read_text())["result"] == "pass"


def test_recovery_refuses_series_without_full_snapshot(tmp_path):
    sources, _records = complete_series()
    with pytest.raises(SystemExit, match="must begin with the full_snapshot"):
        recovery.recover([sources[0]], tmp_path / "missing-baseline")


def test_recovery_refuses_wrong_previous_archive_identity(tmp_path):
    sources, _records = complete_series()
    sources[0]["payload"]["previous_archive"]["archive_id"] = "wrong-baseline"
    with pytest.raises(SystemExit, match="previous-archive identity mismatch"):
        recovery.recover(sources, tmp_path / "wrong-link")


def test_recovery_refuses_tampered_embedded_record(tmp_path):
    sources, _records = complete_series()
    sources[1]["payload"]["included_records"][0]["content_base64"] = base64.b64encode(
        b"tampered"
    ).decode("ascii")
    with pytest.raises(SystemExit, match="byte length mismatch|SHA-256 mismatch"):
        recovery.recover(sources, tmp_path / "tampered")


def test_zenodo_public_content_link_takes_precedence_over_metadata_self_link():
    assert recovery.zenodo_file_download_url(
        {
            "links": {
                "self": "https://zenodo.example/api/records/1/files/data.json",
                "content": "https://zenodo.example/api/records/1/files/data.json/content",
            }
        }
    ).endswith("/content")


def test_arweave_multi_gateway_requires_byte_consensus_and_expected_hash(monkeypatch):
    raw = json.dumps(complete_series()[0][1]["payload"], sort_keys=True).encode()
    expected = hashlib.sha256(raw).hexdigest()

    monkeypatch.setattr(recovery, "fetch_bytes", lambda *_args, **_kwargs: raw)
    restored = recovery.source_from_arweave(
        "A" * 43,
        [
            "https://gateway-one.example/{txid}",
            "https://gateway-two.example/{txid}",
        ],
        expected,
    )
    transport = restored["transport_verification"]
    assert transport["gateway_success_count"] == 2
    assert transport["gateway_byte_consensus"] is True
    assert transport["expected_payload_sha256_verified"] is True


def test_arweave_multi_gateway_refuses_disagreement(monkeypatch):
    calls = iter([b"first", b"second"])
    monkeypatch.setattr(recovery, "fetch_bytes", lambda *_args, **_kwargs: next(calls))
    with pytest.raises(SystemExit, match="gateway byte disagreement"):
        recovery.source_from_arweave(
            "A" * 43,
            [
                "https://gateway-one.example/{txid}",
                "https://gateway-two.example/{txid}",
            ],
        )
