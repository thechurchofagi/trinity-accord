#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN_TIP = ROOT / "record-chain/chain-tip.json"
OTS_LATEST = ROOT / "api/record-chain-native-ots-latest.json"
ARWEAVE_INDEX = ROOT / "api/record-chain-arweave-index.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))




def native_ots_head_matches_chain(tip: dict[str, Any], ots: dict[str, Any]) -> bool:
    """Return True when current native chain head already has a matching OTS anchor.

    This must not require Bitcoin verification. A pending/upgraded anchor still
    means the current head has already been stamped and should not be stamped again.
    """
    return (
        bool(tip.get("latest_record_id"))
        and ots.get("latest_record_id") == tip.get("latest_record_id")
        and ots.get("latest_record_sha256") == tip.get("latest_record_sha256")
        and ots.get("native_record_count") == tip.get("native_record_count")
        and ots.get("legacy_main_chain_jsonl_is_not_source") is True
        and bool(ots.get("latest_anchor_file"))
        and bool(ots.get("latest_ots_file"))
    )


def native_ots_is_strictly_verified(ots: dict[str, Any]) -> bool:
    """Return True only when strict Bitcoin-node verification succeeded."""
    return (
        ots.get("ots_status") == "verified"
        and ots.get("bitcoin_verified") is True
        and ots.get("strict_bitcoin_verified") is True
    )


def native_ots_has_bitcoin_attestation(ots: dict[str, Any]) -> bool:
    """Return True for upgraded proofs with embedded BitcoinBlockHeaderAttestation."""
    return (
        ots.get("ots_status") == "upgraded"
        and ots.get("bitcoin_attestation_embedded") is True
        and ots.get("bitcoin_pending") is False
    )


def native_ots_archivable_for_arweave(tip: dict[str, Any], ots: dict[str, Any]) -> bool:
    """Return True when native OTS is sufficient for Arweave mirror/archive.

    This does not imply strict Bitcoin verification and must not set
    bitcoin_verified=true.
    """
    return (
        native_ots_head_matches_chain(tip, ots)
        and (
            native_ots_is_strictly_verified(ots)
            or native_ots_has_bitcoin_attestation(ots)
        )
    )

def is_verified_live_archive(arweave_entry: dict[str, Any]) -> bool:
    """Return True only if the archive entry is live AND fully verified.

    Requires: txid present, upload_mode=live, archive_status=archived,
    verified=True, hash_match=True.
    A txid alone is NOT sufficient.
    """
    return (
        bool(arweave_entry.get("arweave_txid") or arweave_entry.get("txid"))
        and arweave_entry.get("source_type") == "native-record-chain"
        and arweave_entry.get("mode") == "live"
        and arweave_entry.get("archive_status") == "archived"
        and arweave_entry.get("verified") is True
        and arweave_entry.get("hash_match") is True
    )


def latest_live_native_archive(index: dict[str, Any]) -> dict[str, Any] | None:
    live = [
        a for a in index.get("archives", [])
        if is_verified_live_archive(a)
    ]
    if not live:
        return None
    live.sort(key=lambda a: (a.get("native_record_count") or 0, a.get("created_at") or ""))
    return live[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()

    tip = read_json(CHAIN_TIP)
    ots = read_json(OTS_LATEST)
    ar = latest_live_native_archive(read_json(ARWEAVE_INDEX)) or {}

    chain_id = tip.get("latest_record_id") or ""
    chain_sha = tip.get("latest_record_sha256") or ""
    chain_count = tip.get("native_record_count") or ""

    ots_id = ots.get("latest_record_id") or ""
    ots_sha = ots.get("latest_record_sha256") or ""
    ots_count = ots.get("native_record_count") or ""

    ar_id = ar.get("native_latest_record_id") or ""
    ar_sha = ar.get("native_latest_record_sha256") or ""
    ar_count = ar.get("native_record_count") or ""

    ots_head_matches_chain = native_ots_head_matches_chain(tip, ots)
    ots_archivable = native_ots_archivable_for_arweave(tip, ots)

    arweave_matches_ots = (
        ar_id == ots_id
        and ar_sha == ots_sha
        and ar_count == ots_count
        and bool(ar_id)
    )

    arweave_matches_chain = (
        ar_id == chain_id
        and ar_sha == chain_sha
        and ar_count == chain_count
        and bool(ar_id)
    )

    result = {
        "chain_latest_record_id": chain_id,
        "chain_latest_record_sha256": chain_sha,
        "chain_native_record_count": str(chain_count),
        "ots_latest_record_id": ots_id,
        "ots_latest_record_sha256": ots_sha,
        "ots_native_record_count": str(ots_count),
        "arweave_latest_record_id": ar_id,
        "arweave_latest_record_sha256": ar_sha,
        "arweave_native_record_count": str(ar_count),

        # Backward-compatible name, corrected semantics:
        # current chain head has a matching native OTS anchor.
        "ots_matches_chain": str(ots_head_matches_chain).lower(),

        # New explicit archive gate.
        "ots_archivable_for_arweave": str(ots_archivable).lower(),

        "arweave_matches_ots": str(arweave_matches_ots).lower(),
        "arweave_matches_chain": str(arweave_matches_chain).lower(),

        # Do not restamp an already-stamped head.
        "ots_anchor_needed": str(not ots_head_matches_chain).lower(),

        # Full native record-chain archive waits for archivable OTS.
        "arweave_archive_needed": str(ots_archivable and not arweave_matches_ots).lower(),

        "pipeline_current": str(ots_archivable and arweave_matches_chain).lower(),
    }

    if args.github_output:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
