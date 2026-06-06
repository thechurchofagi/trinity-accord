#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label} marker found: {needle}")


def main() -> None:
    workflow = Path(".github/workflows/ots-bitcoin-verification-watch.yml")
    runner = Path("scripts/run_phase6_ots_bitcoin_verify_and_verified_arweave_upload.py")

    if not workflow.exists():
        raise SystemExit(f"missing workflow: {workflow}")
    if not runner.exists():
        raise SystemExit(f"missing runner: {runner}")

    workflow_text = workflow.read_text(encoding="utf-8")
    runner_text = runner.read_text(encoding="utf-8")

    workflow_markers = [
        'cron: "17 * * * *"',
        "workflow_dispatch:",
        "contents: write",
        "concurrency:",
        "cancel-in-progress: false",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "Run Phase 6 workflow contract test",
        "ARKEY_SECRET: ${{ secrets.ARKEY }}",
        "printf '%s' \"$ARKEY_SECRET\"",
        "Verify JWK owner if available",
        "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE",
        "RESULT=$(python3 -c",
        'if [ "$RESULT" != "pass" ] && [ "$RESULT" != "verified" ] && [ "$RESULT" != "upgraded" ]; then',
        "api/record-chain-ots-latest.json",
        "record-chain/audit/phase6/${{ env.PHASE6_RUN_ID }}/",
        "if-no-files-found: warn",
        "sync verified OTS anchor and latest status",
        'OTS_UPGRADE_TIMEOUT: "180"',
    ]

    # OTS_SKIP_UPGRADE must NOT be present in the workflow
    workflow_forbidden = [
        "OTS_SKIP_UPGRADE",
    ]

    runner_markers = [
        "already_verified_archived",
        "pending_tx_exists",
        "has_verified_archive",
        "registry_has_bundle_sha",
        "verified bundle sha already exists in registry; refusing duplicate paid upload",
        "main.chain.jsonl changed unexpectedly",
        "api/record-chain-head.json changed unexpectedly",
        "estimated cost exceeds 0.10",
        "wallet owner mismatch",
        "readback hash/byte match failed",
        "latest_verified_tx_id not updated to verified tx",
        "strict verify returned success but anchor is not marked verified",
        "OTS verify failed for non-pending reason",
        "sync_latest_ots_from_anchor",
        "calendar_attested",
        "bitcoin_attestation_embedded",
        "strict_bitcoin_verified",
        "strict_verify_unavailable_reason",
    ]

    for marker in workflow_markers:
        require(workflow_text, marker, "workflow")

    for marker in workflow_forbidden:
        forbid(workflow_text, marker, "workflow")

    for marker in runner_markers:
        require(runner_text, marker, "runner")

    print("PASS: phase6 OTS watch formal workflow contract")


if __name__ == "__main__":
    main()
