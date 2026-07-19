#!/usr/bin/env python3
"""Apply round-six CI/runtime alignment edits on the audit branch."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_OLD = "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
CHECKOUT_NEW = "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"{label}: target missing")
    return text.replace(old, new, 1)


# Deploy Pages must use the same Node runtime as all repository Node tests.
path = ".github/workflows/deploy-pages.yml"
text = read(path)
text = text.replace('          node-version: "20"\n', '          node-version-file: ".node-version"\n')
write(path, text)

# Required current-system CI must never repair a stale sitemap before testing it.
path = ".github/workflows/run-current-tests.yml"
text = read(path).replace(CHECKOUT_OLD, CHECKOUT_NEW)
text = text.replace(
    "      - name: Regenerate sitemap from current files\n        run: python3 scripts/generate_sitemap.py\n",
    "      - name: Verify sitemap has no committed drift\n        run: python3 scripts/generate_sitemap.py --check\n",
)
write(path, text)

# Required repository integrity: strict JSON, no mutation masking, compile coverage,
# nested Node lock validation, and the new CI/code alignment contract.
path = ".github/workflows/repository-integrity.yml"
text = read(path).replace(CHECKOUT_OLD, CHECKOUT_NEW)
text = text.replace(
    '      - name: Validate JSON\n        run: find . -name "*.json" -not -path "*/node_modules/*" -print0 | xargs -0 -n1 python3 -m json.tool > /dev/null\n',
    '      - name: Validate strict repository JSON\n        run: python3 scripts/validate_json_strict.py\n',
)
text = text.replace(
    "      - name: Regenerate sitemap from current files\n        run: python3 scripts/generate_sitemap.py\n",
    "      - name: Verify sitemap has no committed drift\n        run: python3 scripts/generate_sitemap.py --check\n",
)
text = replace_once(
    text,
    "      - name: Install Python dependencies\n        run: python3 -m pip install -r requirements-ci.txt\n",
    "      - name: Install Python dependencies\n        run: python3 -m pip install -r requirements-ci.txt\n\n"
    "      - name: Verify CI and code alignment\n        run: python3 scripts/test_ci_code_alignment.py\n\n"
    "      - name: Compile current Python sources\n        run: python3 -m compileall -q scripts apps tests\n",
    "repository integrity Python alignment",
)
text = replace_once(
    text,
    "      - name: Verify Node dependency lockfile\n        run: npm ci\n",
    "      - name: Verify root Node dependency lockfile\n        run: npm ci\n\n"
    "      - name: Verify retired Node service dependency lockfile\n"
    "        run: |\n"
    "          npm ci --ignore-scripts --prefix examples/github-app-backend\n"
    "          node --check examples/github-app-backend/server.js\n",
    "repository integrity Node alignment",
)
write(path, text)

# Scheduled full integrity must use the same reviewed checkout, strict parser, and
# validate the nested package-lock used by the retired Render tombstone.
path = ".github/workflows/repository-full-integrity.yml"
text = read(path).replace(CHECKOUT_OLD, CHECKOUT_NEW)
text = text.replace(
    '      - name: Validate JSON\n        run: find . -name "*.json" -not -path "*/node_modules/*" -print0 | xargs -0 -n1 python3 -m json.tool > /dev/null\n',
    '      - name: Validate strict repository JSON\n        run: python3 scripts/validate_json_strict.py\n',
)
text = replace_once(
    text,
    "      - name: Install Python dependencies\n        run: python3 -m pip install -r requirements-ci.txt\n",
    "      - name: Install Python dependencies\n        run: python3 -m pip install -r requirements-ci.txt\n\n"
    "      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4\n"
    "        with:\n"
    "          node-version-file: .node-version\n"
    "          cache: npm\n\n"
    "      - name: Verify retired Node service dependency lockfile\n"
    "        run: npm ci --ignore-scripts --prefix examples/github-app-backend\n",
    "full integrity nested Node lock",
)
write(path, text)

# Deep scheduled slices had a competing hard-coded Node 20 runtime and did not
# install the root lock before Node commands.
path = ".github/workflows/deep-integrity.yml"
text = read(path).replace(CHECKOUT_OLD, CHECKOUT_NEW)
text = text.replace('          node-version: "20"\n', '          node-version-file: ".node-version"\n          cache: "npm"\n')
text = replace_once(
    text,
    "      - name: Install Python test dependencies\n        run: python3 -m pip install -r requirements-ci.txt\n",
    "      - name: Install locked test dependencies\n"
    "        run: |\n"
    "          python3 -m pip install -r requirements-ci.txt\n"
    "          npm ci\n",
    "deep integrity dependency install",
)
write(path, text)

# Record-chain CI is required and must have bounded execution/concurrency.
path = ".github/workflows/record-chain-ci.yml"
text = read(path)
if "concurrency:" not in text:
    text = replace_once(
        text,
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\n\n"
        "concurrency:\n"
        "  group: record-chain-ci-${{ github.workflow }}-${{ github.ref }}\n"
        "  cancel-in-progress: true\n",
        "record-chain CI concurrency",
    )
text = replace_once(
    text,
    "  verify-record-chain:\n    runs-on: ubuntu-24.04\n",
    "  verify-record-chain:\n    runs-on: ubuntu-24.04\n    timeout-minutes: 15\n",
    "record-chain CI timeout",
)
write(path, text)

# Gateway CI must execute the production Python 3.11 runtime, validate strict
# JSON, and retain a smaller 3.12 forward-compatibility job.
path = ".github/workflows/record-chain-gateway-tests.yml"
text = read(path)
text = replace_once(
    text,
    "  gateway-tests:\n    runs-on: ubuntu-24.04\n",
    "  gateway-tests:\n    runs-on: ubuntu-24.04\n    timeout-minutes: 30\n",
    "gateway timeout",
)
text = text.replace('          python-version: "3.12"\n', '          python-version: "3.11"\n', 1)
text = text.replace(
    "      - name: Validate public JSON\n        run: python -m json.tool api/record-chain-submission-schema.v1.json >/tmp/record-chain-submission-schema.checked.json\n",
    "      - name: Validate strict repository JSON\n        run: python scripts/validate_json_strict.py\n",
)
if "gateway-python-312-compat:" not in text:
    text += """

  gateway-python-312-compat:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          show-progress: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
        with:
          python-version: "3.12"
      - name: Install Gateway test dependencies
        run: python -m pip install -r requirements-ci.txt -r apps/record_chain_intake_gateway/requirements.txt
      - name: Compile and test Gateway on Python 3.12
        env:
          PYTHONPATH: apps/record_chain_intake_gateway
        run: |
          python -m compileall -q apps/record_chain_intake_gateway
          python -m pytest apps/record_chain_intake_gateway/tests -q
