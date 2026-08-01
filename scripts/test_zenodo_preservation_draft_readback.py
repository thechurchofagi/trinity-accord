#!/usr/bin/env python3
"""Regression tests for Zenodo draft/public file byte readback ordering."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publish_preservation_capsule_to_zenodo_v2 import (  # noqa: E402
    download_verified_bytes,
    remote_download_candidates,
)


class FakeClient:
    def __init__(self, responses: dict[str, bytes | SystemExit]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def request_bytes(self, url: str) -> bytes:
        self.calls.append(url)
        value = self.responses[url]
        if isinstance(value, SystemExit):
            raise value
        return value


def main() -> int:
    payload = b"verified-draft-byte-readback"
    expected_sha = hashlib.sha256(payload).hexdigest()

    draft = {
        "submitted": False,
        "state": "inprogress",
        "links": {"bucket": "https://zenodo.org/api/files/bucket-id"},
    }
    draft_item = {
        "filename": "capsule file.json",
        "links": {
            "download": "https://zenodo.org/records/not-public/files/capsule%20file.json",
            "self": "https://zenodo.org/api/files/bucket-id/capsule%20file.json",
        },
    }
    draft_candidates = remote_download_candidates(draft, draft_item, "capsule file.json")
    expected_bucket = "https://zenodo.org/api/files/bucket-id/capsule%20file.json"
    assert draft_candidates[0] == expected_bucket, draft_candidates
    draft_client = FakeClient({expected_bucket: payload})
    result = download_verified_bytes(
        draft_client,
        draft_candidates,
        expected_size=len(payload),
        expected_sha256=expected_sha,
        name="capsule file.json",
        attempts=1,
        sleep_fn=lambda _: None,
    )
    assert result == payload
    assert draft_client.calls == [expected_bucket]

    published = {"submitted": True, "state": "done"}
    published_item = {
        "filename": "capsule.json",
        "links": {
            "download": "https://zenodo.org/records/1/files/capsule.json",
            "content": "https://zenodo.org/api/records/1/files/capsule.json/content",
        },
    }
    public_candidates = remote_download_candidates(published, published_item, "capsule.json")
    assert public_candidates[:2] == [
        "https://zenodo.org/records/1/files/capsule.json",
        "https://zenodo.org/api/records/1/files/capsule.json/content",
    ]
    public_client = FakeClient(
        {
            public_candidates[0]: SystemExit(
                "Zenodo file download failed: HTTP Error 404: NOT FOUND"
            ),
            public_candidates[1]: payload,
        }
    )
    result = download_verified_bytes(
        public_client,
        public_candidates,
        expected_size=len(payload),
        expected_sha256=expected_sha,
        name="capsule.json",
        attempts=1,
        sleep_fn=lambda _: None,
    )
    assert result == payload
    assert public_client.calls == public_candidates[:2]

    mismatch_client = FakeClient({expected_bucket: b"wrong"})
    try:
        download_verified_bytes(
            mismatch_client,
            [expected_bucket],
            expected_size=len(payload),
            expected_sha256=expected_sha,
            name="capsule file.json",
            attempts=1,
            sleep_fn=lambda _: None,
        )
    except SystemExit as exc:
        assert "exact byte readback failed" in str(exc)
    else:
        raise AssertionError("hash/size mismatch was not rejected")

    print("ZENODO_PRESERVATION_DRAFT_READBACK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
