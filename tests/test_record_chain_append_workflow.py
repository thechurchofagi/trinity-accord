"""Tests for the record-chain append GitHub Actions workflow."""
from __future__ import annotations

from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "record-chain-append.yml"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


class TestRecordChainAppendWorkflow:
    def test_append_step_outputs_changed_only_from_record_chain_diff(self):
        workflow = _workflow_text()
        assert "- name: Append pending records" in workflow
        assert "id: append_run" in workflow
        assert "python scripts/trinity_record_chain.py append --all" in workflow
        assert "git diff --quiet -- record-chain/" in workflow
        assert '"changed=false"' in workflow
        assert '"changed=true"' in workflow

    def test_status_commit_is_skipped_when_append_makes_no_record_chain_change(self):
        workflow = _workflow_text()
        guarded_steps = [
            "- name: Verify record chain after append",
            "- name: Commit and push append updates",
        ]
        guard = "if: steps.append_run.outputs.changed == 'true'"
        for step in guarded_steps:
            step_index = workflow.find(step)
            assert step_index != -1, f"missing workflow step: {step}"
            guard_index = workflow.find(guard, step_index)
            assert guard_index != -1, f"missing guard after workflow step: {step}"
            next_step_index = workflow.find("\n      - name:", step_index + 1)
            if next_step_index != -1:
                assert guard_index < next_step_index, f"guard for {step} must appear before the next step"

        # Status generation is handled by homepage-status-sync.yml via workflow_run trigger.
        # The append workflow must NOT directly commit generated status files.
        assert "generate_public_home_status" not in workflow, "append workflow must not run homepage status generator; use homepage-status-sync.yml"
        assert "generate_record_chain_status" not in workflow, "append workflow must not run record-chain status generator; use homepage-status-sync.yml"
