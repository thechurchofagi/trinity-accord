#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "trinity_record_chain.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_module():
    spec = importlib.util.spec_from_file_location("trinity_record_chain_invariant_test", MODULE_PATH)
    require(spec is not None and spec.loader is not None, "could not load trinity_record_chain")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_record(module, index: int) -> dict:
    record = {
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": module.CHAIN_ID,
        "record_type": "context_insufficient_notice",
        "record_index": index,
        "record_id": module.record_id(index),
        "assigned_at": "2026-07-12T00:00:00Z",
        "previous_record_sha256": None,
        "reason": "invariant test",
        "boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }
    record["content_sha256"] = module.content_hash(record)
    record["record_sha256"] = module.record_hash(record)
    return record


def test_chain_tip_fields(module, root: Path) -> None:
    records = root / "records"
    records.mkdir(parents=True)
    tip_path = root / "chain-tip.json"
    record = make_record(module, 1)
    module.write_json(records / "R-000000001.json", record)
    module.write_json(tip_path, {
        "chain_id": module.CHAIN_ID,
        "latest_record_id": "R-999999999",
        "latest_record_sha256": record["record_sha256"],
        "latest_record_index": 1,
        "native_record_count": 999,
    })
    module.RECORDS = records
    module.CHAIN_TIP = tip_path
    errors = module.verify_native_records()
    require("chain-tip latest_record_id mismatch" in errors, "verify must reject wrong chain-tip latest_record_id")
    require("chain-tip native_record_count mismatch" in errors, "verify must reject wrong chain-tip native_record_count")


def test_batch_binding(module, root: Path) -> None:
    records = root / "batch-records"
    batches = root / "batches"
    genesis = root / "genesis"
    records.mkdir(parents=True)
    (batches / "batch-000001").mkdir(parents=True)
    genesis.mkdir(parents=True)
    record = make_record(module, 1)
    module.write_json(records / "R-000000001.json", record)
    genesis_hash = "b" * 64
    module.write_json(genesis / "genesis-batch-manifest.json", {"batch_manifest_sha256": genesis_hash})
    manifest = {
        "schema": "trinityaccord.record-batch-manifest.v1",
        "batch_id": "batch-000001",
        "chain_id": module.CHAIN_ID,
        "created_at": "2026-07-12T00:00:00Z",
        "record_count": 1,
        "record_ids": ["R-999999999"],
        "first_record_index": 1,
        "last_record_index": 1,
        "first_record_sha256": record["record_sha256"],
        "last_record_sha256": record["record_sha256"],
        "record_sha256_list": [record["record_sha256"]],
        "merkle_root_sha256": module.merkle_root([record["record_sha256"]]),
        "previous_batch_manifest_sha256": genesis_hash,
        "batch_manifest_sha256": None,
        "ots": {"stamped": False, "ots_file": None, "upgraded": False},
        "arweave_archive": {"enabled": False},
        "non_amending_boundary": True,
    }
    manifest["batch_manifest_sha256"] = module.manifest_hash(manifest)
    module.write_json(batches / "batch-000001" / "manifest.json", manifest)
    module.RECORDS = records
    module.BATCHES = batches
    module.GENESIS = genesis
    module.CHAIN_TIP = root / "missing-tip.json"
    errors = module.verify_batches()
    require(any("record_ids do not match" in error for error in errors), "verify must bind batch record_ids to index range")
    require(any("referenced record does not exist" in error for error in errors), "verify must bind batch entries to real records")


def main() -> int:
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        test_chain_tip_fields(module, root / "tip")
        test_batch_binding(module, root / "batch")
    print("PASS: record-chain verifier invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
