#!/usr/bin/env python3
"""Verify that the canonical public Builder is downloadable and executable.

The check intentionally starts from the single public entrypoint file.  It
verifies the manifest binding, then executes ``--help`` in an otherwise empty
temporary directory so the entrypoint must bootstrap its pinned recovery layer
and core exactly as an external zero-clone agent would.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MANIFEST_PATH = "/api/record-chain-builder-bundles.v1.json"
BUILDER_PATH = "/downloads/record-chain-builder.mjs"
HELP_MARKER = "Zero-clone Record-Chain submission builder"


def _strict_object(raw: bytes, label: str) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    def reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    value = json.loads(
        raw.decode("utf-8"),
        parse_constant=reject_constant,
        object_pairs_hook=reject_pairs,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{label} root is not an object")
    return value


def _live_bytes(site: str, path: str, timeout: int) -> bytes:
    token = str(time.time_ns())
    url = urllib.parse.urljoin(site.rstrip("/") + "/", path.lstrip("/"))
    separator = "&" if "?" in url else "?"
    request = urllib.request.Request(
        f"{url}{separator}builder_smoke={token}",
        headers={
            "User-Agent": "TrinityCanonicalBuilderSmoke/1.0",
            "Accept": "application/json,text/javascript,application/javascript,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"{path} returned HTTP {response.status}")
        return response.read()


def _deployed_bytes(
    *, site: str | None, site_dir: Path | None, path: str, timeout: int
) -> bytes:
    if site_dir is not None:
        return (site_dir / path.lstrip("/")).read_bytes()
    if site is None:
        raise ValueError("site is required when site_dir is absent")
    return _live_bytes(site, path, timeout)


def verify_builder(
    *, site: str | None = None, site_dir: Path | None = None, timeout: int = 30
) -> list[str]:
    errors: list[str] = []
    try:
        manifest_raw = _deployed_bytes(
            site=site, site_dir=site_dir, path=MANIFEST_PATH, timeout=timeout
        )
        manifest = _strict_object(manifest_raw, "Builder manifest")
        canonical = manifest.get("canonical_builder")
        if not isinstance(canonical, dict):
            raise ValueError("canonical_builder is absent or not an object")
        expected_sha = canonical.get("sha256")
        expected_size = canonical.get("size_bytes")
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            raise ValueError("canonical builder SHA-256 is invalid")
        if not isinstance(expected_size, int) or expected_size <= 0:
            raise ValueError("canonical builder size is invalid")

        builder = _deployed_bytes(
            site=site, site_dir=site_dir, path=BUILDER_PATH, timeout=timeout
        )
        actual_sha = hashlib.sha256(builder).hexdigest()
        if len(builder) != expected_size:
            errors.append(
                f"Builder size mismatch: manifest={expected_size} downloaded={len(builder)}"
            )
        if actual_sha != expected_sha:
            errors.append(
                f"Builder SHA-256 mismatch: manifest={expected_sha} downloaded={actual_sha}"
            )
        if errors:
            return errors

        with tempfile.TemporaryDirectory(prefix="trinity-builder-smoke-") as temp:
            temp_path = Path(temp)
            entrypoint = temp_path / "record-chain-builder.mjs"
            entrypoint.write_bytes(builder)
            completed = subprocess.run(
                ["node", str(entrypoint), "--help"],
                cwd=temp_path,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=max(30, timeout * 3),
                check=False,
            )
            output = completed.stdout or ""
            if completed.returncode != 0:
                errors.append(
                    "single-file Builder execution failed with exit code "
                    f"{completed.returncode}: {output[-1200:]}"
                )
            elif HELP_MARKER not in output:
                errors.append("single-file Builder help output is missing the canonical marker")
    except Exception as exc:  # noqa: BLE001 - command diagnostics
        errors.append(f"canonical Builder verification failed: {type(exc).__name__}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--site")
    source.add_argument("--site-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    errors = verify_builder(site=args.site, site_dir=args.site_dir, timeout=args.timeout)
    if errors:
        print("FAIL: canonical public Builder smoke errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: canonical Builder download, manifest binding, and single-file execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
