#!/usr/bin/env python3
"""Contract: native OTS upgraded/verified proof bundle lifecycle.

The current native path may upgrade and archive proofs, but every repository
write must be serialized with other main writers, bound to main, complete, and
reconciled after rebase without repeating a paid upload.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label} marker found: {needle}")


def main() -> None:
    workflow_path = ROOT / ".github/workflows/native-ots-upgrade-watch.yml"
    runner_path = ROOT / "scripts/run_native_ots_upgrade_verify.py"
    reconciler_path = ROOT / "scripts/reconcile_native_ots_generated_state.py"
    behavior_path = ROOT / "scripts/test_native_ots_transaction_behavior.py"
    status_generator_path = ROOT / "scripts/generate_record_chain_status.py"
    home_generator_path = ROOT / "scripts/generate_public_home_status.py"

    for path in [
        workflow_path,
        runner_path,
        reconciler_path,
        behavior_path,
        status_generator_path,
        home_generator_path,
    ]:
        if not path.exists():
            raise SystemExit(f"missing required file: {path.relative_to(ROOT)}")

    workflow = workflow_path.read_text(encoding="utf-8")
    runner = runner_path.read_text(encoding="utf-8")
    reconciler = reconciler_path.read_text(encoding="utf-8")
    status_generator = status_generator_path.read_text(encoding="utf-8")
    home_generator = home_generator_path.read_text(encoding="utf-8")

    workflow_markers = [
        "workflow_dispatch:",
        "contents: write",
        "group: main-write-lock",
        "queue: max",
        "timeout-minutes: 45",
        "fetch-depth: 0",
        "ref: main",
        'actor="${GITHUB_ACTOR:-}"',
        '[[ "$actor" != "thechurchofagi" && "$actor" != "github-actions[bot]" ]]',
        "Run Native OTS upgrade workflow contract test",
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
        "record-chain/audit/native-ots/",
        "ARKEY_CONFIGURED: ${{ secrets.ARKEY || vars.ARKEY }}",
        "ARWEAVE_JWK_CONFIGURED: ${{ secrets.ARWEAVE_JWK || vars.ARWEAVE_JWK }}",
        'ARWEAVE_JWK_JSON="${ARKEY_CONFIGURED:-${ARWEAVE_JWK_CONFIGURED:-}}"',
        "::add-mask::$ARWEAVE_JWK_JSON",
        "steps.jwk.outputs.has_jwk == 'true'",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE",
        "scripts/reconcile_native_ots_generated_state.py",
        "reconcile_and_stage",
        "git rebase origin/main",
        "git commit --amend --no-edit",
        "git push origin HEAD:main",
        "done < <(git diff --cached --name-only)",
        "git diff --cached --check",
        "--untracked-files=no",
        "never upgrade or upload again here",
        "scripts/restore_json_if_only_volatile_changes.py",
    ]
    for marker in workflow_markers:
        require(workflow, marker, "workflow")

    for marker in [
        "group: native-ots-upgrade-watch",
        "git stash",
        "if git push; then",
        "${GITHUB_REF_NAME",
    ]:
        forbid(workflow, marker, "unsafe workflow transaction")

    # Workflow must NOT directly write homepage generated artifacts.
    for marker in [
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        forbid(workflow, marker, "workflow scattered homepage write")

    home_sync_path = ROOT / ".github/workflows/homepage-status-sync.yml"
    if not home_sync_path.exists():
        raise SystemExit(f"missing workflow: {home_sync_path.relative_to(ROOT)}")
    home_sync = home_sync_path.read_text(encoding="utf-8")
    require(home_sync, "Native OTS Upgrade Watch", "homepage sync workflow_run native OTS watch")
    require(home_sync, "scripts/update_public_generated_artifacts.py", "homepage sync updater")

    runner_markers = [
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-arweave-bundles/",
        "record-chain/ots/native-arweave-registry.json",
        "api/record-chain-native-ots-arweave-registry.json",
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
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
        "upload_native_ots_bundle_to_arweave",
        "ALLOW_PAID_ARWEAVE_CANARY",
        "arweave_archived",
        "registered_without_arweave_tx",
        "claims arweave_archived without tx_id",
        "has_upgraded_archive",
        "has_verified_archive",
    ]
    for marker in runner_markers:
        require(runner, marker, "runner")

    start = runner.index("def refresh_native_ots_backlog")
    end = runner.index("\n\ndef ", start + 1)
    refresh_block = runner[start:end]
    require(refresh_block, "check=True", "fail-closed backlog refresh")
    forbid(refresh_block, "check=False", "ignored backlog refresh failure")

    for marker in [
        "record-chain/hash-chain/main.chain.jsonl",
        "api/record-chain-head.json",
        "api/record-chain-ots-latest.json",
        "record-chain/ots/arweave-registry.json",
        "api/record-chain-ots-arweave-registry.json",
        "record-chain/ots/arweave-bundles/",
    ]:
        forbid(runner, marker, "runner legacy path")

    require(runner, "bitcoin_verified must be false for upgraded", "runner upgraded bitcoin_verified guard")
    require(
        runner,
        "cannot build verified bundle before strict Bitcoin verification",
        "runner verified strict verify guard",
    )

    reconciler_markers = [
        "never upgrades an OTS proof and never uploads to Arweave",
        "sync_native_latest_from_anchor",
        "validate_native_registry",
        "scripts/detect_archive_backlog.py",
        "--write",
        "scripts/generate_arweave_wallet_status.py",
        '"paid_upload_performed": False',
        '"ots_upgrade_performed": False',
        '"derived_state_reconciled": True',
    ]
    for marker in reconciler_markers:
        require(reconciler, marker, "reconciler")
    for forbidden_marker in [
        "arweave_upload_payload.mjs",
        "arweave_cost_gate.mjs",
        "--enable-paid-upload",
        "--upgrade",
    ]:
        forbid(reconciler, forbidden_marker, "reconciler active operation")

    status_markers = [
        "latest_native_ots_proof_bundle_archive",
        "proof_bundle_archive",
        "api/record-chain-native-ots-arweave-registry.json",
        "arweave_archived",
        "registered_without_arweave_tx",
        "waiting-for-ots-upgrade",
        "ots_proof_bundle_arweave_archive_is_mirror_only",
        "ots_proof_bundle_arweave_archive_is_not_authority",
        "ots_proof_bundle_arweave_archive_is_not_attestation",
        "ots_proof_bundle_arweave_archive_is_not_amendment",
        "ots_proof_bundle_arweave_archive_is_not_successor_reception",
    ]
    for marker in status_markers:
        require(status_generator, marker, "status generator")

    for marker in [
        "proof_bundle_archive",
        "Native OTS proof bundle Arweave archive",
        "not authority, attestation, amendment, or successor reception",
    ]:
        require(home_generator, marker, "public home generator")

    behavior = subprocess.run(
        [sys.executable, str(behavior_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if behavior.returncode != 0:
        raise SystemExit(
            "native OTS transaction behavior failed:\n"
            + (behavior.stderr or behavior.stdout)[-5000:]
        )

    print("PASS: native OTS upgrade workflow contract")


if __name__ == "__main__":
    main()
