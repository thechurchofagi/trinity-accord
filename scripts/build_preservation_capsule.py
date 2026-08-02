#!/usr/bin/env python3
"""Build a self-contained, GitHub-independent repository preservation capsule."""
from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from preservation_capsule import (
    CHECKSUM_TARGET_NAMES,
    MANIFEST_HASHED_NAMES,
    PACKAGE_SCHEMA,
    PACKAGE_TITLE,
    PUBLISHED_FILE_NAMES,
    RIGHTS_BOUNDARY_VERSION,
    TRACKED_FILES_SCHEMA,
    ZENODO_LICENSE_ID,
    canonical_sha256,
    manifest_identity,
    sha256,
    verify_local_package,
)


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/thechurchofagi/trinity-accord"
RESEARCH_DOI = "10.5281/zenodo.21699878"
REQUIRED_CHECKPOINTS = (
    "archive/authority-manifest/authority.jcs.json",
    "archive/btc-signature/btc-signature.json",
    "archive/eth-witness/eth-witness.json",
    "archive/trust-root-policy.json",
    "archive/evidence/digest-manifest.json",
    "archive/evidence/digest-manifest.csv",
    "api/corrections-index.json",
    "api/recovery-index.json",
    "RECOVERY.md",
)

FORBIDDEN_HISTORY_PATHS = re.compile(
    r"(^|/)(?:\.env(?:\..+)?|[^/]*\.jwk|wallet(?:\..+)?|"
    r"[^/]*private[^/]*\.pem|[^/]*secrets?[^/]*\.json|"
    r"credentials?(?:\..+)?|id_rsa|id_ed25519)$",
    re.IGNORECASE,
)
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    ("github_classic_token", re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("github_fine_grained_token", re.compile(rb"github_pat_[A-Za-z0-9_]{30,}")),
    ("aws_access_key", re.compile(rb"AKIA[0-9A-Z]{16}")),
    (
        "openai_api_key",
        re.compile(
            rb"\bsk-(?:[A-Za-z0-9]{48}|proj-[A-Za-z0-9_-]{40,}|"
            rb"svcacct-[A-Za-z0-9_-]{40,})\b"
        ),
    ),
    ("anthropic_api_key", re.compile(rb"\bsk-ant-api03-[A-Za-z0-9_-]{20,}\b")),
)
PRIVATE_KEY_PEM_RE = re.compile(
    rb"-----BEGIN (?P<label>(?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY|"
    rb"PGP PRIVATE KEY BLOCK)-----\s*"
    rb"(?P<body>[A-Za-z0-9+/=\r\n]{20,})\s*"
    rb"-----END (?P=label)-----",
    re.DOTALL,
)
# This exact, publicly committed red-team fixture intentionally contains a
# synthetic token that exercises the production intake scanner.  Pinning its
# full SHA-256 keeps the history scan narrow: any past or future byte change at
# the path fails closed and requires an explicit review/update.
ALLOWLISTED_SYNTHETIC_SECRET_FIXTURES = {
    "tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json": {
        "123dc8009acb3432b9fd58223fb12d6ba33d63a61ff78b180cc2b74a6ec78e26"
    }
}
ALLOWLISTED_SYNTHETIC_SECRET_MATCH_SHA256 = {
    # Fake GitHub token in the red-team payload and its committed scan reports.
    "8841c2397d5af2017f16d8f94da2d34ce7e25b4992bbf8dadc4fef13b06e410e",
    # Fake Anthropic key in the intake-integrity regression source.
    "37b3f835cd1f565671da9267f372bc82b2987314bed6f679540c4a6db1cd747e",
}


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    input_bytes: bytes | None = None,
    env: dict[str, str] | None = None,
) -> bytes:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            input=input_bytes,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"required executable is missing: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace")[-4000:]
        raise SystemExit(f"command failed ({' '.join(command)}): {detail}") from exc
    return result.stdout


def git_text(root: Path, *args: str) -> str:
    return run(["git", *args], cwd=root).decode("utf-8").strip()


