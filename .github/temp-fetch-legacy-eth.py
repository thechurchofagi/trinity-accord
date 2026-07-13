#!/usr/bin/env python3
"""Temporary one-shot retrieval of legacy Ethereum non-NFT calldata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "archive" / "legacy-pointers" / "eth-raw"
OUT.mkdir(parents=True, exist_ok=True)

TRANSACTIONS = {
    "0x59cf33b1291de63c4840b79e7c674b8fc7c6a771d8a3ba2bb50def1fe55a71c6": {
        "label": "BTC-ETH Guardianship Mirrors Attestation",
        "expected_len": 3231,
        "expected_sha256": "f4af38f0f42c9b38deaccbace119736da57a245a6601e5d0ea5698deec4a8a01",
        "status": "final_valid",
    },
    "0x55a0c131642f71c7b2386ccaac8bcee36563992226befb35363e978044a18e8f": {
        "label": "BIP-322 notice (non-amending)",
        "expected_len": 412,
        "expected_sha256": "abd10a807323ef3a07fe22eb3a3cc083e77db93d7362eb29c939c195825f2c2d",
        "status": "final_valid",
    },
    "0xa4023b1eb0de76993e1a8dcd571e5e033bf64e2d32a9a113b030b4094a19cf51": {
        "label": "Mirror correction (final version)",
        "expected_len": 4994,
        "expected_sha256": "fc009f5393b11e95f013464405e24c9713a55415fa326b2707886d436d4cbd6f",
        "status": "final_valid_supersedes_error",
    },
    "0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6": {
        "label": "Mirror correction (superseded erroneous version)",
        "expected_len": None,
        "expected_sha256": None,
        "status": "superseded_error_preserved",
    },
}

RPCS = [
    "https://ethereum-rpc.publicnode.com",
    "https://eth.llamarpc.com",
    "https://1rpc.io/eth",
    "https://rpc.flashbots.net",
]


def rpc_fetch(tx_hash: str) -> tuple[dict[str, object], str]:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionByHash", "params": [tx_hash]},
        separators=(",", ":"),
    )
    errors: list[str] = []
    for rpc in RPCS:
        result = subprocess.run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--location",
                "--retry",
                "2",
                "--connect-timeout",
                "20",
                "--max-time",
                "90",
                "-H",
                "Content-Type: application/json",
                "--data",
                body,
                rpc,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(f"{rpc}: curl exit {result.returncode}: {result.stderr.strip()}")
            time.sleep(1)
            continue
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"{rpc}: invalid JSON: {exc}")
            continue
        transaction = payload.get("result")
        if isinstance(transaction, dict) and isinstance(transaction.get("input"), str):
            return transaction, rpc
        errors.append(f"{rpc}: missing transaction result: {payload.get('error')}")
    raise RuntimeError(f"Unable to retrieve {tx_hash}: {'; '.join(errors)}")


def main() -> None:
    metadata: list[dict[str, object]] = []
    checksum_lines: list[str] = []

    for tx_hash, spec in TRANSACTIONS.items():
        transaction, rpc = rpc_fetch(tx_hash)
        input_hex = str(transaction["input"])
        if not input_hex.startswith("0x"):
            raise ValueError(f"{tx_hash}: input does not start with 0x")
        raw = bytes.fromhex(input_hex[2:])
        if not raw:
            raise ValueError(f"{tx_hash}: empty calldata")

        actual_len = len(raw)
        actual_sha = hashlib.sha256(raw).hexdigest()
        expected_len = spec["expected_len"]
        expected_sha = spec["expected_sha256"]
        length_matches = expected_len is None or actual_len == expected_len
        sha256_matches = expected_sha is None or actual_sha == expected_sha

        filename = f"{tx_hash}.raw"
        path = OUT / filename
        path.write_bytes(raw)
        checksum_lines.append(f"{actual_sha}  archive/legacy-pointers/eth-raw/{filename}")
        metadata.append(
            {
                "label": spec["label"],
                "tx_hash": tx_hash,
                "status": spec["status"],
                "chain_id": transaction.get("chainId"),
                "from": transaction.get("from"),
                "to": transaction.get("to"),
                "input_len": actual_len,
                "input_sha256": actual_sha,
                "expected_input_len": expected_len,
                "expected_input_sha256": expected_sha,
                "length_matches_expected": length_matches,
                "sha256_matches_expected": sha256_matches,
                "source_rpc": rpc,
                "path": f"archive/legacy-pointers/eth-raw/{filename}",
                "boundary": "Non-amending Ethereum calldata mirror; Bitcoin Originals prevail.",
            }
        )
        print(
            f"retrieved {tx_hash}: {actual_len} bytes, {actual_sha}, "
            f"length_match={length_matches}, sha_match={sha256_matches}"
        )

    (OUT / "SHA256SUMS").write_text("\n".join(sorted(checksum_lines)) + "\n", encoding="utf-8")
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "schema": "trinityaccord.ethereum-non-nft-calldata-mirror.v1",
                "boundary": "Non-amending Ethereum calldata mirror; Bitcoin Originals prevail.",
                "transactions": metadata,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
