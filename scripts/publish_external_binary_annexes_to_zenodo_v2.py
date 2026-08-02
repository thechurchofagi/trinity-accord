#!/usr/bin/env python3
"""Publish complete V2 annexes with public bytes and metadata verification."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any, Iterable

import external_binary_annex as package_module
import external_binary_annex_v2 as builder_v2
import publish_external_binary_annexes_to_zenodo as legacy
from publish_preservation_capsule_to_zenodo import (
    DEFAULT_API,
    ZenodoClient,
    clear_files,
    deposition_id,
    is_published,
    list_depositions,
    refresh,
)

ROOT = Path(__file__).resolve().parents[1]
RIGHTS_ACKNOWLEDGEMENT = "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED"


def _nested_identifier(value: Any, *path: str) -> str:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return str(current or "")


def _record_doi(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    return next(
        (
            value
            for value in (
                str(record.get("doi") or ""),
                str(metadata.get("doi") or ""),
                _nested_identifier(record, "pids", "doi", "identifier"),
            )
            if value
        ),
        "",
    )


def _concept_doi(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    return next(
        (
            value
            for value in (
                str(record.get("conceptdoi") or ""),
                str(metadata.get("conceptdoi") or ""),
                _nested_identifier(record, "parent", "pids", "doi", "identifier"),
            )
            if value
        ),
        "",
    )


def _concept_record_id(record: dict[str, Any]) -> int | None:
    for value in (record.get("conceptrecid"), _nested_identifier(record, "parent", "id")):
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _license_ids(metadata: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    legacy_license = metadata.get("license")
    if isinstance(legacy_license, str):
        result.add(legacy_license)
    elif isinstance(legacy_license, dict):
        value = legacy_license.get("id") or legacy_license.get("title")
        if value:
            result.add(str(value))
    rights = metadata.get("rights")
    if isinstance(rights, list):
        for item in rights:
            if not isinstance(item, dict):
                continue
            value = item.get("id") or item.get("identifier")
            if value:
                result.add(str(value))
    return result


def _creator_names(value: Any) -> list[str]:
    result: list[str] = []
    if not isinstance(value, list):
        return result
    for item in value:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not name and isinstance(item.get("person_or_org"), dict):
            name = item["person_or_org"].get("name")
        if name:
            result.append(str(name))
    return result


def _relation_id(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("id") or value.get("title") or ""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _related_pairs(value: Any) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    if not isinstance(value, list):
        return result
    for item in value:
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("identifier") or "")
        relation = _relation_id(item.get("relation"))
        if identifier and relation:
            result.add((identifier, relation))
    return result


def _public_access_is_open(record: dict[str, Any], metadata: dict[str, Any]) -> bool:
    if str(metadata.get("access_right") or record.get("access_right") or "") == "open":
        return True
    access = record.get("access")
    if not isinstance(access, dict):
        return False
    return (
        str(access.get("status") or "") == "open"
        or (
            str(access.get("record") or "") == "public"
            and str(access.get("files") or "") == "public"
        )
    )


def validate_public_metadata(record: dict[str, Any], expected: dict[str, Any]) -> None:
    observed = record.get("metadata")
    if not isinstance(observed, dict):
        raise SystemExit("Zenodo public record has no metadata object")
    for field in ("title", "version", "publication_date", "description", "notes"):
        if str(observed.get(field) or "") != str(expected.get(field) or ""):
            raise SystemExit(f"Zenodo public metadata mismatch: {field}")
    if not _public_access_is_open(record, observed):
        raise SystemExit("Zenodo public metadata mismatch: access_right")
    if str(expected.get("license") or "") not in _license_ids(observed):
        raise SystemExit("Zenodo public metadata mismatch: license")
    if _creator_names(observed.get("creators")) != _creator_names(expected.get("creators")):
        raise SystemExit("Zenodo public metadata mismatch: creators")
    if list(observed.get("keywords") or []) != list(expected.get("keywords") or []):
        raise SystemExit("Zenodo public metadata mismatch: keywords")
    expected_related = _related_pairs(expected.get("related_identifiers"))
    if not expected_related.issubset(_related_pairs(observed.get("related_identifiers"))):
        raise SystemExit("Zenodo public metadata mismatch: related_identifiers")


def _public_file_items(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = record.get("files")
    result: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        iterable: Iterable[tuple[str, Any]] = (
            (str(item.get("key") or item.get("filename") or ""), item)
            for item in raw
            if isinstance(item, dict)
        )
    elif isinstance(raw, dict):
        entries = raw.get("entries")
        if isinstance(entries, dict):
            iterable = (
                (str(key), item)
                for key, item in entries.items()
                if isinstance(item, dict)
            )
        elif isinstance(entries, list):
            iterable = (
                (str(item.get("key") or item.get("filename") or ""), item)
                for item in entries
                if isinstance(item, dict)
            )
        else:
            iterable = ()
    else:
        iterable = ()
    for fallback, item in iterable:
        name = str(item.get("key") or item.get("filename") or fallback)
        if not name:
            continue
        if name in result:
            raise SystemExit(f"duplicate Zenodo public file name: {name}")
        normalized = dict(item)
        normalized.setdefault("key", name)
        result[name] = normalized
    return result


def _item_checksum(item: dict[str, Any]) -> str:
    value = item.get("checksum")
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        for key in ("md5", "sha256"):
            candidate = value.get(key)
            if candidate:
                return f"{key}:{str(candidate).lower()}"
    return ""


def _public_url(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    return str(links.get("content") or links.get("download") or links.get("self") or "")


def verify_public_record_v2(
    record_id: int,
    package_dir: Path,
    package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = legacy.public_record(record_id)
    remote = _public_file_items(record)
    expected_names = set(package_module.PUBLISHED_FILE_NAMES)
    if set(remote) != expected_names:
        raise SystemExit(
            "Zenodo annex public file set mismatch: "
            f"missing={sorted(expected_names-set(remote))} "
            f"unexpected={sorted(set(remote)-expected_names)}"
        )
    local = package_module.file_inventory(package_dir)
    with tempfile.TemporaryDirectory(prefix="trinity-annex-v2-public-readback-") as temp_name:
        temp = Path(temp_name)
        for name in package_module.PUBLISHED_FILE_NAMES:
            item = remote[name]
            size = item.get("size", item.get("filesize"))
            if int(size or -1) != local[name]["bytes"]:
                raise SystemExit(f"Zenodo public size mismatch: {name}")
            checksum = _item_checksum(item)
            if checksum:
                algorithm, _, expected = checksum.partition(":")
                if algorithm == "md5" and expected != local[name]["md5"]:
                    raise SystemExit(f"Zenodo public MD5 mismatch: {name}")
                if algorithm == "sha256" and expected != local[name]["sha256"]:
                    raise SystemExit(f"Zenodo public SHA-256 metadata mismatch: {name}")
            url = _public_url(item)
            if not url:
                raise SystemExit(f"Zenodo public URL missing: {name}")
            target = temp / name
            legacy.curl_download(url, target)
            if target.stat().st_size != local[name]["bytes"]:
                raise SystemExit(f"Zenodo public downloaded size mismatch: {name}")
            if package_module.hash_file(target) != local[name]["sha256"]:
                raise SystemExit(f"Zenodo public downloaded SHA-256 mismatch: {name}")
    verified = package or package_module.verify_local_package(package_dir)
    validate_public_metadata(record, verified["metadata"])
    return record


def _state_entry_v2(
    record: dict[str, Any], package: dict[str, Any], api_base: str
) -> dict[str, Any]:
    record_id = int(record.get("id") or record.get("record_id"))
    doi = _record_doi(record)
    if not doi:
        raise SystemExit("published annex record lacks DOI")
    return {
        "status": "published",
        "annex_type": package["annex_type"],
        "annex_id": package["annex_id"],
        "record_id": record_id,
        "doi": doi,
        "doi_url": f"https://doi.org/{doi}",
        "concept_record_id": _concept_record_id(record),
        "concept_doi": _concept_doi(record),
        "package_identity_sha256": package["package_identity_sha256"],
        "asset_count": package["asset_count"],
        "payload_bytes": package["payload_bytes"],
        "files": package["inventory"],
        "api_base": api_base,
        "public_download_verification": "passed",
        "public_cold_restore": "pending",
    }


def _new_version_draft(client: ZenodoClient, previous: dict[str, Any]) -> dict[str, Any] | None:
    links = previous.get("links")
    newversion = links.get("newversion") if isinstance(links, dict) else None
    if not isinstance(newversion, str) or not newversion:
        return None
    response = client.request("POST", newversion, payload={})
    if not isinstance(response, dict):
        raise SystemExit("Zenodo new-version action returned a non-object")
    if response.get("id"):
        return refresh(client, response)
    response_links = response.get("links")
    latest_draft = response_links.get("latest_draft") if isinstance(response_links, dict) else None
    if isinstance(latest_draft, str) and latest_draft:
        value = client.request("GET", latest_draft)
        if isinstance(value, dict):
            return value
    raise SystemExit("Zenodo new-version action did not expose a draft")


def publish_one_v2(client: ZenodoClient, token: str, package_dir: Path, api_base: str) -> dict[str, Any]:
    package = package_module.verify_local_package(package_dir)
    source_commit = str(package["manifest"].get("source_commit_sha") or "")
    if len(source_commit) != 40:
        raise SystemExit("annex manifest lacks exact source_commit_sha")
    title = str(package["metadata"]["title"])
    annex_id = str(package["annex_id"])
    records = legacy.series_records(list_depositions(client), title)
    same = [item for item in records if legacy.version(item) == annex_id]
    published = [item for item in same if is_published(item)]
    drafts = [item for item in same if not is_published(item)]
    if len(published) > 1 or len(drafts) > 1:
        raise SystemExit(f"duplicate Zenodo annex version: {annex_id}")
    if published:
        record_id = int(published[0].get("record_id") or deposition_id(published[0]))
        public = verify_public_record_v2(record_id, package_dir, package)
        entry = _state_entry_v2(public, package, api_base)
        entry["source_commit_sha"] = source_commit
        entry["public_metadata_verification"] = "passed"
        return entry

    if drafts:
        draft = refresh(client, drafts[0])
    else:
        older_published = [item for item in records if is_published(item)]
        draft = _new_version_draft(client, older_published[-1]) if older_published else None
        if draft is None:
            draft = legacy.create_draft(client, package["metadata"])

    draft_id = deposition_id(draft)
    updated = client.request(
        "PUT", f"/deposit/depositions/{draft_id}", payload={"metadata": package["metadata"]}
    )
    if not isinstance(updated, dict):
        raise SystemExit("Zenodo annex metadata update returned a non-object")
    draft = refresh(client, updated)
    clear_files(client, draft)
    draft = legacy.wait_for_empty_draft(client, draft_id)
    bucket = legacy.draft_bucket(draft)
    for name in package_module.PUBLISHED_FILE_NAMES:
        legacy.curl_upload(bucket + "/" + urllib.parse.quote(name), package_dir / name, token)
    draft = refresh(client, {"id": draft_id})
    legacy.verify_bucket_bytes(draft, package_dir, token)
    published_response = client.request(
        "POST", f"/deposit/depositions/{draft_id}/actions/publish", payload={}
    )
    if not isinstance(published_response, dict):
        raise SystemExit("Zenodo annex publish returned a non-object")
    record_id = int(published_response.get("record_id") or published_response.get("id") or draft_id)
    public = verify_public_record_v2(record_id, package_dir, package)
    entry = _state_entry_v2(public, package, api_base)
    entry["source_commit_sha"] = source_commit
    entry["public_metadata_verification"] = "passed"
    return entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-package-dir", required=True)
    parser.add_argument("--nft-package-dir", required=True)
    parser.add_argument("--state", default="preservation/external-binary-annex-state.json")
    parser.add_argument("--api-base", default=os.environ.get("ZENODO_API_BASE", DEFAULT_API))
    parser.add_argument("--rights-boundary-ack", default=os.environ.get("EXTERNAL_BINARY_ANNEX_RIGHTS_ACK", ""))
    parser.add_argument("--source-commit", default=os.environ.get("TRINITY_PUBLICATION_SOURCE_SHA", ""))
    args = parser.parse_args()
    if args.rights_boundary_ack != RIGHTS_ACKNOWLEDGEMENT:
        raise SystemExit("external binary annex publication requires the exact rights acknowledgement")
    source_commit = builder_v2._valid_commit_sha(args.source_commit)
    builder_v2.activate_v2_specs()
    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = ZenodoClient(token, args.api_base)
    evidence = publish_one_v2(client, token, Path(args.evidence_package_dir).resolve(), args.api_base)
    nft = publish_one_v2(client, token, Path(args.nft_package_dir).resolve(), args.api_base)
    for entry in (evidence, nft):
        if entry["source_commit_sha"] != source_commit:
            raise SystemExit("annex source commit differs from the workflow source")
    state = {
        "schema": package_module.STATE_SCHEMA,
        "publication_status": "published_pending_public_cold_restore",
        "source_commit_sha": source_commit,
        "core_repository_preservation_doi": "10.5281/zenodo.21739344",
        "rights_boundary_schema": "trinityaccord.external-binary-annex-rights.v1",
        "annexes": {"evidence": evidence, "nft": nft},
        "all_named_release_assets_embedded": True,
        "release_asset_pagination_complete": True,
        "public_metadata_verification": "passed",
        "deprecated_failed_nft_attempts_embedded": False,
        "external_binary_payload_recovery_requires_github": False,
    }
    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("annex state path must remain inside the repository")
    package_module.write_json(state_path, state)
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
