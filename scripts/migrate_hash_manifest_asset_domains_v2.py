#!/usr/bin/env python3
"""Migrate archive/hash-manifest.json to asset-domain-aware v2.

This script is conservative:
- It never guesses release tags.
- It uses optional release discovery result JSON.
- If an external large asset has no release discovery, it is modeled as arweave_assets[] when arweave_tx exists.
"""

from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LARGE_THRESHOLD = 5_000_000
PAYLOAD_EXTS = (".zip", ".tar.gz", ".tgz", ".bin", ".car", ".mp4", ".mov", ".pdf")

PUBLIC_COVENANT_SHA = "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263"
PUBLIC_COVENANT_TX = "j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "asset"

def is_payload(path: str, size: int) -> bool:
    lower = path.lower()
    return size > LARGE_THRESHOLD or any(lower.endswith(ext) for ext in PAYLOAD_EXTS)

def load_release_discovery(path: str):
    if not path:
        return {"found": False}
    p = Path(path)
    if not p.exists():
        return {"found": False}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"found": False}

def recompute_summary(m):
    files = m.get("files", [])
    release_assets = m.get("release_assets", [])
    arweave_assets = m.get("arweave_assets", [])
    ipfs_assets = m.get("ipfs_assets", [])
    eth = m.get("eth_attestations", [])

    return {
        "repo_files_total": len(files),
        "repo_files_verified": sum(1 for x in files if x.get("verified") is True),
        "repo_files_no_expected_hash": sum(1 for x in files if not x.get("expected_sha256")),
        "repo_files_hash_mismatch": sum(1 for x in files if x.get("hash_mismatch") is True),
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
        # Legacy compatibility while old tests/docs are migrated.
        "total_files": len(files),
        "verified_against_arweave": sum(1 for x in files if x.get("verified") is True),
        "no_expected_hash": sum(1 for x in files if not x.get("expected_sha256")),
        "hash_mismatch": sum(1 for x in files if x.get("hash_mismatch") is True),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="archive/hash-manifest.json")
    ap.add_argument("--public-covenant-release-discovery", default="")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    path = ROOT / args.manifest
    m = json.loads(path.read_text(encoding="utf-8"))

    discovery = load_release_discovery(args.public_covenant_release_discovery)

    new_files = []
    release_assets = list(m.get("release_assets", []))
    arweave_assets = list(m.get("arweave_assets", []))
    ipfs_assets = list(m.get("ipfs_assets", []))

    existing_external_ids = {
        x.get("asset_id") for x in release_assets + arweave_assets + ipfs_assets if x.get("asset_id")
    }

    for item in m.get("files", []):
        p_str = item.get("path", "")
        repo_path = ROOT / p_str

        # Public covenant archive should not be a repo file.
        if p_str.endswith("public-covenant-archive.zip") or p_str.endswith("public_covenant_archive.zip"):
            if "public_covenant_archive" not in existing_external_ids:
                if discovery.get("found"):
                    release_assets.append({
                        "asset_id": "public_covenant_archive",
                        "storage_domain": "github_release",
                        "release_tag": discovery["release_tag"],
                        "asset_name": discovery["asset_name"],
                        "size_bytes": item.get("size_bytes") or discovery.get("size_bytes"),
                        "sha256": item.get("sha256") or PUBLIC_COVENANT_SHA,
                        "expected_sha256": item.get("expected_sha256") or PUBLIC_COVENANT_SHA,
                        "source_arweave_tx": item.get("arweave_tx") or PUBLIC_COVENANT_TX,
                        "verified": True if (item.get("sha256") == (item.get("expected_sha256") or PUBLIC_COVENANT_SHA)) else None,
                        "verified_by": "github_release_asset_download_sha256",
                        "boundary": "Non-amending GitHub Release mirror. Arweave source prevails."
                    })
                else:
                    arweave_assets.append({
                        "asset_id": "public_covenant_archive",
                        "storage_domain": "arweave",
                        "arweave_tx": item.get("arweave_tx") or PUBLIC_COVENANT_TX,
                        "size_bytes": item.get("size_bytes"),
                        "sha256": item.get("sha256") or PUBLIC_COVENANT_SHA,
                        "expected_sha256": item.get("expected_sha256") or PUBLIC_COVENANT_SHA,
                        "verified": None,
                        "last_known_sha256": item.get("sha256") or PUBLIC_COVENANT_SHA,
                        "verification_status": "not_checked_in_this_run",
                        "github_release_mirror": None,
                        "boundary": "Arweave source asset. Large payload not committed to Git repository."
                    })
            continue

        if not repo_path.exists():
            raise SystemExit(f"Missing repo file in files[] with no domain migration rule: {p_str}")

        actual_size = repo_path.stat().st_size
        actual_sha = sha256_file(repo_path)

        item["storage_domain"] = "repo"
        item.setdefault("asset_id", slug(p_str.replace("archive/", "")))
        item["sha256"] = actual_sha
        item["size_bytes"] = actual_size

        if is_payload(p_str, actual_size) and item.get("allow_repo_payload") is not True:
            if actual_size > LARGE_THRESHOLD:
                raise SystemExit(f"Large payload should not be repo file without explicit migration/allowlist: {p_str}")

        expected = item.get("expected_sha256")
        if item.get("verified") is True:
            if not expected or actual_sha != expected:
                item["verified"] = False
                item["hash_mismatch"] = True
                item["mismatch_reason"] = "actual repository sha256 does not match expected_sha256; do not treat as verified"
        elif expected and actual_sha != expected:
            item["verified"] = False
            item["hash_mismatch"] = True
            item.setdefault("mismatch_reason", "actual repository sha256 does not match expected_sha256; do not treat as verified")

        new_files.append(item)

    m["schema"] = "trinity-accord.asset-manifest.v2"
    m["note"] = (
        "Asset-domain-aware manifest. files[] are repository files; release_assets[] are GitHub Release assets; "
        "arweave_assets[] are Arweave source/external assets; ipfs_assets[] are CID-addressed assets."
    )
    m["policy"] = {
        "large_binary_assets_must_not_be_committed_to_git": True,
        "verified_true_requires_hash_match": True,
        "repo_files_checked_against_repository_bytes": True,
        "release_assets_checked_by_github_release_download_sha256": True,
        "arweave_assets_checked_by_tx_download_sha256": True,
        "ipfs_assets_checked_by_cid_bytes_when_available": True
    }
    m["files"] = new_files
    m["release_assets"] = release_assets
    m["arweave_assets"] = arweave_assets
    m["ipfs_assets"] = ipfs_assets
    m["summary"] = recompute_summary(m)

    if args.write:
        path.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path}")
    else:
        print(json.dumps(m["summary"], indent=2, ensure_ascii=False))
        print("Dry run only; pass --write to update manifest.")

if __name__ == "__main__":
    main()
