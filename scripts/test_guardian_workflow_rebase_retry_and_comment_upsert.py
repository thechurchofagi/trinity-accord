#!/usr/bin/env python3
"""Static checks for Guardian auto-list workflow rebase retry and comment upsert."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "guardian-registry-auto-list.yml"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = WORKFLOW.read_text(encoding="utf-8")

    # --- Rebase retry ---
    require("Rebase and retry direct push" in text, "workflow missing rebase retry step")
    require("git fetch origin main" in text, "workflow missing git fetch before rebase")
    require("git rebase origin/main" in text, "workflow missing rebase onto origin/main")
    require("git rebase --abort || true" in text, "workflow should abort failed rebase before fallback")
    require("push_main_rebased" in text, "workflow missing push_main_rebased step id/condition")

    # The rebase step's own if must NOT reference its own outcome (push_main_rebased).
    rebase_block = re.search(
        r"- name: Rebase and retry direct push\n\s+if:\s*(.+)\n\s+id:\s*push_main_rebased",
        text,
    )
    require(rebase_block is not None, "Could not find rebase step if condition")
    rebase_if = rebase_block.group(1)
    require(
        "push_main_rebased" not in rebase_if,
        f"Rebase step must not reference its own outcome in if condition: {rebase_if}",
    )
    require(
        "push_main.outcome" in rebase_if,
        f"Rebase step if must check push_main.outcome: {rebase_if}",
    )

    # Fallback steps (branch, PR, comment) must require both pushes to fail.
    require(
        "steps.push_main.outcome != 'success' && steps.push_main_rebased.outcome != 'success'" in text,
        "fallback must require both direct push and rebased push to fail",
    )

    # Rebase step must output refreshed commit SHA.
    require(
        "rebased_commit_sha" in text,
        "rebase step should output rebased_commit_sha for use in success comment",
    )

    # --- Comment upsert ---
    require("upsertWorkflowComment" in text, "workflow missing comment upsert helper")
    require("issues.listComments" in text, "workflow should list existing comments before writing")
    require("issues.updateComment" in text, "workflow should update existing bot marker comment")
    require("trinity-guardian-auto-registration:v1" in text, "workflow missing registration marker")

    # All four comment steps must call upsertWorkflowComment (not raw createComment).
    upsert_calls = len(re.findall(r"await upsertWorkflowComment\(", text))
    require(
        upsert_calls >= 4,
        f"Expected at least 4 await upsertWorkflowComment() calls, found {upsert_calls}",
    )

    # Verify createComment is only used inside upsertWorkflowComment helper definitions,
    # not as a direct comment-posting mechanism in comment steps.
    # Strategy: split into step blocks (by "- name:"), check each block that is a comment step.
    comment_step_names = [
        "Comment complete after direct push",
        "Comment fallback PR created",
        "Comment already registered",
        "Comment blocked or write failed",
    ]

    # Split workflow into step blocks
    step_blocks = re.split(r"\n\s*- name: ", text)
    for block in step_blocks:
        # Get the step name (first line of block)
        first_line = block.split("\n")[0].strip()
        if first_line not in comment_step_names:
            continue

        # In a comment step, the script must contain "await upsertWorkflowComment("
        # and any createComment must be inside the helper function definition.
        # Find the script portion
        script_match = re.search(r"script:\s*\|(.+)", block, re.DOTALL)
        if not script_match:
            continue
        script = script_match.group(1)

        # Check that the script calls upsertWorkflowComment
        require(
            "await upsertWorkflowComment(" in script,
            f"Comment step '{first_line}' must call upsertWorkflowComment()",
        )

        # Find createComment calls outside the helper definition.
        # The helper is defined as "async function upsertWorkflowComment(...) {"
        # We track brace depth to know when we're inside the helper.
        lines = script.split("\n")
        in_helper = False
        brace_depth = 0
        bare_create_lines = []
        for line in lines:
            stripped = line.strip()
            if "async function upsertWorkflowComment" in stripped:
                in_helper = True
                brace_depth = 0
            if in_helper:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0:
                    in_helper = False
                    brace_depth = 0
                continue
            if "issues.createComment(" in stripped:
                bare_create_lines.append(stripped)

        require(
            len(bare_create_lines) == 0,
            f"Comment step '{first_line}' must use upsertWorkflowComment, not raw createComment. "
            f"Found bare createComment: {bare_create_lines}",
        )

    print("GUARDIAN_WORKFLOW_REBASE_RETRY_AND_COMMENT_UPSERT_OK")


if __name__ == "__main__":
    main()
