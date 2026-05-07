#!/usr/bin/env python3
"""Data consistency regression: api/evidence-manifest.json must mirror asset-domain summary."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

evidence = json.loads((ROOT / "api" / "evidence-manifest.json").read_text(encoding="utf-8"))
asset_manifest = json.loads((ROOT / "archive" / "hash-manifest.json").read_text(encoding="utf-8"))

mirror = evidence.get("github_archive_mirror", {})
stats = mirror.get("stats", {})
summary = asset_manifest.get("summary", {})

if mirror.get("asset_manifest") != "archive/hash-manifest.json":
    errors.append("github_archive_mirror.asset_manifest must be archive/hash-manifest.json")

if mirror.get("stats_source") != "archive/hash-manifest.json.summary":
    errors.append("github_archive_mirror.stats_source must be archive/hash-manifest.json.summary")

required = [
    "repo_files_total",
    "repo_files_verified",
    "repo_files_no_expected_hash",
    "repo_files_hash_mismatch",
    "release_assets_total",
    "release_assets_verified",
    "release_assets_not_checked",
    "arweave_assets_total",
    "arweave_assets_verified",
    "arweave_assets_not_checked",
    "ipfs_assets_total",
    "ipfs_assets_verified",
    "ipfs_assets_not_checked",
    "eth_attestations_verified",
    "eth_attestations_failed",
]

for key in required:
    if stats.get(key) != summary.get(key):
        errors.append(f"github_archive_mirror.stats.{key}={stats.get(key)} != summary.{key}={summary.get(key)}")

policy = mirror.get("storage_domain_policy", {})
for key in ["repo_files", "release_assets", "arweave_assets", "ipfs_assets"]:
    if key not in policy:
        errors.append(f"github_archive_mirror.storage_domain_policy missing {key}")

pca = evidence.get("public_covenant_archive", {})
if pca.get("storage_policy") != "large_asset_not_committed_to_git":
    errors.append("public_covenant_archive.storage_policy must be large_asset_not_committed_to_git")
if pca.get("repo_path") is not None:
    errors.append("public_covenant_archive.repo_path must be null")
if "github_path" in pca:
    errors.append("public_covenant_archive.github_path is ambiguous; replace with repo_path/github_release_mirror/arweave_tx")

if errors:
    print("EVIDENCE_MANIFEST_STATS_SYNC_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("EVIDENCE_MANIFEST_STATS_SYNC_OK")
