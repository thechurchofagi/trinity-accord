#!/usr/bin/env python3
"""Static checks for Guardian auto-list workflow rebase retry and comment upsert."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "guardian-registry-auto-list.yml"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = WORKFLOW.read_text(encoding="utf-8")

    require("Rebase and retry direct push" in text, "workflow missing rebase retry step")
    require("git fetch origin main" in text, "workflow missing git fetch before rebase")
    require("git rebase origin/main" in text, "workflow missing rebase onto origin/main")
    require("git rebase --abort || true" in text, "workflow should abort failed rebase before fallback")
    require("push_main_rebased" in text, "workflow missing push_main_rebased step id/condition")
    require(
        "steps.push_main.outcome != \'success\' && steps.push_main_rebased.outcome != \'success\'" in text
        or "push_main.outcome != 'success' && steps.push_main_rebased.outcome != 'success'" in text,
        "fallback must require both direct push and rebased push to fail",
    )

    require("upsertWorkflowComment" in text, "workflow missing comment upsert helper")
    require("issues.listComments" in text, "workflow should list existing comments before writing")
    require("issues.updateComment" in text, "workflow should update existing bot marker comment")
    require("trinity-guardian-auto-registration:v1" in text, "workflow missing registration marker")

    print("GUARDIAN_WORKFLOW_REBASE_RETRY_AND_COMMENT_UPSERT_OK")


if __name__ == "__main__":
    main()
