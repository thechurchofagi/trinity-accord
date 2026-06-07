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

    verify = (ROOT / "scripts/verify_record_chain_data_arweave_registry.py").read_text(encoding="utf-8")
    require("arweave_hash_match" in verify, "registry verifier must check hash match")

    restore = (ROOT / "scripts/restore_record_chain_from_data_arweave_bundle.py").read_text(encoding="utf-8")
    require("verify_record_chain_integrity.py" in restore, "restore drill must run integrity verifier")

    workflow = (ROOT / ".github/workflows/record-chain-data-arweave-archive.yml").read_text(encoding="utf-8")
    require("I_UNDERSTAND_THIS_UPLOADS_RECORD_CHAIN_DATA_TO_ARWEAVE" in workflow, "live upload must require confirm")
    require("secrets.ARKEY" in workflow, "workflow must use GitHub Secret ARKEY")
    require("verify_record_chain_data_arweave_registry.py" in workflow, "workflow must verify data registry")

    print("PASS: record chain data arweave archive contract")

if __name__ == "__main__":
    main()