"""
write(path, text)

# Exact workflow_run binding and identical push/PR path coverage for the
# record-chain write-path guard.
write(
    ".github/workflows/record-chain-write-path-guard.yml",
    """name: Record Chain Write Path Guard

on:
  workflow_dispatch:
  workflow_run:
    workflows: ["Archive backlog repair"]
    types: [completed]
  pull_request:
    branches: [main]
    paths:
      - "record-chain/**"
      - "api/record-chain-*.json"
      - "api/public-home-status.json"
      - "index.md"
      - "sitemap.xml"
      - ".github/workflows/record-chain-*.yml"
      - ".github/workflows/homepage-status-sync.yml"
      - ".github/workflows/deploy-pages.yml"
      - "scripts/check_homepage_live_freshness.py"
      - "scripts/test_homepage_status_sync_contract.py"
      - "scripts/check_record_chain_write_path_guard.py"
      - "scripts/test_record_chain_write_path_guard_contract.py"
      - "scripts/test_ci_code_alignment.py"
      - "scripts/run_current_system_tests.py"
  push:
    branches: [main]
    paths:
      - "record-chain/**"
      - "api/record-chain-*.json"
      - "api/public-home-status.json"
      - "index.md"
      - "sitemap.xml"
      - ".github/workflows/record-chain-*.yml"
      - ".github/workflows/homepage-status-sync.yml"
      - ".github/workflows/deploy-pages.yml"
      - "scripts/check_homepage_live_freshness.py"
      - "scripts/test_homepage_status_sync_contract.py"
      - "scripts/check_record_chain_write_path_guard.py"
      - "scripts/test_record_chain_write_path_guard_contract.py"
      - "scripts/test_ci_code_alignment.py"
      - "scripts/run_current_system_tests.py"

permissions:
  contents: read

concurrency:
  group: record-chain-write-path-guard-${{ github.ref }}
  cancel-in-progress: false

