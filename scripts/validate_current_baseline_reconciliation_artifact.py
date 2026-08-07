#!/usr/bin/env python3
"""Validate and materialize the retained proof from the interrupted baseline run."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "preservation/current-baseline-publication-reconciliation-v1.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def one(root: Path, pattern: str) -> Path:
    matches = sorted(root.rglob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one {pattern!r} in {root}; found {len(matches)}")
    return matches[0]


def safe_extract(archive_path: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or member.issym() or member.islnk():
                raise SystemExit(f"unsafe snapshot member: {member.name}")
        archive.extractall(target, members=members, filter="data")


def git_bytes(source: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{source}:{path}"], cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof-dir", required=True)
    parser.add_argument("--output-work-state", required=True)
    parser.add_argument("--output-receipt", required=True)
    parser.add_argument("--output-payload", required=True)
    args = parser.parse_args()

    proof = Path(args.proof_dir).resolve()
    authorization = read_json(AUTHORIZATION)
    if authorization.get("status") != "pending":
        raise SystemExit("reconciliation authorization is not pending")
    if authorization.get("external_writes_already_complete") is not True:
        raise SystemExit("authorization does not identify completed external writes")
    if authorization.get("allow_zenodo_write") is not False or authorization.get("allow_arweave_post") is not False:
        raise SystemExit("reconciliation authorization does not forbid external writes")

    source = str(authorization["source_git_commit_sha"])
    doi = str(authorization["version_doi"])
    record_id = int(authorization["zenodo_record_id"])
    package = str(authorization["package_identity_sha256"])
    txid = str(authorization["arweave_txid"])
    expected_payload = str(authorization["arweave_payload_sha256"])
    expected_bytes = int(authorization["arweave_payload_bytes"])

    work_path = one(proof, "current-baseline-publish-work.json")
    receipt_path = one(proof, "homepage-arweave-receipt.json")
    payload_path = one(proof, "trinity-homepage-machine-*.tar.gz")
    work = read_json(work_path)
    receipt = read_json(receipt_path)

    checks = {
        "published work status": work.get("publication_status") == "published",
        "published source": work.get("latest_git_commit_sha") == source,
        "published DOI": work.get("latest_doi") == doi,
        "published record": work.get("latest_record_id") == record_id,
        "published package": work.get("latest_package_identity_sha256") == package,
        "receipt transaction": (receipt.get("txid") or receipt.get("tx_id")) == txid,
        "receipt source": receipt.get("source_git_commit_sha") == source,
        "receipt DOI": receipt.get("repository_version_doi") == doi,
        "receipt result": receipt.get("result") == "uploaded",
        "receipt hash match": receipt.get("hash_match") is True,
        "payload bytes": payload_path.stat().st_size == expected_bytes,
        "payload digest": sha256(payload_path) == expected_payload,
        "receipt payload digest": receipt.get("payload_sha256") == expected_payload,
        "receipt readback digest": receipt.get("readback_sha256") == expected_payload,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("retained proof mismatch: " + ", ".join(failed))

    extracted = proof / "validated-snapshot"
    safe_extract(payload_path, extracted)
    manifest = read_json(extracted / "manifest.json")
    if manifest.get("source_git_commit_sha") != source or manifest.get("repository_version_doi") != doi:
        raise SystemExit("snapshot manifest binding mismatch")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("snapshot manifest has no files")
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise SystemExit("invalid snapshot file entry")
        name = item["path"]
        local = extracted / name
        if not local.is_file():
            raise SystemExit(f"snapshot file missing: {name}")
        if sha256(local) != item.get("sha256") or local.stat().st_size != item.get("bytes"):
            raise SystemExit(f"snapshot file identity mismatch: {name}")
        if name != "rendered-homepage.html" and local.read_bytes() != git_bytes(source, name):
            raise SystemExit(f"snapshot file differs from exact source: {name}")

    checksum_lines = (extracted / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    for line in checksum_lines:
        digest, separator, name = line.partition("  ")
        if not separator or sha256(extracted / name) != digest:
            raise SystemExit(f"snapshot checksum mismatch: {name or line}")

    for source_path, output in (
        (work_path, Path(args.output_work_state)),
        (receipt_path, Path(args.output_receipt)),
        (payload_path, Path(args.output_payload)),
    ):
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, output)
    print(f"Validated retained baseline proof: doi={doi} txid={txid} sha256={expected_payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
