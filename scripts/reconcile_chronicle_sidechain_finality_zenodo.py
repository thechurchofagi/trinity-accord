#!/usr/bin/env python3
"""Finish Chronicle sidechain Finality Zenodo publication from the public Records API.

This is the fail-closed recovery path for the narrow case where Zenodo accepts a
publish action but the legacy deposition file URLs briefly return 404 while the
published record is propagating. It never uploads or mutates Zenodo files.

The reconciler:
- verifies the exact local Finality deposit first;
- finds exactly one published Zenodo record for the requested version;
- waits for the public /api/records/<id> representation to expose the full file set;
- streams every public file back and checks size, MD5 metadata, and SHA-256 bytes;
- writes the same verified DOI state only after the public readback passes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import time
from typing import Any

import publish_chronicle_sidechain_to_zenodo as publisher

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "archive" / "chronicle-sidechain-finality-zenodo-state.json"
DEFAULT_SETTLE_TIMEOUT = 900
DEFAULT_SETTLE_POLL = 10


def public_record_id(rec: dict[str, Any]) -> int:
    for key in ("record_id", "recid", "id"):
        value = rec.get(key)
        if value not in (None, ""):
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    raise SystemExit("published Zenodo deposition missing public record id")


def public_download_url(item: dict[str, Any], *, name: str) -> str:
    links = item.get("links") if isinstance(item.get("links"), dict) else {}
    # Public Records API currently exposes file bytes as links.self; legacy
    # deposition responses may instead expose download/content.
    url = str(
        links.get("download")
        or links.get("content")
        or links.get("self")
        or ""
    )
    if not url:
        raise SystemExit(f"Zenodo public download link missing: {name}")
    return url


def wait_for_public_record(
    client: publisher.Client,
    published: dict[str, Any],
    *,
    expected_names: set[str],
    expected_version: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> dict[str, Any]:
    record_id = public_record_id(published)
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    last_error = "public record not queried"

    while True:
        attempt += 1
        try:
            record = client.request("GET", f"/records/{record_id}")
            if not isinstance(record, dict):
                raise SystemExit("Zenodo public record response invalid")
            if not publisher.is_published(record):
                raise SystemExit("Zenodo public record is not yet published")
            if publisher.version(record) != expected_version:
                raise SystemExit(
                    "Zenodo public record version mismatch: "
                    f"{publisher.version(record)} != {expected_version}"
                )
            remote = publisher.remote_files(record)
            if set(remote) != expected_names:
                missing = sorted(expected_names - set(remote))
                unexpected = sorted(set(remote) - expected_names)
                raise SystemExit(
                    f"Zenodo public record file set not settled "
                    f"missing={missing} unexpected={unexpected}"
                )
            client.log(
                "public_record_ready",
                record_id=record_id,
                attempt=attempt,
                files=len(remote),
                doi=publisher.doi(record),
            )
            return record
        except SystemExit as exc:
            last_error = str(exc)
            remaining = max(0, int(deadline - time.monotonic()))
            client.log(
                "public_record_wait",
                record_id=record_id,
                attempt=attempt,
                remaining_seconds=remaining,
                error=last_error[:500],
            )
            if time.monotonic() >= deadline:
                raise SystemExit(
                    "Zenodo published record did not become readable within "
                    f"{timeout_seconds}s: {last_error}"
                ) from exc
            time.sleep(min(poll_seconds, max(1, remaining)))


def verify_public_remote(
    client: publisher.Client,
    record: dict[str, Any],
    local: dict[str, dict[str, Any]],
) -> None:
    remote = publisher.remote_files(record)
    if set(remote) != set(local):
        raise SystemExit(
            "Zenodo public file set mismatch "
            f"missing={sorted(set(local) - set(remote))} "
            f"unexpected={sorted(set(remote) - set(local))}"
        )

    client.log(
        "public_manifest_verify_start",
        files=len(local),
        bytes=sum(int(row["bytes"]) for row in local.values()),
    )
    for name, expect in local.items():
        item = remote[name]
        if not publisher.remote_metadata_matches(item, expect):
            raise SystemExit(
                f"Zenodo public metadata mismatch {name}: "
                f"remote_size={item.get('filesize', item.get('size'))} "
                f"remote_checksum={item.get('checksum')} "
                f"expected_size={expect['bytes']} expected_md5={expect['md5']}"
            )
        client.verify_download(
            public_download_url(item, name=name),
            name=name,
            expect=expect,
            phase="public-post-publish",
        )
        client.log(
            "public_file_verified",
            name=name,
            bytes=expect["bytes"],
            sha256=expect["sha256"],
        )
    client.log("public_manifest_verify_ok", files=len(local))


def write_state(
    state_path: pathlib.Path,
    *,
    record: dict[str, Any],
    package: dict[str, Any],
    version_id: str,
    api_base: str,
) -> dict[str, Any]:
    record_doi = publisher.doi(record)
    concept = publisher.concept_doi(record)
    if not record_doi:
        raise SystemExit("published Zenodo public record missing DOI")
    if concept != "10.5281/zenodo.22012615":
        raise SystemExit(f"unexpected Zenodo Concept DOI: {concept}")

    state = {
        "schema": "trinity-accord/chronicle-sidechain-zenodo-state/v1",
        "updated_at": dt.datetime.now(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "latest_version": version_id,
        "source_release_tag": package["source_release_tag"],
        "source_commit_sha": package["source_commit_sha"],
        "package_identity_sha256": package["package_identity_sha256"],
        "deposition_id": public_record_id(record),
        "record_id": public_record_id(record),
        "doi": record_doi,
        "concept_doi": concept,
        "api_base": api_base,
        "remote_full_readback_sha256_verified": True,
        "readback_surface": "public-records-api",
    }
    publisher.write_json(state_path, state)
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument(
        "--api-base",
        default=os.getenv("ZENODO_API_BASE", publisher.DEFAULT_API),
    )
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.getenv("CHRONICLE_SIDECHAIN_ZENODO_RIGHTS_ACK", ""),
    )
    parser.add_argument(
        "--settle-timeout",
        type=int,
        default=int(os.getenv("ZENODO_PUBLISH_SETTLE_TIMEOUT_SECONDS", str(DEFAULT_SETTLE_TIMEOUT))),
    )
    parser.add_argument(
        "--settle-poll",
        type=int,
        default=int(os.getenv("ZENODO_PUBLISH_SETTLE_POLL_SECONDS", str(DEFAULT_SETTLE_POLL))),
    )
    args = parser.parse_args()

    if args.rights_boundary_ack != publisher.RIGHTS_ACK:
        raise SystemExit("Finality Zenodo rights acknowledgement mismatch")
    if args.settle_timeout < 30 or args.settle_poll < 1:
        raise SystemExit("invalid Zenodo publish settlement timing")

    deposit = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit.parents or not deposit.is_dir():
        raise SystemExit("deposit directory must exist inside repository")
    local = publisher.verify_local(deposit)
    package = local["package"]
    version_id = str(package.get("version") or "")
    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("state path must be inside repository")

    client = publisher.Client(
        os.getenv("ZENODO_ACCESS_TOKEN", "").strip(),
        args.api_base,
        deposit / "PUBLIC-RECONCILE-DEBUG.jsonl",
        upload_timeout=int(os.getenv("ZENODO_UPLOAD_TIMEOUT_SECONDS", "3600")),
        download_timeout=int(os.getenv("ZENODO_DOWNLOAD_TIMEOUT_SECONDS", "3600")),
        upload_retries=max(1, int(os.getenv("ZENODO_UPLOAD_RETRIES", "3"))),
        download_retries=max(1, int(os.getenv("ZENODO_DOWNLOAD_RETRIES", "3"))),
    )

    series = publisher.list_series(client)
    same = [row for row in series if publisher.version(row) == version_id]
    published = [row for row in same if publisher.is_published(row)]
    drafts = [row for row in same if not publisher.is_published(row)]
    if len(published) != 1:
        raise SystemExit(
            f"expected exactly one published Zenodo record for {version_id}; "
            f"published={len(published)} drafts={len(drafts)}"
        )

    record = wait_for_public_record(
        client,
        published[0],
        expected_names=set(local["inventory"]),
        expected_version=version_id,
        timeout_seconds=args.settle_timeout,
        poll_seconds=args.settle_poll,
    )
    verify_public_remote(client, record, local["inventory"])
    state = write_state(
        state_path,
        record=record,
        package=package,
        version_id=version_id,
        api_base=args.api_base,
    )

    print(
        "[FINALITY ZENODO PUBLIC RECONCILE PASS] "
        f"doi={state['doi']} concept={state['concept_doi']} record={state['record_id']}",
        flush=True,
    )
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(
                f"doi={state['doi']}\n"
                f"concept_doi={state['concept_doi']}\n"
                f"record_id={state['record_id']}\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
