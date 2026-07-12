#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

SPECS: dict[str, dict[str, str]] = {
    "arweave-wallet-status-update.yml": {
        "INPUT_BALANCE_AR": "${{ inputs.balance_ar }}",
        "INPUT_LOW_BALANCE_THRESHOLD_AR": "${{ inputs.low_balance_threshold_ar }}",
        "INPUT_WALLET_ADDRESS_SHA256": "${{ inputs.wallet_address_sha256 }}",
    },
    "diagnose-single-nft-timestamp.yml": {
        "INPUT_CONTRACT": "${{ github.event.inputs.contract }}",
        "INPUT_TOKEN_ID": "${{ github.event.inputs.token_id }}",
        "INPUT_START_BLOCK": "${{ github.event.inputs.start_block }}",
        "INPUT_END_BLOCK": "${{ github.event.inputs.end_block }}",
        "INPUT_CHUNK": "${{ github.event.inputs.chunk }}",
        "INPUT_APPLY": "${{ github.event.inputs.apply }}",
    },
    "enrich-nft-timestamps.yml": {
        "INPUT_START_BLOCK": "${{ github.event.inputs.start_block }}",
        "INPUT_END_BLOCK": "${{ github.event.inputs.end_block }}",
        "INPUT_CHUNK": "${{ github.event.inputs.chunk }}",
    },
    "operator-secret-smoke.yml": {
        "INPUT_NETWORK": "${{ github.event.inputs.network }}",
    },
    "paid-echo-arweave-canary.yml": {
        "INPUT_RECORD_TYPE": "${{ github.event.inputs.record_type }}",
    },
    "phase5-ots-arweave-paid-upload.yml": {
        "INPUT_CONFIRM": "${{ github.event.inputs.confirm }}",
    },
    "pre-scale-e2e-orchestrator-v2.yml": {
        "INPUT_CONFIRM": "${{ inputs.confirm }}",
        "INPUT_REQUIRE_NEW_RECORDS": "${{ inputs.require_new_records }}",
        "INPUT_MAX_RECORDS": "${{ inputs.max_records }}",
        "INPUT_MODE": "${{ inputs.mode }}",
        "INPUT_FROM_HEIGHT_EXCLUSIVE": "${{ inputs.from_height_exclusive }}",
    },
    "record-chain-anchor.yml": {
        "INPUT_FORCE_BATCH": "${{ github.event.inputs.force_batch }}",
    },
    "record-chain-append.yml": {
        "INPUT_PENDING_FILE_PATH": "${{ github.event.inputs.pending_file_path }}",
        "INPUT_RECEIPT_ID": "${{ github.event.inputs.receipt_id }}",
    },
    "record-chain-auto-finalize.yml": {
        "INPUT_CONFIRM": "${{ inputs.confirm }}",
        "INPUT_MAX_RECORDS": "${{ inputs.max_records }}",
        "INPUT_MODE": "${{ inputs.mode }}",
    },
    "record-chain-data-arweave-archive.yml": {
        "INPUT_MODE": "${{ inputs.mode }}",
        "INPUT_UPLOAD_MODE": "${{ inputs.upload_mode }}",
        "INPUT_TO_HEIGHT_INCLUSIVE": "${{ inputs.to_height_inclusive }}",
        "INPUT_FROM_HEIGHT_EXCLUSIVE": "${{ inputs.from_height_exclusive }}",
        "INPUT_SNAPSHOT_HEIGHT": "${{ inputs.snapshot_height }}",
        "INPUT_CONFIRM": "${{ inputs.confirm }}",
    },
    "render-manual-deploy.yml": {
        "INPUT_SERVICE": "${{ github.event.inputs.service }}",
        "INPUT_DEPLOY": "${{ github.event.inputs.deploy }}",
        "INPUT_ALLOW_LEGACY": "${{ github.event.inputs.emergency_allow_legacy_retired_gateway }}",
        "INPUT_LEGACY_CONFIRM": "${{ github.event.inputs.legacy_emergency_confirm }}",
    },
    "site-agent-entrypoint-journey-smoke.yml": {
        "INPUT_SITE_URL": "${{ github.event.inputs.site_url || 'https://www.trinityaccord.org' }}",
    },
    "site-agent-journey-swarm-smoke.yml": {
        "INPUT_SITE_URL": "${{ github.event.inputs.site_url || 'https://www.trinityaccord.org' }}",
        "INPUT_AGENTS": "${{ github.event.inputs.agents || '14' }}",
        "INPUT_ROUNDS": "${{ github.event.inputs.rounds || '2' }}",
    },
    "site-agent-write-lifecycle-canary.yml": {
        "INPUT_SITE_URL": "${{ github.event.inputs.site_url || 'https://www.trinityaccord.org' }}",
        "INPUT_MODE": "${{ github.event.inputs.mode || 'preflight-only' }}",
        "INPUT_ROUTE": "${{ github.event.inputs.route || 'pure_echo' }}",
        "INPUT_CONFIRM_LIVE_CANARY": "${{ github.event.inputs.confirm_live_canary || '' }}",
    },
    "site-live-discovery-smoke.yml": {
        "INPUT_STRICT_DIGEST": "${{ github.event.inputs.strict_digest || 'false' }}",
        "INPUT_SITE_URL": "${{ github.event.inputs.site_url || 'https://www.trinityaccord.org' }}",
    },
}


def harden_workflow(path: Path, mapping: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    if "\nenv:\n" in text:
        raise RuntimeError(f"unexpected existing top-level env block: {path}")
    marker = "\njobs:\n"
    if marker not in text:
        raise RuntimeError(f"jobs marker missing: {path}")
    env_block = "\nenv:\n" + "".join(
        f"  {name}: {expression}\n" for name, expression in mapping.items()
    )
    text = text.replace(marker, env_block + marker, 1)

    lines = text.splitlines()
    output: list[str] = []
    in_run = False
    run_indent = -1
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if in_run and stripped and indent <= run_indent:
            in_run = False
        if stripped.startswith("run:"):
            in_run = True
            run_indent = indent
        if in_run:
            for name, expression in mapping.items():
                line = line.replace(expression, f"${name}")
        output.append(line)
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def register_gate() -> None:
    path = ROOT / "scripts" / "run_ci_group.py"
    text = path.read_text(encoding="utf-8")
    command = '        ["python3", "scripts/test_workflow_dispatch_input_safety.py"],\n'
    if command in text:
        return
    anchor = '        ["python3", "scripts/test_no_remote_script_execution.py"],\n'
    if anchor not in text:
        raise RuntimeError("P0 CI registration anchor missing")
    path.write_text(text.replace(anchor, anchor + command, 1), encoding="utf-8")


def main() -> None:
    for filename, mapping in SPECS.items():
        harden_workflow(WORKFLOWS / filename, mapping)
    register_gate()
    print(f"Hardened {len(SPECS)} workflows and registered the safety gate")


if __name__ == "__main__":
    main()
