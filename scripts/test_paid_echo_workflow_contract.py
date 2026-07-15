#!/usr/bin/env python3
"""Contract for the retired, read-only Echo Arweave cost audit."""

from pathlib import Path

WORKFLOW = Path(".github/workflows/paid-echo-arweave-canary.yml")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    header, jobs = text.split("jobs:", 1)
    job_env = jobs.split("steps:", 1)[0]

    require("Paid Canary Retired" in text, "workflow does not declare retirement")
    require("workflow_dispatch:" in header, "retired audit is not manual-only")
    require("contents: read" in header, "retired audit is not read-only")
    require("contents: write" not in text, "retired audit can write repository contents")
    require("secrets.ARKEY" not in text, "retired audit can access the wallet secret")
    require("git push" not in text, "retired audit retains a push path")
    require('ARWEAVE_UPLOAD_MODE: "dry_run"' in text, "audit is not pinned to dry-run mode")
    require('ALLOW_PAID_ARWEAVE_CANARY: "false"' in text, "paid canary is not disabled")
    require("runner.temp" not in job_env, "job-level env uses unavailable runner context")
    require("$RUNNER_TEMP/legacy-echo-arweave/" in text, "ephemeral audit directory is not initialized at runtime")

    print("PASS: retired Echo Arweave audit is parse-safe, manual-only, and read-only")


if __name__ == "__main__":
    main()
