#!/usr/bin/env python3
"""Validate exact local mirrors named by the legacy AR/ETH registry.

The registry intentionally records metadata-only, extracted, Release-backed,
sealed, and unresolved objects. This script promotes none of those statuses: it
checks only rows explicitly marked as exact repository payload mirrors.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "archive" / "legacy-pointers" / "index.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    columns = data.get(f"{key}_columns")
    values = data.get(key, [])
    if not isinstance(columns, list) or not all(isinstance(c, str) for c in columns):
        raise ValueError(f"missing or invalid {key}_columns")
    result: list[dict[str, Any]] = []
    for number, value in enumerate(values, start=1):
        if not isinstance(value, list) or len(value) != len(columns):
            raise ValueError(f"{key} row {number} does not match its columns")
        result.append(dict(zip(columns, value, strict=True)))
    return result


def check_one(path_text: str, expected: str, subject: str, failures: list[str]) -> bool:
    path = ROOT / path_text
    if not path.is_file():
        failures.append(f"{subject}: missing {path_text}")
        return False
    actual = sha256_file(path)
    if actual != expected:
        failures.append(f"{subject}: {path_text} expected {expected}, got {actual}")
        return False
    return True


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    failures: list[str] = []
    checked = 0

    if data.get("schema") != "trinityaccord.legacy-pointer-coverage.v1":
        failures.append("unexpected registry schema")

    try:
        arweave = rows(data, "arweave")
        ethereum = rows(data, "ethereum_non_nft")
    except ValueError as exc:
        print(f"FAIL\n  - {exc}")
        return 1

    for item in arweave:
        if item.get("mirror_status") != "repo_exact_hash_verified":
            continue
        expected = item.get("sha256")
        paths = item.get("github_paths") or []
        subject = str(item.get("txid"))
        if not isinstance(expected, str) or len(paths) != 1:
            failures.append(f"{subject}: exact AR status requires one path and SHA-256")
            continue
        checked += check_one(str(paths[0]), expected, subject, failures)

    for item in ethereum:
        if item.get("payload_mirror") not in {"exact_hash_match", "exact_hash_match_reused"}:
            continue
        expected = item.get("input_sha256")
        paths = item.get("payload_paths") or []
        subject = str(item.get("tx_hash"))
        if not isinstance(expected, str) or len(paths) != 1:
            failures.append(f"{subject}: exact ETH status requires one path and SHA-256")
            continue
        checked += check_one(str(paths[0]), expected, subject, failures)

    expected_ar = data.get("summary", {}).get("arweave_records")
    expected_eth = data.get("summary", {}).get("ethereum_non_nft_records")
    if expected_ar != len(arweave):
        failures.append(f"AR summary count {expected_ar} != {len(arweave)} rows")
    if expected_eth != len(ethereum):
        failures.append(f"ETH summary count {expected_eth} != {len(ethereum)} rows")

    print(f"legacy AR registry: {len(arweave)} records")
    print(f"Ethereum non-NFT registry: {len(ethereum)} records")
    print(f"exact repository payloads checked: {checked}")
    print("known unresolved raw AR payloads:")
    for txid in data.get("summary", {}).get("known_raw_payload_gaps", []):
        print(f"  - {txid}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
