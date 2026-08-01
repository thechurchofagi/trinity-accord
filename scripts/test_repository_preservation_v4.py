#!/usr/bin/env python3
"""Regression tests for fresh-draft Zenodo publication V4."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_preservation_capsule_to_zenodo_v4 as v4  # noqa: E402


class FakeClient:
    def __init__(self) -> None:
        self.events: list[tuple[str, Any]] = []

    def delete(self, url: str) -> None:
        self.events.append(("delete", url))

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        del data, content_type
        self.events.append((method, (url, payload)))
        if method == "PUT":
            return {"id": 300, "metadata": {"title": "capsule"}, "files": []}
        if method == "POST" and url.endswith("/actions/publish"):
            return {
                "id": 300,
                "record_id": 300,
                "submitted": True,
                "state": "done",
                "doi": "10.0000/example",
                "metadata": {"title": "capsule", "version": "repository-test"},
                "files": [],
            }
        raise AssertionError((method, url, payload))


def draft(record_id: int) -> dict[str, Any]:
    return {
        "id": record_id,
        "submitted": False,
        "state": "inprogress",
        "metadata": {"title": v4.publisher.PACKAGE_TITLE, "version": "repository-test"},
    }


def published(record_id: int) -> dict[str, Any]:
    return {
        "id": record_id,
        "record_id": record_id,
        "submitted": True,
        "state": "done",
        "doi": "10.0000/published",
        "metadata": {"title": v4.publisher.PACKAGE_TITLE, "version": "repository-old"},
    }


def test_delete_unpublished_only_and_wait() -> None:
    client = FakeClient()
    stale = draft(v4.STALE_DRAFT_ID)
    stable = published(10)
    listings = [[stable, stale], [stable]]
    original_list = v4.publisher.list_depositions
    original_sleep = v4.time.sleep
    v4.publisher.list_depositions = lambda _client: listings.pop(0)
    v4.time.sleep = lambda _seconds: None
    try:
        deleted = v4.delete_unpublished_series_drafts(client, [stable, stale], attempts=2)
    finally:
        v4.publisher.list_depositions = original_list
        v4.time.sleep = original_sleep
    assert deleted == [v4.STALE_DRAFT_ID]
    assert client.events == [
        ("delete", f"/deposit/depositions/{v4.STALE_DRAFT_ID}")
    ]


def test_fresh_draft_is_created_after_stale_deletion() -> None:
    client = FakeClient()
    stale = draft(v4.STALE_DRAFT_ID)
    fresh = {
        "id": 300,
        "submitted": False,
        "state": "inprogress",
        "metadata": {"title": v4.publisher.PACKAGE_TITLE, "version": "repository-test"},
        "files": [],
        "links": {"bucket": "https://zenodo.org/api/files/new-bucket"},
    }
    published_fresh = {
        **fresh,
        "submitted": True,
        "state": "done",
        "record_id": 300,
        "doi": "10.0000/example",
    }
    package = {
        "capsule_id": "repository-test",
        "metadata": {
            "title": v4.publisher.PACKAGE_TITLE,
            "version": "repository-test",
        },
        "git_commit_sha": "a" * 40,
        "git_tree_oid": "b" * 40,
        "package_identity_sha256": "c" * 64,
        "inventory": {},
    }
    listing_calls = iter([[stale], [], [], [published_fresh]])
    events: list[str] = []

    originals = {
        "verify_local_package": v4.publisher.verify_local_package,
        "list_depositions": v4.publisher.list_depositions,
        "series_records": v4.publisher.series_records,
        "create_draft": v4.publisher.create_draft,
        "refresh": v4.publisher.refresh,
        "build_state": v4.publisher.build_state,
        "clear_files": v4.publisher_v3.clear_files,
        "upload_files": v4.publisher_v3.upload_files,
        "verify_remote_files": v4.publisher_v3.verify_remote_files,
        "delete": v4.delete_unpublished_series_drafts,
    }
    try:
        v4.publisher.verify_local_package = lambda _path: package
        v4.publisher.list_depositions = lambda _client: next(listing_calls)
        v4.publisher.series_records = lambda records: records

        def fake_delete(_client: Any, records: list[dict[str, Any]]) -> list[int]:
            assert records == [stale]
            events.append("delete")
            return [v4.STALE_DRAFT_ID]

        def fake_create(
            _client: Any, latest: dict[str, Any] | None, metadata: dict[str, Any]
        ) -> dict[str, Any]:
            assert latest is None
            assert metadata == package["metadata"]
            assert events == ["delete"]
            events.append("create")
            return fresh

        v4.delete_unpublished_series_drafts = fake_delete
        v4.publisher.create_draft = fake_create
        v4.publisher.refresh = lambda _client, record: (
            published_fresh if record.get("submitted") is True else fresh
        )
        v4.publisher_v3.clear_files = lambda _client, _draft: events.append("clear")
        v4.publisher_v3.upload_files = (
            lambda _client, _draft, _path: events.append("upload")
        )
        v4.publisher_v3.verify_remote_files = (
            lambda _client, record, _path: events.append(
                "verify-published" if record.get("submitted") else "verify-draft"
            )
        )
        v4.publisher.build_state = (
            lambda _published, _package, _api, _records, _state: {"ok": True}
        )

        result = v4.publish_from_fresh_draft(
            client, Path("/tmp/capsule"), {}, "https://zenodo.org/api"
        )
    finally:
        v4.publisher.verify_local_package = originals["verify_local_package"]
        v4.publisher.list_depositions = originals["list_depositions"]
        v4.publisher.series_records = originals["series_records"]
        v4.publisher.create_draft = originals["create_draft"]
        v4.publisher.refresh = originals["refresh"]
        v4.publisher.build_state = originals["build_state"]
        v4.publisher_v3.clear_files = originals["clear_files"]
        v4.publisher_v3.upload_files = originals["upload_files"]
        v4.publisher_v3.verify_remote_files = originals["verify_remote_files"]
        v4.delete_unpublished_series_drafts = originals["delete"]

    assert result == {"ok": True}
    assert events == [
        "delete",
        "create",
        "clear",
        "upload",
        "verify-draft",
        "verify-published",
    ]


def main() -> int:
    test_delete_unpublished_only_and_wait()
    test_fresh_draft_is_created_after_stale_deletion()
    print("REPOSITORY_PRESERVATION_V4_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