def git_bytes(root: Path, *args: str) -> bytes:
    return run(["git", *args], cwd=root)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def github_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe Git path in repository: {value!r}")
    return str(path)


def batch_blob_bytes(repo: Path, oids: Iterable[str]) -> dict[str, bytes]:
    unique = list(dict.fromkeys(oids))
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=repo,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None or process.stdout is None:
        raise SystemExit("failed to start git cat-file --batch")
    result: dict[str, bytes] = {}
    try:
        for oid in unique:
            process.stdin.write(oid.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().rstrip(b"\n")
            parts = header.split()
            if len(parts) != 3 or parts[1] != b"blob":
                raise SystemExit(f"Git object is not an available blob: {oid}")
            size = int(parts[2])
            raw = process.stdout.read(size)
            terminator = process.stdout.read(1)
            if len(raw) != size or terminator != b"\n":
                raise SystemExit(f"truncated Git blob read: {oid}")
            result[oid] = raw
    finally:
        process.stdin.close()
    return_code = process.wait()
    if return_code != 0:
        detail = (process.stderr.read() if process.stderr else b"").decode(
            "utf-8", errors="replace"
        )
        raise SystemExit(f"git cat-file --batch failed: {detail[-2000:]}")
    return result


def tracked_file_inventory(root: Path, commit: str, tree_oid: str) -> dict[str, Any]:
    output = git_bytes(root, "ls-tree", "-rlz", "--full-tree", commit)
    entries: list[dict[str, Any]] = []
    for raw_entry in output.split(b"\x00"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, object_type, oid, size = metadata.decode("ascii").split()
            name = safe_path(raw_path.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise SystemExit("unable to parse Git tree entry") from exc
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise SystemExit(
                f"repository capsule currently supports regular tracked files only: {name}"
            )
        entries.append(
            {
                "path": name,
                "mode": mode,
                "git_blob_oid": oid,
                "bytes": int(size),
            }
        )
    entries.sort(key=lambda item: item["path"])
    blobs = batch_blob_bytes(root, (item["git_blob_oid"] for item in entries))
    for item in entries:
        raw = blobs[item["git_blob_oid"]]
        if len(raw) != item["bytes"]:
            raise SystemExit(f"Git tree/blob size mismatch: {item['path']}")
        item["sha256"] = hashlib.sha256(raw).hexdigest()
    return {
        "schema": TRACKED_FILES_SCHEMA,
        "repository": REPOSITORY_URL,
        "git_commit_sha": commit,
        "git_tree_oid": tree_oid,
        "file_count": len(entries),
        "inventory_sha256": canonical_sha256(entries),
        "files": entries,
    }



def materialize_commit_tree_repository(
    source: Path,
    target: Path,
    tree_oid: str,
    tracked: dict[str, Any],
) -> None:
    """Create a clean history-free repository containing only the frozen tree.

    The frozen tree is reconstructed directly in the Git index from its exact
    modes, blob OIDs, and paths. This deliberately avoids a worktree and
    ``git add`` so repository ignore rules, filesystem permissions, checkout
    filters, and clone depth cannot alter the published recovery object graph.
    """
    run(["git", "init", "-b", "main", str(target)])
    blobs = batch_blob_bytes(
        source, (item["git_blob_oid"] for item in tracked["files"])
    )
    for item in tracked["files"]:
        expected_oid = item["git_blob_oid"]
        observed_oid = run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=target,
            input_bytes=blobs[expected_oid],
        ).decode("ascii").strip()
        if observed_oid != expected_oid:
            raise SystemExit(
                "clean recovery blob identity mismatch: "
                f"{item['path']}: expected {expected_oid}, observed {observed_oid}"
            )
        git_text(
            target,
            "update-index",
            "--add",
            "--cacheinfo",
            item["mode"],
            expected_oid,
            item["path"],
        )
    rebuilt_tree = git_text(target, "write-tree")
    if rebuilt_tree != tree_oid:
        raise SystemExit(
            "clean recovery repository tree mismatch: "
            f"expected {tree_oid}, observed {rebuilt_tree}"
        )


def delete_all_refs_and_set_main(bare: Path, commit: str) -> None:
    refs = git_text(bare, "for-each-ref", "--format=%(refname)")
    for ref in refs.splitlines():
        if ref:
            git_text(bare, "update-ref", "-d", ref)
    git_text(bare, "update-ref", "refs/heads/main", commit)
    git_text(bare, "symbolic-ref", "HEAD", "refs/heads/main")


def create_recovery_snapshot_commit(
    bare: Path,
    tree_oid: str,
    source_commit: str,
    commit_epoch: int,
) -> str:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Trinity Accord Preservation",
            "GIT_AUTHOR_EMAIL": "preservation@trinityaccord.org",
            "GIT_AUTHOR_DATE": f"@{commit_epoch} +0000",
            "GIT_COMMITTER_NAME": "Trinity Accord Preservation",
            "GIT_COMMITTER_EMAIL": "preservation@trinityaccord.org",
            "GIT_COMMITTER_DATE": f"@{commit_epoch} +0000",
        }
    )
    message = (
        "Trinity Accord GitHub-independent recovery snapshot\n\n"
        f"Source production commit: {source_commit}\n"
        f"Exact source tree: {tree_oid}\n\n"
        "This synthetic root commit intentionally omits production parent history and "
        "tags so an immutable public deposit does not republish historical credentials.\n"
    ).encode("utf-8")
    return run(
        ["git", "commit-tree", tree_oid],
        cwd=bare,
        input_bytes=message,
        env=env,
    ).decode("ascii").strip()


