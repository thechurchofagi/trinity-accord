#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
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


def verify_record_variant(module, root: Path, *, filename: str = "R-000000001.json", **changes) -> list[str]:
    records = root / "records"
    records.mkdir(parents=True)
    record = make_record(module, 1)
    record.update(changes)
    record.pop("content_sha256", None)
    record.pop("record_sha256", None)
    record["content_sha256"] = module.content_hash(record)
    record["record_sha256"] = module.record_hash(record)
    module.write_json(records / filename, record)
    module.RECORDS = records
    module.CHAIN_TIP = root / "missing-tip.json"
    return module.verify_native_records()


def test_native_record_semantic_domain(module, root: Path) -> None:
    cases = [
        (
            "filename",
            {"filename": "R-999999999.json"},
            "filename expected R-000000001.json",
        ),
        (
            "schema",
            {"schema": "attacker.self-consistent-record.v1"},
            "is not an allowed native Record-Chain schema",
        ),
        (
            "chain",
            {"chain_id": "attacker-chain"},
            "does not match 'trinity-accord-public-reception-ledger'",
        ),
        (
            "record-type",
            {"record_type": "invented_record_type"},
            "is not an allowed native Record-Chain record type",
        ),
    ]
    for name, changes, expected_error in cases:
        errors = verify_record_variant(module, root / name, **changes)
        require(
            any(expected_error in error for error in errors),
            f"verify must reject self-consistent record with wrong {name}: {errors}",
        )

    draft_base = {
        "record_type": "invented_record_type",
        "actor_identity": {"label": "invariant-test"},
        "context_readiness": {"declared_context_level": "CC-0"},
        "boundary_acknowledgement": dict(module.BOUNDARY),
    }
    try:
        module.normalize_record_draft(draft_base)
    except ValueError as exc:
        require(
            "is not an allowed native Record-Chain record type" in str(exc),
            f"append normalization rejected unknown type for the wrong reason: {exc}",
        )
    else:
        require(False, "append normalization must reject unknown native record types")


def test_frozen_v1_schema_generation(module, root: Path) -> None:
    chain = root / "record-chain"
    paths = {
        "CHAIN": chain,
        "GENESIS": chain / "genesis",
        "LEGACY_RECORDS": chain / "genesis" / "legacy-records",
        "RECORDS": chain / "records",
        "PENDING": chain / "pending",
        "PROCESSED": chain / "processed",
        "REJECTED": chain / "rejected",
        "RECEIPT_STATUS": chain / "receipt-status",
        "BATCHES": chain / "batches",
        "INDEXES": chain / "indexes",
        "POLICIES": chain / "policies",
        "SCHEMAS": chain / "schemas",
        "ANCHORS": chain / "anchors",
        "ARWEAVE_ARCHIVES": chain / "arweave-archives",
    }
    for name, path in paths.items():
        setattr(module, name, path)

    module.init_policies()
    generated = json.loads((paths["SCHEMAS"] / "record-chain-entry.v1.schema.json").read_text(encoding="utf-8"))
    committed = json.loads(
        (ROOT / "record-chain" / "schemas" / "record-chain-entry.v1.schema.json").read_text(encoding="utf-8")
    )
    require(generated == committed, "init must not rewrite the published record-chain-entry.v1 schema")


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
        test_native_record_semantic_domain(module, root / "domain")
        test_batch_binding(module, root / "batch")
        test_frozen_v1_schema_generation(module, root / "schema")
    print("PASS: record-chain verifier invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
