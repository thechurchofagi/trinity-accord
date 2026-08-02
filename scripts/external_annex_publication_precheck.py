#!/usr/bin/env python3
"""Validate external-annex authorization and current-main completion state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

COMPLETE = "published_and_publicly_restored"

EXPECTED_AUTHORIZATION: dict[str, Any] = {
    "schema": "trinityaccord.external-binary-annex-publication-authorization.v1",
    "authorized_by": "thechurchofagi",
    "authorized_at": "2026-08-01T21:45:00+08:00",
    "authorization": "publish_all_necessary_external_binary_annexes",
    "publication_confirmation": "PUBLISH_TRINITY_EXTERNAL_BINARY_ANNEXES_V1",
    "rights_boundary_ack": "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED",
    "core_repository_preservation_doi": "10.5281/zenodo.21739344",
    "scope": {
        "all_custom_assets_from_named_valid_releases": True,
        "evidence_annex": True,
        "chronicle_nft_media_annex": True,
        "already_public_release_bytes_only": True,
        "deprecated_failed_nft_attempts": False,
        "github_generated_source_archives": False,
        "publicly_readable_for_preservation": True,
        "deposit_grants_no_new_reuse_rights": True,
    },
    "user_authorization_text": (
        "你把该做的都做了吧？你觉得该做的都做了，反正用程序做也简单。"
        "你这个写程序写得又快又好。这不是什么那个，反正容量也有，对不对？"
        "DOI 的容量是足够的，是不是？既然有容量，就把它全部做了呗。"
    ),
}

EXPECTED_TRIGGER: dict[str, Any] = {
    "schema": "trinityaccord.external-binary-annex-publication-trigger.v1",
    "authorized_by": "thechurchofagi",
    "operation": "publish_evidence_and_nft_binary_annexes",
    "requested_at": "2026-08-01T21:45:00+08:00",
    "publication_confirmation": "PUBLISH_TRINITY_EXTERNAL_BINARY_ANNEXES_V1",
    "expected_core_doi": "10.5281/zenodo.21739344",
    "rights_boundary_ack": "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED",
    "expected_annex_types": ["evidence", "nft"],
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def is_complete(path: Path) -> bool:
    return read_object(path).get("publication_status") == COMPLETE


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-state", required=True)
    parser.add_argument("--authorization")
    parser.add_argument("--trigger")
    parser.add_argument("--complete-only", action="store_true")
    parser.add_argument("--github-output")
    args = parser.parse_args()

    current_state = Path(args.current_state)
    complete = is_complete(current_state)
    if args.complete_only:
        return 0 if complete else 1

    if not args.authorization or not args.trigger or not args.github_output:
        raise SystemExit("authorization, trigger and github-output are required")
    output = Path(args.github_output)
    if complete:
        with output.open("a", encoding="utf-8") as handle:
            handle.write("required=false\n")
        return 0

    if read_object(Path(args.authorization)) != EXPECTED_AUTHORIZATION:
        raise SystemExit("external-binary annex owner authorization changed")
    if read_object(Path(args.trigger)) != EXPECTED_TRIGGER:
        raise SystemExit("external-binary annex publication trigger changed")
    with output.open("a", encoding="utf-8") as handle:
        handle.write("required=true\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
