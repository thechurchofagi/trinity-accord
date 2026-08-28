#!/usr/bin/env python3
"""Build and verify the Trinity Accord offline dependency capsule.

The capsule has two goals:
1. prove that the current Python verification stack can be installed without
   PyPI from a complete wheelhouse for the CI platform; and
2. preserve source distributions and npm registry tarballs so the dependency
   graph is not represented only by mutable package-index metadata.

This is a preservation aid, not a new authority layer.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "trinityaccord.offline-dependency-capsule.v1"
DEFAULT_LOCKS = (
    ("root", "package.json", "package-lock.json"),
    (
        "ethereum-verification",
        "evidence/ethereum-evidence-annex-v1/verification/package.json",
        "evidence/ethereum-evidence-annex-v1/verification/package-lock.json",
    ),
)
ALLOWED_NPM_PREFIX = "https://registry.npmjs.org/"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def requirement_lines(path: Path) -> list[str]:
    result: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            result.append(line)
    if not result:
        raise SystemExit(f"requirements file is empty: {path}")
    return result


def safe_name(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe path: {value!r}")
    return str(path)


def npm_tarball_entries(lock_path: Path) -> list[dict[str, str]]:
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, dict):
        raise SystemExit(f"package-lock has no packages map: {lock_path}")
    result: dict[tuple[str, str], dict[str, str]] = {}
    for package_path, metadata in packages.items():
        if not package_path or not isinstance(metadata, dict):
            continue
        resolved = metadata.get("resolved")
        integrity = metadata.get("integrity")
        version = metadata.get("version")
        if not isinstance(resolved, str) or not resolved:
            continue
        if not resolved.startswith(ALLOWED_NPM_PREFIX):
            raise SystemExit(
                f"refusing non-registry npm dependency URL in {lock_path}: {resolved}"
            )
        if not isinstance(integrity, str) or not integrity:
            raise SystemExit(f"npm dependency lacks SRI integrity in {lock_path}: {package_path}")
        entry = {
            "package_path": safe_name(str(package_path)),
            "version": str(version or ""),
            "resolved": resolved,
            "integrity": integrity,
        }
        result[(resolved, integrity)] = entry
    return sorted(result.values(), key=lambda item: (item["resolved"], item["integrity"]))


def verify_sri(raw: bytes, integrity: str) -> str:
    candidates: list[tuple[int, str, bytes]] = []
    rank = {"sha512": 3, "sha384": 2, "sha256": 1}
    for token in integrity.split():
        if "-" not in token:
            continue
        algorithm, encoded = token.split("-", 1)
        if algorithm not in rank:
            continue
        try:
            expected = base64.b64decode(encoded, validate=True)
        except Exception:
            continue
        candidates.append((rank[algorithm], algorithm, expected))
    if not candidates:
        raise SystemExit(f"unsupported npm SRI value: {integrity}")
    _priority, algorithm, expected = max(candidates)
    observed = hashlib.new(algorithm, raw).digest()
    if observed != expected:
        raise SystemExit(f"npm tarball SRI mismatch ({algorithm})")
    return algorithm


def download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Trinity-Accord-Preservation/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def copy_lock_inputs(root: Path, output: Path, label: str, package_json: str, lock_json: str) -> tuple[Path, Path]:
    target = output / "node" / label
    target.mkdir(parents=True, exist_ok=True)
    src_package = root / package_json
    src_lock = root / lock_json
    if not src_package.is_file() or not src_lock.is_file():
        raise SystemExit(f"missing Node dependency lock inputs: {package_json}, {lock_json}")
    dst_package = target / "package.json"
    dst_lock = target / "package-lock.json"
    shutil.copy2(src_package, dst_package)
    shutil.copy2(src_lock, dst_lock)
    return dst_package, dst_lock


def build(root: Path, output: Path, python: str) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    if output.exists():
        if any(output.iterdir()):
            raise SystemExit(f"output directory must be empty: {output}")
    else:
        output.mkdir(parents=True)

    requirements = root / "requirements-ci.txt"
    if not requirements.is_file():
        raise SystemExit("requirements-ci.txt is missing")

    python_dir = output / "python"
    wheels = python_dir / "wheels"
    sdists = python_dir / "direct-sdists"
    wheels.mkdir(parents=True)
    sdists.mkdir(parents=True)
    shutil.copy2(requirements, python_dir / "requirements-ci.txt")

    # Complete current-platform wheelhouse, including transitive dependencies.
    run(
        [
            python,
            "-m",
            "pip",
            "download",
            "--disable-pip-version-check",
            "--dest",
            str(wheels),
            "-r",
            str(requirements),
        ],
        cwd=root,
    )

    # Ask pip to record the exact resolved graph, then preserve a source
    # distribution for every resolved Python distribution. The wheelhouse is
    # the immediately executable offline layer; the full sdist set is the
    # longer-horizon portability layer.
    resolution = python_dir / "pip-resolution.json"
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--dry-run",
            "--ignore-installed",
            "--report",
            str(resolution),
            "-r",
            str(requirements),
        ],
        cwd=root,
    )
    report = json.loads(resolution.read_text(encoding="utf-8"))
    resolved: list[str] = []
    for item in report.get("install", []):
        metadata = item.get("metadata") if isinstance(item, dict) else None
        if not isinstance(metadata, dict):
            continue
        name = metadata.get("name")
        version = metadata.get("version")
        if isinstance(name, str) and name and isinstance(version, str) and version:
            resolved.append(f"{name}=={version}")
    resolved = sorted(set(resolved), key=str.lower)
    if not resolved:
        raise SystemExit("pip resolution report did not contain any distributions")
    for requirement in resolved:
        run(
            [
                python,
                "-m",
                "pip",
                "download",
                "--disable-pip-version-check",
                "--no-deps",
                "--no-binary=:all:",
                "--dest",
                str(sdists),
                requirement,
            ],
            cwd=root,
        )

    node_groups: list[dict[str, Any]] = []
    for label, package_json, lock_json in DEFAULT_LOCKS:
        _package_copy, lock_copy = copy_lock_inputs(
            root, output, label, package_json, lock_json
        )
        tarball_dir = lock_copy.parent / "packages"
        tarball_dir.mkdir()
        entries = npm_tarball_entries(lock_copy)
        saved: list[dict[str, Any]] = []
        for index, entry in enumerate(entries, start=1):
            raw = download(entry["resolved"])
            sri_algorithm = verify_sri(raw, entry["integrity"])
            basename = entry["resolved"].rsplit("/", 1)[-1] or f"package-{index}.tgz"
            filename = f"{index:04d}-{basename}"
            target = tarball_dir / filename
            target.write_bytes(raw)
            saved.append(
                {
                    **entry,
                    "file": f"node/{label}/packages/{filename}",
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "sri_algorithm_verified": sri_algorithm,
                }
            )
        node_groups.append(
            {
                "label": label,
                "source_package_json": package_json,
                "source_package_lock": lock_json,
                "tarball_count": len(saved),
                "tarballs": saved,
            }
        )

    readme = output / "README.txt"
    readme.write_text(
        """Trinity Accord Offline Dependency Capsule
