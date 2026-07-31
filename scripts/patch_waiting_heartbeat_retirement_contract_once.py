#!/usr/bin/env python3
"""One-time PR #825 patch; removed by its branch-only applying workflow."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "test_waiting_heartbeat_summary_metrics.py"
text = PATH.read_text(encoding="utf-8")
old = '''def test_capsule_workflow_preserves_upload_result_before_status_update() -> None:
    text = CAPSULE_WORKFLOW.read_text(encoding="utf-8")
    require("capsule_readback_repair_needed" in text, "capsule workflow must support readback repair mode")
    require("repair_waiting_heartbeat_arweave_capsule_readback.mjs" in text, "capsule workflow must call readback repair script")
    require("steps.capsule_preflight.outputs.capsule_path" in text, "capsule workflow must use the preflight-selected payload path")
    require("echo \\"exit_code=$?\\" >> \\"$GITHUB_OUTPUT\\"" in text, "capsule workflow must capture upload/repair exit code without skipping commit")
    require("Commit capsule metadata" in text, "capsule workflow must still commit generated capsule metadata")
'''
new = '''def test_standalone_capsule_workflow_is_retired_but_historical_tools_remain() -> None:
    text = CAPSULE_WORKFLOW.read_text(encoding="utf-8")
    require("Retired" in text, "standalone capsule workflow must declare retirement")
    require("contents: read" in text, "retired standalone capsule workflow must be read-only")
    require("schedule:" not in text, "retired standalone capsule workflow must not be scheduled")
    require("workflow_run:" not in text, "retired standalone capsule workflow must not auto-trigger")
    require("ARKEY" not in text, "retired standalone capsule workflow must have no wallet secret")
    require("arweave_upload_waiting_heartbeat_capsule" not in text, "retired workflow must not upload")
    require("repair_waiting_heartbeat_arweave_capsule_readback" not in text, "retired workflow must not initiate paid-path repair")
    require("weekly continuity bundle" in text.lower(), "retired workflow must point to weekly continuity preservation")

    # Historical capsule evidence and readback-only repair tools remain available
    # for already-posted transactions; retirement removes only automatic spending.
    require(CAPSULE_BUILDER.exists(), "historical capsule builder must remain available")
    require(CAPSULE_UPLOAD.exists(), "historical capsule uploader source must remain auditable")
    require(CAPSULE_REPAIR.exists(), "historical capsule readback repair tool must remain available")
'''
if old not in text:
    raise SystemExit("target heartbeat capsule workflow test block changed unexpectedly")
text = text.replace(old, new)
text = text.replace(
    "    test_capsule_workflow_preserves_upload_result_before_status_update()\n",
    "    test_standalone_capsule_workflow_is_retired_but_historical_tools_remain()\n",
)
PATH.write_text(text, encoding="utf-8")
