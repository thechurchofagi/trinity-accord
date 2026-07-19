#!/usr/bin/env python3
"""Static fail-closed contract for the Pages publication workflow."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/deploy-pages.yml"


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
    for job in ("verify", "build", "deploy"):
        if job not in jobs:
            errors.append(f"missing jobs.{job}")
    if jobs.get("build", {}).get("needs") != "verify":
        errors.append("build must depend on verify")
    if jobs.get("deploy", {}).get("needs") != "build":
        errors.append("deploy must depend on build")

    required = [
        "source_sha: ${{ steps.source.outputs.source_sha }}",
        "ref: ${{ needs.verify.outputs.source_sha }}",
        "ref: ${{ needs.build.outputs.source_sha }}",
        "Resolve immutable current-main source revision",
        "git fetch --no-tags --prune --depth=1 origin +refs/heads/main:refs/remotes/origin/main",
        'if [[ "${source_sha}" != "${main_sha}" ]]',
        "Refusing to publish ${source_sha}; current main is ${main_sha}",
        "Confirm immutable verify/build handoff",
        "Confirm immutable build/deploy handoff",
        "trinity-pages-source-receipt.v1",
        "pages-source-receipt-${{ github.run_id }}",
        "python3 scripts/verify_retired_builder_bundle_archive.py",
        "python3 scripts/verify_retired_builder_bundle_archive.py --site-dir _site",
        "python3 scripts/check_deployment_freshness_v2.py --site-dir _site",
        "python3 scripts/smoke_live_discovery_contract_v2.py",
        "python3 scripts/check_deployment_freshness_v2.py --site",
        "cmp builder-bundles/download_and_run_builder_bundle.py _site/builder-bundles/download_and_run_builder_bundle.py",
        "cp -a builder-bundles _site/builder-bundles",
        "cp -a record-chain/. _site/record-chain/",
        'rendered_downloads="$(mktemp -d)"',
        'cp -a _site/downloads/. "$rendered_downloads/"',
        'cp -a "$rendered_downloads/." _site/downloads/',
        '".github/workflows/homepage-deployment-receipt.yml"',
        '"scripts/**"',
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"missing required publication marker: {marker}")

    forbidden = [
        "export_formal_builder_bundles.py --out-dir builder-bundles --update-api",
        "git push --force",
        "peaceiris/actions-gh-pages",
        "JamesIves/github-pages-deploy-action",
        "/gateway/submit",
        "while true",
        "git ls-remote",
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
    print("PASS: deploy-pages workflow contract (current-main exact-SHA publication)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
