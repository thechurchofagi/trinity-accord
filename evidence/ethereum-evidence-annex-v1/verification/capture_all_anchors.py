#!/usr/bin/env python3
"""Capture and bind RPC history for every Ethereum annex anchor.

This is a preservation helper, not an Ethereum writer. It calls the single-anchor
capture helper for each audited transaction, checks captured calldata against the
pre-existing length/SHA-256 commitment, and records the observed block context.
RPC history capture remains reference evidence only; it never promotes L2/L3.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ANNEX_DIR = Path(__file__).resolve().parents[1]
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
CAPTURE = Path(__file__).resolve().with_name("capture_eth_anchor.py")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iso_utc(hex_timestamp: str) -> str:
    value = int(hex_timestamp, 16)
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", required=True)
    ap.add_argument("--sleep-seconds", type=float, default=1.0)
    args = ap.parse_args()

    data = load(MANIFEST)
    anchors = data.get("anchors", [])
    if len(anchors) != 12:
        raise SystemExit(f"expected 12 audited anchors, found {len(anchors)}")

    proof_root = ANNEX_DIR / "proof-material"
    for anchor in anchors:
        txh = anchor["tx_hash"]
        out = proof_root / txh
        subprocess.run(
            [sys.executable, str(CAPTURE), "--rpc", args.rpc, "--tx", txh, "--out", str(out)],
            check=True,
        )

        tx = load(out / "transaction.json")
        receipt = load(out / "receipt.json")
        block = load(out / "block.json")
        capture_manifest = load(out / "capture-manifest.json")

        if tx.get("hash", "").lower() != txh.lower():
            raise SystemExit(f"{txh}: transaction hash mismatch")
        if receipt.get("transactionHash", "").lower() != txh.lower():
            raise SystemExit(f"{txh}: receipt transaction hash mismatch")
        if tx.get("blockHash") != receipt.get("blockHash") or tx.get("blockHash") != block.get("hash"):
            raise SystemExit(f"{txh}: block hash mismatch")
        if capture_manifest.get("chain_id") != "0x1":
            raise SystemExit(f"{txh}: unexpected chain id {capture_manifest.get('chain_id')}")

        raw = bytes.fromhex(tx.get("input", "0x")[2:])
        actual_sha = hashlib.sha256(raw).hexdigest()
        if len(raw) != anchor["input_len"] or actual_sha != anchor["input_sha256"]:
            raise SystemExit(
                f"{txh}: calldata commitment mismatch: len={len(raw)} sha256={actual_sha}"
            )

        ts_hex = block["timestamp"]
        anchor["execution_reference"] = {
            "block_number": int(block["number"], 16),
            "block_hash": block["hash"],
            "block_timestamp_unix": int(ts_hex, 16),
            "block_timestamp_utc": iso_utc(ts_hex),
            "transaction_index": int(tx["transactionIndex"], 16),
            "receipt_status": receipt.get("status"),
            "reference_checked": True,
            "reference_kind": "preserved_rpc_capture",
            "reference_capture_path": str((out / "capture-manifest.json").relative_to(Path.cwd())),
            "reference_provider": args.rpc,
            "claim_boundary": (
                "Provider-returned historical evidence preserved for future inspection; "
                "not by itself an offline Merkle inclusion or PoS finality proof."
            ),
        }
        anchor["rpc_capture_status"] = "REFERENCE_CAPTURED"
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    policy = data.setdefault("proof_material_policy", {})
    policy["rpc_history_capture"] = "PRESERVED_FOR_ALL_12_ANCHORS_REFERENCE_ONLY"
    policy["rpc_history_capture_boundary"] = (
        "Preserving transaction/receipt/block JSON freezes the observed Ethereum block timestamp "
        "and commitment context, but does not upgrade L2/L3 without independent inclusion/finality proof validation."
    )
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: captured and bound Ethereum history for 12/12 audited anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
