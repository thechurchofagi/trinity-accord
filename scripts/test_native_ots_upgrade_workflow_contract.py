#!/usr/bin/env python3
"""Contract: native OTS upgraded/verified proof bundle lifecycle.

Asserts:
  - native upgrade workflow exists and uses native paths
  - native runner uses native latest API and native anchors directory
  - supports pending/upgraded/verified states
  - upgraded bundle keeps bitcoin_verified=false
  - verified bundle requires strict verify success
  - paid upload requires explicit confirmation
  - registry keyed by anchored_file_sha256 and bundle_sha256
"""
from __future__ import annotations

from pathlib import Path


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label} marker found: {needle}")


def main() -> None:
    workflow_path = Path(".github/workflows/native-ots-upgrade-watch.yml")
    runner_path = Path("scripts/run_native_ots_upgrade_verify.py")
    contract_path = Path("scripts/test_native_ots_upgrade_workflow_contract.py")

    if not workflow_path.exists():
        raise SystemExit(f"missing workflow: {workflow_path}")
    if not runner_path.exists():
        raise SystemExit(f"missing runner: {runner_path}")
    if not contract_path.exists():
        raise SystemExit(f"missing contract test: {contract_path}")

    workflow = workflow_path.read_text(encoding="utf-8")
    runner = runner_path.read_text(encoding="utf-8")

    # Workflow markers
    workflow_markers = [
        "workflow_dispatch:",
        "contents: write",
        "concurrency:",
        "native-ots-upgrade-watch",
        "actions/checkout@",
        "Run Native OTS upgrade workflow contract test",
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        "record-chain/audit/native-ots/",
    ]
    for marker in workflow_markers:
        require(workflow, marker, "workflow")

    # Runner markers — native paths only
    runner_markers = [
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-arweave-bundles/",
        "record-chain/ots/native-arweave-registry.json",
        "api/record-chain-native-ots-arweave-registry.json",
        "trinityaccord.native-record-chain-ots-latest.v1",
        "trinityaccord.native-record-chain-ots-anchor.v1",
        "trinityaccord.native-ots-arweave-registry.v1",
        "bitcoin_attestation_embedded",
        "strict_bitcoin_verified",
        "upgraded",
        "verified",
        "pending",
        "already_verified_archived",
        "build_native_upgraded_bundle",
        "build_native_verified_bundle",
        "sync_native_latest_from_anchor",
        "ots_upgrade_and_verify",
        "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE",
        "registry_has_bundle_sha",
        "has_upgraded_archive",
        "has_verified_archive",
    ]
    for marker in runner_markers:
        require(runner, marker, "runner")

    # Runner must NOT use legacy paths
    runner_forbidden = [
        "record-chain/hash-chain/main.chain.jsonl",
        "api/record-chain-head.json",
        "api/record-chain-ots-latest.json",
        "record-chain/ots/arweave-registry.json",
        "api/record-chain-ots-arweave-registry.json",
        "record-chain/ots/arweave-bundles/",
    ]
    for marker in runner_forbidden:
        forbid(runner, marker, "runner")

    # Runner must enforce bitcoin_verified=false for upgraded
    require(
        runner,
        'bitcoin_verified must be false for upgraded',
        "runner upgraded bitcoin_verified guard",
    )

    # Runner must require strict verify for verified
    require(
        runner,
        "cannot build verified bundle before strict Bitcoin verification",
        "runner verified strict verify guard",
    )

    # Contract test exists and self-references
    contract = contract_path.read_text(encoding="utf-8")
    require(
        contract,
        "native-ots-upgrade-watch.yml",
        "contract self-reference",
    )

    print("PASS: native OTS upgrade workflow contract")


if __name__ == "__main__":
    main()
