#!/usr/bin/env python3
"""Fail closed when a public Trinity Accord recovery route drifts or disappears.

The monitor is deliberately metadata-only.  It verifies the published file
inventories, byte counts, and MD5 values exposed by Zenodo, but it never
downloads the roughly 1 GB recovery payloads during a routine availability
check.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = "thechurchofagi/trinity-accord"
DEFAULT_SITE = "https://www.trinityaccord.org"
DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com"
DEFAULT_GITHUB_API = "https://api.github.com"
DEFAULT_ZENODO_API = "https://zenodo.org/api"
EXPECTED_GATEWAY_SERVICE = "record-chain-intake-gateway"
EXPECTED_PROTECTION_ENTRYPOINT = (
    "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
)


class MonitorError(RuntimeError):
    """A local or public recovery contract failed validation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MonitorError(message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MonitorError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def release_by_tag(registry: dict[str, Any], tag: str) -> dict[str, Any]:
    matches = [
        item
        for item in registry.get("release_registry", [])
        if isinstance(item, dict) and item.get("tag") == tag
    ]
    require(len(matches) == 1, f"release registry must contain exactly one {tag} entry")
    return matches[0]


def load_expected_contract(root: Path = ROOT) -> dict[str, Any]:
    """Load and cross-check the checked-in sources of recovery truth."""
    registry = load_object(root / "GUARDIANSHIP-SYSTEM-REGISTRY.json")
    site_status = load_object(root / "api/status.json")
    recovery_catalog = load_object(root / "preservation/recovery-catalog.json")
    annex_state = load_object(root / "preservation/external-binary-annex-state.json")
    repository_state = load_object(root / "preservation/repository-preservation-state-v2.json")

    status_nft = site_status.get("nft_media_availability", {})
    historical_status = status_nft.get("historical_individual_archive_release", {})
    current_status = status_nft.get("current_content_recovery", {})
    historical_tag = str(historical_status.get("tag") or "")
    backup_tag = str(current_status.get("github_release_tag") or "")
    require(historical_tag != "", "api/status.json lacks the historical NFT release tag")
    require(backup_tag != "", "api/status.json lacks the current NFT backup release tag")

    historical = release_by_tag(registry, historical_tag)
    backup = release_by_tag(registry, backup_tag)
    observed_historical_names = historical.get("observed_custom_asset_names")
    expected_backup_names = backup.get("expected_custom_asset_names")
    require(
        isinstance(observed_historical_names, list)
        and all(isinstance(name, str) and name for name in observed_historical_names),
        "historical NFT release must declare observed_custom_asset_names",
    )
    require(
        isinstance(expected_backup_names, list)
        and all(isinstance(name, str) and name for name in expected_backup_names),
        "NFT backup release must declare expected_custom_asset_names",
    )
    require(
        len(observed_historical_names) == len(set(observed_historical_names)),
        "historical NFT release declares duplicate asset names",
    )
    require(
        len(expected_backup_names) == len(set(expected_backup_names)),
        "NFT backup release declares duplicate asset names",
    )
    require(
        historical.get("observed_custom_asset_count") == len(observed_historical_names),
        "historical NFT release asset count/name inventory drift",
    )
    require(
        historical_status.get("observed_custom_asset_count") == len(observed_historical_names),
        "public status historical NFT asset count drift",
    )
    require(
        current_status.get("custom_asset_count") == len(expected_backup_names),
        "public status NFT backup asset count drift",
    )
    require(
        backup.get("custom_assets")
        == f"{len(expected_backup_names)}/{len(expected_backup_names)}",
        "release registry NFT backup asset count drift",
    )

    nft_annex = annex_state.get("annexes", {}).get("nft", {})
    catalog_nft = recovery_catalog.get("external_binary_annexes", {}).get("nft", {})
    require(nft_annex.get("status") == "published", "NFT Zenodo annex is not marked published")
    require(
        nft_annex.get("public_cold_restore") == "passed",
        "NFT Zenodo annex lacks a passed public cold restore",
    )
    require(
        nft_annex.get("doi") == current_status.get("zenodo_annex_doi") == catalog_nft.get("doi"),
        "NFT Zenodo DOI drift across recovery sources",
    )
    require(
        nft_annex.get("record_id") == catalog_nft.get("record_id"),
        "NFT Zenodo record id drift across recovery sources",
    )
    require(
        nft_annex.get("asset_count") == len(expected_backup_names),
        "NFT annex source asset count does not match the GitHub backup inventory",
    )

    core_catalog = recovery_catalog.get("core_repository", {})
    latest_record_id = repository_state.get("latest_record_id")
    latest_doi = repository_state.get("latest_doi")
    require(
        latest_doi == core_catalog.get("current_verified_version_doi"),
        "current core recovery DOI drift",
    )
    require(
        latest_doi
        == site_status.get("current_evidence_checkpoint", {}).get("published_version_doi"),
        "public status current checkpoint DOI drift",
    )
    matching_versions = [
        item
        for item in repository_state.get("versions", [])
        if isinstance(item, dict) and item.get("record_id") == latest_record_id
    ]
    require(len(matching_versions) == 1, "latest core Zenodo version inventory is missing or duplicated")
    latest_version = matching_versions[0]
    require(latest_version.get("doi") == latest_doi, "latest core Zenodo version DOI drift")

    return {
        "releases": [
            {
                "label": "historical empty NFT release",
                "tag": historical_tag,
                "asset_names": list(observed_historical_names),
            },
            {
                "label": "content-complete NFT backup release",
                "tag": backup_tag,
                "asset_names": list(expected_backup_names),
            },
        ],
        "zenodo_records": [
            {
                "label": "Chronicle NFT annex",
                "record_id": nft_annex.get("record_id"),
                "doi": nft_annex.get("doi"),
                "files": nft_annex.get("files"),
            },
            {
                "label": "current core repository checkpoint",
                "record_id": latest_record_id,
                "doi": latest_doi,
                "files": latest_version.get("files"),
            },
        ],
        "site_status": site_status,
    }


def validate_release(
    payload: Any, *, label: str, tag: str, expected_asset_names: list[str]
) -> None:
    require(isinstance(payload, dict), f"{label}: GitHub response is not an object")
    require(payload.get("tag_name") == tag, f"{label}: release tag drift")
    require(payload.get("draft") is False, f"{label}: release is a draft")
    require(payload.get("prerelease") is False, f"{label}: release is a prerelease")
    assets = payload.get("assets")
    require(isinstance(assets, list), f"{label}: release assets are not a list")
    require(all(isinstance(item, dict) for item in assets), f"{label}: invalid release asset")
    actual_names = [str(item.get("name") or "") for item in assets]
    require(all(actual_names), f"{label}: release asset without a name")
    require(len(actual_names) == len(set(actual_names)), f"{label}: duplicate release asset name")
    require(
        set(actual_names) == set(expected_asset_names),
        f"{label}: asset set mismatch; expected={sorted(expected_asset_names)!r} "
        f"actual={sorted(actual_names)!r}",
    )
    for item in assets:
        name = str(item["name"])
        require(item.get("state") == "uploaded", f"{label}: {name} is not uploaded")
        size = item.get("size")
        require(isinstance(size, int) and size > 0, f"{label}: {name} has no bytes")


def _normalise_md5(value: Any) -> str:
    text = str(value or "").lower()
    return text.removeprefix("md5:")


def validate_zenodo_record(
    payload: Any, *, label: str, record_id: int, doi: str, expected_files: dict[str, Any]
) -> None:
    require(isinstance(payload, dict), f"{label}: Zenodo response is not an object")
    require(str(payload.get("id")) == str(record_id), f"{label}: Zenodo record id drift")
    require(payload.get("doi") == doi, f"{label}: Zenodo DOI drift")
    files = payload.get("files")
    require(isinstance(files, list), f"{label}: Zenodo files are not a list")
    require(all(isinstance(item, dict) for item in files), f"{label}: invalid Zenodo file")
    by_name: dict[str, dict[str, Any]] = {}
    for item in files:
        name = str(item.get("key") or item.get("filename") or "")
        require(name != "", f"{label}: Zenodo file without a name")
        require(name not in by_name, f"{label}: duplicate Zenodo file {name}")
        by_name[name] = item
    require(
        set(by_name) == set(expected_files),
        f"{label}: Zenodo file set mismatch; expected={sorted(expected_files)!r} "
        f"actual={sorted(by_name)!r}",
    )
    for name, expected in expected_files.items():
        item = by_name[name]
        size = item.get("size", item.get("filesize"))
        require(size == expected.get("bytes"), f"{label}: {name} byte count drift")
        require(
            _normalise_md5(item.get("checksum")) == str(expected.get("md5") or "").lower(),
            f"{label}: {name} MD5 metadata drift",
        )


def validate_site_status(payload: Any, expected: dict[str, Any]) -> None:
    require(isinstance(payload, dict), "public status response is not an object")
    require(payload == expected, "public /api/status.json differs from the checked-in status")


def validate_gateway_health(payload: Any) -> None:
    require(isinstance(payload, dict), "Gateway health response is not an object")
    require(payload.get("ok") is True, "Gateway health is not ready")
    require(payload.get("service") == EXPECTED_GATEWAY_SERVICE, "Gateway service identity drift")
    require(isinstance(payload.get("version"), str) and payload["version"], "Gateway version missing")
    require(payload.get("protection_required") is True, "Gateway protection is not required")
    require(payload.get("protection_layer_active") is True, "Gateway protection is not active")
    require(
        payload.get("protection_entrypoint") == EXPECTED_PROTECTION_ENTRYPOINT,
        "Gateway protected entrypoint drift",
    )
    for key in (
        "repo_configured",
        "branch_configured",
        "token_configured",
        "cooldown_secret_configured",
    ):
        require(payload.get(key) is True, f"Gateway {key} is not true")


def https_base(value: str, label: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    require(parsed.scheme == "https", f"{label} must use https")
    require(bool(parsed.hostname), f"{label} must include a hostname")
    require(parsed.username is None and parsed.password is None, f"{label} must not contain credentials")
    return value.rstrip("/")


def fetch_json(url: str, *, timeout: int, attempts: int, github_token: str = "") -> Any:
    headers = {
        "Accept": "application/vnd.github+json, application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "trinity-accord-public-recovery-monitor/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if github_token and urllib.parse.urlsplit(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {github_token}"
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            return payload
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 4))
    raise MonitorError(f"failed to fetch {url} after {attempts} attempt(s): {last_error}")


def run_live_checks(
    expected: dict[str, Any],
    *,
    repository: str,
    site: str,
    gateway: str,
    github_api: str,
    zenodo_api: str,
    timeout: int,
    attempts: int,
    fetcher: Callable[..., Any] = fetch_json,
) -> tuple[list[str], list[str]]:
    checks: list[str] = []
    errors: list[str] = []
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

    def check(name: str, operation: Callable[[], None]) -> None:
        try:
            operation()
        except (MonitorError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}: {exc}")
        else:
            checks.append(name)

    for release in expected["releases"]:
        tag = release["tag"]
        url = f"{github_api}/repos/{repository}/releases/tags/{urllib.parse.quote(tag, safe='')}"

        def release_check(release: dict[str, Any] = release, url: str = url) -> None:
            payload = fetcher(url, timeout=timeout, attempts=attempts, github_token=token)
            validate_release(
                payload,
                label=release["label"],
                tag=release["tag"],
                expected_asset_names=release["asset_names"],
            )

        check(f"github_release:{tag}", release_check)

    for record in expected["zenodo_records"]:
        record_id = record["record_id"]
        url = f"{zenodo_api}/records/{record_id}"

        def zenodo_check(record: dict[str, Any] = record, url: str = url) -> None:
            payload = fetcher(url, timeout=timeout, attempts=attempts, github_token="")
            validate_zenodo_record(
                payload,
                label=record["label"],
                record_id=record["record_id"],
                doi=record["doi"],
                expected_files=record["files"],
            )

        check(f"zenodo_record:{record_id}", zenodo_check)

    def status_check() -> None:
        payload = fetcher(
            f"{site}/api/status.json", timeout=timeout, attempts=attempts, github_token=""
        )
        validate_site_status(payload, expected["site_status"])

    check("public_site:/api/status.json", status_check)

    def gateway_check() -> None:
        payload = fetcher(f"{gateway}/healthz", timeout=timeout, attempts=attempts, github_token="")
        validate_gateway_health(payload)

    check("gateway:/healthz", gateway_check)
    return checks, errors


def write_report(path: str, report: dict[str, Any]) -> None:
    if not path:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--github-api", default=DEFAULT_GITHUB_API)
    parser.add_argument("--zenodo-api", default=DEFAULT_ZENODO_API)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--report", default="")
    parser.add_argument("--contract-only", action="store_true")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "schema": "trinityaccord.public-recovery-availability-monitor.v1",
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "metadata_only": True,
        "large_payload_bytes_downloaded": 0,
        "checks": [],
        "errors": [],
    }
    try:
        require(args.timeout > 0, "timeout must be positive")
        require(args.attempts > 0, "attempts must be positive")
        require(args.repository.count("/") == 1, "repository must be owner/name")
        expected = load_expected_contract()
        report["checks"].append("checked_in_recovery_topology")
        if not args.contract_only:
            site = https_base(args.site, "site")
            gateway = https_base(args.gateway, "gateway")
            github_api = https_base(args.github_api, "GitHub API")
            zenodo_api = https_base(args.zenodo_api, "Zenodo API")
            checks, errors = run_live_checks(
                expected,
                repository=args.repository,
                site=site,
                gateway=gateway,
                github_api=github_api,
                zenodo_api=zenodo_api,
                timeout=args.timeout,
                attempts=args.attempts,
            )
            report["checks"].extend(checks)
            report["errors"].extend(errors)
    except MonitorError as exc:
        report["errors"].append(str(exc))

    report["status"] = "PASS" if not report["errors"] else "FAIL"
    write_report(args.report, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
