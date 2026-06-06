#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTNET_CHAIN_ID = "trinity-record-chain-testnet"

REQUIRED_RECORDS = [
    ("echo", None),
    ("verification", "V0"),
    ("verification", "V1"),
    ("verification", "V2"),
    ("verification", "V3"),
    ("guardian_application", None),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def record_key_from_payload(payload: dict):
    rt = payload.get("record_type")
    level = None
    if rt == "verification":
        level = payload.get("source_summary", {}).get("verification_level")
        if level is None:
            level = payload.get("source_summary", {}).get("verification_content", {}).get("verification_level")
    return rt, level


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 7B real testnet outputs.")
    parser.add_argument("--external-summary", required=True)
    parser.add_argument("--ots-summary", required=True)
    args = parser.parse_args()

    external_summary = read_json(Path(args.external_summary))
    ots_summary = read_json(Path(args.ots_summary))

    require(external_summary.get("result") == "pass", "external agent summary must pass")
    require(ots_summary.get("result") == "pass", "OTS/Arweave summary must pass")
    require(ots_summary.get("chain_id") == TESTNET_CHAIN_ID, "OTS summary chain_id mismatch")
    require(ots_summary.get("readback_hash_match") is True, "Arweave readback hash must match")
    require(ots_summary.get("mainnet_unchanged") is True, "mainnet must be unchanged in OTS summary")

    tags = {tag.get("name"): tag.get("value") for tag in ots_summary.get("arweave_extra_tags", [])}
    require(tags.get("Chain-Id") == TESTNET_CHAIN_ID, "Arweave tx missing Chain-Id testnet tag")
    require(tags.get("Environment") == "testnet", "Arweave tx missing Environment=testnet tag")
    require(tags.get("Test-Only") == "true", "Arweave tx missing Test-Only=true tag")
    require(tags.get("Not-Mainnet") == "true", "Arweave tx missing Not-Mainnet=true tag")

    ledger = load_jsonl(ROOT / "record-chain/testnet/hash-chain/testnet.chain.jsonl")
    require(len(ledger) >= 7, "testnet ledger should contain genesis + at least 6 external records")

    seen = set()
    for entry in ledger:
        require(entry.get("chain_id") == TESTNET_CHAIN_ID, "testnet ledger entry chain_id mismatch")
        record = entry.get("record", {})
        rid = record.get("record_id")
        require(isinstance(rid, str) and rid.startswith("T-"), "testnet record_id must start with T-")

        payload_path = ROOT / record.get("payload_file", "")
        if payload_path.exists():
            payload = read_json(payload_path)
            require(payload.get("chain_id") == TESTNET_CHAIN_ID, "payload chain_id mismatch")
            require(payload.get("not_mainnet") is True, "payload not_mainnet must be true")
            require(payload.get("test_only") is True, "payload test_only must be true")
            raw = json.dumps(payload, ensure_ascii=False)
            require("readback_text" not in raw, "finalized payload must not embed raw readback_text")
            require("client_oath_readback" not in raw, "finalized payload must not embed client_oath_readback")
            rt = payload.get("record_type")
            level = payload.get("source_summary", {}).get("verification_level")
            if rt == "verification" and level:
                seen.add((rt, level))
            elif rt in ["echo", "guardian_application"]:
                seen.add((rt, None))

    missing = [item for item in REQUIRED_RECORDS if item not in seen]
    require(not missing, f"missing required finalized testnet records: {missing}")

    head = read_json(ROOT / "api/record-chain-testnet/record-chain-head.json")
    require(head.get("chain_id") == TESTNET_CHAIN_ID, "testnet head chain_id mismatch")
    require(head.get("entry_count") == len(ledger), "testnet head entry_count mismatch")

    registry = read_json(ROOT / "api/record-chain-testnet/ots-arweave-registry.json")
    require(registry.get("chain_id") == TESTNET_CHAIN_ID, "testnet registry chain_id mismatch")

    main_head = read_json(ROOT / "api/record-chain-head.json")
    require(main_head.get("chain_id") == "trinity-record-chain-main", "mainnet head chain_id changed")

    print("PASS: Phase 7B real testnet outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
