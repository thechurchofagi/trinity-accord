#!/usr/bin/env python3
"""Verify release manifest assets by downloading and checking SHA-256 + size.

Usage:
    python3 tools/verify_release_manifest_assets.py <manifest.json> [--tmpdir DIR]

Supports evidence-images-manifest.json format (trinityaccord.evidence-image-manifest.v1).
Downloads each asset to a temporary directory, verifies sha256 and size_bytes,
then reports pass/fail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import urllib.request
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-verify"})
    with urllib.request.urlopen(req) as resp, dest.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


def verify(manifest_path: Path, tmpdir: Path | None = None) -> int:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = data.get("assets", [])
    if not assets:
        print("ERROR: no assets in manifest", file=sys.stderr)
        return 1

    use_tmpdir = tmpdir is None
    if use_tmpdir:
        tmpdir = Path(tempfile.mkdtemp(prefix="verify-release-"))

    errors = 0
    for i, asset in enumerate(assets):
        filename = asset.get("filename", f"asset_{i}")
        expected_sha = asset.get("sha256", "")
        expected_size = asset.get("size_bytes", 0)
        url = asset.get("download_url", "")

        if not url:
            print(f"SKIP  {filename} — no download_url")
            continue

        dest = tmpdir / filename
        print(f"  [{i+1}/{len(assets)}] Downloading {filename}...", end=" ", flush=True)
        try:
            download(url, dest)
        except Exception as e:
            print(f"FAIL (download error: {e})")
            errors += 1
            continue

        actual_size = dest.stat().st_size
        actual_sha = sha256_file(dest)

        size_ok = actual_size == expected_size
        sha_ok = actual_sha.lower() == expected_sha.lower()

        if size_ok and sha_ok:
            print(f"OK  sha256={actual_sha[:16]}... size={actual_size}")
        else:
            parts = []
            if not sha_ok:
                parts.append(f"sha256 mismatch: got {actual_sha[:16]}..., expected {expected_sha[:16]}...")
            if not size_ok:
                parts.append(f"size mismatch: got {actual_size}, expected {expected_size}")
            print(f"FAIL  {'; '.join(parts)}")
            errors += 1

        if use_tmpdir and dest.exists():
            dest.unlink()

    if use_tmpdir:
        try:
            tmpdir.rmdir()
        except OSError:
            pass

    print()
    if errors:
        print(f"RESULT: {errors} error(s) out of {len(assets)} assets")
        return 1
    else:
        print(f"RESULT: all {len(assets)} assets verified OK")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release manifest assets")
    parser.add_argument("manifest", type=Path, help="Path to manifest JSON")
    parser.add_argument("--tmpdir", type=Path, default=None, help="Directory for downloads (default: auto temp)")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: manifest not found: {args.manifest}", file=sys.stderr)
        return 2

    return verify(args.manifest, args.tmpdir)


if __name__ == "__main__":
    raise SystemExit(main())
