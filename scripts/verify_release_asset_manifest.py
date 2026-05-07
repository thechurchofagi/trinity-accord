#!/usr/bin/env python3
"""Verify GitHub Release assets declared in archive/hash-manifest.json.

Offline mode validates metadata shape only.
Network mode requires gh CLI and downloads assets to verify SHA-256.
"""

from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    return p.stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="thechurchofagi/trinity-accord")
    ap.add_argument("--manifest", default="archive/hash-manifest.json")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    m = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))
    assets = m.get("release_assets", [])
    errors = []

    for a in assets:
        asset_id = a.get("asset_id") or a.get("asset_name")
        if a.get("storage_domain") != "github_release":
            errors.append(f"{asset_id}: storage_domain must be github_release")
        for key in ["release_tag", "asset_name", "sha256", "expected_sha256"]:
            if not a.get(key):
                errors.append(f"{asset_id}: missing {key}")
        if a.get("verified") is True and a.get("sha256") != a.get("expected_sha256"):
            errors.append(f"{asset_id}: verified=true but sha256 != expected_sha256")

    if errors:
        print("RELEASE_ASSET_MANIFEST_SHAPE_FAIL")
        for e in errors:
            print("-", e)
        return 1

    if args.offline:
        print("RELEASE_ASSET_MANIFEST_OFFLINE_OK")
        return 0

    if not assets:
        print("RELEASE_ASSET_MANIFEST_VERIFY_OK: no release_assets declared")
        return 0

    if shutil.which("gh") is None:
        print("FAIL: gh CLI not available. Use --offline for shape-only validation.", file=sys.stderr)
        return 1

    work = Path(tempfile.mkdtemp(prefix="trinity-release-assets-"))
    try:
        for a in assets:
            tag = a["release_tag"]
            asset_name = a["asset_name"]
            expected = a["expected_sha256"].lower()
            out_dir = work / tag
            out_dir.mkdir(parents=True, exist_ok=True)

            run([
                "gh", "release", "download", tag,
                "--repo", args.repo,
                "--pattern", asset_name,
                "--dir", str(out_dir),
                "--clobber",
            ])

            p = out_dir / asset_name
            if not p.exists():
                errors.append(f"{tag}/{asset_name}: download did not produce asset")
                continue

            actual = sha256_file(p)
            if actual != expected:
                errors.append(f"{tag}/{asset_name}: expected {expected}, got {actual}")
            else:
                print(f"OK release asset: {tag}/{asset_name}")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if errors:
        print("RELEASE_ASSET_MANIFEST_VERIFY_FAIL")
        for e in errors:
            print("-", e)
        return 1

    print("RELEASE_ASSET_MANIFEST_VERIFY_OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
