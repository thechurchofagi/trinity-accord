#!/usr/bin/env python3
"""Restore and verify a Trinity Accord external-binary annex."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

PUBLISHED_FILE_NAMES = (
    "payload.tar",
    "annex-manifest.json",
    "checksums.sha256",
    "README.txt",
    "restore-trinity-annex.py",
    "zenodo-metadata.json",
)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        sha, name = line.split("  ", 1)
        if len(sha) != 64 or name in result:
            raise SystemExit(f"invalid checksum line: {line!r}")
        result[name] = sha
    return result


def safe_member(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or "\x00" in name:
        raise SystemExit(f"unsafe tar member: {name!r}")
    return str(path)


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "curl",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--retry",
            "6",
            "--retry-delay",
            "3",
            "--retry-all-errors",
            "--output",
            str(target),
            url,
        ],
        check=True,
    )


def zenodo_record(record_id: int) -> dict[str, Any]:
    request = urllib.request.Request(
        f"https://zenodo.org/api/records/{record_id}",
        headers={
            "Accept": "application/json",
            "User-Agent": "trinity-external-binary-annex-restore/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            value = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Zenodo record lookup failed: HTTP {exc.code}: {detail[:1000]}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Zenodo public record response is not an object")
    return value


def public_files(record: dict[str, Any]) -> dict[str, str]:
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit("Zenodo public record has no files list")
    result: dict[str, str] = {}
    for item in files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("key") or item.get("filename") or "")
        links = item.get("links")
        url = ""
        if isinstance(links, dict):
            url = str(links.get("self") or links.get("content") or links.get("download") or "")
        if name and url:
            result[name] = url
    return result


def acquire_from_zenodo(record_id: int, destination: Path) -> None:
    record = zenodo_record(record_id)
    remote = public_files(record)
    missing = sorted(set(PUBLISHED_FILE_NAMES) - set(remote))
    if missing:
        raise SystemExit(f"Zenodo annex record is missing files: {missing}")
    for name in PUBLISHED_FILE_NAMES:
        download(remote[name], destination / name)


def verify_package(deposit_dir: Path) -> dict[str, Any]:
    missing = sorted(
        name for name in PUBLISHED_FILE_NAMES if not (deposit_dir / name).is_file()
    )
    if missing:
        raise SystemExit(f"annex package is missing files: {missing}")
    checksums = parse_checksums(deposit_dir / "checksums.sha256")
    expected_targets = set(PUBLISHED_FILE_NAMES) - {"checksums.sha256"}
    if set(checksums) != expected_targets:
        raise SystemExit("annex checksum coverage mismatch")
    for name, expected in checksums.items():
        observed = hash_file(deposit_dir / name)
        if observed != expected:
            raise SystemExit(f"annex package checksum mismatch: {name}")
    manifest = strict_json(deposit_dir / "annex-manifest.json")
    if manifest.get("schema") != "trinityaccord.external-binary-annex.v1":
        raise SystemExit("unsupported annex manifest schema")
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise SystemExit("annex manifest asset list is empty")
    return manifest


def extract_and_verify(deposit_dir: Path, output_dir: Path, source: str) -> dict[str, Any]:
    manifest = verify_package(deposit_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"output directory must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_dir = output_dir / "payload"
    payload_dir.mkdir()
    with tarfile.open(deposit_dir / "payload.tar", mode="r:") as archive:
        for member in archive.getmembers():
            name = safe_member(member.name)
            if not member.isfile():
                raise SystemExit(f"annex tar contains non-file member: {name}")
            target = payload_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            source_handle = archive.extractfile(member)
            if source_handle is None:
                raise SystemExit(f"unable to read annex tar member: {name}")
            with source_handle, target.open("wb") as output:
                shutil.copyfileobj(source_handle, output, length=4 * 1024 * 1024)
    assets = manifest["assets"]
    expected_paths = {str(item["path"]) for item in assets}
    observed_paths = {
        path.relative_to(payload_dir).as_posix()
        for path in payload_dir.rglob("*")
        if path.is_file()
    }
    if observed_paths != expected_paths:
        raise SystemExit(
            f"restored asset set mismatch: missing={sorted(expected_paths-observed_paths)} "
            f"unexpected={sorted(observed_paths-expected_paths)}"
        )
    restored_bytes = 0
    for item in assets:
        path = payload_dir / safe_member(str(item["path"]))
        if path.stat().st_size != int(item["bytes"]):
            raise SystemExit(f"restored annex size mismatch: {item['path']}")
        if hash_file(path) != str(item["sha256"]):
            raise SystemExit(f"restored annex SHA-256 mismatch: {item['path']}")
        restored_bytes += path.stat().st_size
    report = {
        "schema": "trinityaccord.external-binary-annex-recovery-report.v1",
        "status": "passed",
        "source": source,
        "annex_type": manifest.get("annex_type"),
        "annex_id": manifest.get("annex_id"),
        "package_identity_sha256": manifest.get("package_identity_sha256"),
        "asset_count": len(assets),
        "payload_bytes": restored_bytes,
        "github_credentials_used": False,
        "zenodo_credentials_used": False,
        "bitcoin_originals_remain_authoritative": True,
    }
    (output_dir / "recovery-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--deposit-dir")
    group.add_argument("--zenodo-record-id", type=int)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    if args.deposit_dir:
        deposit_dir = Path(args.deposit_dir).resolve()
        return 0 if extract_and_verify(deposit_dir, output_dir, f"directory:{deposit_dir}") else 1
    with tempfile.TemporaryDirectory(prefix="trinity-annex-download-") as temp_name:
        deposit_dir = Path(temp_name)
        acquire_from_zenodo(args.zenodo_record_id, deposit_dir)
        return 0 if extract_and_verify(
            deposit_dir, output_dir, f"zenodo:{args.zenodo_record_id}"
        ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
