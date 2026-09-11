#!/usr/bin/env python3
"""Build a DOI-ready Zenodo deposit from a published sidechain Finality Release.

The workflow downloads the exact GitHub Release assets into one directory. This
builder verifies those bytes in place and adds only two small deposit metadata
files, so the ~17.5 GB payload is never duplicated on the runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

TITLE = "Trinity Accord Chronicle Polygon and Base NFT Evidence v2"
SCHEMA = "trinity-accord/chronicle-sidechain-zenodo-deposit/v1"
TAG_RE = re.compile(r"chronicle-sidechain-finality-v1-([0-9a-f]{12})$")
PART_RE = re.compile(r"chronicle-sidechain-finality-v1-[0-9a-f]{12}\.tar\.zst\.part-\d{4}$")
SIDECARS = {
    "BASE-OP-STACK-DERIVATION.json",
    "COLD-VERIFICATION.json",
    "ETHEREUM-BEACON-FINALITY.json",
    "RELEASE-ASSETS-SHA256.txt",
    "RELEASE-ASSETS.json",
    "SOURCE-BINDING.json",
    "STRICT-VERIFICATION.json",
}
GENERATED = {"SIDECHAIN-ZENODO-DEPOSIT.json", "SHA256SUMS", "DEBUG.jsonl"}


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: pathlib.Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def inventory(paths: list[pathlib.Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(paths, key=lambda p: p.name):
        rows.append(
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def parse_checksum_file(path: pathlib.Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise SystemExit(f"invalid checksum line: {raw!r}")
        digest, name = parts
        name = name.strip().lstrip("*")
        if len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise SystemExit(f"invalid SHA-256 digest for {name}")
        if name in out:
            raise SystemExit(f"duplicate checksum entry: {name}")
        out[name] = digest.lower()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-dir", required=True)
    ap.add_argument("--source-tag", required=True)
    ap.add_argument("--source-sha", required=True)
    args = ap.parse_args()

    root = pathlib.Path(args.release_dir).resolve()
    if not root.is_dir():
        raise SystemExit("release directory missing")
    match = TAG_RE.fullmatch(args.source_tag)
    if not match:
        raise SystemExit("unexpected Finality Release tag")
    short = match.group(1)
    source_sha = args.source_sha.strip().lower()
    if len(source_sha) != 40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise SystemExit("source SHA must be 40 lowercase hex characters")
    if source_sha[:12] != short:
        raise SystemExit("Finality tag is not bound to source commit short SHA")

    for name in GENERATED:
        p = root / name
        if p.exists():
            p.unlink()

    files = [p for p in root.iterdir() if p.is_file()]
    names = {p.name for p in files}
    parts = sorted([p for p in files if PART_RE.fullmatch(p.name)], key=lambda p: p.name)
    if len(parts) != 19:
        raise SystemExit(f"expected 19 Finality archive parts, found {len(parts)}")
    if not SIDECARS.issubset(names):
        raise SystemExit(f"missing Finality sidecars: {sorted(SIDECARS - names)}")
    unexpected = names - {p.name for p in parts} - SIDECARS
    if unexpected:
        raise SystemExit(f"unexpected source Release files: {sorted(unexpected)}")

    release_assets = read_json(root / "RELEASE-ASSETS.json")
    archive_name = str(release_assets.get("archive_name") or "")
    expected_archive_name = f"chronicle-sidechain-finality-v1-{short}.tar.zst"
    if archive_name != expected_archive_name:
        raise SystemExit(f"archive name mismatch: {archive_name!r}")
    rows = release_assets.get("parts")
    if not isinstance(rows, list) or len(rows) != 19:
        raise SystemExit("RELEASE-ASSETS.json must describe exactly 19 parts")
    expected_parts: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("invalid RELEASE-ASSETS part row")
        name = str(row.get("name") or "")
        if name in expected_parts:
            raise SystemExit(f"duplicate RELEASE-ASSETS part: {name}")
        expected_parts[name] = row
    if set(expected_parts) != {p.name for p in parts}:
        raise SystemExit("Release part inventory mismatch")

    part_total = 0
    for part in parts:
        row = expected_parts[part.name]
        expected_size = int(row.get("bytes", -1))
        expected_sha = str(row.get("sha256") or "").lower()
        actual_size = part.stat().st_size
        actual_sha = sha256_file(part)
        if actual_size != expected_size or actual_sha != expected_sha:
            raise SystemExit(
                f"Finality part mismatch {part.name}: bytes={actual_size}/{expected_size} "
                f"sha256={actual_sha}/{expected_sha}"
            )
        part_total += actual_size
        print(f"[PART PASS] {part.name} bytes={actual_size} sha256={actual_sha}", flush=True)

    checksums = parse_checksum_file(root / "RELEASE-ASSETS-SHA256.txt")
    required_checksum_names = SIDECARS - {"RELEASE-ASSETS-SHA256.txt"}
    if set(checksums) != required_checksum_names:
        raise SystemExit(
            "Finality sidecar checksum inventory mismatch "
            f"missing={sorted(required_checksum_names - set(checksums))} "
            f"unexpected={sorted(set(checksums) - required_checksum_names)}"
        )
    for name, expected in sorted(checksums.items()):
        actual = sha256_file(root / name)
        if actual != expected:
            raise SystemExit(f"Finality sidecar SHA-256 mismatch: {name}")
        print(f"[SIDECAR PASS] {name} sha256={actual}", flush=True)

    cold = read_json(root / "COLD-VERIFICATION.json")
    if cold.get("pass") is not True:
        raise SystemExit("COLD-VERIFICATION.json is not pass:true")

    source_files = sorted(parts + [root / name for name in SIDECARS], key=lambda p: p.name)
    source_inventory = inventory(source_files)
    package_identity = hashlib.sha256(
        json.dumps(source_inventory, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    deposit = {
        "schema": SCHEMA,
        "version": f"finality-v1-{short}",
        "source_release_tag": args.source_tag,
        "source_commit_sha": source_sha,
        "package_identity_sha256": package_identity,
        "inventory": source_inventory,
        "metadata": {
            "title": TITLE,
            "upload_type": "dataset",
            "description": (
                "Finality preservation version for the Trinity Accord Chronicle Polygon/Base evidence series. "
                "It preserves the exact published GitHub Finality Release: 19 split archive parts plus Base OP Stack "
                "derivation, KZG-bound L1 evidence, Ethereum Beacon finality evidence, strict verification, source binding, "
                "checksums, and a cold-verification receipt. The source Release was published only after remote cold recovery. "
                "This version is non-amending and does not alter the three Bitcoin Originals or their canonical authority."
            ),
            "creators": [{"name": "Trinity Accord"}],
            "version": f"finality-v1-{short}",
            "keywords": [
                "Trinity Accord",
                "Polygon",
                "Base",
                "finality",
                "Ethereum",
                "OP Stack",
                "KZG",
                "Beacon Chain",
                "cryptographic evidence",
                "cold recovery",
            ],
            "notes": (
                "Supplementary non-amending finality and recovery proof. Ethereum weak subjectivity remains explicit. "
                "Mixed-rights boundaries from the Chronicle sidechain evidence series remain unchanged."
            ),
        },
        "rights_boundary": (
            "This preservation version may contain evidence derived from mixed-rights NFT records. It does not claim ownership "
            "of third-party material, does not relicense third-party material, and does not amend Canon."
        ),
        "finality_summary": {
            "cold_verification_pass": True,
            "archive_parts": len(parts),
            "archive_part_bytes": part_total,
            "github_release_assets": len(source_files),
        },
    }
    manifest = root / "SIDECHAIN-ZENODO-DEPOSIT.json"
    manifest.write_text(
        json.dumps(deposit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    sums_paths = source_files + [manifest]
    sums = root / "SHA256SUMS"
    sums.write_text(
        "\n".join(f"{sha256_file(p)}  {p.name}" for p in sorted(sums_paths, key=lambda p: p.name)) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "source_tag": args.source_tag,
                "source_sha": source_sha,
                "version": f"finality-v1-{short}",
                "source_files": len(source_files),
                "source_bytes": sum(p.stat().st_size for p in source_files),
                "package_identity_sha256": package_identity,
                "deposit_files": len(source_files) + 2,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
