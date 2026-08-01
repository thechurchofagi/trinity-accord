#!/usr/bin/env python3
"""Regression tests for deterministic builds and Zenodo V3 publication gates."""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_preservation_capsule_v2 as build_v2  # noqa: E402
import publish_preservation_capsule_to_zenodo_v3 as publish_v3  # noqa: E402


class FakeClient:
    def __init__(
        self,
        record: dict[str, Any],
        payloads: dict[str, bytes],
        refresh_records: list[dict[str, Any]] | None = None,
    ) -> None:
        self.record = record
        self.payloads = payloads
        self.refresh_records = list(refresh_records or [])
        self.requests: list[tuple[str, str]] = []

    def request_bytes(self, url: str) -> bytes:
        self.requests.append(("GET_BYTES", url))
        value = self.payloads.get(url)
        if value is None:
            raise SystemExit(f"unexpected byte URL: {url}")
        return value

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        del payload, data, content_type
        self.requests.append((method, url))
        if method == "GET":
            if self.refresh_records:
                return self.refresh_records.pop(0)
            return self.record
        return {}

    def delete(self, url: str) -> None:
        self.requests.append(("DELETE", url))


def make_capsule_and_record(
    directory: Path, *, published: bool, stale_bundle_metadata: bool
) -> tuple[dict[str, Any], dict[str, bytes]]:
    files: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}
    bucket = "https://zenodo.org/api/files/test-bucket"
    for name in publish_v3.publisher.PUBLISHED_FILE_NAMES:
        raw = ("payload:" + name).encode("utf-8")
        (directory / name).write_bytes(raw)
        md5 = hashlib.md5(raw, usedforsecurity=False).hexdigest()
        size = len(raw)
        if name == "trinity-accord-recovery.bundle" and stale_bundle_metadata:
            size += 2
            md5 = "0" * 32
        quoted = publish_v3.urllib.parse.quote(name)
        bucket_url = bucket + "/" + quoted
        public_url = "https://zenodo.org/records/123/files/" + quoted
        item = {
            "filename": name,
            "filesize": size,
            "checksum": "md5:" + md5,
            "links": {
                "self": bucket_url,
                "download": public_url,
                "content": public_url,
            },
        }
        files.append(item)
        payloads[bucket_url] = raw
        payloads[public_url] = raw
    record = {
        "id": 123,
        "submitted": published,
        "state": "done" if published else "inprogress",
        "links": {"bucket": bucket},
        "files": files,
    }
    return record, payloads


def test_deterministic_bundle_command() -> None:
    calls: list[tuple[str, ...]] = []

    def fake_git_text(root: Path, *args: str) -> str:
        del root
        calls.append(tuple(args))
        return "ok"

    original = build_v2.ORIGINAL_GIT_TEXT
    build_v2.ORIGINAL_GIT_TEXT = fake_git_text
    try:
        assert (
            build_v2.deterministic_git_text(
                Path("."), "bundle", "create", "capsule.bundle", "--all"
            )
            == "ok"
        )
        assert calls[-1] == (
            "-c",
            "pack.threads=1",
            "bundle",
            "create",
            "capsule.bundle",
            "--all",
        )
        build_v2.deterministic_git_text(Path("."), "bundle", "verify", "capsule.bundle")
        assert calls[-1] == ("bundle", "verify", "capsule.bundle")
    finally:
        build_v2.ORIGINAL_GIT_TEXT = original


def test_draft_metadata_lag_does_not_override_exact_bytes() -> None:
    with tempfile.TemporaryDirectory() as temp_name:
        directory = Path(temp_name)
        record, payloads = make_capsule_and_record(
            directory, published=False, stale_bundle_metadata=True
        )
        client = FakeClient(record, payloads)
        original_sleep = publish_v3.time.sleep
        publish_v3.time.sleep = lambda _seconds: None
        try:
            result = publish_v3.verify_remote_files(client, record, directory)
        finally:
            publish_v3.time.sleep = original_sleep
        assert result["trinity-accord-recovery.bundle"]["bytes"] > 0


def test_published_metadata_mismatch_remains_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as temp_name:
        directory = Path(temp_name)
        record, payloads = make_capsule_and_record(
            directory, published=True, stale_bundle_metadata=True
        )
        client = FakeClient(record, payloads)
        original_sleep = publish_v3.time.sleep
        publish_v3.time.sleep = lambda _seconds: None
        try:
            try:
                publish_v3.verify_remote_files(client, record, directory)
            except SystemExit as exc:
                assert "published metadata did not converge" in str(exc)
            else:
                raise AssertionError("published stale metadata was accepted")
        finally:
            publish_v3.time.sleep = original_sleep


def test_clear_waits_for_empty_draft() -> None:
    initial = {
        "id": 123,
        "files": [{"filename": "old", "links": {"self": "https://example/old"}}],
    }
    empty = {"id": 123, "files": []}
    client = FakeClient(initial, {}, refresh_records=[initial, empty])
    cleared: list[bool] = []
    original_clear = publish_v3.ORIGINAL_CLEAR_FILES
    original_sleep = publish_v3.time.sleep
    publish_v3.ORIGINAL_CLEAR_FILES = lambda _client, _draft: cleared.append(True)
    publish_v3.time.sleep = lambda _seconds: None
    try:
        publish_v3.clear_files(client, initial)
    finally:
        publish_v3.ORIGINAL_CLEAR_FILES = original_clear
        publish_v3.time.sleep = original_sleep
    assert cleared == [True]
    assert [method for method, _url in client.requests].count("GET") == 2


def main() -> int:
    test_deterministic_bundle_command()
    test_draft_metadata_lag_does_not_override_exact_bytes()
    test_published_metadata_mismatch_remains_fail_closed()
    test_clear_waits_for_empty_draft()
    print("REPOSITORY_PRESERVATION_V3_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
