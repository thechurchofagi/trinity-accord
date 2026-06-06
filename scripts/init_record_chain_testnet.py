#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTNET_CHAIN_ID = "trinity-record-chain-testnet"

TESTNET_LEDGER = ROOT / "record-chain/testnet/hash-chain/testnet.chain.jsonl"
TESTNET_HEAD = ROOT / "api/record-chain-testnet/record-chain-head.json"
TESTNET_OTS_LATEST = ROOT / "api/record-chain-testnet/ots-latest.json"
TESTNET_REGISTRY = ROOT / "record-chain/testnet/ots/arweave-registry.json"
TESTNET_REGISTRY_API = ROOT / "api/record-chain-testnet/ots-arweave-registry.json"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    # Create directories
    for d in [
        TESTNET_LEDGER.parent,
        TESTNET_HEAD.parent,
        ROOT / "record-chain/testnet/ots/anchors",
        ROOT / "record-chain/testnet/ots/arweave-bundles",
        ROOT / "record-chain/testnet/audit",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Initialize empty ledger if not exists
    if not TESTNET_LEDGER.exists():
        TESTNET_LEDGER.write_text("", encoding="utf-8")
        print(f"[INIT] Created empty testnet ledger: {TESTNET_LEDGER}")

    # Initialize empty head if not exists
    if not TESTNET_HEAD.exists():
        write_json(TESTNET_HEAD, {
            "schema": "trinity_record_chain_head.v1",
            "chain_id": TESTNET_CHAIN_ID,
            "chain_version": "1.0.0",
            "head_entry_hash": None,
            "entry_count": 0,
            "generated_at": utc_now(),
        })
        print(f"[INIT] Created testnet head: {TESTNET_HEAD}")

    # Initialize OTS latest
    if not TESTNET_OTS_LATEST.exists():
        write_json(TESTNET_OTS_LATEST, {
            "schema": "trinity_record_chain_ots_latest.v1",
            "chain_id": TESTNET_CHAIN_ID,
            "head_entry_hash": None,
            "latest_anchor_file": None,
            "latest_anchored_file": None,
            "latest_ots_file": None,
            "ots_status": "dry_run",
            "updated_at": utc_now(),
        })
        print(f"[INIT] Created testnet OTS latest: {TESTNET_OTS_LATEST}")

    # Initialize registries
    empty_registry = {
        "schema": "trinity_record_chain_ots_arweave_registry.v1",
        "chain_id": TESTNET_CHAIN_ID,
        "authority": (
            "registry of Arweave archives for TESTNET OTS head anchors; "
            "testnet.chain.jsonl remains authoritative"
        ),
        "entries": [],
        "latest_by_head": {},
        "generated_at": utc_now(),
    }
    if not TESTNET_REGISTRY.exists():
        write_json(TESTNET_REGISTRY, empty_registry)
        print(f"[INIT] Created testnet registry: {TESTNET_REGISTRY}")
    if not TESTNET_REGISTRY_API.exists():
        write_json(TESTNET_REGISTRY_API, empty_registry)
        print(f"[INIT] Created testnet API registry: {TESTNET_REGISTRY_API}")

    print(f"[INIT] Testnet chain_id: {TESTNET_CHAIN_ID}")
    print("[INIT] Done. Testnet infrastructure initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
