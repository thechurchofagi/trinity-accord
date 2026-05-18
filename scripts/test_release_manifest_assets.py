#!/usr/bin/env python3
"""Verify that release manifest assets have required metadata fields."""
import json
import subprocess
import sys
from pathlib import Path

MANIFESTS = [
    "evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json",
    "api/evidence-manifest.json",
]


def check_images_manifest(path):
    errors = []
    with open(path) as f:
        d = json.load(f)

    assets = d.get("assets", [])
    if not assets:
        errors.append(f"{path}: no assets found")
        return errors

    for asset in assets:
        name = asset.get("filename", asset.get("name", "?"))
        if "sha256" not in asset:
            errors.append(f"{path}/{name}: missing sha256")
        if "size_bytes" not in asset:
            errors.append(f"{path}/{name}: missing size_bytes")
        if "download_url" not in asset:
            errors.append(f"{path}/{name}: missing download_url")
        if not asset.get("non_amending", False):
            errors.append(f"{path}/{name}: non_amending not true")

    return errors


def check_evidence_manifest(path):
    errors = []
    with open(path) as f:
        d = json.load(f)

    for key, val in d.items():
        if not isinstance(val, dict):
            continue
        policy = val.get("storage_policy", "")
        repo_path = val.get("repo_path")

        # Large assets must be externalized
        if policy == "large_asset_not_committed_to_git":
            if repo_path is not None:
                errors.append(
                    f"{path}/{key}: storage_policy says not committed but repo_path={repo_path}"
                )

    return errors


def check_no_large_binaries_in_tree():
    """Verify no JPGs under notarial cert path and no large zips."""
    errors = []
    out = subprocess.check_output(["git", "ls-tree", "-r", "HEAD"], text=True)
    for line in out.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        path = parts[4]
        if "公证书" in path and path.endswith((".jpg", ".jpeg")):
            errors.append(f"JPG still in tree: {path}")
        if path.endswith((".zip", ".tar.gz", ".tgz")):
            if "public-covenant-archive" in path or "flaw-archive-bundle" in path:
                errors.append(f"Large asset still in tree: {path}")
    return errors


def main():
    all_errors = []

    for manifest in MANIFESTS:
        if not Path(manifest).exists():
            print(f"WARN: {manifest} not found, skipping")
            continue
        if "images-manifest" in manifest:
            all_errors.extend(check_images_manifest(manifest))
        else:
            all_errors.extend(check_evidence_manifest(manifest))

    all_errors.extend(check_no_large_binaries_in_tree())

    if all_errors:
        for e in all_errors:
            print("FAIL:", e)
        sys.exit(1)

    print("PASS: release manifest assets metadata")


if __name__ == "__main__":
    main()