def reachable_blob_inventory(
    bare: Path,
) -> tuple[list[tuple[str, int]], dict[str, str]]:
    listing = git_text(bare, "rev-list", "--objects", "--all")
    object_paths: dict[str, str] = {}
    object_oids: list[str] = []
    for line in listing.splitlines():
        oid, separator, name = line.partition(" ")
        object_oids.append(oid)
        if separator and name:
            object_paths.setdefault(oid, name)
    metadata = run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        cwd=bare,
        input_bytes=("\n".join(object_oids) + "\n").encode("ascii"),
    ).decode("ascii")
    result: list[tuple[str, int]] = []
    for line in metadata.splitlines():
        oid, object_type, raw_size = line.split()
        if object_type == "blob":
            result.append((oid, int(raw_size)))
    return result, object_paths


def contains_probable_private_key_pem(raw: bytes) -> bool:
    for match in PRIVATE_KEY_PEM_RE.finditer(raw):
        body_lines = [
            line.strip()
            for line in match.group("body").splitlines()
            if line.strip() and not line.strip().startswith(b"=")
        ]
        try:
            decoded = base64.b64decode(b"".join(body_lines), validate=True)
        except (binascii.Error, ValueError):
            continue
        if len(decoded) >= 32:
            return True
    return False


def scan_recovery_snapshot_for_secrets(bare: Path) -> dict[str, Any]:
    blob_meta, object_paths = reachable_blob_inventory(bare)
    fixture_oids: dict[str, set[str]] = {
        path: set() for path in ALLOWLISTED_SYNTHETIC_SECRET_FIXTURES
    }
    forbidden_paths: list[str] = []
    for oid, name in object_paths.items():
        if name in fixture_oids:
            fixture_oids[name].add(oid)
        if (
            FORBIDDEN_HISTORY_PATHS.search(name)
            and not name.endswith(".env.example")
            and name not in ALLOWLISTED_SYNTHETIC_SECRET_FIXTURES
        ):
            forbidden_paths.append(name)
    if forbidden_paths:
        raise SystemExit(
            "refusing to preserve current secret-bearing filename(s): "
            + ", ".join(sorted(set(forbidden_paths))[:20])
        )

    suspicious: list[dict[str, str]] = []
    blobs = batch_blob_bytes(bare, (oid for oid, _size in blob_meta))
    allowlisted_blob_oids: set[str] = set()
    allowlisted_match_count = 0
    for name, oids in fixture_oids.items():
        if not oids:
            continue
        allowed_hashes = ALLOWLISTED_SYNTHETIC_SECRET_FIXTURES[name]
        for oid in oids:
            observed = hashlib.sha256(blobs[oid]).hexdigest()
            if observed not in allowed_hashes:
                raise SystemExit(
                    f"synthetic secret fixture hash mismatch in current snapshot: {name}"
                )
            allowlisted_blob_oids.add(oid)
    for oid, _size in blob_meta:
        raw = blobs[oid]
        if b"\x00" in raw[:8192]:
            continue
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(raw):
                match_sha256 = hashlib.sha256(match.group()).hexdigest()
                if match_sha256 in ALLOWLISTED_SYNTHETIC_SECRET_MATCH_SHA256:
                    allowlisted_match_count += 1
                    continue
                suspicious.append(
                    {
                        "git_blob_oid": oid,
                        "path": object_paths.get(oid, ""),
                        "pattern": label,
                    }
                )
        if contains_probable_private_key_pem(raw):
            suspicious.append(
                {
                    "git_blob_oid": oid,
                    "path": object_paths.get(oid, ""),
                    "pattern": "probable_private_key_pem",
                }
            )
        if (
            re.search(rb'"kty"\s*:\s*"RSA"', raw)
            and re.search(rb'"d"\s*:', raw)
            and re.search(rb'"p"\s*:', raw)
            and re.search(rb'"q"\s*:', raw)
        ):
            suspicious.append(
                {"git_blob_oid": oid, "path": object_paths.get(oid, ""), "pattern": "private_rsa_jwk"}
            )
    if suspicious:
        summary = ", ".join(
            f"{item['pattern']}:{item['path'] or item['git_blob_oid']}" for item in suspicious[:20]
        )
        raise SystemExit(f"refusing to preserve suspected secret material: {summary}")
    return {
        "snapshot_reachable_blob_count_scanned": len(blob_meta),
        "secret_pattern_match_count": 0,
        "forbidden_path_match_count": 0,
        "allowlisted_synthetic_fixture_blob_count": len(allowlisted_blob_oids),
        "allowlisted_synthetic_secret_match_count": allowlisted_match_count,
    }


