#!/usr/bin/env python3
"""Contract for the retired legacy hash-chain data archive surface.

The historical recovery/audit tools remain verifiable, but only the current
native Record-Chain Arweave workflow may sign, upload, mutate registries, or
trigger public status synchronization.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    required = [
        "scripts/build_record_chain_data_arweave_bundle.py",
        "scripts/update_record_chain_data_arweave_registry.py",
        "scripts/verify_record_chain_data_arweave_bundle.py",
        "scripts/verify_record_chain_data_arweave_registry.py",
        "scripts/restore_record_chain_from_data_arweave_bundle.py",
        "scripts/test_legacy_arweave_retirement_behavior.py",
        ".github/workflows/record-chain-data-arweave-archive.yml",
        ".github/workflows/record-chain-arweave-archive.yml",
    ]
    for relative in required:
        require((ROOT / relative).exists(), f"missing {relative}")

    builder = (ROOT / "scripts/build_record_chain_data_arweave_bundle.py").read_text(encoding="utf-8")
    for marker in [
        "record_chain_data_delta",
        "record_chain_data_snapshot",
        "record_payload",
        "client_oath_readback",
        "readback_text",
        "bundle_identity_sha256",
        "bundle['bundle_identity_sha256'][:12]",
        "legacy-data-delta-height",
        "legacy-data-snapshot-height",
        "refusing to overwrite",
        "historical recovery/audit tooling only",
        "not_current_native_record_chain",
    ]:
        require(marker in builder, f"legacy builder missing contract marker: {marker}")
    require("utc_now" not in builder, "frozen legacy bundle identity must not depend on wall-clock time")
    require('"native_chain_tip"' in builder, "logical identity must explicitly exclude accidental historical native_chain_tip")

    updater = (ROOT / "scripts/update_record_chain_data_arweave_registry.py").read_text(encoding="utf-8")
    require("legacy record-chain data Arweave uploads are retired" in updater, "legacy updater must fail closed for live mode")
    require("would_write_registry" in updater and "retired_read_only_preview" in updater, "legacy updater must be preview-only")
    require("write_json" not in updater, "retired registry updater must have no write helper")

    verifier = (ROOT / "scripts/verify_record_chain_data_arweave_registry.py").read_text(encoding="utf-8")
    for marker in [
        "verify_bundle",
        "bundle_raw_file_sha256",
        "arweave_payload_sha256",
        "arweave_readback_sha256",
        "KNOWN_DUPLICATE_LIVE_TX_IDS",
        "preserved_not_endorsed",
    ]:
        require(marker in verifier, f"historical registry verifier missing: {marker}")

    restore = (ROOT / "scripts/restore_record_chain_from_data_arweave_bundle.py").read_text(encoding="utf-8")
    require("verify_record_chain_integrity.py" in restore, "restore drill must run integrity verifier")

    legacy_workflow = (ROOT / ".github/workflows/record-chain-data-arweave-archive.yml").read_text(encoding="utf-8")
    for required_text in [
        "Legacy Hash-Chain Data Archive Audit (Retired)",
        "permissions:\n  contents: read",
        "Confirm legacy-only source boundary",
        "Verify frozen legacy hash-chain view",
        "Prove audit did not mutate repository state",
        "--allow-known-historical-duplicates",
    ]:
        require(required_text in legacy_workflow, f"retired workflow missing: {required_text}")
    for forbidden in [
        "contents: write",
        "secrets.ARKEY",
        "upload_mode:",
        "arweave_upload_payload.mjs",
        "record_arweave_upload_result.py",
        "update_record_chain_data_arweave_registry.py",
        "generate_arweave_wallet_status.py",
        "git commit",
        "git push",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        require(forbidden not in legacy_workflow, f"retired workflow retains forbidden capability: {forbidden}")

    current_workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")
    for marker in [
        "Record Chain Arweave Archive",
        "contents: write",
        "group: main-write-lock",
        "secrets.ARKEY",
        "build_record_chain_arweave_archive.py",
    ]:
        require(marker in current_workflow, f"current native archive route missing: {marker}")

    home_sync = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    require('      - "Record Chain Arweave Archive"' in home_sync, "homepage sync must listen to current native archive")
    require('      - "Record Chain Data Arweave Archive"' not in home_sync, "homepage sync must not listen to retired legacy archive name")
    require("Legacy Hash-Chain Data Archive Audit (Retired)" not in home_sync, "read-only historical audit must not trigger public status sync")

    behavior = subprocess.run(
        [sys.executable, "scripts/test_legacy_arweave_retirement_behavior.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(
        behavior.returncode == 0,
        "legacy archive behavioral contract failed:\n" + (behavior.stderr or behavior.stdout)[-4000:],
    )

    print("PASS: legacy hash-chain data archive is retired; current native Arweave route remains authoritative")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
