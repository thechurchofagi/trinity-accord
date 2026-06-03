#!/usr/bin/env python3
"""Phase 6B — Render Deploy Boundary Contract Test.

Ensures that record-chain data/status/sitemap/public-home commits
cannot trigger a redeploy of the trinity-record-chain-gateway service
on Render.

Checks:
  1. Root render.yaml contains trinity-record-chain-gateway service.
  2. That service has autoDeploy: false.
  3. App mirror render.yaml has the same autoDeploy: false setting.
  4. Record-chain data workflows do not mention Render deploy hooks.
  5. deploy-pages workflow does not deploy the Gateway.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def load_text(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing {rel}")
    return p.read_text(encoding="utf-8")


# ------------------------------------------------------------------
# 1 & 2. Root render.yaml — gateway service exists with autoDeploy: false
# ------------------------------------------------------------------
def check_root_render_yaml():
    text = load_text("render.yaml")

    # Find the trinity-record-chain-gateway service block
    # We look for the service name and then check autoDeploy in its vicinity.
    svc_pattern = re.compile(
        r"name:\s*trinity-record-chain-gateway", re.IGNORECASE
    )
    if not svc_pattern.search(text):
        fail("root render.yaml missing trinity-record-chain-gateway service")

    # Extract from the service start to the next service (or end)
    # A service block starts with "  - type:" and ends at the next "  - type:" or EOF
    blocks = re.split(r"(?=\n  - type:)", text)
    gw_block = None
    for block in blocks:
        if "trinity-record-chain-gateway" in block:
            gw_block = block
            break

    if gw_block is None:
        fail("could not isolate trinity-record-chain-gateway block in render.yaml")

    if "autoDeploy: false" not in gw_block:
        fail(
            "trinity-record-chain-gateway in root render.yaml "
            "is missing autoDeploy: false"
        )
    ok("root render.yaml: trinity-record-chain-gateway has autoDeploy: false")


# ------------------------------------------------------------------
# 3. App mirror render.yaml — same autoDeploy: false
# ------------------------------------------------------------------
def check_app_mirror_render_yaml():
    text = load_text("apps/record_chain_intake_gateway/render.yaml")

    if "trinity-record-chain-gateway" not in text:
        fail("app mirror render.yaml missing trinity-record-chain-gateway")

    if "autoDeploy: false" not in text:
        fail(
            "app mirror render.yaml "
            "is missing autoDeploy: false for trinity-record-chain-gateway"
        )
    ok("app mirror render.yaml: autoDeploy: false present")


# ------------------------------------------------------------------
# 4. Data-commit workflows must not contain Render deploy hooks
# ------------------------------------------------------------------
RENDER_DEPLOY_KEYWORDS = [
    "render-deploy",
    "render deploy",
    "deploy.render.com",
    "api.render.com",
    "onrender.com/deploy",
]

DATA_WORKFLOW_PATTERNS = [
    "record-chain-anchor",
    "record-chain-arweave-archive",
    "record-chain-append",
]


def check_data_workflows_no_render_hooks():
    workflows_dir = ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        fail("missing .github/workflows directory")

    for wf_name in DATA_WORKFLOW_PATTERNS:
        # Match any yml file whose stem contains the pattern
        matches = [p for p in workflows_dir.glob("*.yml") if wf_name in p.stem]
        for wf_path in matches:
            wtext = wf_path.read_text(encoding="utf-8").lower()
            for kw in RENDER_DEPLOY_KEYWORDS:
                if kw.lower() in wtext:
                    fail(
                        f"{wf_path.name} contains Render deploy keyword: {kw!r}"
                    )
    ok("data-commit workflows have no Render deploy hooks")


# ------------------------------------------------------------------
# 5. deploy-pages workflow does not deploy the Gateway
# ------------------------------------------------------------------
def check_deploy_pages_no_gateway():
    wf_path = ROOT / ".github" / "workflows" / "deploy-pages.yml"
    if not wf_path.exists():
        # If there's no deploy-pages workflow, nothing to check
        ok("deploy-pages workflow absent — skip Gateway deploy check")
        return

    text = wf_path.read_text(encoding="utf-8").lower()

    # The deploy-pages workflow should not call render deploy or
    # contain the gateway service name as a deploy target.
    gateway_deploy_indicators = [
        "render deploy",
        "render-deploy",
        "deploy.render.com",
    ]
    for indicator in gateway_deploy_indicators:
        if indicator in text:
            fail(
                f"deploy-pages workflow contains Gateway deploy indicator: {indicator!r}"
            )

    # Also ensure it doesn't reference the gateway startCommand
    if "uvicorn apps.record_chain_intake_gateway" in text:
        fail("deploy-pages workflow references gateway startCommand")

    ok("deploy-pages workflow does not deploy the Gateway")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> int:
    check_root_render_yaml()
    check_app_mirror_render_yaml()
    check_data_workflows_no_render_hooks()
    check_deploy_pages_no_gateway()

    print("\n=== ALL RENDER DEPLOY BOUNDARY CONTRACT TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
