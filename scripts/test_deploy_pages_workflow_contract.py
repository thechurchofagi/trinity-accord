#!/usr/bin/env python3
"""Static fail-closed contract for the Pages publication workflow."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/deploy-pages.yml"


def _needs_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    errors: list[str] = []

    if not isinstance(data, dict):
        errors.append("workflow YAML root must be a mapping")
        data = {}

    permissions = data.get("permissions", {})
    for key, expected in {"contents": "read", "pages": "write", "id-token": "write"}.items():
        if permissions.get(key) != expected:
            errors.append(f"permissions.{key} must be {expected}")

    jobs = data.get("jobs", {})
    required_jobs = (
        "verify",
        "deploy-gateway-before-pages",
        "build",
        "deploy-primary",
        "deploy-retry",
        "verify-live-deployment",
    )
    for job in required_jobs:
        if job not in jobs:
            errors.append(f"missing jobs.{job}")

    if jobs.get("deploy-gateway-before-pages", {}).get("needs") != "verify":
        errors.append("Gateway rollout must depend on verify")

    build_needs = _needs_list(jobs.get("build", {}).get("needs", []))
    if set(build_needs) != {"verify", "deploy-gateway-before-pages"}:
        errors.append(
            "build must depend on verify and deploy-gateway-before-pages"
        )

    primary_needs = _needs_list(jobs.get("deploy-primary", {}).get("needs", []))
    if primary_needs != ["build"]:
        errors.append("deploy-primary must depend only on build")

    retry_needs = _needs_list(jobs.get("deploy-retry", {}).get("needs", []))
    if set(retry_needs) != {"build", "deploy-primary"}:
        errors.append("deploy-retry must depend on build and deploy-primary")

    verify_live_needs = _needs_list(
        jobs.get("verify-live-deployment", {}).get("needs", [])
    )
    if set(verify_live_needs) != {
        "build",
        "deploy-primary",
        "deploy-retry",
    }:
        errors.append(
            "verify-live-deployment must depend on build, deploy-primary, and deploy-retry"
        )

    retry_if = str(jobs.get("deploy-retry", {}).get("if", ""))
    if "needs.deploy-primary.outputs.outcome == 'failure'" not in retry_if:
        errors.append("deploy-retry must run only after primary deployment failure")

    verify_if = str(jobs.get("verify-live-deployment", {}).get("if", ""))
    if "always()" not in verify_if:
        errors.append("verify-live-deployment must evaluate after skipped retry jobs")

    required = [
        "source_sha: ${{ steps.source.outputs.source_sha }}",
        "ref: ${{ needs.verify.outputs.source_sha }}",
        "ref: ${{ needs.build.outputs.source_sha }}",
        "Resolve immutable current-main source revision",
        '"apps/record_chain_intake_gateway/**"',
        '"render.yaml"',
        '".github/workflows/render-manual-deploy.yml"',
        "git fetch --no-tags --prune --depth=1 origin +refs/heads/main:refs/remotes/origin/main",
        'if [[ "${source_sha}" != "${main_sha}" ]]',
        "Refusing to publish ${source_sha}; current main is ${main_sha}",
        "Confirm immutable verify/build handoff",
        "required=true",
        "Confirm immutable build/deploy handoff",
        "Confirm immutable retry handoff",
        "Refuse stale source before retry",
        "Refuse stale source before live verification",
        "trinity-pages-source-receipt.v1",
        "pages-source-receipt-${{ github.run_id }}",
        "python3 scripts/verify_retired_builder_bundle_archive.py",
        "python3 scripts/verify_retired_builder_bundle_archive.py --site-dir _site",
        "python3 scripts/check_deployment_freshness_v2.py --site-dir _site",
        "python3 scripts/smoke_live_discovery_contract_v2.py",
        "python3 scripts/check_deployment_freshness_v2.py --site",
        "--reconcile-config",
        "cmp builder-bundles/download_and_run_builder_bundle.py _site/builder-bundles/download_and_run_builder_bundle.py",
        "cp -a builder-bundles _site/builder-bundles",
        "cp -a record-chain/. _site/record-chain/",
        'rendered_downloads="$(mktemp -d)"',
        'cp -a _site/downloads/. "$rendered_downloads/"',
        'cp -a "$rendered_downloads/." _site/downloads/',
        '".github/workflows/homepage-deployment-receipt.yml"',
        '"scripts/**"',
        "outcome: ${{ steps.deployment.outcome }}",
        "Pause before independent GitHub Pages retry",
        "Retry GitHub Pages deployment in fresh job",
        "Select Pages deployment candidate for strict live verification",
        "strict live byte verification will decide the deployment result",
        "No GitHub Pages deployment candidate URL is available.",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"missing required publication marker: {marker}")

    if text.count("actions/deploy-pages@") != 2:
        errors.append("Pages publication must contain exactly two pinned deployment attempts")
    if text.count("timeout: 600000") != 2:
        errors.append("both Pages deployment attempts must use the supported 600000 ms timeout")
    if text.count("continue-on-error: true") < 2:
        errors.append("both Pages action attempts must expose outcome for live verification")

    forbidden = [
        "export_formal_builder_bundles.py --out-dir builder-bundles --update-api",
        "git push --force",
        "peaceiris/actions-gh-pages",
        "JamesIves/github-pages-deploy-action",
        "/gateway/submit",
        "while true",
        "git ls-remote",
        "timeout: 1800000",
        "if: steps.deployment-primary.outcome == 'failure'",
        "No successful GitHub Pages deployment is available.",
    ]
    for marker in forbidden:
        if marker in text:
            errors.append(f"forbidden publication behavior: {marker}")

    for action in re.findall(r"uses:\s*([^\s#]+)", text):
        if "@" not in action:
            errors.append(f"unpinned action: {action}")

    if errors:
        print("FAIL: deploy-pages workflow contract errors:")
        for error in errors:
            print("  -", error)
        return 1
    print(
        "PASS: deploy-pages workflow contract "
        "(current-main exact-SHA publication with isolated retry and live-byte authority)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