jobs:
  guard:
    if: >-
      ${{
        github.event_name != 'workflow_run' ||
        (
          github.event.workflow_run.conclusion == 'success' &&
          github.event.workflow_run.head_branch == 'main' &&
          github.event.workflow_run.head_repository.full_name == github.repository
        )
      }}
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          ref: ${{ github.event_name == 'workflow_run' && github.event.workflow_run.head_sha || github.event_name == 'workflow_dispatch' && 'main' || github.sha }}
          fetch-depth: 2

      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
        with:
          python-version: "3.11"

      - name: Check pull request protected paths
        if: github.event_name == 'pull_request'
        run: |
          git fetch origin "${{ github.base_ref }}" --depth=1
          python3 scripts/check_record_chain_write_path_guard.py \
            --mode pull-request \
            --base "origin/${{ github.base_ref }}" \
            --head HEAD

      - name: Check push protected paths
        if: github.event_name == 'push'
        run: |
          python3 scripts/check_record_chain_write_path_guard.py \
            --mode push \
            --base "${{ github.event.before }}" \
            --head "${{ github.sha }}" \
            --github-actor "${{ github.actor }}" \
            --gateway-actors "${{ vars.RECORD_CHAIN_GATEWAY_ACTORS }}"

      - name: Check latest main commit after manual dispatch
        if: github.event_name == 'workflow_dispatch'
        run: |
          test "$(git rev-parse --abbrev-ref HEAD)" = "main"
          BASE="$(git rev-parse HEAD~1)"
          HEAD="$(git rev-parse HEAD)"
          ACTOR="$(git log -1 --pretty=format:'%an' HEAD)"
          python3 scripts/check_record_chain_write_path_guard.py \
            --mode push \
            --base "$BASE" \
            --head "$HEAD" \
            --github-actor "$ACTOR" \
            --gateway-actors "${{ vars.RECORD_CHAIN_GATEWAY_ACTORS }}"

      - name: Check exact commit produced by archive repair
        if: github.event_name == 'workflow_run'
        run: |
          test "$(git rev-parse HEAD)" = "${{ github.event.workflow_run.head_sha }}"
          BASE="$(git rev-parse HEAD~1)"
          ACTOR="$(git log -1 --pretty=format:'%an' HEAD)"
          python3 scripts/check_record_chain_write_path_guard.py \
            --mode push \
            --base "$BASE" \
            --head HEAD \
            --github-actor "$ACTOR" \
            --gateway-actors "${{ vars.RECORD_CHAIN_GATEWAY_ACTORS }}"
""",
)

# Register permanent alignment/strictness checks in both the required runner and
# p0-current hard gate.
path = "scripts/run_current_system_tests.py"
text = read(path)
anchor = '        "scripts/test_deploy_pages_workflow_contract.py",\n'
insert = (
    '        "scripts/test_ci_code_alignment.py",\n'
    '        "scripts/validate_json_strict.py",\n'
    '        "scripts/test_workflows_do_not_reference_missing_scripts.py",\n'
    '        "scripts/test_workflow_permissions.py",\n'
)
if '"scripts/test_ci_code_alignment.py"' not in text:
    text = replace_once(text, anchor, insert + anchor, "current-system alignment registration")
write(path, text)

path = "scripts/run_ci_group.py"
text = read(path)
anchor = '        # CI hardening\n'
insert = (
    '        # CI hardening\n'
    '        ["python3", "scripts/test_ci_code_alignment.py"],\n'
    '        ["python3", "scripts/validate_json_strict.py"],\n'
    '        ["python3", "scripts/test_workflows_do_not_reference_missing_scripts.py"],\n'
    '        ["python3", "scripts/test_workflow_permissions.py"],\n'
)
if 'scripts/test_ci_code_alignment.py' not in text:
    text = replace_once(text, anchor, insert, "p0-current alignment registration")
write(path, text)

# Deep-integrity contract must enforce the locked Node runtime/install.
path = "scripts/test_deep_integrity_includes_pages_build.py"
text = read(path)
if "node-version-file: \".node-version\"" not in text:
    text = replace_once(
        text,
        'for marker in ["pages-build:", "actions/jekyll-build-pages@", "test -s _site/index.html"]:\n',
        'for marker in [\n'
        '    "pages-build:",\n'
        '    "actions/jekyll-build-pages@",\n'
        '    "test -s _site/index.html",\n'
        '    \'node-version-file: ".node-version"\',\n'
        '    "npm ci",\n'
        ']:\n',
        "deep-integrity Node contract",
    )
write(path, text)

print("ROUND6_CI_ALIGNMENT_APPLIED")
