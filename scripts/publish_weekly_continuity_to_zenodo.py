#!/usr/bin/env python3
"""Publish and reconcile the dedicated Weekly Continuity Zenodo series.

Publication is deliberately fail-closed:

* all six package files are uploaded;
* Zenodo's size/checksum metadata and a full byte download are verified before
  the irreversible publish action and again afterwards;
* an existing draft or already-published archive is reconciled by archive ID
  and exact package identity, so a GitHub state-push failure cannot create a
  second DOI or concept on retry;
* a versioned mixed-rights acknowledgement is required explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from weekly_continuity_package import (
    PACKAGE_TITLE,
    PUBLISHED_FILE_NAMES,
    RIGHTS_BOUNDARY_VERSION,
    file_inventory,
    package_identity,
    verify_local_package,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "record-chain" / "weekly-continuity-zenodo-state.json"
DEFAULT_API = "https://zenodo.org/api"
RIGHTS_ACKNOWLEDGEMENT = "TRINITY_WEEKLY_CONTINUITY_RIGHTS_V1_APPROVED"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ZenodoClient:
    def __init__(self, token: str, api_base: str) -> None:
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required for publication")
        self.token = token
        self.api_base = api_base.rstrip("/")

    def _url(self, url: str) -> str:
        return self.api_base + url if url.startswith("/") else url

    def _headers(self, *, content_type: str | None = None) -> dict[str, str]:
        headers = {
            "User-Agent": "trinity-weekly-continuity/1.1",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        body = data
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self._url(url),
            data=body,
            method=method,
            headers=self._headers(content_type=content_type if body is not None else None),
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(
                f"Zenodo API {method} failed with HTTP {exc.code}: {detail[:2000]}"
            ) from exc
        except OSError as exc:
            raise SystemExit(f"Zenodo API {method} failed: {exc}") from exc
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SystemExit("Zenodo API returned non-JSON data") from exc

    def request_bytes(self, url: str) -> bytes:
        request = urllib.request.Request(
            self._url(url),
            method="GET",
            headers=self._headers(),
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            raise SystemExit(
                f"Zenodo file download failed with HTTP {exc.code}"
            ) from exc
        except OSError as exc:
            raise SystemExit(f"Zenodo file download failed: {exc}") from exc

    def delete(self, url: str) -> None:
        self.request("DELETE", url)


def deposition_id(record: dict[str, Any]) -> int:
    value = record.get("id")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SystemExit("Zenodo response is missing deposition id") from exc


def record_metadata(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def archive_id_from_record(record: dict[str, Any]) -> str:
    return str(record_metadata(record).get("version") or "")


def is_published(record: dict[str, Any]) -> bool:
    return (
        record.get("submitted") is True
        or str(record.get("state") or "").lower() == "done"
        or bool(record.get("doi") or record_metadata(record).get("doi"))
    )


def list_depositions(client: ZenodoClient) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in range(1, 101):
        query = urllib.parse.urlencode({"size": 100, "page": page, "sort": "mostrecent"})
        data = client.request("GET", f"/deposit/depositions?{query}")
        if not isinstance(data, list):
            raise SystemExit("Zenodo deposition listing returned a non-list response")
        page_records = [item for item in data if isinstance(item, dict)]
        records.extend(page_records)
        if len(page_records) < 100:
            break
    else:
        raise SystemExit("Zenodo deposition listing exceeded the bounded pagination limit")
    return records


def series_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = [
        record
        for record in records
        if record_metadata(record).get("title") == PACKAGE_TITLE
    ]
    return sorted(result, key=deposition_id)


def remote_file_name(item: dict[str, Any]) -> str:
    return str(item.get("filename") or item.get("key") or "")


def remote_file_size(item: dict[str, Any]) -> int | None:
    value = item.get("filesize")
    if value is None:
        value = item.get("size")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def remote_download_url(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    return str(links.get("download") or links.get("content") or "")


def verify_remote_files(
    client: ZenodoClient,
    record: dict[str, Any],
    deposit_dir: Path,
) -> dict[str, dict[str, Any]]:
    local = file_inventory(deposit_dir)
    remote_files = record.get("files")
    if not isinstance(remote_files, list):
        raise SystemExit("Zenodo record files list is missing")
    remote = {
        remote_file_name(item): item
        for item in remote_files
        if isinstance(item, dict) and remote_file_name(item)
    }
    if set(remote) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(
            "Zenodo remote file set mismatch: "
            f"missing={sorted(set(PUBLISHED_FILE_NAMES) - set(remote))} "
            f"unexpected={sorted(set(remote) - set(PUBLISHED_FILE_NAMES))}"
        )

    for name in PUBLISHED_FILE_NAMES:
        item = remote[name]
        if remote_file_size(item) != local[name]["bytes"]:
            raise SystemExit(f"Zenodo remote size mismatch: {name}")
        checksum = str(item.get("checksum") or "")
        normalized_checksum = checksum.split(":", 1)[-1].lower()
        if not checksum or normalized_checksum != local[name]["md5"]:
            raise SystemExit(f"Zenodo remote checksum mismatch: {name}")
        download = remote_download_url(item)
        if not download:
            raise SystemExit(f"Zenodo remote download link is missing: {name}")
        raw = client.request_bytes(download)
        if len(raw) != local[name]["bytes"]:
            raise SystemExit(f"Zenodo downloaded size mismatch: {name}")
        if hashlib.sha256(raw).hexdigest() != local[name]["sha256"]:
            raise SystemExit(f"Zenodo downloaded SHA-256 mismatch: {name}")
    return local


def refresh_deposition(client: ZenodoClient, record: dict[str, Any]) -> dict[str, Any]:
    refreshed = client.request("GET", f"/deposit/depositions/{deposition_id(record)}")
    if not isinstance(refreshed, dict):
        raise SystemExit("Zenodo deposition readback returned a non-object")
    return refreshed


def clear_draft_files(client: ZenodoClient, draft: dict[str, Any]) -> None:
    files = draft.get("files")
    if not isinstance(files, list):
        return
    for item in files:
        if not isinstance(item, dict):
            continue
        links = item.get("links")
        self_url = links.get("self") if isinstance(links, dict) else None
        if isinstance(self_url, str) and self_url:
            client.delete(self_url)


def upload_files(client: ZenodoClient, draft: dict[str, Any], deposit_dir: Path) -> None:
    links = draft.get("links")
    bucket = links.get("bucket") if isinstance(links, dict) else None
    if not isinstance(bucket, str) or not bucket:
        raise SystemExit("Zenodo draft is missing upload bucket")
    for name in PUBLISHED_FILE_NAMES:
        path = deposit_dir / name
        client.request(
            "PUT",
            bucket.rstrip("/") + "/" + urllib.parse.quote(name),
            data=path.read_bytes(),
            content_type="application/octet-stream",
        )


def create_version_draft(
    client: ZenodoClient,
    latest_published: dict[str, Any] | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    if latest_published is None:
        # Bind title/version in the creation request. If the response is lost
        # after Zenodo creates the deposition, the next run can still discover
        # and reconcile the draft instead of creating a duplicate concept.
        draft = client.request(
            "POST", "/deposit/depositions", payload={"metadata": metadata}
        )
        if not isinstance(draft, dict):
            raise SystemExit("Zenodo new-deposition response is not an object")
        return draft
    response = client.request(
        "POST",
        f"/deposit/depositions/{deposition_id(latest_published)}/actions/newversion",
        payload={},
    )
    if not isinstance(response, dict):
        raise SystemExit("Zenodo new-version response is not an object")
    links = response.get("links")
    latest_draft = links.get("latest_draft") if isinstance(links, dict) else None
    if not isinstance(latest_draft, str) or not latest_draft:
        raise SystemExit("Zenodo new-version response is missing links.latest_draft")
    draft = client.request("GET", latest_draft)
    if not isinstance(draft, dict):
        raise SystemExit("Zenodo latest draft response is not an object")
    return draft


def record_doi(record: dict[str, Any]) -> str:
    return str(record.get("doi") or record_metadata(record).get("doi") or "")


def record_doi_url(record: dict[str, Any]) -> str:
    links = record.get("links")
    link = links.get("doi") if isinstance(links, dict) else None
    doi = record_doi(record)
    return str(record.get("doi_url") or link or (f"https://doi.org/{doi}" if doi else ""))


def concept_doi(record: dict[str, Any]) -> str:
    return str(record.get("conceptdoi") or record_metadata(record).get("conceptdoi") or "")


def version_entry(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "archive_id": archive_id_from_record(record),
        "deposition_id": deposition_id(record),
        "record_id": record.get("record_id") or deposition_id(record),
        "doi": record_doi(record),
        "doi_url": record_doi_url(record),
    }


def build_state(
    *,
    published: dict[str, Any],
    package: dict[str, Any],
    api_base: str,
    deposit_dir: Path,
    known_series: Iterable[dict[str, Any]],
    old_state: dict[str, Any],
) -> dict[str, Any]:
    versions: dict[str, dict[str, Any]] = {}
    old_versions = old_state.get("versions")
    if isinstance(old_versions, list):
        for item in old_versions:
            if isinstance(item, dict) and item.get("archive_id"):
                versions[str(item["archive_id"])] = dict(item)
    for record in known_series:
        archive_id = archive_id_from_record(record)
        if archive_id and is_published(record):
            versions[archive_id] = version_entry(record)

    current = version_entry(published)
    current.update(
        {
            "package_identity_sha256": package["package_identity_sha256"],
            "files": package["inventory"],
        }
    )
    versions[package["archive_id"]] = current
    ordered_versions = sorted(
        versions.values(), key=lambda item: int(item.get("deposition_id") or 0)
    )
    doi = record_doi(published)
    if not doi:
        raise SystemExit("Zenodo published response did not include a DOI")
    return {
        "schema": "trinityaccord.weekly-continuity-zenodo-state.v2",
        "rights_boundary_schema": RIGHTS_BOUNDARY_VERSION,
        "latest_archive_id": package["archive_id"],
        "latest_deposition_id": deposition_id(published),
        "latest_record_id": published.get("record_id") or deposition_id(published),
        "latest_doi": doi,
        "latest_doi_url": record_doi_url(published),
        "concept_record_id": published.get("conceptrecid") or old_state.get("concept_record_id"),
        "concept_doi": concept_doi(published) or old_state.get("concept_doi"),
        "latest_package_identity_sha256": package["package_identity_sha256"],
        "latest_files": package["inventory"],
        "versions": ordered_versions,
        "api_base": api_base,
        "source_deposit_dir": str(deposit_dir.relative_to(ROOT)),
    }


def publish_or_reconcile(
    *,
    client: ZenodoClient,
    deposit_dir: Path,
    state: dict[str, Any],
    api_base: str,
) -> dict[str, Any]:
    package = verify_local_package(deposit_dir)
    records = series_records(list_depositions(client))
    same_archive = [
        record for record in records if archive_id_from_record(record) == package["archive_id"]
    ]
    same_published = [record for record in same_archive if is_published(record)]
    same_drafts = [record for record in same_archive if not is_published(record)]
    if len(same_published) > 1 or len(same_drafts) > 1:
        raise SystemExit(
            f"multiple Zenodo depositions already use archive_id {package['archive_id']}"
        )

    if same_published:
        published = refresh_deposition(client, same_published[0])
        verify_remote_files(client, published, deposit_dir)
        print(
            "ZENODO_RECONCILED_EXISTING_PUBLICATION "
            f"archive_id={package['archive_id']} doi={record_doi(published)}"
        )
        return build_state(
            published=published,
            package=package,
            api_base=api_base,
            deposit_dir=deposit_dir,
            known_series=records,
            old_state=state,
        )

    if same_drafts:
        draft = refresh_deposition(client, same_drafts[0])
        if is_published(draft):
            raise SystemExit("Zenodo draft changed to published during reconciliation")
    else:
        published_series = [record for record in records if is_published(record)]
        latest_published = published_series[-1] if published_series else None
        orphan_drafts = [record for record in records if not is_published(record)]
        if len(orphan_drafts) > 1:
            raise SystemExit("multiple unfinished Weekly Continuity drafts require reconciliation")
        if orphan_drafts:
            # A new-version draft initially inherits the prior version metadata.
            # Reuse that one bounded series draft after an interrupted run.
            draft = refresh_deposition(client, orphan_drafts[0])
        else:
            draft = create_version_draft(client, latest_published, package["metadata"])

    draft_id = deposition_id(draft)
    metadata = package["metadata"]
    updated = client.request(
        "PUT", f"/deposit/depositions/{draft_id}", payload={"metadata": metadata}
    )
    if not isinstance(updated, dict):
        raise SystemExit("Zenodo metadata update response is not an object")
    draft = refresh_deposition(client, updated)
    clear_draft_files(client, draft)
    draft = refresh_deposition(client, draft)
    upload_files(client, draft, deposit_dir)
    draft = refresh_deposition(client, draft)
    verify_remote_files(client, draft, deposit_dir)

    published = client.request(
        "POST",
        f"/deposit/depositions/{deposition_id(draft)}/actions/publish",
        payload={},
    )
    if not isinstance(published, dict):
        raise SystemExit("Zenodo publish response is not an object")
    published = refresh_deposition(client, published)
    verify_remote_files(client, published, deposit_dir)
    records = series_records(list_depositions(client))
    return build_state(
        published=published,
        package=package,
        api_base=api_base,
        deposit_dir=deposit_dir,
        known_series=records,
        old_state=state,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument("--api-base", default=os.environ.get("ZENODO_API_BASE", DEFAULT_API))
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.environ.get("WEEKLY_CONTINUITY_ZENODO_RIGHTS_ACK", ""),
    )
    args = parser.parse_args()

    deposit_dir = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit_dir.parents:
        raise SystemExit("deposit directory must be inside the repository")
    verify_local_package(deposit_dir)
    if args.rights_boundary_ack != RIGHTS_ACKNOWLEDGEMENT:
        raise SystemExit(
            "weekly continuity DOI publication is disabled until the versioned "
            "mixed-rights boundary is explicitly approved"
        )

    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("Zenodo state path must be inside the repository")
    state = read_json(state_path) if state_path.is_file() else {}
    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = ZenodoClient(token, args.api_base)
    next_state = publish_or_reconcile(
        client=client,
        deposit_dir=deposit_dir,
        state=state,
        api_base=args.api_base,
    )
    write_json(state_path, next_state)
    print(json.dumps(next_state, ensure_ascii=False, indent=2))

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"doi={next_state['latest_doi']}\n")
            handle.write(f"concept_doi={next_state.get('concept_doi') or ''}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
