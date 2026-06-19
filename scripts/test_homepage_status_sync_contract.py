#!/usr/bin/env python3
"""Contract test for centralized homepage status synchronization.

This prevents the old scattered-update architecture from returning.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

HOME_SYNC = WORKFLOWS / "homepage-status-sync.yml"
DEPLOY_PAGES = WORKFLOWS / "deploy-pages.yml"
OLD_PAGES = WORKFLOWS / "pages.yml"

BUSINESS_WORKFLOWS = [
    "record-chain-append.yml",
    "record-chain-head-ots-anchor.yml",
    "record-chain-arweave-archive.yml",
    "native-ots-upgrade-watch.yml",
    "archive-backlog-repair.yml",
    "record-chain-data-arweave-archive.yml",
    "build-echo-index.yml",
    "record-chain-anchor.yml",
    "record-chain-ots-upgrade.yml",
    "arweave-wallet-status-update.yml",
    "echo-human-review-action.yml",
    "rebuild-agent-declared-index.yml",
]

PUBLIC_GENERATED = [
    "api/record-chain-status.json",
    "api/public-home-status.json",
    "index.md",
    "sitemap.xml",
]

OLD_GENERATORS = [
    "generate_public_home_status.py",
    "patch_public_home_status_primary.py",
    "check_public_home_status_contract.py",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    require(HOME_SYNC.exists(), "missing centralized homepage-status-sync.yml")
    require(DEPLOY_PAGES.exists(), "missing deploy-pages.yml")
    require(not OLD_PAGES.exists(), "old duplicate .github/workflows/pages.yml must be deleted")

    home = read(HOME_SYNC)
    deploy = read(DEPLOY_PAGES)

    for marker in [
        "name: Homepage Status Sync",
        "workflow_dispatch:",
        "schedule:",
        'cron: "7,22,37,52 * * * *"',
        "workflow_run:",
        "contents: write",
        "actions: write",
        "concurrency:",
        "cancel-in-progress: false",
        "ubuntu-24.04",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        "scripts/update_public_generated_artifacts.py",
        "scripts/generate_arweave_wallet_status.py --check",
        "scripts/generate_record_chain_status.py --check",
        "scripts/generate_public_home_status.py --check",
        "scripts/patch_public_home_status_primary.py --check",
        "scripts/check_public_home_status_contract.py",
        "scripts/test_historic_autonomous_agent_reception_contract.py",
        "scripts/test_home_public_status_sync.py",
        "scripts/test_homepage_status_sync_contract.py",
        "scripts/generate_sitemap.py --check",
        "api/arweave-wallet-status.json",
        "api/record-chain-status.json",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
        "home: sync public homepage status",
        'gh workflow run deploy-pages.yml --repo "$GITHUB_REPOSITORY" --ref main',
        "scripts/check_homepage_live_freshness.py",
    ]:
        require(marker in home, f"homepage sync workflow missing marker: {marker}")

    for workflow_name in [
        "Record Chain Auto Finalize",
        "Append Record Chain Entries",
        "Record Chain Head OTS Anchor",
        "Record Chain Arweave Archive",
        "Native OTS Upgrade Watch",
        "Archive backlog repair",
        "Record Chain Data Arweave Archive",
        "Build Echo Index",
        "Record Chain Anchor",
        "Upgrade OpenTimestamps Proofs",
        "Arweave wallet status update",
        "Echo human review action",
    ]:
        require(workflow_name in home, f"homepage sync must listen to workflow_run: {workflow_name}")

    # Deploy conditions must not be weakened.
    for marker in [
        "steps.commit.outputs.changed == 'true'",
        "github.event.inputs.force_deploy == 'true'",
        "steps.live_pre.outcome == 'failure'",
    ]:
        require(marker in home, f"homepage sync deploy condition missing marker: {marker}")

    # Deploy reason logging markers (observability, not behavior change).
    for marker in [
        "deploy_reason=",
        "generated_files_changed",
        "manual_force_deploy",
        "live_freshness_failed",
    ]:
        require(marker in home, f"homepage sync deploy reason logging missing marker: {marker}")

    # Deploy workflow should verify committed artifacts, not generate a deployment-only state.
    for marker in [
        "Verify public home status has no drift",
        "generate_record_chain_status.py --check",
        "check_public_home_status_contract.py",
        "test_historic_autonomous_agent_reception_contract.py",
        "test_home_public_status_sync.py",
        "cmp ./api/public-home-status.json ./_site/api/public-home-status.json",
        "cmp ./api/record-chain-status.json ./_site/api/record-chain-status.json",
    ]:
        require(marker in deploy, f"deploy-pages.yml missing marker: {marker}")

    forbidden_deploy_snippets = [
        "python3 scripts/generate_public_home_status.py\n          python3 scripts/patch_public_home_status_primary.py\n          python3 scripts/patch_public_home_status_primary.py --check",
        "wallet.get('balance_ar') != '2.878082248532'",
    ]
    for snippet in forbidden_deploy_snippets:
        require(snippet not in deploy, f"deploy-pages.yml still contains old/stale deploy snippet: {snippet}")

    # Business workflows must not directly write homepage generated artifacts anymore.
    for name in BUSINESS_WORKFLOWS:
        path = WORKFLOWS / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for generator in OLD_GENERATORS:
            require(
                generator not in text,
                f"{name} must not directly run homepage generator/checker {generator}; use homepage-status-sync.yml",
            )
        for generated in PUBLIC_GENERATED:
            require(
                generated not in text,
                f"{name} must not directly commit public generated file {generated}; use homepage-status-sync.yml",
            )

    # CI/check workflows may mention generators, but only in check-only or contract contexts.
    allowed_check_workflows = [
        "deploy-pages.yml",
        "record-chain-ci.yml",
        "repository-integrity.yml",
        "homepage-status-sync.yml",
    ]
    for name in allowed_check_workflows:
        path = WORKFLOWS / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "generate_public_home_status.py" in text:
            require(
                "generate_public_home_status.py --check" in text
                or "scripts/update_public_generated_artifacts.py" in text,
                f"{name} mentions generate_public_home_status.py but not in allowed check/sync form",
            )

    print("PASS: centralized homepage status sync contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
