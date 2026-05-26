#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ARCHIVE_ID = "gz2-notarial-certificate-redacted-attachments-2026-05-14"
TAG = "core-object-alpha-notarial-certificate-gz2-custody-public-backup-v1"

REQUIRED_ASSETS = [
    f"{ARCHIVE_ID}.zip",
    f"{ARCHIVE_ID}-arweave-index.json",
    f"{ARCHIVE_ID}-timestamp-files.zip",
    "sealed-disc-custody-record.json",
    f"{ARCHIVE_ID}-release-assets.sha256",
    f"{ARCHIVE_ID}-release-notes.md",
]

TIMESTAMP_FILES_EXPECTED = [
    "manifest.json",
    "manifest.json.ots",
    "manifest_ots_info.txt",
    "manifest.sha256.txt",
    "evidence_hashes.txt",
    "final_evidence_hashes.txt",
    "timestamp_anchor_arweave_results.json",
]

SEALED_DISC_EXPECTED_FALSE = [
    "opened",
    "content_accessed",
    "iso_image_created",
    "file_level_hashes_computed",
    "disc_to_disc_comparison_performed",
    "content_hash_compared_to_cunzhengtong",
    "content_hash_compared_to_arweave",
]

REQUIRED_ARWEAVE_INDEX_FIELDS = [
    "photo_txids",
    "manifest_json_txid",
    "ots_proof_txid",
    "ots_info_txid",
    "manifest_sha256_txid",
    "evidence_hashes_txid",
    "photo_upload_results_txid",
    "timestamp_anchor_upload_results_txid",
    "final_evidence_hashes_txid",
]


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    return p.stdout


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="thechurchofagi/trinity-accord")
    ap.add_argument("--tag", default=TAG)
    ap.add_argument("--work", default="")
    args = ap.parse_args()

    if args.work:
        work = Path(args.work)
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        cleanup = False
    else:
        work = Path(tempfile.mkdtemp(prefix="gz2-notarial-release-verify-"))
        cleanup = True

    try:
        print(f"Verifying release {args.repo} {args.tag}")
        run(["gh", "release", "view", args.tag, "--repo", args.repo])
        run(
            [
                "gh",
                "release",
                "download",
                args.tag,
                "--repo",
                args.repo,
                "--dir",
                str(work),
                "--clobber",
            ]
        )

        # Check required assets
        actual_assets = {p.name for p in work.iterdir() if p.is_file()}
        required_set = set(REQUIRED_ASSETS)

        missing = required_set - actual_assets
        extra = actual_assets - required_set

        if missing:
            raise RuntimeError(f"Missing release asset(s): {sorted(missing)}")
        if extra:
            raise RuntimeError(f"Unexpected extra release asset(s): {sorted(extra)}")

        # Verify SHA-256 hashes
        sha256_file_path = work / f"{ARCHIVE_ID}-release-assets.sha256"
        expected_hashed_assets = required_set - {f"{ARCHIVE_ID}-release-assets.sha256"}

        expected = {}
        for line in sha256_file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, name = line.split(None, 1)
            expected[name.strip()] = digest.strip()

        missing_hash_lines = expected_hashed_assets - set(expected)
        extra_hash_lines = set(expected) - expected_hashed_assets

        if missing_hash_lines:
            raise RuntimeError(
                f"release-assets.sha256 missing entries: {sorted(missing_hash_lines)}"
            )
        if extra_hash_lines:
            raise RuntimeError(
                f"release-assets.sha256 has unexpected entries: {sorted(extra_hash_lines)}"
            )

        for name, digest in expected.items():
            p = work / name
            actual = sha256_file(p)
            if actual != digest:
                raise RuntimeError(
                    f"Asset SHA mismatch: {name}: expected {digest}, got {actual}"
                )
            print(f"OK asset sha256: {name}")

        # Verify sealed-disc custody record
        custody = json.loads(
            (work / "sealed-disc-custody-record.json").read_text(encoding="utf-8")
        )
        discs = custody.get("holder_retained_sealed_discs", {})
        for field in SEALED_DISC_EXPECTED_FALSE:
            if discs.get(field) not in (False, None):
                raise RuntimeError(
                    f"sealed-disc-custody-record.json: holder_retained_sealed_discs.{field} must be false, got {discs.get(field)}"
                )
        print("OK sealed-disc custody record boundary check")

        # Verify Arweave index JSON
        arweave_index = json.loads(
            (work / f"{ARCHIVE_ID}-arweave-index.json").read_text(encoding="utf-8")
        )
        for field in REQUIRED_ARWEAVE_INDEX_FIELDS:
            if field not in arweave_index:
                raise RuntimeError(
                    f"Arweave index JSON missing required field: {field}"
                )
        if len(arweave_index.get("photo_txids", [])) != 10:
            raise RuntimeError(
                f"Expected 10 photo_txids, got {len(arweave_index.get('photo_txids', []))}"
            )
        print("OK Arweave index JSON has all required fields")

        # Verify timestamp files ZIP
        ts_zip = work / f"{ARCHIVE_ID}-timestamp-files.zip"
        unzip_dir = work / "ts_unzipped"
        unzip_dir.mkdir()
        with zipfile.ZipFile(ts_zip, "r") as z:
            z.extractall(unzip_dir)

        ts_files = {p.name for p in unzip_dir.rglob("*") if p.is_file()}
        for expected_file in TIMESTAMP_FILES_EXPECTED:
            if expected_file not in ts_files:
                raise RuntimeError(
                    f"Timestamp ZIP missing expected file: {expected_file}"
                )
        print("OK timestamp files ZIP contains all expected files")

        print(
            "\nPASS: GZ2 notarial certificate release backup is valid."
        )
        print(
            "Boundary OK: GZ2 does not claim file-level equality with original Cunzhengtong files."
        )
        print(
            "Boundary OK: sealed-disc contents are not claimed as opened or verified."
        )

    finally:
        if cleanup:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