=========================================

Purpose
-------
This capsule preserves the dependency material needed to reconstruct the
current verification environment without contacting PyPI or npm.

Python
------
python/wheels/ is a complete wheelhouse for the platform on which this capsule
was built. Install it with:

  python -m pip install --no-index --find-links python/wheels \
      -r python/requirements-ci.txt

python/direct-sdists/ additionally preserves source distributions for every resolved Python distribution. It is a portability aid for future
platforms, not a claim that arbitrary future ABIs can be rebuilt without any
toolchain.

Node.js
-------
Each node/<label>/ directory preserves package.json, package-lock.json and every
registry tarball referenced by that lock file. Tarballs are checked against npm
SRI metadata and again by SHA-256 in manifest.json. A current npm client can
seed a local cache from packages/*.tgz and run npm ci --offline.

Authority boundary
------------------
This capsule changes no Trinity Accord original, authority, attestation,
governance rule, or successor relation. It is a recovery/verification aid only.
""",
        encoding="utf-8",
    )

    payloads: list[dict[str, Any]] = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        rel = path.relative_to(output).as_posix()
        payloads.append(
            {"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        )

    manifest = {
        "schema": SCHEMA,
        "purpose": "offline verification dependency preservation",
        "authority_effect": "none",
        "python": {
            "requirements": "python/requirements-ci.txt",
            "wheelhouse": "python/wheels",
            "direct_source_distributions": "python/direct-sdists",
            "wheel_count": len(list(wheels.iterdir())),
            "resolved_distribution_count": len(resolved),
            "sdist_count": len(list(sdists.iterdir())),
        },
        "node": node_groups,
        "payload_file_count": len(payloads),
        "payloads": payloads,
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def verify(output: Path) -> dict[str, Any]:
    output = output.resolve()
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("offline dependency manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported offline dependency capsule schema")
    payloads = manifest.get("payloads")
    if not isinstance(payloads, list) or not payloads:
        raise SystemExit("offline dependency payload list is empty")
    seen: set[str] = set()
    for item in payloads:
        if not isinstance(item, dict):
            raise SystemExit("invalid dependency payload entry")
        rel = safe_name(str(item.get("path") or ""))
        if rel in seen:
            raise SystemExit(f"duplicate dependency payload: {rel}")
        seen.add(rel)
        path = output / rel
        if not path.is_file():
            raise SystemExit(f"missing dependency payload: {rel}")
        if item.get("bytes") != path.stat().st_size:
            raise SystemExit(f"dependency payload size mismatch: {rel}")
        if item.get("sha256") != sha256_file(path):
            raise SystemExit(f"dependency payload SHA-256 mismatch: {rel}")
    observed = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if observed != seen:
        raise SystemExit(
            "dependency capsule file-set mismatch: "
            f"missing={sorted(seen-observed)} unexpected={sorted(observed-seen)}"
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if not args.verify_only:
        build(Path(args.repository_root), output, args.python)
    manifest = verify(output)
    print(
        json.dumps(
            {
                "schema": manifest["schema"],
                "payload_file_count": manifest["payload_file_count"],
                "python_wheel_count": manifest["python"]["wheel_count"],
                "python_sdist_count": manifest["python"]["sdist_count"],
                "node_tarball_count": sum(
                    group["tarball_count"] for group in manifest["node"]
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
