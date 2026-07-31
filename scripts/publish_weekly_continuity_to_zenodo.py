#!/usr/bin/env python3
"""Publish a weekly continuity package to a dedicated Zenodo dataset series.

This direct API publisher is intentionally separate from the repository's
GitHub/Zenodo integration, which is already used for a research preprint. It
creates one dataset concept on the first successful run and a new immutable
version for each later archive.
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "record-chain" / "weekly-continuity-zenodo-state.json"
DEFAULT_API = "https://zenodo.org/api"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksums(deposit_dir: Path) -> None:
    checksum_path = deposit_dir / "checksums.sha256"
    if not checksum_path.is_file():
        raise SystemExit("deposit checksums.sha256 is missing")
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        path = deposit_dir / name
        if not path.is_file() or sha256(path) != expected:
            raise SystemExit(f"deposit checksum mismatch: {name}")


class ZenodoClient:
    def __init__(self, token: str, api_base: str) -> None:
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required for publication")
        self.token = token
        self.api_base = api_base.rstrip("/")

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        if url.startswith("/"):
            url = self.api_base + url
        body = data
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "User-Agent": "trinity-weekly-continuity/1.0",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        if body is not None:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Zenodo API {method} failed with HTTP {exc.code}: {detail}") from exc
        except OSError as exc:
            raise SystemExit(f"Zenodo API {method} failed: {exc}") from exc
        if not raw:
            return {}
        parsed = json.loads(raw.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise SystemExit("Zenodo API returned a non-object response")
        return parsed

    def delete(self, url: str) -> None:
        self.request("DELETE", url)


def deposition_id(record: dict[str, Any]) -> int:
    value = record.get("id")
    if not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise SystemExit("Zenodo response is missing deposition id") from exc
    return value


def new_or_version_draft(client: ZenodoClient, state: dict[str, Any]) -> dict[str, Any]:
    latest_id = state.get("latest_deposition_id")
    if latest_id is None:
        return client.request("POST", "/deposit/depositions", payload={})
    response = client.request(
        "POST",
        f"/deposit/depositions/{int(latest_id)}/actions/newversion",
        payload={},
    )
    latest_draft = response.get("links", {}).get("latest_draft")
    if not isinstance(latest_draft, str) or not latest_draft:
        raise SystemExit("Zenodo new-version response is missing links.latest_draft")
    return client.request("GET", latest_draft)


def clear_draft_files(client: ZenodoClient, draft: dict[str, Any]) -> None:
    files = draft.get("files")
    if not isinstance(files, list):
        return
    for item in files:
        if not isinstance(item, dict):
            continue
        self_url = item.get("links", {}).get("self")
        if isinstance(self_url, str) and self_url:
            client.delete(self_url)


def upload_files(client: ZenodoClient, draft: dict[str, Any], deposit_dir: Path) -> None:
    bucket = draft.get("links", {}).get("bucket")
    if not isinstance(bucket, str) or not bucket:
        raise SystemExit("Zenodo draft is missing upload bucket")
    names = [
        "weekly-continuity-bundle.json",
        "archive-manifest.json",
        "deposit-manifest.json",
        "checksums.sha256",
        "README.txt",
    ]
    for name in names:
        path = deposit_dir / name
        if not path.is_file():
            raise SystemExit(f"deposit file is missing: {name}")
        url = bucket.rstrip("/") + "/" + urllib.parse.quote(name)
        client.request(
            "PUT",
            url,
            data=path.read_bytes(),
            content_type="application/octet-stream",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument("--api-base", default=os.environ.get("ZENODO_API_BASE", DEFAULT_API))
    args = parser.parse_args()

    deposit_dir = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit_dir.parents:
        raise SystemExit("deposit directory must be inside the repository")
    verify_checksums(deposit_dir)
    package_manifest = read_json(deposit_dir / "deposit-manifest.json")
    archive_id = str(package_manifest.get("archive_id") or "")
    if not archive_id:
        raise SystemExit("deposit manifest is missing archive_id")

    state_path = (ROOT / args.state).resolve()
    state = read_json(state_path) if state_path.is_file() else {}
    if state.get("latest_archive_id") == archive_id and state.get("latest_doi"):
        print(f"Zenodo continuity version already published: {state['latest_doi']}")
        return 0

    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = ZenodoClient(token, args.api_base)
    draft = new_or_version_draft(client, state)
    clear_draft_files(client, draft)
    upload_files(client, draft, deposit_dir)

    metadata = read_json(deposit_dir / "zenodo-metadata.json")
    draft_id = deposition_id(draft)
    updated = client.request(
        "PUT",
        f"/deposit/depositions/{draft_id}",
        payload={"metadata": metadata},
    )
    published = client.request(
        "POST",
        f"/deposit/depositions/{deposition_id(updated)}/actions/publish",
        payload={},
    )

    next_state = {
        "schema": "trinityaccord.weekly-continuity-zenodo-state.v1",
        "latest_archive_id": archive_id,
        "latest_deposition_id": deposition_id(published),
        "latest_record_id": published.get("record_id"),
        "latest_doi": published.get("doi"),
        "latest_doi_url": published.get("doi_url"),
        "concept_record_id": published.get("conceptrecid") or state.get("concept_record_id"),
        "concept_doi": published.get("conceptdoi") or state.get("concept_doi"),
        "api_base": args.api_base,
        "source_deposit_dir": str(deposit_dir.relative_to(ROOT)),
    }
    if not next_state["latest_doi"]:
        raise SystemExit("Zenodo published response did not include a DOI")
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
