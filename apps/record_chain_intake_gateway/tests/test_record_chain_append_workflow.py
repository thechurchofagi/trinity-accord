"""Tests for the record-chain append GitHub Actions workflow."""
from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "record-chain-append.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps() -> list[dict]:
    return _workflow()["jobs"]["append"]["steps"]


def _step_named(name: str) -> dict:
    for step in _steps():
        if step.get("name") == name:
            return step
    raise AssertionError(f"Missing workflow step: {name}")


class TestRecordChainAppendWorkflow:
    def test_append_step_outputs_changed_only_from_record_chain_diff(self):
        step = _step_named("Append pending records")
        assert step.get("id") == "append_run"
        run = step.get("run", "")
        assert "python scripts/trinity_record_chain.py append --all" in run
        assert "git diff --quiet -- record-chain/" in run
        assert '"changed=false"' in run
        assert '"changed=true"' in run

    def test_status_commit_is_skipped_when_append_makes_no_record_chain_change(self):
        gated_steps = [
            "Verify record chain after append",
            "Regenerate phase-aware public status and homepage counters",
            "Commit and push append updates",
        ]
        for name in gated_steps:
            step = _step_named(name)
            assert step.get("if") == "steps.append_run.outputs.changed == 'true'"
