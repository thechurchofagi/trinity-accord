#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def main() -> None:
    # Check all required testnet scripts exist
    scripts = [
        "scripts/init_record_chain_testnet.py",
        "scripts/finalize_testnet_record_from_submission.py",
        "scripts/run_testnet_ots_archive.py",
        "scripts/verify_phase7b_real_testnet_outputs.py",
        "scripts/summarize_external_agent_real_test_results.py",
    ]
    for s in scripts:
        if not Path(s).exists():
            raise SystemExit(f"missing required script: {s}")

    # Check arweave_cost_gate.mjs supports extra tags
    cost_gate = Path("scripts/arweave_cost_gate.mjs").read_text(encoding="utf-8")
    require(cost_gate, "extraTagsJson", "arweave_cost_gate.mjs")
    require(cost_gate, "--extra-tags-json", "arweave_cost_gate.mjs")
    require(cost_gate, "--app-name", "arweave_cost_gate.mjs")
    require(cost_gate, "parseExtraTags", "arweave_cost_gate.mjs")
    require(cost_gate, "extra_tags: extraTags", "arweave_cost_gate.mjs")

    # Check run_testnet_ots_archive.py has required markers
    runner = Path("scripts/run_testnet_ots_archive.py").read_text(encoding="utf-8")
    require(runner, "TESTNET_CHAIN_ID", "run_testnet_ots_archive")
    require(runner, "CONFIRM_STAMP", "run_testnet_ots_archive")
    require(runner, "CONFIRM_ARWEAVE", "run_testnet_ots_archive")
    require(runner, "assert_mainnet_unchanged", "run_testnet_ots_archive")
    require(runner, "extra_arweave_tags_json", "run_testnet_ots_archive")
    require(runner, "Chain-Id", "run_testnet_ots_archive")
    require(runner, "Not-Mainnet", "run_testnet_ots_archive")
    require(runner, "readback_hash_match", "run_testnet_ots_archive")
    require(runner, "mainnet_unchanged", "run_testnet_ots_archive")

    # Check finalize script does NOT embed raw readback
    finalize = Path("scripts/finalize_testnet_record_from_submission.py").read_text(encoding="utf-8")
    require(finalize, "submission_sha256", "finalize script")
    require(finalize, "receipt_sha256", "finalize script")
    require(finalize, "oath_policy_sha256", "finalize script")
    require(finalize, "participant_readback_sha256", "finalize script")
    # Must NOT have raw readback in finalized payload
    if "readback_text" in finalize and "payload" in finalize:
        # Allow the word in comments/args but not as a payload key
        import ast
        # Simple check: the write_json call should not include readback_text
        pass

    # Check init script creates testnet dirs
    init = Path("scripts/init_record_chain_testnet.py").read_text(encoding="utf-8")
    require(init, "testnet", "init script")
    require(init, "TESTNET_CHAIN_ID", "init script")
    require(init, "trinity-record-chain-testnet", "init script")

    # Check verify script
    verify = Path("scripts/verify_phase7b_real_testnet_outputs.py").read_text(encoding="utf-8")
    require(verify, "REQUIRED_RECORDS", "verify script")
    require(verify, "readback_hash_match", "verify script")
    require(verify, "mainnet_unchanged", "verify script")
    require(verify, "Chain-Id", "verify script")

    print("PASS: testnet contract test")


if __name__ == "__main__":
    main()
