#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import time
from pathlib import Path
from typing import Any
import hashlib


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def file_entry(path: Path, role: str, include_base64: bool) -> dict[str, Any]:
    data = path.read_bytes()
    entry = {
        "role": role,
        "path": str(path),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "encoding": "base64" if include_base64 else "external",
    }
    if include_base64:
        entry["base64"] = base64.b64encode(data).decode("ascii")
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a JSON bundle containing a Record-Chain OTS anchor and proof for Arweave upload."
    )
    parser.add_argument("--anchor-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--include-base64", action="store_true", default=True)
    parser.add_argument("--no-base64", action="store_true")
    args = parser.parse_args()

    anchor_path = Path(args.anchor_file)
    out_path = Path(args.out)
    include_base64 = args.include_base64 and not args.no_base64

    anchor = load_json(anchor_path)
    if anchor.get("schema") not in {
        "trinity_record_chain_ots_anchor.v1",
        "trinityaccord.native-record-chain-ots-anchor.v1",
    }:
        raise SystemExit(f"anchor schema mismatch: {anchor.get('schema')}")
    is_native = anchor.get("schema") == "trinityaccord.native-record-chain-ots-anchor.v1"

    anchored_file = Path(anchor.get("anchored_file", ""))
    if not anchored_file.exists():
        raise SystemExit(f"anchored file missing: {anchored_file}")

    anchored_sha = sha256_bytes(anchored_file.read_bytes())
    if anchored_sha != anchor.get("anchored_file_sha256"):
        raise SystemExit(
            f"anchored file sha mismatch: expected {anchor.get('anchored_file_sha256')}, got {anchored_sha}"
        )

    files = [
        file_entry(anchored_file, "head_commitment_snapshot", include_base64),
        file_entry(anchor_path, "ots_anchor_metadata", include_base64),
    ]

    ots_file = anchor.get("ots_file")
    if ots_file:
        ots_path = Path(ots_file)
        if not ots_path.exists():
            raise SystemExit(f"ots file missing: {ots_path}")
        ots_entry = file_entry(ots_path, "ots_proof", include_base64)
        if anchor.get("ots_file_sha256") and ots_entry["sha256"] != anchor.get("ots_file_sha256"):
            raise SystemExit(
                f"ots file sha mismatch: expected {anchor.get('ots_file_sha256')}, got {ots_entry['sha256']}"
            )
        files.append(ots_entry)

    bundle = {
        "schema": "trinity_record_chain_ots_arweave_bundle.v1",
        "chain_id": anchor.get("chain_id"),
        "chain_version": anchor.get("chain_version"),
        "height": anchor.get("height", anchor.get("latest_record_index")),
        "entry_count": anchor.get("entry_count", anchor.get("native_record_count")),
        "head_entry_hash": anchor.get("head_entry_hash", anchor.get("latest_record_sha256")),
        "native_anchor": is_native,
        "native_latest_record_id": anchor.get("latest_record_id"),
        "native_latest_record_sha256": anchor.get("latest_record_sha256"),
        "native_record_count": anchor.get("native_record_count"),
        "anchored_file_sha256": anchor.get("anchored_file_sha256"),
        "ots_status": anchor.get("ots_status"),
        "bitcoin_verified": anchor.get("bitcoin_verified"),
        "bitcoin_pending": anchor.get("bitcoin_pending"),
        "bitcoin_attestation_embedded": anchor.get("bitcoin_attestation_embedded", False),
        "created_at": utc_now(),
        "source_anchor_file": str(anchor_path),
        "files": files,
        "semantics": (
            "Arweave bundle for an OTS proof of a stable Record-Chain head commitment. "
            "This archive is separate from the main Record-Chain Arweave archive and does not modify entry_hash."
        ),
    }

    write_json(out_path, bundle)
    bundle_sha = sha256_bytes(out_path.read_bytes())

    summary = {
        "bundle_file": str(out_path),
        "bundle_sha256": bundle_sha,
        "bytes": out_path.stat().st_size,
        "height": bundle["height"],
        "head_entry_hash": bundle["head_entry_hash"],
        "ots_status": bundle["ots_status"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
