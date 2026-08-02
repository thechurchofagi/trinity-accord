#!/usr/bin/env python3
"""Seal publicly restored annex state and synchronize recovery discovery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_object(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def canonical_digest(value: dict[str, Any]) -> str:
    canonical = dict(value)
    canonical.pop("source_digest", None)
    return hashlib.sha256(
        json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()[:16]


def valid_commit(value: Any, label: str) -> str:
    normalized = str(value or "").strip().lower()
    if len(normalized) != 40 or any(
        ch not in "0123456789abcdef" for ch in normalized
    ):
        raise SystemExit(f"{label} must be an exact 40-character Git SHA-1")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state", default="preservation/external-binary-annex-state.json"
    )
    parser.add_argument(
        "--observation",
        default="preservation/external-binary-annex-observation.json",
    )
    parser.add_argument("--recovery-index", default="api/recovery-index.json")
    parser.add_argument("--repository-state", default="preservation/zenodo-state.json")
    parser.add_argument("--evidence-report", required=True)
    parser.add_argument("--nft-report", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    source_commit = valid_commit(args.source_commit, "source commit")
    state_path = ROOT / args.state
    observation_path = ROOT / args.observation
    index_path = ROOT / args.recovery_index
    repository_state = read_object(ROOT / args.repository_state)
    if repository_state.get("publication_status") != "published":
        raise SystemExit("core repository preservation DOI is not published")
    if repository_state.get("latest_doi") != "10.5281/zenodo.21739344":
        raise SystemExit("unexpected core repository preservation DOI")

    state = read_object(state_path)
    if state.get("publication_status") not in {
        "published_pending_public_cold_restore",
        "published_and_publicly_restored",
    }:
        raise SystemExit("annex state is not at a sealable publication stage")
    if state.get("source_commit_sha") != source_commit:
        raise SystemExit("annex state source commit mismatch")
    workflow_source = valid_commit(
        state.get("publication_workflow_source_commit_sha", state.get("source_commit_sha")),
        "publication workflow source commit",
    )
    if workflow_source != source_commit:
        raise SystemExit("publication workflow source commit mismatch")

    raw_annex_sources = state.get("annex_source_commits")
    if not isinstance(raw_annex_sources, dict):
        raw_annex_sources = {
            "evidence": source_commit,
            "nft": source_commit,
        }
    annex_sources = {
        annex_type: valid_commit(
            raw_annex_sources.get(annex_type),
            f"{annex_type} annex source commit",
        )
        for annex_type in ("evidence", "nft")
    }
    state["publication_workflow_source_commit_sha"] = workflow_source
    state["annex_source_commits"] = annex_sources

    reports = {
        "evidence": read_object(Path(args.evidence_report)),
        "nft": read_object(Path(args.nft_report)),
    }
    for annex_type, report in reports.items():
        if report.get("status") != "passed" or report.get("annex_type") != annex_type:
            raise SystemExit(f"public cold restore did not pass: {annex_type}")
        entry = state["annexes"][annex_type]
        if report.get("package_identity_sha256") != entry["package_identity_sha256"]:
            raise SystemExit(f"public restore package identity mismatch: {annex_type}")
        if int(report.get("asset_count") or -1) != int(entry["asset_count"]):
            raise SystemExit(f"public restore asset count mismatch: {annex_type}")
        if int(report.get("payload_bytes") or -1) != int(entry["payload_bytes"]):
            raise SystemExit(f"public restore payload byte mismatch: {annex_type}")
        if entry.get("source_commit_sha") != annex_sources[annex_type]:
            raise SystemExit(f"annex source commit mismatch: {annex_type}")
        if entry.get("public_metadata_verification") != "passed":
            raise SystemExit(f"public metadata verification missing: {annex_type}")
        entry["public_cold_restore"] = "passed"
        entry["public_cold_restore_report"] = report

    state["publication_status"] = "published_and_publicly_restored"
    state["all_named_release_assets_embedded"] = True
    state["release_asset_pagination_complete"] = True
    state["public_metadata_verification"] = "passed"
    state["external_binary_payload_recovery_requires_github"] = False
    write_object(state_path, state)

    observation = {
        "schema": "trinityaccord.external-binary-annex-public-observation.v3",
        "source_commit_sha": source_commit,
        "publication_workflow_source_commit_sha": workflow_source,
        "annex_source_commits": annex_sources,
        "observed_without_github_credentials": True,
        "observed_without_zenodo_credentials": True,
        "core_repository_preservation_doi": repository_state["latest_doi"],
        "core_repository_git_commit_sha": repository_state["latest_git_commit_sha"],
        "publication_status": state["publication_status"],
        "release_asset_pagination_complete": True,
        "public_metadata_verification": "passed",
        "annexes": state["annexes"],
    }
    write_object(observation_path, observation)

    index = read_object(index_path)
    entrypoints = index.setdefault("recovery_entrypoints", {})
    entrypoints.update(
        {
            "external_binary_annex_state": "preservation/external-binary-annex-state.json",
            "external_binary_annex_observation": "preservation/external-binary-annex-observation.json",
            "external_binary_annex_restore_cli": "scripts/restore_external_binary_annex.py",
        }
    )
    mirrors = index.setdefault("mirror_classes", {})
    mirrors["external_binary_annex_zenodo"] = (
        "verified complete paginated release-asset packages with public metadata, "
        "byte readback and unauthenticated DOI-only cold restoration"
    )
    index["latest_trusted_release"] = {
        "status": "published_and_publicly_restored",
        "repository_preservation": {
            "doi": repository_state["latest_doi"],
            "record_id": repository_state["latest_record_id"],
            "git_commit_sha": repository_state["latest_git_commit_sha"],
            "git_tree_oid": repository_state["latest_git_tree_oid"],
            "package_identity_sha256": repository_state[
                "latest_package_identity_sha256"
            ],
            "github_required_for_recovery": False,
        },
        "external_binary_annexes": {
            annex_type: {
                "doi": entry["doi"],
                "record_id": entry["record_id"],
                "annex_id": entry["annex_id"],
                "source_commit_sha": entry["source_commit_sha"],
                "asset_count": entry["asset_count"],
                "payload_bytes": entry["payload_bytes"],
                "package_identity_sha256": entry["package_identity_sha256"],
                "public_metadata_verification": entry[
                    "public_metadata_verification"
                ],
                "public_cold_restore": entry["public_cold_restore"],
            }
            for annex_type, entry in state["annexes"].items()
        },
    }
    replacement = (
        "The core repository capsule and the separately published evidence and "
        "Chronicle NFT binary annex DOI records together preserve the current "
        "Git-tracked repository and every custom asset from the named valid releases."
    )
    limitations = [
        item
        for item in index.get("limitations", [])
        if not (
            isinstance(item, str)
            and (
                "does not embed the separately hosted large binary" in item
                or "separately published evidence and Chronicle NFT" in item
            )
        )
    ]
    if replacement not in limitations:
        limitations.append(replacement)
    index["limitations"] = limitations
    index["source_digest"] = canonical_digest(index)
    write_object(index_path, index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
