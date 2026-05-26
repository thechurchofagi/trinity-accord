#!/usr/bin/env python3
"""Static asset-domain consistency test for archive/hash-manifest.json."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "archive" / "hash-manifest.json"

LARGE_THRESHOLD = 5_000_000
PAYLOAD_EXTS = (".zip", ".tar.gz", ".tgz", ".bin", ".car", ".mp4", ".mov", ".pdf")

errors = []

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_payload(path: str, size: int) -> bool:
    lower = path.lower()
    return size > LARGE_THRESHOLD or any(lower.endswith(ext) for ext in PAYLOAD_EXTS)

m = json.loads(MANIFEST.read_text(encoding="utf-8"))

if m.get("schema") != "trinity-accord.asset-manifest.v2":
    errors.append("schema must be trinity-accord.asset-manifest.v2")

files = m.get("files", [])
release_assets = m.get("release_assets", [])
arweave_assets = m.get("arweave_assets", [])
ipfs_assets = m.get("ipfs_assets", [])
eth = m.get("eth_attestations", [])

for key, value in [
    ("files", files),
    ("release_assets", release_assets),
    ("arweave_assets", arweave_assets),
    ("ipfs_assets", ipfs_assets),
    ("eth_attestations", eth),
]:
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")

seen = set()
repo_files_total = 0
repo_files_verified = 0
repo_files_no_expected = 0
repo_files_hash_mismatch = 0

for item in files:
    asset_id = item.get("asset_id") or item.get("path")
    if asset_id in seen:
        errors.append(f"duplicate asset id/path: {asset_id}")
    seen.add(asset_id)

    if item.get("storage_domain") != "repo":
        errors.append(f"{asset_id}: files[] entry must have storage_domain=repo")

    path = item.get("path")
    if not path:
        errors.append(f"{asset_id}: files[] entry missing path")
        continue

    p = ROOT / path
    if not p.exists():
        errors.append(f"{path}: files[] path does not exist; move to release_assets/arweave_assets/ipfs_assets")
        continue

    repo_files_total += 1
    actual_size = p.stat().st_size
    actual_sha = sha256_file(p)

    if item.get("size_bytes") != actual_size:
        errors.append(f"{path}: size_bytes mismatch: manifest={item.get('size_bytes')} actual={actual_size}")

    if item.get("sha256") != actual_sha:
        errors.append(f"{path}: sha256 mismatch: manifest={item.get('sha256')} actual={actual_sha}")

    if is_payload(path, actual_size) and item.get("allow_repo_payload") is not True and actual_size > LARGE_THRESHOLD:
        errors.append(f"{path}: large payload must not be repo file unless allow_repo_payload=true with justification")

    expected = item.get("expected_sha256")
    if item.get("verified") is True:
        repo_files_verified += 1
        if not expected:
            errors.append(f"{path}: verified=true requires expected_sha256")
        if item.get("sha256") != expected:
            errors.append(f"{path}: verified=true but sha256 != expected_sha256")
    elif expected and item.get("sha256") != expected:
        repo_files_hash_mismatch += 1
        if item.get("verified") is not False:
            errors.append(f"{path}: hash mismatch requires verified=false")
        if item.get("hash_mismatch") is not True:
            errors.append(f"{path}: hash mismatch requires hash_mismatch=true")
        if not item.get("mismatch_reason"):
            errors.append(f"{path}: hash mismatch requires mismatch_reason")
    elif not expected:
        repo_files_no_expected += 1

for item in release_assets:
    asset_id = item.get("asset_id") or item.get("asset_name")
    if asset_id in seen:
        errors.append(f"duplicate asset id/path: {asset_id}")
    seen.add(asset_id)

    if item.get("storage_domain") != "github_release":
        errors.append(f"{asset_id}: release_assets[] entry must have storage_domain=github_release")
    for key in ["release_tag", "asset_name", "sha256", "expected_sha256"]:
        if not item.get(key):
            errors.append(f"{asset_id}: release asset missing {key}")
    if item.get("path"):
        errors.append(f"{asset_id}: release asset must not use repo path")
    if item.get("verified") is True and item.get("sha256") != item.get("expected_sha256"):
        errors.append(f"{asset_id}: release verified=true but sha256 != expected_sha256")

for item in arweave_assets:
    asset_id = item.get("asset_id") or item.get("arweave_tx")
    if asset_id in seen:
        errors.append(f"duplicate asset id/path: {asset_id}")
    seen.add(asset_id)

    if item.get("storage_domain") != "arweave":
        errors.append(f"{asset_id}: arweave_assets[] entry must have storage_domain=arweave")
    if not item.get("arweave_tx"):
        errors.append(f"{asset_id}: arweave asset missing arweave_tx")
    if item.get("path"):
        errors.append(f"{asset_id}: arweave asset must not use repo path")
    if item.get("verified") is True and item.get("sha256") != item.get("expected_sha256"):
        errors.append(f"{asset_id}: arweave verified=true but sha256 != expected_sha256")

for item in ipfs_assets:
    asset_id = item.get("asset_id") or item.get("cid")
    if item.get("storage_domain") != "ipfs":
        errors.append(f"{asset_id}: ipfs_assets[] entry must have storage_domain=ipfs")
    if not item.get("cid"):
        errors.append(f"{asset_id}: ipfs asset missing cid")

summary = m.get("summary", {})
expected_summary = {
    "repo_files_total": repo_files_total,
    "repo_files_verified": repo_files_verified,
    "repo_files_no_expected_hash": repo_files_no_expected,
    "repo_files_hash_mismatch": repo_files_hash_mismatch,
    "release_assets_total": len(release_assets),
    "release_assets_verified": sum(1 for x in release_assets if x.get("verified") is True),
    "release_assets_not_checked": sum(1 for x in release_assets if x.get("verified") is None),
    "arweave_assets_total": len(arweave_assets),
    "arweave_assets_verified": sum(1 for x in arweave_assets if x.get("verified") is True),
    "arweave_assets_not_checked": sum(1 for x in arweave_assets if x.get("verified") is None),
    "ipfs_assets_total": len(ipfs_assets),
    "ipfs_assets_verified": sum(1 for x in ipfs_assets if x.get("verified") is True),
    "ipfs_assets_not_checked": sum(1 for x in ipfs_assets if x.get("verified") is None),
    "eth_attestations_verified": sum(1 for x in eth if x.get("verified") is True),
    "eth_attestations_failed": sum(1 for x in eth if x.get("verified") is False),
    # legacy compatibility
    "total_files": repo_files_total,
    "verified_against_arweave": repo_files_verified,
    "no_expected_hash": repo_files_no_expected,
    "hash_mismatch": repo_files_hash_mismatch,
}

for key, expected in expected_summary.items():
    if summary.get(key) != expected:
        errors.append(f"summary.{key}={summary.get(key)} != computed {expected}")

if "public-covenant-archive.zip" in json.dumps(files):
    errors.append("public-covenant-archive.zip must not be in files[]")

if errors:
    print("ASSET_MANIFEST_DOMAIN_CONSISTENCY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ASSET_MANIFEST_DOMAIN_CONSISTENCY_OK")
