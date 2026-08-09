#!/usr/bin/env python3
"""Publish or reconcile the repository preservation capsule Zenodo series."""
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

from preservation_capsule import (
    PACKAGE_TITLE,
    PUBLISHED_FILE_NAMES,
    RIGHTS_BOUNDARY_VERSION,
    file_inventory,
    verify_local_package,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "preservation" / "zenodo-state.json"
DEFAULT_API = "https://zenodo.org/api"
RIGHTS_ACKNOWLEDGEMENT = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


class ZenodoClient:
    def __init__(self, token: str, api_base: str) -> None:
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required for publication")
        self.token = token
        self.api_base = api_base.rstrip("/")

    def _url(self, value: str) -> str:
        return self.api_base + value if value.startswith("/") else value

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "trinity-repository-preservation/1.0",
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
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        request = urllib.request.Request(
            self._url(url),
            data=body,
            method=method,
            headers=self._headers(content_type if body is not None else None),
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
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
            self._url(url), method="GET", headers=self._headers()
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read()
        except (urllib.error.URLError, OSError) as exc:
            raise SystemExit(f"Zenodo file download failed: {exc}") from exc

    def delete(self, url: str) -> None:
        self.request("DELETE", url)


def deposition_id(record: dict[str, Any]) -> int:
    try:
        return int(record.get("id"))
    except (TypeError, ValueError) as exc:
        raise SystemExit("Zenodo response is missing deposition id") from exc


def metadata(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("metadata")
    return value if isinstance(value, dict) else {}


def capsule_id(record: dict[str, Any]) -> str:
    return str(metadata(record).get("version") or "")


def is_published(record: dict[str, Any]) -> bool:
    return (
        record.get("submitted") is True
        or str(record.get("state") or "").lower() == "done"
        or bool(record.get("doi") or metadata(record).get("doi"))
    )


def list_depositions(client: ZenodoClient) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for page in range(1, 101):
        query = urllib.parse.urlencode({"size": 100, "page": page, "sort": "mostrecent"})
        value = client.request("GET", f"/deposit/depositions?{query}")
        if not isinstance(value, list):
            raise SystemExit("Zenodo deposition listing returned a non-list response")
        records = [item for item in value if isinstance(item, dict)]
        result.extend(records)
        if len(records) < 100:
            return result
    raise SystemExit("Zenodo deposition listing exceeded the bounded pagination limit")


def series_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [item for item in records if metadata(item).get("title") == PACKAGE_TITLE],
        key=deposition_id,
    )


def remote_name(item: dict[str, Any]) -> str:
    return str(item.get("filename") or item.get("key") or "")


def remote_size(item: dict[str, Any]) -> int | None:
    value = item.get("filesize", item.get("size"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def remote_download(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    return str(links.get("download") or links.get("content") or "")


def verify_remote_files(
    client: ZenodoClient, record: dict[str, Any], capsule_dir: Path
) -> dict[str, dict[str, Any]]:
    local = file_inventory(capsule_dir)
    remote_files = record.get("files")
    if not isinstance(remote_files, list):
        raise SystemExit("Zenodo record files list is missing")
    remote = {
        remote_name(item): item
        for item in remote_files
        if isinstance(item, dict) and remote_name(item)
    }
    if set(remote) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(
            "Zenodo preservation file set mismatch: "
            f"missing={sorted(set(PUBLISHED_FILE_NAMES) - set(remote))} "
            f"unexpected={sorted(set(remote) - set(PUBLISHED_FILE_NAMES))}"
        )
    for name in PUBLISHED_FILE_NAMES:
        item = remote[name]
        if remote_size(item) != local[name]["bytes"]:
            raise SystemExit(f"Zenodo remote size mismatch: {name}")
        checksum = str(item.get("checksum") or "")
        if checksum.split(":", 1)[-1].lower() != local[name]["md5"]:
            raise SystemExit(f"Zenodo remote checksum mismatch: {name}")
        url = remote_download(item)
        if not url:
            raise SystemExit(f"Zenodo remote download URL is missing: {name}")
        raw = client.request_bytes(url)
        if len(raw) != local[name]["bytes"]:
            raise SystemExit(f"Zenodo downloaded size mismatch: {name}")
        if hashlib.sha256(raw).hexdigest() != local[name]["sha256"]:
            raise SystemExit(f"Zenodo downloaded SHA-256 mismatch: {name}")
    return local


def refresh(client: ZenodoClient, record: dict[str, Any]) -> dict[str, Any]:
    value = client.request("GET", f"/deposit/depositions/{deposition_id(record)}")
    if not isinstance(value, dict):
        raise SystemExit("Zenodo deposition readback returned a non-object")
    return value


def clear_files(client: ZenodoClient, draft: dict[str, Any]) -> None:
    files = draft.get("files")
    if not isinstance(files, list):
        return
    for item in files:
        links = item.get("links") if isinstance(item, dict) else None
        self_url = links.get("self") if isinstance(links, dict) else None
        if isinstance(self_url, str) and self_url:
            client.delete(self_url)


def upload_files(client: ZenodoClient, draft: dict[str, Any], capsule_dir: Path) -> None:
    links = draft.get("links")
    bucket = links.get("bucket") if isinstance(links, dict) else None
    if not isinstance(bucket, str) or not bucket:
        raise SystemExit("Zenodo draft is missing upload bucket")
    for name in PUBLISHED_FILE_NAMES:
        client.request(
            "PUT",
            bucket.rstrip("/") + "/" + urllib.parse.quote(name),
            data=(capsule_dir / name).read_bytes(),
            content_type="application/octet-stream",
        )


def create_draft(
    client: ZenodoClient,
    latest_published: dict[str, Any] | None,
    record_metadata: dict[str, Any],
) -> dict[str, Any]:
    if latest_published is None:
        value = client.request(
            "POST", "/deposit/depositions", payload={"metadata": record_metadata}
        )
    else:
        response = client.request(
            "POST",
            f"/deposit/depositions/{deposition_id(latest_published)}/actions/newversion",
            payload={},
        )
        links = response.get("links") if isinstance(response, dict) else None
        latest_draft = links.get("latest_draft") if isinstance(links, dict) else None
        if not isinstance(latest_draft, str) or not latest_draft:
            raise SystemExit("Zenodo new-version response is missing latest_draft")
        value = client.request("GET", latest_draft)
    if not isinstance(value, dict):
        raise SystemExit("Zenodo draft response is not an object")
    return value


def doi(record: dict[str, Any]) -> str:
    return str(record.get("doi") or metadata(record).get("doi") or "")


def concept_doi(record: dict[str, Any]) -> str:
    return str(record.get("conceptdoi") or metadata(record).get("conceptdoi") or "")


def concept_record_id(record: dict[str, Any]) -> int | None:
    value = record.get("conceptrecid")
    if value in (None, ""):
        value = metadata(record).get("conceptrecid")
    if value in (None, ""):
        parent = record.get("parent")
        if isinstance(parent, dict):
            value = parent.get("id")
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError) as exc:
        raise SystemExit("Zenodo response has an invalid concept record id") from exc


def require_concept_series(
    record: dict[str, Any], expected_doi: str, expected_record_id: int
) -> None:
    observed_doi = concept_doi(record)
    observed_record_id = concept_record_id(record)
    if not observed_doi and observed_record_id is None:
        raise SystemExit("Zenodo record lacks a fail-closed Concept DOI identity")
    if observed_doi and observed_doi != expected_doi:
        raise SystemExit(
            f"Zenodo record belongs to a different Concept DOI: {observed_doi!r}"
        )
    if observed_record_id is not None and observed_record_id != expected_record_id:
        raise SystemExit(
            "Zenodo record belongs to a different concept record id: "
            f"{observed_record_id!r}"
        )


def doi_url(record: dict[str, Any]) -> str:
    value = doi(record)
    links = record.get("links")
    link = links.get("doi") if isinstance(links, dict) else None
    return str(record.get("doi_url") or link or (f"https://doi.org/{value}" if value else ""))


def version_entry(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "capsule_id": capsule_id(record),
        "deposition_id": deposition_id(record),
        "record_id": record.get("record_id") or deposition_id(record),
        "doi": doi(record),
        "doi_url": doi_url(record),
    }


def build_state(
    published: dict[str, Any],
    package: dict[str, Any],
    api_base: str,
    known_series: Iterable[dict[str, Any]],
    old_state: dict[str, Any],
) -> dict[str, Any]:
    versions: dict[str, dict[str, Any]] = {}
    for item in old_state.get("versions", []):
        if isinstance(item, dict) and item.get("capsule_id"):
            versions[str(item["capsule_id"])] = dict(item)
    for record in known_series:
        if capsule_id(record) and is_published(record):
            key = capsule_id(record)
            # Remote history supplies current DOI/deposition coordinates, while
            # the checked-in state may carry richer verified Git and file
            # identities that Zenodo cannot reconstruct.  Never replace those
            # rich fields with a minimal remote entry on a later publication.
            merged = dict(versions.get(key, {}))
            merged.update(version_entry(record))
            versions[key] = merged
    current = version_entry(published)
    current.update(
        {
            "git_commit_sha": package["git_commit_sha"],
            "git_tree_oid": package["git_tree_oid"],
            "package_identity_sha256": package["package_identity_sha256"],
            "files": package["inventory"],
        }
    )
    versions[package["capsule_id"]] = current
    current_doi = doi(published)
    if not current_doi:
        raise SystemExit("published Zenodo capsule response lacks DOI")
    return {
        "schema": "trinityaccord.repository-preservation-zenodo-state.v1",
        "publication_status": "published",
        "rights_boundary_schema": RIGHTS_BOUNDARY_VERSION,
        "latest_capsule_id": package["capsule_id"],
        "latest_git_commit_sha": package["git_commit_sha"],
        "latest_git_tree_oid": package["git_tree_oid"],
        "latest_record_id": published.get("record_id") or deposition_id(published),
        "latest_doi": current_doi,
        "latest_doi_url": doi_url(published),
        "concept_record_id": published.get("conceptrecid") or old_state.get("concept_record_id"),
        "concept_doi": concept_doi(published) or old_state.get("concept_doi"),
        "latest_package_identity_sha256": package["package_identity_sha256"],
        "versions": sorted(
            versions.values(), key=lambda item: int(item.get("deposition_id") or 0)
        ),
        "api_base": api_base,
        "github_required_for_repository_recovery": False,
        "external_large_binary_annex_embedded": False,
    }


def publish_or_reconcile(
    client: ZenodoClient,
    capsule_dir: Path,
    state: dict[str, Any],
    api_base: str,
) -> dict[str, Any]:
    package = verify_local_package(capsule_dir)
    records = series_records(list_depositions(client))
    same = [item for item in records if capsule_id(item) == package["capsule_id"]]
    published_matches = [item for item in same if is_published(item)]
    draft_matches = [item for item in same if not is_published(item)]
    if len(published_matches) > 1 or len(draft_matches) > 1:
        raise SystemExit(f"duplicate Zenodo capsule id: {package['capsule_id']}")
    if published_matches:
        published = refresh(client, published_matches[0])
        verify_remote_files(client, published, capsule_dir)
        return build_state(published, package, api_base, records, state)

    if draft_matches:
        draft = refresh(client, draft_matches[0])
    else:
        published_series = [item for item in records if is_published(item)]
        orphan_drafts = [item for item in records if not is_published(item)]
        if len(orphan_drafts) > 1:
            raise SystemExit("multiple unfinished preservation drafts require reconciliation")
        if orphan_drafts:
            draft = refresh(client, orphan_drafts[0])
        else:
            draft = create_draft(
                client,
                published_series[-1] if published_series else None,
                package["metadata"],
            )

    draft_id = deposition_id(draft)
    updated = client.request(
        "PUT", f"/deposit/depositions/{draft_id}", payload={"metadata": package["metadata"]}
    )
    if not isinstance(updated, dict):
        raise SystemExit("Zenodo metadata update response is not an object")
    draft = refresh(client, updated)
    clear_files(client, draft)
    draft = refresh(client, draft)
    upload_files(client, draft, capsule_dir)
    draft = refresh(client, draft)
    verify_remote_files(client, draft, capsule_dir)
    published = client.request(
        "POST", f"/deposit/depositions/{draft_id}/actions/publish", payload={}
    )
    if not isinstance(published, dict):
        raise SystemExit("Zenodo publish response is not an object")
    published = refresh(client, published)
    verify_remote_files(client, published, capsule_dir)
    records = series_records(list_depositions(client))
    return build_state(published, package, api_base, records, state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capsule-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument("--api-base", default=os.environ.get("ZENODO_API_BASE", DEFAULT_API))
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.environ.get("PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK", ""),
    )
    args = parser.parse_args()
    if args.rights_boundary_ack != RIGHTS_ACKNOWLEDGEMENT:
        raise SystemExit(
            "repository preservation DOI publication requires the exact versioned rights acknowledgement"
        )
    capsule_dir = Path(args.capsule_dir).resolve()
    verify_local_package(capsule_dir)
    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("preservation Zenodo state must remain inside the repository")
    old_state = strict_json(state_path) if state_path.is_file() else {}
    client = ZenodoClient(os.environ.get("ZENODO_ACCESS_TOKEN", "").strip(), args.api_base)
    next_state = publish_or_reconcile(client, capsule_dir, old_state, args.api_base)
    write_json(state_path, next_state)
    print(json.dumps(next_state, ensure_ascii=False, indent=2))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"doi={next_state['latest_doi']}\n")
            handle.write(f"record_id={next_state['latest_record_id']}\n")
            handle.write(f"concept_doi={next_state.get('concept_doi') or ''}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
