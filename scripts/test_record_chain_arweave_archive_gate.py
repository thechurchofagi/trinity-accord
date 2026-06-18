#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label}: {needle}")


def main() -> None:
    pipeline_detector = (ROOT / "scripts/detect_record_chain_pipeline_backlog.py").read_text(encoding="utf-8")
    rc_status = (ROOT / "scripts/generate_record_chain_status.py").read_text(encoding="utf-8")
    ar_workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")
    builder = (ROOT / "scripts/build_record_chain_arweave_archive.py").read_text(encoding="utf-8")
    backlog_detector = (ROOT / "scripts/detect_archive_backlog.py").read_text(encoding="utf-8")
    backlog_lib = (ROOT / "scripts/archive_backlog_lib.py").read_text(encoding="utf-8")

    for needle in [
        "def native_ots_head_matches_chain",
        "def native_ots_is_strictly_verified",
        "def native_ots_has_bitcoin_attestation",
        "def native_ots_archivable_for_arweave",
        "\"ots_anchor_needed\": str(not ots_head_matches_chain).lower()",
        "\"arweave_archive_needed\": str(ots_archivable and not arweave_matches_ots).lower()",
        "\"ots_archivable_for_arweave\": str(ots_archivable).lower()",
    ]:
        require(pipeline_detector, needle, "pipeline detector")

    for needle in [
        "native_ots_archivable_for_arweave",
        "ots_archivable_for_arweave",
        "arweave_archive_needed",
        "bitcoin_attestation_embedded",
        "strict_bitcoin_verified",
    ]:
        require(rc_status, needle, "record chain status")

    require(ar_workflow, "Native OTS Upgrade Watch", "archive workflow must listen to native OTS upgrade")
    require(builder, "def native_ots_archivable_for_chain", "builder must enforce native OTS archive gate")
    require(backlog_detector, "def is_verified_live_native_archive", "backlog detector must require verified live archive")
    require(backlog_detector, "def native_ots_archivable_for_current_chain", "backlog detector must check OTS archivable")
    require(backlog_lib, "waiting_for_ots_upgrade_count", "backlog lib must count waiting_for_ots_upgrade")

    print("PASS: record chain arweave archive gate")


if __name__ == "__main__":
    main()
