#!/usr/bin/env python3
"""Compare the built/live Pages contract with the current repository bytes."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import check_deployment_freshness as legacy
from public_machine_deployment_contract import (
    DEPLOYMENT_BYTE_SURFACES,
    json_object_from_bytes,
    repo_bytes,
    sha256,
    validate_links_semantics,
    validate_well_known_semantics,
)

FORBIDDEN_CURRENT_GUIDANCE = (
    "/agent-submit",
    "/gateway/preflight",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
)


def deployed_bytes(
    site_dir: Path | None,
    site: str | None,
    path: str,
    token: str,
    timeout: int,
) -> bytes:
    if site_dir is not None:
        return legacy.read_site_dir(site_dir, path)
    assert site is not None
    return legacy.read_live(site, path, token, timeout)


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--site-dir", type=Path)
    source.add_argument("--site")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    source_material = b"".join(repo_bytes(path) for path in DEPLOYMENT_BYTE_SURFACES)
    source_material += b"".join(
        (legacy.ROOT / path).read_bytes() for path in legacy.STATIC_SOURCE_FILES
    )
    token = f"{sha256(source_material)[:16]}-{time.time_ns()}"
    errors: list[str] = []
    deployed: dict[str, bytes] = {}

    for path in DEPLOYMENT_BYTE_SURFACES:
        expected = repo_bytes(path)
        try:
            actual = deployed_bytes(args.site_dir, args.site, path, token, args.timeout)
        except Exception as exc:  # noqa: BLE001 - command-line diagnostics
            errors.append(f"{path}: failed to read deployed artifact: {exc}")
            continue
        deployed[path] = actual
        expected_sha = sha256(expected)
        actual_sha = sha256(actual)
        print(f"{path}: repo={expected_sha} deployed={actual_sha}")
        if expected != actual:
            errors.append(
                f"{path}: digest mismatch repo={expected_sha} deployed={actual_sha}"
            )

    for path in ("/llms.txt", "/ai.txt", "/api/agent-first-contact.json", "/api/agent-start.v2.json"):
        data = deployed.get(path)
        if data is None:
            continue
        text = data.decode("utf-8", errors="replace")
        for forbidden in FORBIDDEN_CURRENT_GUIDANCE:
            if forbidden in text:
                errors.append(f"{path} contains retired active route {forbidden!r}")

    links_bytes = deployed.get("/api/links.json")
    if links_bytes is not None:
        try:
            validate_links_semantics(
                "deployed", json_object_from_bytes(links_bytes, "deployed links.json"), errors
            )
        except ValueError as exc:
            errors.append(str(exc))

    well_known_bytes = deployed.get("/.well-known/trinity-accord.json")
    if well_known_bytes is not None:
        try:
            validate_well_known_semantics(
                "deployed",
                json_object_from_bytes(well_known_bytes, "deployed well-known"),
                errors,
            )
        except ValueError as exc:
            errors.append(str(exc))

    for path, markers in legacy.STATIC_PAGE_MARKERS.items():
        try:
            page_bytes = (
                legacy.read_static_site_dir(args.site_dir, path)
                if args.site_dir is not None
                else legacy.read_live(args.site, path, token, args.timeout)
            )
            page = page_bytes.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: failed to read static page: {exc}")
            continue
        for marker in markers:
            if marker not in page:
                errors.append(f"{path}: missing current static marker {marker!r}")
        if not any(marker not in page for marker in markers):
            print(f"{path}: current static markers present")

    if errors:
        print("FAIL: deployment freshness check errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "PASS: complete current machine bytes, active-route boundaries, and static "
        "reading surfaces match repository state"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