def create_source_archive(root: Path, commit: str, target: Path) -> None:
    process = subprocess.Popen(
        ["git", "archive", "--format=tar", "--prefix=trinity-accord/", commit],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None:
        raise SystemExit("failed to start git archive")
    with target.open("wb") as raw_output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_output, mtime=0) as compressed:
            shutil.copyfileobj(process.stdout, compressed, length=1024 * 1024)
    return_code = process.wait()
    if return_code != 0:
        detail = (process.stderr.read() if process.stderr else b"").decode(
            "utf-8", errors="replace"
        )
        raise SystemExit(f"git archive failed: {detail[-2000:]}")


def git_show_bytes(root: Path, commit: str, path: str) -> bytes:
    return git_bytes(root, "show", f"{commit}:{path}")


def checkpoint_inventory(root: Path, commit: str) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for name in REQUIRED_CHECKPOINTS:
        raw = git_show_bytes(root, commit, name)
        checkpoints.append(
            {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
    return checkpoints


def latest_record_identity(root: Path, commit: str, tracked: dict[str, Any]) -> dict[str, Any]:
    names = [
        item["path"]
        for item in tracked["files"]
        if re.fullmatch(r"record-chain/records/R-[0-9]{9}\.json", item["path"])
    ]
    if not names:
        raise SystemExit("repository capsule cannot find native Record-Chain records")
    name = sorted(names)[-1]
    try:
        record = json.loads(git_show_bytes(root, commit, name).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"latest native Record-Chain record is invalid: {name}") from exc
    return {
        "record_count": len(names),
        "latest_record_path": name,
        "latest_record_id": record.get("record_id"),
        "latest_record_sha256": record.get("record_sha256"),
    }


def external_asset_summary(root: Path, commit: str) -> dict[str, Any]:
    large = json.loads(
        git_show_bytes(root, commit, "RELEASE-LARGE-DATA-MANIFEST.json").decode("utf-8")
    )
    nft = json.loads(
        git_show_bytes(root, commit, "nft-text-descriptions/nft-cars-manifest.json").decode(
            "utf-8"
        )
    )
    large_assets = large.get("assets") if isinstance(large, dict) else []
    nft_files = nft.get("files") if isinstance(nft, dict) else []
    return {
        "embedded_in_core_capsule": False,
        "reason": (
            "Large external payloads have separate hash-bound Arweave/Release recovery "
            "domains and mixed rights. Their manifests and recovery tools are embedded, "
            "but their bytes require a separately approved annex."
        ),
        "large_data_manifest": {
            "path": "RELEASE-LARGE-DATA-MANIFEST.json",
            "asset_count": len(large_assets) if isinstance(large_assets, list) else 0,
            "declared_bytes": sum(
                int(item.get("size_bytes") or 0)
                for item in large_assets
                if isinstance(item, dict)
            ),
        },
        "nft_car_manifest": {
            "path": "nft-text-descriptions/nft-cars-manifest.json",
            "asset_count": len(nft_files) if isinstance(nft_files, list) else 0,
            "declared_bytes": sum(
                int(item.get("size") or 0) for item in nft_files if isinstance(item, dict)
            ),
        },
    }


def reference_inventory(bare: Path) -> list[dict[str, str]]:
    output = git_text(
        bare,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)",
        "refs/heads",
        "refs/tags",
    )
    result: list[dict[str, str]] = []
    for line in output.splitlines():
        name, oid = line.split("\t", 1)
        result.append({"ref": name, "object_oid": oid})
    return sorted(result, key=lambda item: item["ref"])


def production_tag_identity_inventory(root: Path) -> list[dict[str, str | None]]:
    output = git_text(
        root,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(*objectname)",
        "refs/tags",
    )
    result: list[dict[str, str | None]] = []
    for line in output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) not in {2, 3}:
            raise SystemExit("unable to parse production tag identity")
        name, oid = parts[:2]
        peeled = parts[2] if len(parts) == 3 else ""
        result.append(
            {
                "ref": name,
                "object_oid": oid,
                "peeled_object_oid": peeled or None,
            }
        )
    return sorted(result, key=lambda item: str(item["ref"]))


