#!/usr/bin/env python3
"""Dispatch a GitHub Actions workflow with bounded transient-error retries.

GitHub may accept a workflow-dispatch request and still return a 5xx response.
Callers must therefore use this helper only for idempotent downstream workflows:
a retry can legitimately create more than one run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from collections.abc import Callable, Sequence


RETRYABLE_HTTP = re.compile(r"\bHTTP\s+(?:408|429|5\d\d)\b", re.IGNORECASE)
RETRYABLE_NETWORK = re.compile(
    r"(?:"
    r"\btimeout\b|timed\s+out|"
    r"connection\s+(?:reset|refused|closed|aborted)|"
    r"temporary\s+failure|temporarily\s+unavailable|"
    r"tls\s+handshake|unexpected\s+eof|\beof\b|"
    r"network\s+is\s+unreachable"
    r")",
    re.IGNORECASE,
)

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1 or parsed > 10:
        raise argparse.ArgumentTypeError("must be between 1 and 10")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0 or parsed > 60:
        raise argparse.ArgumentTypeError("must be between 0 and 60")
    return parsed


def build_command(
    workflow: str,
    *,
    repository: str,
    ref: str,
    fields: Sequence[str],
) -> list[str]:
    command = [
        "gh",
        "workflow",
        "run",
        workflow,
        "--repo",
        repository,
        "--ref",
        ref,
    ]
    for field in fields:
        command.extend(["-f", field])
    return command


def default_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
    )


def emit_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(
            result.stderr,
            end="" if result.stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )


def is_retryable_failure(output: str) -> bool:
    return bool(RETRYABLE_HTTP.search(output) or RETRYABLE_NETWORK.search(output))


def dispatch_workflow(
    workflow: str,
    *,
    repository: str,
    ref: str = "main",
    fields: Sequence[str] = (),
    max_attempts: int = 5,
    base_delay_seconds: float = 5.0,
    runner: Runner = default_runner,
    sleeper: Sleeper = time.sleep,
) -> int:
    command = build_command(
        workflow,
        repository=repository,
        ref=ref,
        fields=fields,
    )

    for attempt in range(1, max_attempts + 1):
        try:
            result = runner(command)
        except OSError as exc:
            print(f"::error::Could not execute GitHub CLI: {exc}", file=sys.stderr)
            return 127

        emit_output(result)
        if result.returncode == 0:
            print(
                f"DISPATCH_WORKFLOW_OK workflow={workflow} "
                f"attempt={attempt}/{max_attempts}"
            )
            return 0

        exit_code = result.returncode if result.returncode > 0 else 1
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        if not is_retryable_failure(output):
            print(
                f"::error::Non-retryable workflow dispatch failure for {workflow}; "
                "not retrying.",
                file=sys.stderr,
            )
            return exit_code

        if attempt == max_attempts:
            print(
                f"::error::Workflow dispatch for {workflow} still failed after "
                f"{max_attempts} transient-error attempts.",
                file=sys.stderr,
            )
            return exit_code

        delay = min(base_delay_seconds * (2 ** (attempt - 1)), 60.0)
        print(
            f"::warning::Transient workflow dispatch failure for {workflow}; "
            f"retrying attempt {attempt + 1}/{max_attempts} in {delay:g}s.",
            file=sys.stderr,
        )
        sleeper(delay)

    return 1


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", help="Workflow file name or workflow id")
    parser.add_argument("--repo", required=True, help="Repository in owner/name form")
    parser.add_argument("--ref", default="main", help="Git ref for the dispatch")
    parser.add_argument(
        "-f",
        "--field",
        action="append",
        default=[],
        help="Workflow input in key=value form; may be repeated",
    )
    parser.add_argument("--max-attempts", type=positive_int, default=5)
    parser.add_argument(
        "--base-delay-seconds",
        type=nonnegative_float,
        default=5.0,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    return dispatch_workflow(
        args.workflow,
        repository=args.repo,
        ref=args.ref,
        fields=args.field,
        max_attempts=args.max_attempts,
        base_delay_seconds=args.base_delay_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
