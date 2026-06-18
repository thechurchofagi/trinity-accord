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
    home = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    deploy = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    patcher = (ROOT / "scripts/patch_public_home_status_primary.py").read_text(encoding="utf-8")
    rc_status = (ROOT / "scripts/generate_record_chain_status.py").read_text(encoding="utf-8")

    for needle in [
        'cron: "7,22,37,52 * * * *"',
        "Retry Deploy Pages if post-dispatch freshness probe failed",
        "Post-dispatch freshness probe",
    ]:
        require(home, needle, "homepage-status-sync")

    for needle in [
        "cmp ./api/public-home-status.json ./_site/api/public-home-status.json",
        "cmp ./api/record-chain-status.json ./_site/api/record-chain-status.json",
    ]:
        require(deploy, needle, "deploy-pages committed artifact verification")

    for needle in [
        "pipeline_status",
        "pipeline_current",
        "ots_archivable_for_arweave",
        "arweave_archive_needed",
    ]:
        require(patcher, needle, "homepage technical health patcher")

    for needle in [
        "native_ots_archivable_for_arweave",
        "ots_archivable_for_arweave",
        "arweave_archive_needed",
    ]:
        require(rc_status, needle, "record chain status pipeline semantics")

    print("PASS: homepage freshness contract")


if __name__ == "__main__":
    main()