def build(root: Path, output_dir: Path, commitish: str) -> Path:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"capsule output directory must be new or empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    commit = git_text(root, "rev-parse", "--verify", f"{commitish}^{{commit}}")
    tree_oid = git_text(root, "rev-parse", f"{commit}^{{tree}}")
    commit_date = git_text(root, "show", "-s", "--format=%cI", commit)
    commit_epoch = int(git_text(root, "show", "-s", "--format=%ct", commit))
    capsule_id = f"repository-{commit[:12]}"
    tracked = tracked_file_inventory(root, commit, tree_oid)

    with tempfile.TemporaryDirectory(prefix="trinity-preservation-build-") as temp_name:
        temp = Path(temp_name)
        recovery_repo = temp / "repository"
        materialize_commit_tree_repository(
            root, recovery_repo, tree_oid, tracked
        )
        recovery_commit = create_recovery_snapshot_commit(
            recovery_repo, tree_oid, commit, commit_epoch
        )
        delete_all_refs_and_set_main(recovery_repo, recovery_commit)
        secret_scan = scan_recovery_snapshot_for_secrets(recovery_repo)
        references = reference_inventory(recovery_repo)
        if references != [{"ref": "refs/heads/main", "object_oid": recovery_commit}]:
            raise SystemExit("recovery bundle contains an unexpected ref")
        bundle = output_dir / "trinity-accord-recovery.bundle"
        # Git pack delta selection is parallel by default and can produce
        # byte-distinct bundles for the same exact object graph.  The public
        # preservation package identity includes the bundle bytes, so force a
        # single deterministic pack worker and disable bitmap reuse.
        git_text(
            recovery_repo,
            "-c",
            "pack.threads=1",
            "-c",
            "pack.useBitmaps=false",
            "-c",
            "pack.reuseDeltas=false",
            "-c",
            "pack.reuseObjects=false",
            "bundle",
            "create",
            "--version=2",
            str(bundle),
            "refs/heads/main",
        )
        git_text(recovery_repo, "bundle", "verify", str(bundle))

    create_source_archive(root, commit, output_dir / "trinity-accord-source.tar.gz")
    write_json(output_dir / "tracked-files.json", tracked)
    restore_bytes = git_show_bytes(root, commit, "scripts/restore_preservation_capsule.py")
    (output_dir / "restore-trinity-accord.py").write_bytes(restore_bytes)

    metadata = {
        "upload_type": "software",
        "title": PACKAGE_TITLE,
        "creators": [{"name": "Liu, Hongju"}],
        "description": (
            "A versioned, non-authoritative preservation capsule for the Trinity Accord "
            "public repository. It contains an exact source snapshot plus a cloneable Git "
            "recovery bundle for the exact immutable publication-baseline tree, allowing every "
            "Git-tracked byte in that baseline to be restored without GitHub. Production parent history and "
            "tag objects and live tag refs are deliberately excluded from the public bundle "
            "and package identity so historical credentials are not republished and later "
            "mutable refs cannot alter a frozen capsule. Large "
            "externally hosted evidence and NFT payloads remain hash-bound references and "
            "require a separately approved binary annex. The Bitcoin Originals remain "
            "authoritative."
        ),
        "access_right": "open",
        "license": ZENODO_LICENSE_ID,
        "publication_date": commit_date[:10],
        "version": capsule_id,
        "keywords": [
            "Trinity Accord",
            "repository preservation",
            "disaster recovery",
            "Git bundle",
            "civilizational memory",
        ],
        "related_identifiers": [
            {
                "identifier": REPOSITORY_URL,
                "relation": "isDerivedFrom",
                "resource_type": "software",
            },
            {
                "identifier": "https://www.trinityaccord.org",
                "relation": "isDocumentedBy",
                "resource_type": "other",
            },
            {
                "identifier": f"https://doi.org/{RESEARCH_DOI}",
                "relation": "isSupplementTo",
                "resource_type": "publication-report",
            },
        ],
        "notes": (
            "Open access permits public retrieval for preservation. The repository has no "
            "single blanket reuse licence; this deposit grants no new reuse rights. Each "
            "component remains subject to its existing rights, and third-party rights are "
            "not transferred. This mirror is not authority, amendment, attestation, "
            "governance, or successor reception."
        ),
    }
    write_json(output_dir / "zenodo-metadata.json", metadata)
    (output_dir / "README.txt").write_text(
        "Trinity Accord Repository Preservation Capsule\n"
        "===============================================\n\n"
        f"Capsule ID: {capsule_id}\n"
        f"Git commit: {commit}\n"
        f"Git tree: {tree_oid}\n"
        f"Tracked files: {tracked['file_count']}\n\n"
        "One-command restore from a downloaded capsule directory:\n\n"
        "  python3 restore-trinity-accord.py --deposit-dir . --output-dir ./restored-trinity-accord\n\n"
        "One-command restore after downloading only this standalone script:\n\n"
        "  python3 restore-trinity-accord.py --zenodo-record-id <RECORD_ID> "
        "--output-dir ./restored-trinity-accord\n\n"
        "The result contains repository/ and recovery-report.json. GitHub is not\n"
        "required after the capsule files have been obtained. The Git source tree,\n"
        "source archive, and cloneable single-root recovery bundle are independently\n"
        "cross-checked. The production commit and tag identities are recorded in the\n"
        "manifest, but historical parent objects, tag objects, and mutable live tag\n"
        "refs are not publicly embedded or included in the package identity.\n\n"
        "Scope boundary\n"
        "--------------\n"
        "This core capsule embeds every Git-tracked byte in the declared publication\n"
        "baseline. Large external evidence and NFT payload bytes are not duplicated\n"
        "here; their TXIDs, hashes, manifests, and\n"
        "recovery tools are embedded in the repository. A separate mixed-rights binary\n"
        "annex requires explicit approval. No blanket reuse licence is granted.\n",
        encoding="utf-8",
    )
    (output_dir / "checksums.sha256").write_text(
        "".join(
            f"{sha256(output_dir / name)}  {name}\n" for name in CHECKSUM_TARGET_NAMES
        ),
        encoding="utf-8",
    )

    manifest: dict[str, Any] = {
        "schema": PACKAGE_SCHEMA,
        "capsule_id": capsule_id,
        "created_at": commit_date,
        "source_date_epoch": commit_epoch,
        "repository": REPOSITORY_URL,
        "git": {
            "commit_sha": commit,
            "tree_oid": tree_oid,
            "recovery_commit_sha": recovery_commit,
            "default_branch": "main",
            "bundle_ref_count": len(references),
            "bundle_refs": references,
            "production_parent_history_embedded": False,
            "production_tags_embedded": False,
            "production_tag_identity_count": 0,
            "production_tag_identities": [],
            "production_tag_identity_policy": (
                "Live Git tag refs are mutable outside the frozen source tree and are "
                "therefore deliberately excluded from the commit-bound capsule identity."
            ),
            "history_exclusion_reason": (
                "An immutable public DOI must not republish historical credential-bearing "
                "objects. The exact declared publication-baseline tree is preserved through a synthetic root "
                "recovery commit; mutable live tag refs are deliberately outside the commit-bound identity."
            ),
        },
        "tracked_files": {
            "file_count": tracked["file_count"],
            "inventory_sha256": tracked["inventory_sha256"],
        },
        "record_chain": latest_record_identity(root, commit, tracked),
        "recovery_checkpoints": checkpoint_inventory(root, commit),
        "secret_scan": secret_scan,
        "external_assets": external_asset_summary(root, commit),
        "published_file_names": list(PUBLISHED_FILE_NAMES),
        "files": [
            {
                "name": name,
                "bytes": (output_dir / name).stat().st_size,
                "sha256": sha256(output_dir / name),
            }
            for name in MANIFEST_HASHED_NAMES
        ],
        "scope": {
            "git_tracked_repository_embedded": True,
            "main_history_and_tags_embedded": False,
            "exact_publication_baseline_tree_embedded": True,
            "live_main_equivalence_claimed": False,
            "cloneable_single_root_recovery_bundle_embedded": True,
            "production_commit_identity_recorded": True,
            "production_tag_identities_recorded": False,
            "source_snapshot_embedded": True,
            "github_required_for_repository_recovery": False,
            "network_required_after_capsule_download": False,
            "external_large_binary_annex_embedded": False,
            "zenodo_only_restores_complete_git_tracked_repository": True,
            "coverage_scope": "exact_immutable_publication_baseline",
            "zenodo_only_restores_all_external_large_payload_bytes": False,
        },
        "rights_boundary": {
            "schema": RIGHTS_BOUNDARY_VERSION,
            "license_identifier": ZENODO_LICENSE_ID,
            "publicly_readable_for_preservation": True,
            "deposit_grants_no_new_reuse_rights": True,
            "components_retain_their_existing_rights": True,
            "third_party_rights_are_not_transferred": True,
            "publisher_grants_no_rights_it_does_not_possess": True,
        },
        "boundary": {
            "capsule_is_non_authoritative_mirror": True,
            "capsule_is_not_amendment": True,
            "capsule_is_not_attestation": True,
            "capsule_is_not_governance": True,
            "capsule_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
        "package_identity_sha256": None,
    }
    manifest["package_identity_sha256"] = manifest_identity(manifest)
    write_json(output_dir / "preservation-manifest.json", manifest)
    verified = verify_local_package(output_dir)
    github_output("capsule_id", capsule_id)
    github_output("capsule_dir", str(output_dir))
    github_output("git_commit_sha", commit)
    github_output("git_tree_oid", tree_oid)
    github_output("recovery_commit_sha", recovery_commit)
    github_output("package_identity_sha256", verified["package_identity_sha256"])
    print(
        f"capsule_id={capsule_id} commit={commit} files={tracked['file_count']} "
        f"package_identity_sha256={verified['package_identity_sha256']}"
    )
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    build(Path(args.repository_root), Path(args.output_dir), args.commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
