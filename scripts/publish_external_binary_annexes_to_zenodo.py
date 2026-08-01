#!/usr/bin/env python3
"""Publish or reconcile Trinity Accord external-binary Zenodo annexes."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from external_binary_annex import (
    PUBLISHED_FILE_NAMES,
    STATE_SCHEMA,
    file_inventory,
    verify_local_package,
    write_json,
)
from publish_preservation_capsule_to_zenodo import (
    DEFAULT_API,
    ZenodoClient,
    clear_files,
    deposition_id,
    is_published,
    list_depositions,
    metadata,
    refresh,
)

ROOT = Path(__file__).resolve().parents[1]
RIGHTS_ACKNOWLEDGEMENT = "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED"


def curl_upload(url: str, path: Path, token: str) -> None:
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
            "5",
            "--retry-all-errors",
            "--header",
            f"Authorization: Bearer {token}",
            "--header",
            "Content-Type: application/octet-stream",
            "--upload-file",
            str(path),
            url,
        ],
        check=True,
    )


def curl_download(url: str, target: Path, token: str = "") -> None:
    command = [
        "curl",
        "--fail",
        "--location",
        "--silent",
        "--show-error",
        "--retry",
        "6",
        "--retry-delay",
        "5",
        "--retry-all-errors",
        "--output",
        str(target),
    ]
    if token:
        command.extend(["--header", f"Authorization: Bearer {token}"])
    command.append(url)
    subprocess.run(command, check=True)


def series_records(records: list[dict[str, Any]], title: str) -> list[dict[str, Any]]:
    return sorted(
        [item for item in records if metadata(item).get("title") == title],
        key=deposition_id,
    )


def version(record: dict[str, Any]) -> str:
    return str(metadata(record).get("version") or "")


def wait_for_empty_draft(client: ZenodoClient, draft_id: int) -> dict[str, Any]:
    for _attempt in range(60):
        value = refresh(client, {"id": draft_id})
        files = value.get("files")
        if not isinstance(files, list) or not files:
            return value
        time.sleep(2)
    raise SystemExit("Zenodo draft did not become empty after file deletion")


def draft_bucket(draft: dict[str, Any]) -> str:
    links = draft.get("links")
    value = links.get("bucket") if isinstance(links, dict) else None
    if not isinstance(value, str) or not value:
        raise SystemExit("Zenodo draft is missing upload bucket")
    return value.rstrip("/")


def verify_bucket_bytes(draft: dict[str, Any], package_dir: Path, token: str) -> None:
    bucket = draft_bucket(draft)
    local = file_inventory(package_dir)
    from external_binary_annex import hash_file

    with tempfile.TemporaryDirectory(prefix="trinity-annex-bucket-readback-") as temp_name:
        temp = Path(temp_name)
        for name in PUBLISHED_FILE_NAMES:
            target = temp / name
            curl_download(bucket + "/" + urllib.parse.quote(name), target, token)
            if target.stat().st_size != local[name]["bytes"]:
                raise SystemExit(f"Zenodo bucket size mismatch: {name}")
            if hash_file(target) != local[name]["sha256"]:
                raise SystemExit(f"Zenodo bucket SHA-256 mismatch: {name}")


def public_record(record_id: int, *, retries: int = 90) -> dict[str, Any]:
    url = f"https://zenodo.org/api/records/{record_id}"
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "trinity-external-binary-annex/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                value = json.loads(response.read().decode("utf-8"))
            if isinstance(value, dict):
                return value
        except urllib.error.HTTPError as exc:
            if exc.code not in {404, 409, 503}:
                detail = exc.read().decode("utf-8", errors="replace")
                raise SystemExit(
                    f"Zenodo public record lookup failed: HTTP {exc.code}: {detail[:1000]}"
                ) from exc
        if attempt + 1 < retries:
            time.sleep(4)
    raise SystemExit(f"Zenodo public record did not become available: {record_id}")


def public_file_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit("Zenodo public record has no files list")
    result: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("key") or item.get("filename") or "")
        if name:
            result[name] = item
    return result


def public_url(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    return str(links.get("self") or links.get("content") or links.get("download") or "")


def verify_public_record(record_id: int, package_dir: Path) -> dict[str, Any]:
    record = public_record(record_id)
    remote = public_file_map(record)
    if set(remote) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(
            f"Zenodo annex public file set mismatch: "
            f"missing={sorted(set(PUBLISHED_FILE_NAMES)-set(remote))} "
            f"unexpected={sorted(set(remote)-set(PUBLISHED_FILE_NAMES))}"
        )
    local = file_inventory(package_dir)
    from external_binary_annex import hash_file

    with tempfile.TemporaryDirectory(prefix="trinity-annex-public-readback-") as temp_name:
        temp = Path(temp_name)
        for name in PUBLISHED_FILE_NAMES:
            item = remote[name]
            value = item.get("size", item.get("filesize"))
            if int(value or -1) != local[name]["bytes"]:
                raise SystemExit(f"Zenodo public size mismatch: {name}")
            checksum = str(item.get("checksum") or "")
            if checksum and checksum.split(":", 1)[-1].lower() != local[name]["md5"]:
                raise SystemExit(f"Zenodo public MD5 mismatch: {name}")
            url = public_url(item)
            if not url:
                raise SystemExit(f"Zenodo public URL missing: {name}")
            target = temp / name
            curl_download(url, target)
            if target.stat().st_size != local[name]["bytes"]:
                raise SystemExit(f"Zenodo public downloaded size mismatch: {name}")
            if hash_file(target) != local[name]["sha256"]:
                raise SystemExit(f"Zenodo public downloaded SHA-256 mismatch: {name}")
    return record


def create_draft(client: ZenodoClient, record_metadata: dict[str, Any]) -> dict[str, Any]:
    value = client.request(
        "POST",
        "/deposit/depositions",
        payload={"metadata": record_metadata},
    )
    if not isinstance(value, dict):
        raise SystemExit("Zenodo draft creation returned a non-object")
    return value


def state_entry(record: dict[str, Any], package: dict[str, Any], api_base: str) -> dict[str, Any]:
    record_id = int(record.get("id") or record.get("record_id"))
    record_doi = str(record.get("doi") or metadata(record).get("doi") or "")
    if not record_doi:
        raise SystemExit("published annex record lacks DOI")
    return {
        "status": "published",
        "annex_type": package["annex_type"],
        "annex_id": package["annex_id"],
        "record_id": record_id,
        "doi": record_doi,
        "doi_url": f"https://doi.org/{record_doi}",
        "concept_record_id": record.get("conceptrecid"),
        "concept_doi": str(record.get("conceptdoi") or ""),
        "package_identity_sha256": package["package_identity_sha256"],
        "asset_count": package["asset_count"],
        "payload_bytes": package["payload_bytes"],
        "files": package["inventory"],
        "api_base": api_base,
        "public_download_verification": "passed",
        "public_cold_restore": "pending",
    }


def publish_one(
    client: ZenodoClient,
    token: str,
    package_dir: Path,
    api_base: str,
) -> dict[str, Any]:
    package = verify_local_package(package_dir)
    title = str(package["metadata"]["title"])
    annex_id = str(package["annex_id"])
    records = series_records(list_depositions(client), title)
    same = [item for item in records if version(item) == annex_id]
    published = [item for item in same if is_published(item)]
    drafts = [item for item in same if not is_published(item)]
    if len(published) > 1 or len(drafts) > 1:
        raise SystemExit(f"duplicate Zenodo annex version: {annex_id}")
    if published:
        record_id = int(published[0].get("record_id") or deposition_id(published[0]))
        public = verify_public_record(record_id, package_dir)
        return state_entry(public, package, api_base)

    draft = refresh(client, drafts[0]) if drafts else create_draft(client, package["metadata"])
    draft_id = deposition_id(draft)
    updated = client.request(
        "PUT",
        f"/deposit/depositions/{draft_id}",
        payload={"metadata": package["metadata"]},
    )
    if not isinstance(updated, dict):
        raise SystemExit("Zenodo annex metadata update returned a non-object")
    draft = refresh(client, updated)
    clear_files(client, draft)
    draft = wait_for_empty_draft(client, draft_id)
    bucket = draft_bucket(draft)
    for name in PUBLISHED_FILE_NAMES:
        curl_upload(
            bucket + "/" + urllib.parse.quote(name),
            package_dir / name,
            token,
        )
    draft = refresh(client, {"id": draft_id})
    verify_bucket_bytes(draft, package_dir, token)
    published_response = client.request(
        "POST",
        f"/deposit/depositions/{draft_id}/actions/publish",
        payload={},
    )
    if not isinstance(published_response, dict):
        raise SystemExit("Zenodo annex publish returned a non-object")
    record_id = int(
        published_response.get("record_id")
        or published_response.get("id")
        or draft_id
    )
    public = verify_public_record(record_id, package_dir)
    return state_entry(public, package, api_base)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-package-dir", required=True)
    parser.add_argument("--nft-package-dir", required=True)
    parser.add_argument(
        "--state",
        default="preservation/external-binary-annex-state.json",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("ZENODO_API_BASE", DEFAULT_API),
    )
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.environ.get("EXTERNAL_BINARY_ANNEX_RIGHTS_ACK", ""),
    )
    args = parser.parse_args()
    if args.rights_boundary_ack != RIGHTS_ACKNOWLEDGEMENT:
        raise SystemExit("external binary annex publication requires the exact rights acknowledgement")
    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = ZenodoClient(token, args.api_base)
    evidence = publish_one(
        client,
        token,
        Path(args.evidence_package_dir).resolve(),
        args.api_base,
    )
    nft = publish_one(
        client,
        token,
        Path(args.nft_package_dir).resolve(),
        args.api_base,
    )
    state = {
        "schema": STATE_SCHEMA,
        "publication_status": "published_pending_public_cold_restore",
        "core_repository_preservation_doi": "10.5281/zenodo.21739344",
        "rights_boundary_schema": "trinityaccord.external-binary-annex-rights.v1",
        "annexes": {
            "evidence": evidence,
            "nft": nft,
        },
        "all_named_release_assets_embedded": True,
        "deprecated_failed_nft_attempts_embedded": False,
        "external_binary_payload_recovery_requires_github": False,
    }
    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("annex state path must remain inside the repository")
    write_json(state_path, state)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"evidence_record_id={evidence['record_id']}\n")
            handle.write(f"evidence_doi={evidence['doi']}\n")
            handle.write(f"nft_record_id={nft['record_id']}\n")
            handle.write(f"nft_doi={nft['doi']}\n")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
