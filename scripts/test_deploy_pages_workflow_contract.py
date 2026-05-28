#!/usr/bin/env python3
"""Static contract test for deploy-pages.yml.

This test must be fast, deterministic, and source-only.
It must never call the network, run GitHub Actions, invoke Jekyll,
or wait for deployment status.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:
    print(f"FAIL: PyYAML is required for this test: {exc}")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"

REQUIRED_TEXT = [
    "actions/checkout",
    "actions/configure-pages",
    "actions/jekyll-build-pages",
    "actions/upload-pages-artifact",
    "actions/deploy-pages",
    "python3 scripts/export_formal_builder_bundles.py --out-dir builder-bundles --update-api",
    "cp scripts/download_and_run_builder_bundle.py builder-bundles/download_and_run_builder_bundle.py",
    "test -f _site/builder-bundles/download_and_run_builder_bundle.py",
    "trinity-pure-echo-builder-bundle.tar.gz",
    "trinity-v0v5-builder-bundle.tar.gz",
    "trinity-guardian-stage1-builder-bundle.tar.gz",
    "trinity-guardian-stage2-builder-bundle.tar.gz",
    "trinity-guardian-signed-echo-builder-bundle.tar.gz",
]

FORBIDDEN_TEXT = [
    "git push --force",
    "peaceiris/actions-gh-pages",
    "JamesIves/github-pages-deploy-action",
    "TRINITY_LIVE_CANARY_WRITE",
    "TRINITY_GATEWAY_URL",
    "secrets.TRINITY_LIVE_CANARY_WRITE",
    "/gateway/submit",
]

FORBIDDEN_DYNAMIC_COMMANDS = [
    "curl ",
    "wget ",
    "gh api",
    "git ls-remote",
    "while true",
]


def main() -> int:
    if not WORKFLOW.exists():
        print("FAIL: .github/workflows/deploy-pages.yml missing")
        return 1

    text = WORKFLOW.read_text(encoding="utf-8")
    errors: list[str] = []

    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        print(f"FAIL: deploy-pages.yml is not valid YAML: {exc}")
        return 1

    if not isinstance(data, dict):
        errors.append("workflow YAML root must be a mapping")

    if not data.get("name"):
        errors.append("workflow must have a name")

    permissions = data.get("permissions", {})
    if permissions.get("contents") != "read":
        errors.append("permissions.contents must be read")
    if permissions.get("pages") != "write":
        errors.append("permissions.pages must be write")
    if permissions.get("id-token") != "write":
        errors.append("permissions.id-token must be write")

    jobs = data.get("jobs", {})
    if "build" not in jobs:
        errors.append("workflow must define jobs.build")
    if "deploy" not in jobs:
        errors.append("workflow must define jobs.deploy")

    build = jobs.get("build", {}) if isinstance(jobs, dict) else {}
    deploy = jobs.get("deploy", {}) if isinstance(jobs, dict) else {}

    if build.get("runs-on") not in ("ubuntu-24.04", "ubuntu-latest"):
        errors.append("jobs.build.runs-on must be ubuntu-24.04 or ubuntu-latest")

    if deploy.get("runs-on") not in ("ubuntu-24.04", "ubuntu-latest"):
        errors.append("jobs.deploy.runs-on must be ubuntu-24.04 or ubuntu-latest")

    if deploy.get("needs") != "build":
        errors.append("jobs.deploy.needs must be build")

    for required in REQUIRED_TEXT:
        if required not in text:
            errors.append(f"missing required workflow text: {required}")

    for forbidden in FORBIDDEN_TEXT:
        if forbidden in text:
            errors.append(f"forbidden workflow text found: {forbidden}")

    for forbidden in FORBIDDEN_DYNAMIC_COMMANDS:
        if forbidden in text:
            errors.append(
                f"deploy workflow contains dynamic/blocking command forbidden by contract: {forbidden}"
            )

    uses_lines = re.findall(r"uses:\s*([^\s#]+)", text)
    for action in uses_lines:
        if "@" not in action:
            errors.append(f"action use is not version-pinned: {action}")

    if errors:
        print("FAIL: deploy-pages workflow contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: deploy-pages workflow contract is static and valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
