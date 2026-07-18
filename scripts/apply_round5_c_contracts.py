#!/usr/bin/env python3
"""Apply small source-contract edits that are awkward to stage through Contents API."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"{label}: target missing")
    return text.replace(old, new, 1)


public_path = ROOT / "scripts/public_machine_deployment_contract.py"
public = public_path.read_text(encoding="utf-8")
if '"/api/agent-live-health.v1.json"' not in public:
    public = replace_once(
        public,
        '    "/.well-known/pages-production-closure.v1.json",\n',
        '    "/.well-known/pages-production-closure.v1.json",\n'
        '    "/api/agent-live-health.v1.json",\n'
        '    "/api/formal-builder-bundles.v1.json",\n'
        '    "/builder-bundles/download_and_run_builder_bundle.py",\n'
        '    "/builder-bundles/trinity-guardian-full-registration-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-guardian-full-registration-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-guardian-retirement-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-guardian-retirement-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-guardian-signed-echo-builder-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-guardian-signed-echo-builder-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-guardian-stage1-builder-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-guardian-stage1-builder-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-guardian-stage2-builder-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-guardian-stage2-builder-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-pure-echo-builder-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-pure-echo-builder-bundle.tar.gz",\n'
        '    "/builder-bundles/trinity-v0v5-builder-bundle.manifest.json",\n'
        '    "/builder-bundles/trinity-v0v5-builder-bundle.tar.gz",\n',
        "deployment byte surfaces",
    )
    public_path.write_text(public, encoding="utf-8")

home_path = ROOT / "scripts/test_homepage_status_sync_contract.py"
home = home_path.read_text(encoding="utf-8")
if '"scripts/check_deployment_freshness_v2.py"' not in home:
    home = replace_once(
        home,
        '        "scripts/check_homepage_live_freshness.py",\n',
        '        "scripts/check_homepage_live_freshness.py",\n'
        '        "scripts/check_deployment_freshness_v2.py",\n'
        '        "Equivalent generated state already reached main",\n'
        '        "retrying the existing rebased commit without rewriting it",\n',
        "homepage freshness markers",
    )
if '"Build Record Chain Batch"' not in home:
    home = replace_once(
        home,
        '        "Waiting Heartbeat Status Sync",\n',
        '        "Waiting Heartbeat Status Sync",\n'
        '        "Build Record Chain Batch",\n'
        '        "Stamp Record Chain Batches with OpenTimestamps",\n'
        '        "Waiting Heartbeat Arweave Capsule",\n'
        '        "Rebuild Agent-Declared Verification Index",\n',
        "writer workflow coverage",
    )
if '        "github.event_name == \'workflow_run\'",\n' not in home:
    home = replace_once(
        home,
        '        "steps.live_pre.outcome == \'failure\'",\n',
        '        "steps.live_pre.outcome == \'failure\'",\n'
        '        "github.event_name == \'workflow_run\'",\n',
        "workflow-run deploy condition marker",
    )
old_condition = "if: ${{ github.event_name == 'push' || needs.sync.outputs.changed == 'true' ||"
new_condition = "if: ${{ github.event_name == 'push' || github.event_name == 'workflow_run' || needs.sync.outputs.changed == 'true' ||"
if old_condition in home:
    home = home.replace(old_condition, new_condition, 1)
if '        "upstream_workflow_completed",\n' not in home:
    home = replace_once(
        home,
        '        "live_freshness_failed",\n',
        '        "live_freshness_failed",\n        "upstream_workflow_completed",\n',
        "workflow-run deploy reason",
    )
home_path.write_text(home, encoding="utf-8")

print("ROUND5_C_CONTRACTS_APPLIED")
