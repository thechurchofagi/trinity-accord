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

ARCHIVE_ID = "core-object-alpha-shenzhen-notary-2026-05-06"
TAG = "core-object-alpha-shenzhen-notary-arweave-backup-v1"
PAYLOAD_ZIP_NAME = f"{ARCHIVE_ID}-arweave-payload.zip"
BACKUP_MANIFEST_NAME = f"{ARCHIVE_ID}-github-release-backup-manifest.json"
ASSET_SHA256_NAME = f"{ARCHIVE_ID}-release-assets.sha256"
RELEASE_NOTES_NAME = f"{ARCHIVE_ID}-release-notes.md"

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
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
        work = Path(tempfile.mkdtemp(prefix="shenzhen-notary-release-verify-"))
        cleanup = True

    try:
        print(f"Verifying release {args.repo} {args.tag}")
        run(["gh", "release", "view", args.tag, "--repo", args.repo])
        run(["gh", "release", "download", args.tag, "--repo", args.repo, "--dir", str(work), "--clobber"])

        required = {PAYLOAD_ZIP_NAME, BACKUP_MANIFEST_NAME, ASSET_SHA256_NAME, RELEASE_NOTES_NAME}
        actual_assets = {p.name for p in work.iterdir() if p.is_file()}

        missing = required - actual_assets
        extra = actual_assets - required

        if missing:
            raise RuntimeError(f"Missing release asset(s): {sorted(missing)}")

        if extra:
            raise RuntimeError(f"Unexpected extra release asset(s): {sorted(extra)}")

        expected_hashed_assets = required - {ASSET_SHA256_NAME}

        expected = {}
        for line in (work / ASSET_SHA256_NAME).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, name = line.split(None, 1)
            expected[name.strip()] = digest.strip()

        missing_hash_lines = expected_hashed_assets - set(expected)
        extra_hash_lines = set(expected) - expected_hashed_assets

        if missing_hash_lines:
            raise RuntimeError(f"release-assets.sha256 missing entries: {sorted(missing_hash_lines)}")

        if extra_hash_lines:
            raise RuntimeError(f"release-assets.sha256 has unexpected entries: {sorted(extra_hash_lines)}")

        for name, digest in expected.items():
            p = work / name
            actual = sha256_file(p)
            if actual != digest:
                raise RuntimeError(f"Asset SHA mismatch: {name}: expected {digest}, got {actual}")
            print(f"OK asset sha256: {name}")

        manifest = json.loads((work / BACKUP_MANIFEST_NAME).read_text(encoding="utf-8"))
        if manifest.get("archive_id") != ARCHIVE_ID:
            raise RuntimeError("archive_id mismatch in backup manifest")
        if manifest.get("release_tag") != TAG:
            raise RuntimeError("release_tag mismatch in backup manifest")
        if manifest.get("hard_failures") not in ([], None):
            raise RuntimeError("backup manifest reports hard failures")
        if manifest.get("payload_skipped"):
            raise RuntimeError("backup manifest indicates payload was skipped")

        unzip_dir = work / "unzipped"
        unzip_dir.mkdir()
        with zipfile.ZipFile(work / PAYLOAD_ZIP_NAME, "r") as z:
            z.extractall(unzip_dir)

        embedded_manifest_path = unzip_dir / "metadata" / "github-release-backup-manifest.json"
        if not embedded_manifest_path.exists():
            raise RuntimeError("embedded backup manifest missing from zip")

        embedded = json.loads(embedded_manifest_path.read_text(encoding="utf-8"))
        files = embedded.get("files", [])
        if len(files) != 153:
            raise RuntimeError(f"Expected 153 files in embedded manifest, got {len(files)}")

        for row in files:
            if not row.get("ok"):
                raise RuntimeError(f"Embedded row not OK: {row}")
            rel = row["path"]
            p = unzip_dir / "payload" / rel
            if not p.exists():
                raise RuntimeError(f"Missing payload file in zip: {rel}")
            actual = sha256_file(p)
            if actual != row["expected_sha256"]:
                raise RuntimeError(f"Payload SHA mismatch for {rel}: {actual} != {row['expected_sha256']}")

        for idx_path in [
            "indices/archive-index.json",
            "indices/archive-index.tsv",
            "indices/index.html",
            "indices/arweave-manifest.json",
            "metadata/payload-files.sha256",
            "metadata/release-notes.md",
        ]:
            if not (unzip_dir / idx_path).exists():
                raise RuntimeError(f"Missing file in zip: {idx_path}")

        print("PASS: GitHub Release backup is valid.")
    finally:
        if cleanup:
            shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
