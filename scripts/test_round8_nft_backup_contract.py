#!/usr/bin/env python3
"""Round 8 contract for NFT Release backup capability and integrity boundaries."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    target = ROOT / path
    require(target.exists(), f"missing {path}")
    return target.read_text(encoding="utf-8")


def workflow(path: str) -> str:
    text = read(path)
    try:
        parsed = yaml.safe_load(text)
    except Exception as exc:
        fail(f"invalid workflow YAML {path}: {exc}")
    require(isinstance(parsed, dict), f"workflow is not a mapping: {path}")
    return text


def main() -> int:
    mirror = workflow(".github/workflows/backup-nft-arweave-mirror.yml")
    for marker in [
        "contents: write",
        "group: release-nft-arweave-mirror",
        "github.ref == 'refs/heads/main'",
        "ref: main",
        "Contract-filtered live mirror runs are disabled",
        "nft-arweave-mirror-175-v1-${source_commit:0:12}",
        "GITHUB_TOKEN: ${{ github.token }}",
        "SOURCE_COMMIT=$source_commit",
        "default: true",
    ]:
        require(marker in mirror, f"NFT mirror workflow missing: {marker}")
    require("secrets.GITHUB_TOKEN" not in mirror, "NFT mirror uses a secret alias instead of the workflow token")
    require(
        mirror.find("Contract-filtered live mirror runs are disabled") < mirror.find("node scripts/backup-nft-arweave-mirror.mjs"),
        "filtered live guard runs after the destructive mirror script",
    )

    for path, script in [
        (".github/workflows/backup-nft-individual.yml", "backup-nft-individual.mjs"),
        (".github/workflows/backup-nft-individual-v2.yml", "backup-nft-individual-v2.mjs"),
    ]:
        text = workflow(path)
        require("contents: read" in text, f"{path} retains Release write permission")
        require("contents: write" not in text, f"{path} retains Release write permission")
        require("GITHUB_TOKEN" not in text, f"{path} receives a GitHub release token")
        require("--dry-run" in text, f"{path} can invoke {script} outside dry-run")
        require("ref: main" in text, f"{path} does not audit current main")
        require("github.ref == 'refs/heads/main'" in text, f"{path} accepts a selected non-main workflow definition")

    cars = workflow(".github/workflows/backup-nft-cars.yml")
    for marker in [
        "contents: write",
        "group: release-nft-cars",
        "ref: main",
        "github.ref == 'refs/heads/main'",
        "GITHUB_TOKEN: ${{ github.token }}",
        "node scripts/download-nft-cars.mjs",
        "default: true",
        "set -euo pipefail",
    ]:
        require(marker in cars, f"verified CAR backup workflow missing: {marker}")
    require("secrets.GITHUB_TOKEN" not in cars, "verified CAR backup uses a secret alias instead of workflow token")

    downloader = read("scripts/download-nft-cars.mjs")
    for marker in [
        "EXPECTED_RECOVERY_PACKAGE_SHA256",
        "validateExpectedInfo",
        "validateTokenIndex",
        "expected_sha256",
        "expected_size",
        "MAX_CAR_BYTES",
        "MAX_TOTAL_BYTES",
        "countTokenIndexNfts",
        "EXPECTED_NFTS",
        "parseCarHeaderStrict",
    ]:
        require(marker in downloader, f"verified CAR downloader missing integrity control: {marker}")

    legacy = read("scripts/backup-nft-individual-v2.mjs").lower()
    for marker in [
        "returned the first match",
        "only 4 nfts",
        "largest token-index json object across all blocks",
    ]:
        require(
            marker in legacy,
            f"v1 retirement no longer documents its partial-index root cause: {marker}",
        )

    print("PASS: NFT Release backup paths separate verified publishing from read-only legacy previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
