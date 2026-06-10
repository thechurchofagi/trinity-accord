#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> int:
    detector = ROOT / "scripts/detect_archive_backlog.py"
    process = ROOT / "scripts/process_archive_backlog.py"
    lib = ROOT / "scripts/archive_backlog_lib.py"
    for path in [detector, process, lib]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    first = run([sys.executable, "scripts/detect_archive_backlog.py"])
    require(first.returncode == 0, first.stderr)
    second = run([sys.executable, "scripts/detect_archive_backlog.py"])
    require(second.returncode == 0, second.stderr)
    require(first.stdout == second.stdout, "detector must be idempotent without --write")
    data = json.loads(first.stdout)

    rc = data["record_chain_arweave"]
    ots = data["native_ots"]
    require(rc["schema"] == "trinityaccord.record-chain-arweave-backlog.v1", "record-chain backlog schema mismatch")
    require(ots["schema"] == "trinityaccord.native-ots-backlog.v1", "native OTS backlog schema mismatch")
    require(rc["boundary"]["arweave_archive_is_mirror_only"] is True, "record-chain mirror-only boundary missing")
    require(rc["boundary"]["arweave_archive_is_not_authority"] is True, "record-chain not-authority boundary missing")
    require(rc["boundary"]["arweave_archive_is_not_attestation"] is True, "record-chain not-attestation boundary missing")
    require(rc["boundary"]["arweave_archive_is_not_amendment"] is True, "record-chain not-amendment boundary missing")
    require(rc["boundary"]["arweave_archive_is_not_successor_reception"] is True, "record-chain not-successor boundary missing")
    require(rc["boundary"]["bitcoin_originals_prevail"] is True, "Bitcoin Originals prevail boundary missing")
    require(ots["boundary"]["native_ots_proof_bundle_arweave_archive_is_mirror_only"] is True, "native OTS mirror-only boundary missing")

    text = detector.read_text(encoding="utf-8")
    for needle in [
        "--github-output",
        "record_chain_arweave_pending",
        "native_ots_pending",
        "arweave_archived",
        "tx_id",
        "native-arweave-bundles",
        "native-arweave-registry.json",
    ]:
        require(needle in text, f"detector missing contract marker: {needle}")

    process_text = process.read_text(encoding="utf-8")
    for needle in ["--max-items", "waiting_for_key", "upload_failed", "readback_failed", "ARKEY/Arweave JWK not configured"]:
        require(needle in process_text, f"processor missing contract marker: {needle}")

    print("PASS: archive backlog detector contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
