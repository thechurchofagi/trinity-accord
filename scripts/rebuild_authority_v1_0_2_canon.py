#!/usr/bin/env python3
"""Reconstruct and verify the exact signed Authority v1.0.2 JCS payload."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from validate_authority_manifest import stable_json


ROOT = Path(__file__).resolve().parents[1]
PRETTY = ROOT / "archive/authority-manifest/authority-v1.0.2-pretty.json"
CANON = ROOT / "archive/authority-manifest/authority-v1.0.2-canon.json"
ADDITIONS = ROOT / "archive/authority-manifest/authority-v1.0.2-additions.json"
SIGNATURE = ROOT / "archive/authority-manifest/authority-v1.0.2-signature.json"
TYPED_DATA = ROOT / "archive/authority-manifest/authority-v1.0.2-typedData.json"
READBACK_AUDIT = (
    ROOT / "evidence/redteam-audit-2026-05-08/audit_report_eth_path2.json"
)

TXID = "TvmjyJBq5ZoGv-tmX0aeiqsEKTGmSyIvBHj1FqZiIpI"
EXPECTED_BYTES = 9174
EXPECTED_SHA256 = "7d6ac9d3184bb5b0bbaf8217354799efef68669c21b4180e28ec06b0c57439e6"
EXPECTED_SHA3_256 = "31442fec86514a84b1d691509bdc66bd6774d96e93941eea153de6a9e118d8d0"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def find_readback_observation(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("label") == "archive/authority-manifest/authority-v1.0.2-canon.json":
            return value
        for child in value.values():
            result = find_readback_observation(child)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = find_readback_observation(child)
            if result is not None:
                return result
    return None


def build_and_validate() -> bytes:
    canonical = stable_json(load(PRETTY)).encode("utf-8")
    sha256 = hashlib.sha256(canonical).hexdigest()
    sha3_256 = hashlib.sha3_256(canonical).hexdigest()
    if len(canonical) != EXPECTED_BYTES:
        raise ValueError(f"canonical byte count drift: {len(canonical)} != {EXPECTED_BYTES}")
    if sha256 != EXPECTED_SHA256:
        raise ValueError(f"canonical SHA-256 drift: {sha256} != {EXPECTED_SHA256}")
    if sha3_256 != EXPECTED_SHA3_256:
        raise ValueError(f"canonical SHA3-256 drift: {sha3_256} != {EXPECTED_SHA3_256}")

    authority = load(ADDITIONS)["authority_v1_0_2"]
    if authority["canon"] != {"txId": TXID, "sha256": EXPECTED_SHA256}:
        raise ValueError("Authority additions canon pointer drift")
    if authority["covers"] != {
        "sha256": EXPECTED_SHA256,
        "sha3_256": EXPECTED_SHA3_256,
    }:
        raise ValueError("Authority additions covered digests drift")

    expected_message = {
        "version": "1.0.2",
        "sha256": "0x" + EXPECTED_SHA256,
        "sha3_256": "0x" + EXPECTED_SHA3_256,
        "createdAt": "2025-09-24T03:43:44.148Z",
    }
    signature = load(SIGNATURE)
    typed_data = load(TYPED_DATA)
    if signature.get("match") is not True or signature.get("recovered") != signature.get("signer"):
        raise ValueError("Authority EIP-712 signer recovery is not a match")
    if signature.get("typedData", {}).get("message") != expected_message:
        raise ValueError("Authority signature message digest drift")
    if typed_data.get("message") != expected_message:
        raise ValueError("Authority typed-data message digest drift")

    observation = find_readback_observation(load(READBACK_AUDIT))
    if observation is None or observation.get("status") != "PASS":
        raise ValueError("checked-in Arweave readback observation is missing or not PASS")
    attempt = observation.get("attempt", {})
    if attempt.get("actual_sha256") != EXPECTED_SHA256:
        raise ValueError("checked-in Arweave readback SHA-256 drift")
    if attempt.get("actual_size") != EXPECTED_BYTES:
        raise ValueError("checked-in Arweave readback byte count drift")
    return canonical


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Replace the checked-in canonical payload after all bindings pass",
    )
    args = parser.parse_args()
    try:
        canonical = build_and_validate()
        if args.write:
            CANON.write_bytes(canonical)
        elif not CANON.is_file() or CANON.read_bytes() != canonical:
            raise ValueError(
                "checked-in Authority v1.0.2 canon bytes drifted; run with --write"
            )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"AUTHORITY_V1_0_2_CANON_FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "AUTHORITY_V1_0_2_CANON_OK "
        f"bytes={len(canonical)} sha256={EXPECTED_SHA256} sha3_256={EXPECTED_SHA3_256}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
