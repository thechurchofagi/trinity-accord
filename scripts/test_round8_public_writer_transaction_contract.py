#!/usr/bin/env python3
"""Round 8 contract for Echo/public-index writers and Render deployment."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_WRITERS = [
    ".github/workflows/build-echo-index.yml",
    ".github/workflows/echo-human-review-action.yml",
    ".github/workflows/rebuild-agent-declared-index.yml",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    target = ROOT / path
    require(target.exists(), f"missing {path}")
    return target.read_text(encoding="utf-8")


def validate_yaml(path: str, content: str) -> None:
    try:
        parsed = yaml.safe_load(content)
    except Exception as exc:
        fail(f"invalid YAML {path}: {exc}")
    require(isinstance(parsed, dict), f"workflow is not a mapping: {path}")


def validate_public_writer(path: str) -> str:
    content = read(path)
    validate_yaml(path, content)
    for marker in [
        "contents: write",
        "group: main-write-lock",
        "queue: max",
        "ref: main",
        "git push origin HEAD:main",
        "set -euo pipefail",
    ]:
        require(marker in content, f"{path} missing transaction marker: {marker}")
    for forbidden in [
        "git push --force",
        "git push --force-with-lease",
        "git pull --rebase -X theirs",
        "${GITHUB_REF_NAME",
    ]:
        require(forbidden not in content, f"{path} retains unsafe marker: {forbidden}")
    for line in content.splitlines():
        require(line.strip() != "git push", f"{path} retains bare git push")
    return content


def main() -> int:
    workflows = {path: validate_public_writer(path) for path in PUBLIC_WRITERS}

    echo_index = workflows[".github/workflows/build-echo-index.yml"]
    require("branches:\n      - main" in echo_index, "Echo index push trigger is not main-only")
    require("rebuild_and_stage" in echo_index, "Echo index lacks a shared rebuild/stage transaction")
    require(
        echo_index.find("git add \\") < echo_index.find("git diff --cached --quiet"),
        "Echo index checks for changes before staging new-quarter files",
    )
    require(
        echo_index.count("rebuild_and_stage") >= 3,
        "Echo index is not regenerated after a push-time rebase",
    )

    human = workflows[".github/workflows/echo-human-review-action.yml"]
    require("Rebase current main before review action" in human, "Echo human review does not start from current main")
    require("rebuild_and_stage" in human, "Echo human review lacks derived-index reconciliation")
    require(
        human.find("git push origin HEAD:main") < human.find("gh issue close"),
        "Echo issue may close before the reviewed archive is durable on main",
    )
    require(
        human.count("rebuild_and_stage") >= 3,
        "Echo human review does not rebuild projections after rebase",
    )

    agent = workflows[".github/workflows/rebuild-agent-declared-index.yml"]
    require("actions: write" in agent, "Agent-declared index cannot dispatch Pages with the workflow token")
    require("gh workflow run deploy-pages.yml" in agent, "Agent-declared index lacks fail-closed Pages dispatch")
    require("GH_PAT" not in agent, "Agent-declared index still depends on a broad PAT")
    require("curl -sS" not in agent, "Agent-declared index still uses non-failing curl dispatch")
    require('[[ "$ACTOR" == "github-actions[bot]"' in agent, "Agent-declared actor gate still has a Bash case-pattern trap")

    render_path = ".github/workflows/render-manual-deploy.yml"
    render = read(render_path)
    validate_yaml(render_path, render)
    for marker in [
        "contents: read",
        "github.ref == 'refs/heads/main'",
        "Authorize production deployment actor and ref",
        "ref: main",
        "secrets.RENDER",
        "set -euo pipefail",
    ]:
        require(marker in render, f"Render deploy workflow missing: {marker}")
    require("contents: write" not in render, "Render deploy workflow has unnecessary repository write permission")
    require("workflow_run:" not in render and "schedule:" not in render and "push:" not in render, "Render deploy has an automatic trigger")

    print("PASS: Round 8 public writers rebuild after rebase and Render deploy is main-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
