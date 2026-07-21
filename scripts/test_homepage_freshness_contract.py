#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_deployment_freshness as deployment_freshness  # noqa: E402
import check_homepage_live_freshness as homepage_live_freshness  # noqa: E402


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label}: {needle}")


def main() -> None:
    index = (ROOT / "index.md").read_text(encoding="utf-8")
    status_page = (ROOT / "status.md").read_text(encoding="utf-8")
    home = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    deploy = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    patcher = (ROOT / "scripts/patch_public_home_status_primary.py").read_text(encoding="utf-8")
    rc_status = (ROOT / "scripts/generate_record_chain_status.py").read_text(encoding="utf-8")

    for needle in [
        'cron: "7,22,37,52 * * * *"',
        "Check live homepage freshness before optional redeploy",
        "Record asynchronous deployment handoff",
    ]:
        require(home, needle, "homepage-status-sync")

    for needle in [
        "cmp api/public-home-status.json _site/api/public-home-status.json",
        "cmp api/record-chain-status.json _site/api/record-chain-status.json",
    ]:
        require(deploy, needle, "deploy-pages committed artifact verification")

    for needle in [
        "pipeline_status",
        "pipeline_current",
        "ots_archivable_for_arweave",
        "arweave_archive_needed",
        "External Witness Record",
        "external_witness_index_record_count",
    ]:
        require(patcher, needle, "homepage technical health/status patcher")

    for needle in [
        "native_ots_archivable_for_arweave",
        "ots_archivable_for_arweave",
        "arweave_archive_needed",
    ]:
        require(rc_status, needle, "record chain status pipeline semantics")

    deploy_markers = deployment_freshness.STATIC_PAGE_MARKERS["/"]
    live_markers = homepage_live_freshness.STATIC_PAGE_MARKERS["/"]
    if deploy_markers != live_markers:
        raise SystemExit(
            "homepage marker drift: deployment and post-deployment freshness checks differ"
        )

    for marker in deploy_markers:
        require(index, marker, "current homepage deployment marker")

    for needle in [
        "External Witness Record",
        "data-home-external-witness",
        "/api/external-witness-index.json",
        "External witness records do not imply endorsement",
    ]:
        require(index, needle, "current external witness homepage signal")

    for needle in [
        "External witness records",
        "Current external witness record count",
        "外部见证记录属于证据来源与过程见证",
    ]:
        require(status_page, needle, "external witness status section")

    for retired in [
        "AI independent verification",
        "data-home-ai-independent-verification",
        "Loaded live from the Echo index",
        "fetch('/api/echo-index.json'",
    ]:
        forbid(index, retired, "retired fourth homepage signal")

    for retired_marker in [
        "p0.8.2-link-affordance",
        "p0.9.1-editorial-doorway",
        "One record, three embodied forms",
        "One completed record, four distinct layers",
        "Why one person chose to leave it before the window closed",
        "Window opens · 2023",
        "Formation · 470 days",
        "Window narrows · 2025–2026",
    ]:
        if retired_marker in deploy_markers:
            raise SystemExit(f"retired homepage marker remains active: {retired_marker}")

    print("PASS: homepage freshness contract")


if __name__ == "__main__":
    main()
