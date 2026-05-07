#!/usr/bin/env python3
"""Data consistency regression: api/evidence-manifest.json stats must mirror archive/hash-manifest.json summary."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

evidence = json.loads((ROOT / "api" / "evidence-manifest.json").read_text(encoding="utf-8"))
hash_manifest = json.loads((ROOT / "archive" / "hash-manifest.json").read_text(encoding="utf-8"))

stats = evidence.get("github_archive_mirror", {}).get("stats", {})
summary = hash_manifest.get("summary", {})

required_map = {
    "total_files": "total_files",
    "sha256_verified_against_arweave": "verified_against_arweave",
    "no_expected_hash": "no_expected_hash",
    "hash_mismatch": "hash_mismatch",
    "eth_attestations_verified": "eth_attestations_verified",
    "eth_attestations_failed": "eth_attestations_failed",
}

for evidence_key, summary_key in required_map.items():
    if stats.get(evidence_key) != summary.get(summary_key):
        errors.append(
            f"github_archive_mirror.stats.{evidence_key}={stats.get(evidence_key)} "
            f"!= archive/hash-manifest.summary.{summary_key}={summary.get(summary_key)}"
        )

eth_total = len(hash_manifest.get("eth_attestations", []))
if stats.get("eth_attestations_total") != eth_total:
    errors.append(
        f"github_archive_mirror.stats.eth_attestations_total={stats.get('eth_attestations_total')} "
        f"!= len(eth_attestations)={eth_total}"
    )

mirror = evidence.get("github_archive_mirror", {})
if mirror.get("stats_source") != "archive/hash-manifest.json.summary":
    errors.append("github_archive_mirror.stats_source must be archive/hash-manifest.json.summary")

availability = mirror.get("availability_only_unverified_mirrors", {})
if availability.get("committed_to_verified_archive") is not False:
    errors.append("availability_only_unverified_mirrors.committed_to_verified_archive must be false")

if "availability only" not in json.dumps(availability).lower():
    errors.append("availability_only_unverified_mirrors must clearly say availability only")

if errors:
    print("EVIDENCE_MANIFEST_STATS_SYNC_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("EVIDENCE_MANIFEST_STATS_SYNC_OK")
