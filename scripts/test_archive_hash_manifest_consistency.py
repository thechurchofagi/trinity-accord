#!/usr/bin/env python3
"""Data consistency regression: archive/hash-manifest.json must match repository bytes and verified semantics."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "archive" / "hash-manifest.json"

errors = []

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

try:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
except Exception as e:
    print(f"ARCHIVE_HASH_MANIFEST_CONSISTENCY_FAIL\n- cannot read manifest: {e}")
    sys.exit(1)

files = manifest.get("files", [])
if not isinstance(files, list) or not files:
    errors.append("manifest.files must be a non-empty list")

seen = set()
computed_total_files = 0
computed_verified = 0
computed_no_expected = 0
computed_hash_mismatch = 0

for item in files:
    path = item.get("path")
    if not path:
        errors.append("file entry missing path")
        continue

    if path in seen:
        errors.append(f"duplicate file path in manifest: {path}")
    seen.add(path)

    repo_path = ROOT / path
    if not repo_path.exists():
        errors.append(f"manifest path does not exist in repository: {path}")
        continue

    computed_total_files += 1

    actual_sha = sha256_file(repo_path)
    actual_size = repo_path.stat().st_size

    if item.get("sha256") != actual_sha:
        errors.append(f"{path}: manifest sha256 {item.get('sha256')} != actual repository sha256 {actual_sha}")

    if item.get("size_bytes") != actual_size:
        errors.append(f"{path}: manifest size_bytes {item.get('size_bytes')} != actual size {actual_size}")

    expected = item.get("expected_sha256")
    verified = item.get("verified")

    if expected:
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected.lower()):
            errors.append(f"{path}: expected_sha256 is not lowercase 64-hex")

    if verified is True:
        computed_verified += 1
        if not expected:
            errors.append(f"{path}: verified=true requires expected_sha256")
        if item.get("sha256") != expected:
            computed_hash_mismatch += 1
            errors.append(f"{path}: verified=true but sha256 != expected_sha256")
    elif expected:
        if item.get("sha256") != expected:
            computed_hash_mismatch += 1
    else:
        computed_no_expected += 1
        note = (item.get("note") or "").lower()
        if "no expected hash" not in note and "availability" not in note and verified is None:
            errors.append(f"{path}: no expected_sha256 should have explicit no-expected/availability note")

summary = manifest.get("summary", {})
if not isinstance(summary, dict):
    errors.append("manifest.summary must be an object")
else:
    if summary.get("total_files") != computed_total_files:
        errors.append(f"summary.total_files {summary.get('total_files')} != computed {computed_total_files}")
    if summary.get("verified_against_arweave") != computed_verified:
        errors.append(f"summary.verified_against_arweave {summary.get('verified_against_arweave')} != computed {computed_verified}")
    if summary.get("no_expected_hash") != computed_no_expected:
        errors.append(f"summary.no_expected_hash {summary.get('no_expected_hash')} != computed {computed_no_expected}")
    if summary.get("hash_mismatch") != computed_hash_mismatch:
        errors.append(f"summary.hash_mismatch {summary.get('hash_mismatch')} != computed {computed_hash_mismatch}")

eth = manifest.get("eth_attestations", [])
eth_verified = sum(1 for x in eth if x.get("verified") is True)
eth_failed = sum(1 for x in eth if x.get("verified") is False)

if summary.get("eth_attestations_verified") != eth_verified:
    errors.append(f"summary.eth_attestations_verified {summary.get('eth_attestations_verified')} != computed {eth_verified}")
if summary.get("eth_attestations_failed") != eth_failed:
    errors.append(f"summary.eth_attestations_failed {summary.get('eth_attestations_failed')} != computed {eth_failed}")

if errors:
    print("ARCHIVE_HASH_MANIFEST_CONSISTENCY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ARCHIVE_HASH_MANIFEST_CONSISTENCY_OK")
