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
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"

REQUIRED_TEXT = [
    "actions/checkout",
    "actions/configure-pages",
    "actions/jekyll-build-pages",
    "actions/upload-pages-artifact",
    "actions/deploy-pages",
    "push:",
    "branches:",
    "- main",
    "api/**",
    '"*.md"',
    '"*.json"',
    '"_layouts/**"',
    '"assets/**"',
    '"bitcoin-inscription-mirrors/**"',
    '"echoes/**"',
    '"first-contact/**"',
    "sitemap.xml",
    "python3 scripts/export_formal_builder_bundles.py --out-dir builder-bundles --update-api",
    "cp scripts/download_and_run_builder_bundle.py builder-bundles/download_and_run_builder_bundle.py",
    "cp -a ./record-chain ./_site/record-chain",
    "cmp ./api/public-home-status.json ./_site/api/public-home-status.json",
    "cmp ./api/record-chain-status.json ./_site/api/record-chain-status.json",
    "cmp ./api/waiting-heartbeat-status.json ./_site/api/waiting-heartbeat-status.json",
    "cmp ./record-chain/chain-tip.json ./_site/record-chain/chain-tip.json",
    "cmp ./record-chain/indexes/statistics.json ./_site/record-chain/indexes/statistics.json",
    "cmp ./record-chain/indexes/record-index.json ./_site/record-chain/indexes/record-index.json",
    "require_file _site/api/waiting-heartbeat-status.json",
    "test -f _site/builder-bundles/download_and_run_builder_bundle.py",
    "test -f _site/record-chain/indexes/statistics.json",
    "test -f _site/record-chain/indexes/record-index.json",
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
    "pip install --upgrade pip",
    '      - "record-chain/**"',
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

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception as exc:
            print(f"FAIL: deploy-pages.yml is not valid YAML: {exc}")
            return 1
    else:
        # Minimal dependency-free fallback for local smoke environments where
        # requirements-ci.txt cannot be installed. CI still uses PyYAML above.
        trigger_block = {"push": {}} if re.search(r"(?m)^  push:\s*$", text) else {}
        data = {
            "name": re.search(r"^name:\s*(.+)$", text, re.M).group(1) if re.search(r"^name:\s*(.+)$", text, re.M) else None,
            "permissions": dict(re.findall(r"^  ([A-Za-z-]+):\s*(read|write)$", text, re.M)),
            True: trigger_block,
            "jobs": {},
        }
        for job in ("build", "deploy"):
            m = re.search(rf"^  {job}:\n(?P<body>(?:    .+\n?)+)", text, re.M)
            body = m.group("body") if m else ""
            data["jobs"][job] = {
                "runs-on": re.search(r"^    runs-on:\s*(.+)$", body, re.M).group(1) if re.search(r"^    runs-on:\s*(.+)$", body, re.M) else None,
                "needs": re.search(r"^    needs:\s*(.+)$", body, re.M).group(1) if re.search(r"^    needs:\s*(.+)$", body, re.M) else None,
            }

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

    on_block = data.get(True) if True in data else data.get("on")
    if not isinstance(on_block, dict) or "push" not in on_block:
        errors.append("deploy-pages.yml must deploy on main pushes as a freshness backstop")
    elif isinstance(on_block.get("push"), dict):
        paths = on_block["push"].get("paths", [])
        site_change_samples = {
            "root page": "*.md",
            "root machine entry": "*.json",
            "layout": "_layouts/**",
            "site assets": "assets/**",
            "canonical mirror": "bitcoin-inscription-mirrors/**",
            "nested Echo guide": "echoes/**",
            "nested first-contact guide": "first-contact/**",
        }
        for label, pattern in site_change_samples.items():
            if pattern not in paths:
                errors.append(f"push.paths does not cover {label}: {pattern}")

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
