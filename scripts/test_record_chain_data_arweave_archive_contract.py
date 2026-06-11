#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(cond, msg):
    if not cond:
        raise SystemExit(msg)

def main():
    required = [
        "scripts/build_record_chain_data_arweave_bundle.py",
        "scripts/update_record_chain_data_arweave_registry.py",
        "scripts/verify_record_chain_data_arweave_registry.py",
        "scripts/restore_record_chain_from_data_arweave_bundle.py",
        ".github/workflows/record-chain-data-arweave-archive.yml",
    ]
    for rel in required:
        require((ROOT / rel).exists(), f"missing {rel}")

    build = (ROOT / "scripts/build_record_chain_data_arweave_bundle.py").read_text(encoding="utf-8")
    require("record_chain_data_delta" in build, "builder must support delta")
    require("record_chain_data_snapshot" in build, "builder must support snapshot")
    require("record_payload" in build, "bundle must include full record payload")
    require("client_oath_readback" in build, "builder must scan client_oath_readback")
    require("readback_text" in build, "builder must scan readback_text")
    # Immutable filename: bundle content hash must be in filename
    require("content_hash[:12]" in build, "builder must include content hash in filename")
    require("data-delta-height" in build, "builder must use delta filename pattern")
    require("data-snapshot-height" in build, "builder must use snapshot filename pattern")
    # Anti-overwrite: must refuse to overwrite different content with same name
    require("refusing to overwrite" in build, "builder must refuse overwriting different content")

    verify = (ROOT / "scripts/verify_record_chain_data_arweave_registry.py").read_text(encoding="utf-8")
    require("arweave_hash_match" in verify, "registry verifier must check hash match")

    restore = (ROOT / "scripts/restore_record_chain_from_data_arweave_bundle.py").read_text(encoding="utf-8")
    require("verify_record_chain_integrity.py" in restore, "restore drill must run integrity verifier")

    workflow = (ROOT / ".github/workflows/record-chain-data-arweave-archive.yml").read_text(encoding="utf-8")
    require("I_UNDERSTAND_THIS_UPLOADS_RECORD_CHAIN_DATA_TO_ARWEAVE" in workflow, "live upload must require confirm")
    require("secrets.ARKEY" in workflow, "workflow must use GitHub Secret ARKEY")
    require("verify_record_chain_data_arweave_registry.py" in workflow, "workflow must verify data registry")
    require("generate_arweave_wallet_status.py" in workflow, "live data archive must refresh wallet status fact source")

    # Workflow must NOT directly write homepage generated artifacts
    for forbidden in [
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        require(forbidden not in workflow, f"data archive workflow must not directly write homepage generated artifact: {forbidden}")

    # Homepage sync must listen to this workflow
    home_sync = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    require("Record Chain Data Arweave Archive" in home_sync, "homepage sync must listen to data archive workflow")
    require("scripts/update_public_generated_artifacts.py" in home_sync, "homepage sync must run centralized updater")

    print("PASS: record chain data arweave archive contract")

if __name__ == "__main__":
    main()
