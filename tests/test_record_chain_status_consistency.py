from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_record_chain_status_matches_chain_tip() -> None:
    tip = _read_json("record-chain/chain-tip.json")
    status = _read_json("api/record-chain-status.json")

    record_chain = status["record_chain"]
    assert record_chain["latest_record_id"] == tip["latest_record_id"]
    assert record_chain["latest_record_index"] == tip["latest_record_index"]
    assert record_chain["latest_record_sha256"] == tip["latest_record_sha256"]
    assert record_chain["native_record_count"] == tip["native_record_count"]
    assert record_chain["current_chain_length"] == tip["native_record_count"]

    pipeline_head = status["pipeline_status"]["chain_head"]
    assert pipeline_head["latest_record_id"] == tip["latest_record_id"]
    assert pipeline_head["latest_record_sha256"] == tip["latest_record_sha256"]
    assert pipeline_head["native_record_count"] == tip["native_record_count"]


def test_latest_record_is_present_in_indexes() -> None:
    tip = _read_json("record-chain/chain-tip.json")
    record_index = _read_json("record-chain/indexes/record-index.json")

    latest = record_index["records"][-1]
    assert latest["record_id"] == tip["latest_record_id"]
    assert latest["record_sha256"] == tip["latest_record_sha256"]
    assert latest["path"] == f"record-chain/records/{tip['latest_record_id']}.json"

    latest_record = _read_json(latest["path"])
    assert latest_record["record_id"] == tip["latest_record_id"]
    assert latest_record["record_index"] == tip["latest_record_index"]
    assert latest_record["record_sha256"] == tip["latest_record_sha256"]


def test_receipt_statuses_point_to_existing_final_records() -> None:
    for path in sorted((ROOT / "record-chain" / "receipt-status").glob("*.json")):
        status = json.loads(path.read_text(encoding="utf-8"))
        if status.get("append_status") != "appended":
            continue
        final_path = status.get("final_record_path")
        assert isinstance(final_path, str), path
        final_record = _read_json(final_path)
        assert final_record["record_id"] == status["final_record_id"]
        assert final_record["record_sha256"] == status["final_record_sha256"]
