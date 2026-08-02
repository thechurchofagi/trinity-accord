#!/usr/bin/env python3
"""Restore the complete Git-tracked Trinity Accord repository without GitHub.

This file is intentionally Python-standard-library-only.  Every published
capsule carries an identical standalone copy named ``restore-trinity-accord.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any


PACKAGE_SCHEMA = "trinityaccord.repository-preservation-capsule.v1"
TRACKED_FILES_SCHEMA = "trinityaccord.repository-tracked-files.v1"
PUBLISHED_FILE_NAMES = (
    "trinity-accord-source.tar.gz",
    "trinity-accord-recovery.bundle",
    "tracked-files.json",
    "preservation-manifest.json",
    "checksums.sha256",
    "README.txt",
    "restore-trinity-accord.py",
    "zenodo-metadata.json",
)
CHECKSUM_TARGET_NAMES = (
    "trinity-accord-source.tar.gz",
    "trinity-accord-recovery.bundle",
    "tracked-files.json",
    "README.txt",
    "restore-trinity-accord.py",
    "zenodo-metadata.json",
)
DEFAULT_ZENODO_API = "https://zenodo.org/api"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OID_RE = re.compile(r"^[0-9a-f]{40,64}$")


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise SystemExit(f"duplicate JSON key {key!r}: {label}")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object in {label}")
    return value


def strict_json(path: Path) -> dict[str, Any]:
    return strict_json_bytes(path.read_bytes(), str(path))


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise SystemExit("tracked repository path is missing")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe tracked repository path: {value!r}")
    return str(path)


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, name = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"invalid checksum line: {line!r}") from exc
        if name in result or SHA256_RE.fullmatch(expected) is None:
            raise SystemExit(f"invalid or duplicate checksum entry: {name}")
        result[name] = expected
    return result


def manifest_identity(manifest: dict[str, Any]) -> str:
    value = dict(manifest)
    value.pop("package_identity_sha256", None)
    return canonical_sha256(value)


def verify_capsule(capsule_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    observed = {path.name for path in capsule_dir.iterdir() if path.is_file()}
    expected = set(PUBLISHED_FILE_NAMES)
    if observed != expected:
        raise SystemExit(
            "preservation capsule file set mismatch: "
            f"missing={sorted(expected - observed)} unexpected={sorted(observed - expected)}"
        )
    checksums = parse_checksums(capsule_dir / "checksums.sha256")
    if set(checksums) != set(CHECKSUM_TARGET_NAMES):
        raise SystemExit("capsule checksum target set mismatch")
    for name, expected_sha in checksums.items():
        if file_digest(capsule_dir / name) != expected_sha:
            raise SystemExit(f"preservation capsule checksum mismatch: {name}")

    tracked = strict_json(capsule_dir / "tracked-files.json")
    if tracked.get("schema") != TRACKED_FILES_SCHEMA:
        raise SystemExit("unsupported tracked-files schema")
    files = tracked.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("tracked-files inventory is empty")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise SystemExit("tracked-files entry is not an object")
        name = safe_repo_path(item.get("path"))
        if name in seen:
            raise SystemExit(f"duplicate tracked repository path: {name}")
        seen.add(name)
        if item.get("mode") not in {"100644", "100755"}:
            raise SystemExit(f"unsupported tracked file mode: {name}")
        if not isinstance(item.get("bytes"), int) or item["bytes"] < 0:
            raise SystemExit(f"invalid tracked byte length: {name}")
        if SHA256_RE.fullmatch(str(item.get("sha256") or "")) is None:
            raise SystemExit(f"invalid tracked SHA-256: {name}")
        if GIT_OID_RE.fullmatch(str(item.get("git_blob_oid") or "")) is None:
            raise SystemExit(f"invalid tracked Git blob identity: {name}")
    if tracked.get("file_count") != len(files):
        raise SystemExit("tracked-files count mismatch")
    if files != sorted(files, key=lambda item: item["path"]):
        raise SystemExit("tracked-files inventory is not path-sorted")
    if tracked.get("inventory_sha256") != canonical_sha256(files):
        raise SystemExit("tracked-files inventory identity mismatch")

    manifest = strict_json(capsule_dir / "preservation-manifest.json")
    if manifest.get("schema") != PACKAGE_SCHEMA:
        raise SystemExit("unsupported preservation capsule schema")
    if manifest.get("published_file_names") != list(PUBLISHED_FILE_NAMES):
        raise SystemExit("preservation manifest file set/order mismatch")
    if manifest.get("package_identity_sha256") != manifest_identity(manifest):
        raise SystemExit("preservation manifest package identity mismatch")
    if manifest.get("git", {}).get("commit_sha") != tracked.get("git_commit_sha"):
        raise SystemExit("manifest/tracked-files commit mismatch")
    if manifest.get("git", {}).get("tree_oid") != tracked.get("git_tree_oid"):
        raise SystemExit("manifest/tracked-files tree mismatch")
    git = manifest.get("git")
    recovery_commit = str(git.get("recovery_commit_sha") or "") if isinstance(git, dict) else ""
    if (
        GIT_OID_RE.fullmatch(recovery_commit) is None
        or git.get("production_parent_history_embedded") is not False
        or git.get("production_tags_embedded") is not False
    ):
        raise SystemExit("manifest safe recovery-bundle boundary is invalid")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise SystemExit("preservation manifest file identities are missing")
    by_name = {
        str(item.get("name")): item
        for item in entries
        if isinstance(item, dict) and item.get("name")
    }
    expected_manifest_names = set(CHECKSUM_TARGET_NAMES) | {"checksums.sha256"}
    if set(by_name) != expected_manifest_names:
        raise SystemExit("preservation manifest non-self file set mismatch")
    for name, item in by_name.items():
        path = capsule_dir / name
        if item.get("bytes") != path.stat().st_size or item.get("sha256") != file_digest(path):
            raise SystemExit(f"preservation manifest file identity mismatch: {name}")
    scope = manifest.get("scope")
    if not isinstance(scope, dict) or scope.get("github_required_for_repository_recovery") is not False:
        raise SystemExit("capsule does not declare GitHub-independent repository recovery")
    baseline_tree = scope.get("exact_publication_baseline_tree_embedded")
    legacy_current_tree = scope.get("exact_current_production_tree_embedded")
    if baseline_tree is not True and legacy_current_tree is not True:
        raise SystemExit("capsule does not declare an exact recoverable tree")
    if baseline_tree is True and scope.get("live_main_equivalence_claimed") is not False:
        raise SystemExit("publication-baseline capsule overclaims live-main equivalence")
    return manifest, tracked


def fetch_bytes(url: str, label: str, attempts: int = 3) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,application/octet-stream,*/*",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "User-Agent": "trinity-preservation-recovery/1.0",
        },
    )
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except (urllib.error.URLError, OSError) as exc:
            last_error = str(exc)
            if attempt < attempts:
                time.sleep(float(attempt))
    raise SystemExit(f"failed to download {label}: {last_error}")


def zenodo_download_url(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    return str(links.get("content") or links.get("download") or links.get("self") or "")


def download_zenodo_record(record_id: str, api_base: str, target: Path) -> None:
    if not record_id.isdigit():
        raise SystemExit("Zenodo record id must be numeric")
    record = strict_json_bytes(
        fetch_bytes(f"{api_base.rstrip('/')}/records/{record_id}", f"Zenodo {record_id}"),
        f"Zenodo record {record_id}",
    )
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit(f"Zenodo record {record_id} has no files list")
    by_name = {
        str(item.get("key") or item.get("filename") or ""): item
        for item in files
        if isinstance(item, dict)
    }
    if set(by_name) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(f"Zenodo record {record_id} is not an exact preservation capsule")
    target.mkdir(parents=True)
    for name in PUBLISHED_FILE_NAMES:
        item = by_name[name]
        url = zenodo_download_url(item)
        if not url:
            raise SystemExit(f"Zenodo record {record_id} lacks download URL for {name}")
        raw = fetch_bytes(url, f"Zenodo {record_id}/{name}")
        checksum = str(item.get("checksum") or "")
        if checksum:
            algorithm, _, expected = checksum.partition(":")
            if algorithm.lower() == "md5" and hashlib.md5(raw, usedforsecurity=False).hexdigest() != expected:
                raise SystemExit(f"Zenodo transport checksum mismatch: {name}")
        (target / name).write_bytes(raw)


def run(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"required executable is missing: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"command failed ({' '.join(command)}):\n{exc.stdout[-4000:]}"
        ) from exc
    return result.stdout.strip()


def validate_tar_members(
    archive: tarfile.TarFile,
    tracked: dict[str, Any] | None = None,
) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    if not members:
        raise SystemExit("source snapshot archive is empty")
    expected_files = (
        {f"trinity-accord/{item['path']}": item for item in tracked["files"]}
        if tracked is not None
        else None
    )
    observed_members: set[str] = set()
    observed_files: set[str] = set()
    for member in members:
        path = PurePosixPath(member.name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or path.parts[0] != "trinity-accord"
            or "\\" in member.name
            or "\x00" in member.name
        ):
            raise SystemExit(f"unsafe source archive member: {member.name!r}")
        if member.name in observed_members:
            raise SystemExit(f"duplicate source archive member: {member.name!r}")
        observed_members.add(member.name)
        if not member.isdir() and not member.isfile():
            raise SystemExit(f"unsupported source archive member type: {member.name!r}")
        if member.isfile() and expected_files is not None:
            item = expected_files.get(member.name)
            if item is None:
                raise SystemExit(f"unexpected source archive file: {member.name!r}")
            observed_files.add(member.name)
            expected_executable = item["mode"] == "100755"
            observed_executable = bool(member.mode & 0o111)
            if member.size != item["bytes"]:
                raise SystemExit(f"source archive byte length mismatch: {member.name!r}")
            if observed_executable != expected_executable:
                raise SystemExit(f"source archive executable mode mismatch: {member.name!r}")
    if expected_files is not None and observed_files != set(expected_files):
        missing = sorted(set(expected_files) - observed_files)
        raise SystemExit(f"source archive tracked file set mismatch: missing={missing[:20]}")
    return members


def compare_tree(root: Path, tracked: dict[str, Any], label: str) -> None:
    expected_paths = {item["path"] for item in tracked["files"]}
    actual_paths = {
        str(path.relative_to(root).as_posix())
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).parts[0] != ".git"
    }
    if actual_paths != expected_paths:
        raise SystemExit(
            f"{label} file set mismatch: missing={sorted(expected_paths - actual_paths)[:20]} "
            f"unexpected={sorted(actual_paths - expected_paths)[:20]}"
        )
    for item in tracked["files"]:
        path = root / item["path"]
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"{label} has unsafe or missing file: {item['path']}")
        if path.stat().st_size != item["bytes"] or file_digest(path) != item["sha256"]:
            raise SystemExit(f"{label} byte identity mismatch: {item['path']}")
        observed_executable = bool(stat.S_IMODE(path.stat().st_mode) & 0o111)
        expected_executable = item["mode"] == "100755"
        if observed_executable != expected_executable:
            raise SystemExit(f"{label} executable mode mismatch: {item['path']}")


def verify_preserved_refs(repository: Path, manifest: dict[str, Any]) -> dict[str, int]:
    git = manifest.get("git")
    expected_entries = git.get("bundle_refs") if isinstance(git, dict) else None
    if not isinstance(expected_entries, list) or not expected_entries:
        raise SystemExit("preservation manifest bundle refs are missing")
    expected: dict[str, str] = {}
    for item in expected_entries:
        if not isinstance(item, dict):
            raise SystemExit("invalid preservation manifest bundle ref")
        name = str(item.get("ref") or "")
        oid = str(item.get("object_oid") or "")
        if (
            name in expected
            or (name != "refs/heads/main" and not name.startswith("refs/tags/"))
            or GIT_OID_RE.fullmatch(oid) is None
        ):
            raise SystemExit(f"invalid or duplicate preservation manifest ref: {name!r}")
        expected[name] = oid
    if git.get("bundle_ref_count") != len(expected):
        raise SystemExit("preservation manifest bundle ref count mismatch")

    output = run(
        [
            "git",
            "for-each-ref",
            "--format=%(refname)%09%(objectname)",
            "refs/heads",
            "refs/tags",
        ],
        cwd=repository,
    )
    observed: dict[str, str] = {}
    for line in output.splitlines():
        name, separator, oid = line.partition("\t")
        if not separator or name in observed:
            raise SystemExit("unable to parse restored Git refs")
        observed[name] = oid
    if observed != expected:
        raise SystemExit(
            "restored Git ref mismatch: "
            f"missing={sorted(set(expected) - set(observed))} "
            f"unexpected={sorted(set(observed) - set(expected))}"
        )
    return {
        "ref_count": len(observed),
        "tag_count": sum(name.startswith("refs/tags/") for name in observed),
    }


def prepare_output(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"output directory must be new or empty: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)


def restore(capsule_dir: Path, output_dir: Path, source_label: str) -> dict[str, Any]:
    manifest, tracked = verify_capsule(capsule_dir)
    prepare_output(output_dir)
    with tempfile.TemporaryDirectory(
        prefix=f".{output_dir.name}.partial-", dir=output_dir.parent
    ) as partial_name:
        partial = Path(partial_name)
        repository = partial / "repository"
        bundle = capsule_dir / "trinity-accord-recovery.bundle"
        bundle_verifier = partial / "bundle-verifier.git"
        run(["git", "init", "--bare", str(bundle_verifier)])
        run(["git", "bundle", "verify", str(bundle)], cwd=bundle_verifier)
        shutil.rmtree(bundle_verifier)
        run(["git", "clone", "--branch", "main", str(bundle), str(repository)])
        commit = run(["git", "rev-parse", "HEAD"], cwd=repository)
        tree = run(["git", "rev-parse", "HEAD^{tree}"], cwd=repository)
        recovery_commit = manifest["git"]["recovery_commit_sha"]
        if commit != recovery_commit or tree != tracked["git_tree_oid"]:
            raise SystemExit("restored Git recovery-commit/tree identity mismatch")
        run(["git", "fsck", "--full", "--strict"], cwd=repository)
        if run(["git", "status", "--porcelain"], cwd=repository):
            raise SystemExit("restored Git working tree is not clean")
        compare_tree(repository, tracked, "Git bundle checkout")
        refs = verify_preserved_refs(repository, manifest)

        source_check = partial / "source-snapshot-check"
        source_check.mkdir()
        with tarfile.open(capsule_dir / "trinity-accord-source.tar.gz", "r:gz") as archive:
            members = validate_tar_members(archive, tracked)
            if "filter" in inspect.signature(archive.extractall).parameters:
                archive.extractall(source_check, members=members, filter="data")
            else:  # Python < 3.12; members were already strictly validated above.
                archive.extractall(source_check, members=members)
        compare_tree(source_check / "trinity-accord", tracked, "source snapshot")
        shutil.rmtree(source_check)

        checkpoints = manifest.get("recovery_checkpoints")
        if not isinstance(checkpoints, list) or not checkpoints:
            raise SystemExit("preservation manifest recovery checkpoints are missing")
        for item in checkpoints:
            if not isinstance(item, dict):
                raise SystemExit("invalid recovery checkpoint")
            name = safe_repo_path(item.get("path"))
            expected = str(item.get("sha256") or "")
            if SHA256_RE.fullmatch(expected) is None:
                raise SystemExit(f"invalid recovery checkpoint SHA-256: {name}")
            if file_digest(repository / name) != expected:
                raise SystemExit(f"recovery checkpoint mismatch: {name}")

        run(["git", "remote", "remove", "origin"], cwd=repository)
        report = {
            "schema": "trinityaccord.repository-preservation-recovery-report.v1",
            "result": "pass",
            "repository_recovery_status": "full_exact_publication_baseline",
            "authority_level_recovery_status": "not_claimed",
            "capsule_id": manifest.get("capsule_id"),
            "package_identity_sha256": manifest.get("package_identity_sha256"),
            "source": source_label,
            "source_git_commit_sha": tracked["git_commit_sha"],
            "recovery_git_commit_sha": commit,
            "git_tree_oid": tree,
            "tracked_file_count": tracked["file_count"],
            "git_snapshot_bundle_verified": True,
            "production_parent_history_embedded": False,
            "production_tags_embedded": False,
            "production_tag_identity_count": manifest["git"].get(
                "production_tag_identity_count", 0
            ),
            "git_ref_count_verified": refs["ref_count"],
            "git_tag_count_verified": refs["tag_count"],
            "source_snapshot_independently_verified": True,
            "recovery_checkpoints_verified": len(checkpoints),
            "github_required": False,
            "network_required_after_capsule_download": False,
            "external_large_binary_annex_embedded": False,
            "limitations": [
                "The capsule restores every byte and executable mode in the exact immutable Git-tracked publication baseline named by its manifest.",
                "Production parent history and tag objects are excluded from the public bundle to avoid republishing historical credentials; original commit and tag identities remain in the manifest.",
                "Large external Release/Arweave/NFT payloads are referenced by verified manifests but are not embedded in this core repository capsule.",
                "Repository recovery does not itself prove authority, attestation, governance, amendment, or successor reception.",
            ],
            "boundary": {
                "bitcoin_originals_prevail": True,
                "recovery_does_not_amend_canonical_material": True,
                "capsule_is_a_non_authoritative_mirror": True,
                "live_main_equivalence_claimed": False,
            },
        }
        (partial / "recovery-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if output_dir.exists():
            output_dir.rmdir()
        os.replace(partial, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--deposit-dir")
    source.add_argument("--zenodo-record-id")
    parser.add_argument("--zenodo-api", default=DEFAULT_ZENODO_API)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.deposit_dir:
        capsule_dir = Path(args.deposit_dir).resolve()
        report = restore(capsule_dir, Path(args.output_dir).resolve(), str(capsule_dir))
    else:
        with tempfile.TemporaryDirectory(prefix="trinity-preservation-download-") as temp:
            capsule_dir = Path(temp) / "capsule"
            download_zenodo_record(args.zenodo_record_id, args.zenodo_api, capsule_dir)
            report = restore(
                capsule_dir,
                Path(args.output_dir).resolve(),
                f"zenodo:{args.zenodo_record_id}",
            )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
