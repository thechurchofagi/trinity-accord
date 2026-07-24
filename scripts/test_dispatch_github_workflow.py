#!/usr/bin/env python3
"""Regression tests for bounded GitHub workflow-dispatch retries."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "dispatch_github_workflow.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("dispatch_github_workflow", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load dispatch helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER_MODULE = load_helper()


class SequenceRunner:
    def __init__(self, results: list[subprocess.CompletedProcess[str]]) -> None:
        self.results = list(results)
        self.calls: list[list[str]] = []

    def __call__(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(list(command))
        if not self.results:
            raise AssertionError("dispatch helper made an unexpected extra attempt")
        return self.results.pop(0)


def completed(
    returncode: int,
    *,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["gh"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def run_quiet(**kwargs) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
        io.StringIO()
    ):
        return HELPER_MODULE.dispatch_workflow(**kwargs)


def test_build_command_keeps_inputs_as_separate_arguments() -> None:
    command = HELPER_MODULE.build_command(
        "record-chain-append.yml",
        repository="owner/repo",
        ref="main",
        fields=["receipt_id=rcg-1", "pending_file_path=record-chain/pending/a.json"],
    )
    assert command == [
        "gh",
        "workflow",
        "run",
        "record-chain-append.yml",
        "--repo",
        "owner/repo",
        "--ref",
        "main",
        "-f",
        "receipt_id=rcg-1",
        "-f",
        "pending_file_path=record-chain/pending/a.json",
    ]


def test_http_500_retries_then_succeeds() -> None:
    runner = SequenceRunner(
        [
            completed(1, stderr="HTTP 500: Failed to run workflow dispatch"),
            completed(0),
        ]
    )
    delays: list[float] = []
    result = run_quiet(
        workflow="record-chain-append.yml",
        repository="owner/repo",
        max_attempts=5,
        base_delay_seconds=5,
        runner=runner,
        sleeper=delays.append,
    )
    assert result == 0
    assert len(runner.calls) == 2
    assert delays == [5]


def test_http_429_and_network_timeout_are_retryable() -> None:
    runner = SequenceRunner(
        [
            completed(1, stderr="HTTP 429: rate limited"),
            completed(1, stderr="request timed out"),
            completed(0),
        ]
    )
    delays: list[float] = []
    result = run_quiet(
        workflow="record-chain-append.yml",
        repository="owner/repo",
        max_attempts=5,
        base_delay_seconds=2,
        runner=runner,
        sleeper=delays.append,
    )
    assert result == 0
    assert len(runner.calls) == 3
    assert delays == [2, 4]


def test_permission_and_validation_failures_do_not_retry() -> None:
    for message in (
        "HTTP 403: Resource not accessible by integration",
        "HTTP 404: workflow not found",
        "HTTP 422: Validation Failed",
    ):
        runner = SequenceRunner([completed(1, stderr=message), completed(0)])
        delays: list[float] = []
        result = run_quiet(
            workflow="record-chain-append.yml",
            repository="owner/repo",
            runner=runner,
            sleeper=delays.append,
        )
        assert result == 1
        assert len(runner.calls) == 1
        assert delays == []


def test_persistent_transient_failure_is_bounded() -> None:
    runner = SequenceRunner(
        [
            completed(1, stderr="HTTP 502: upstream failure"),
            completed(1, stderr="HTTP 503: unavailable"),
            completed(1, stderr="HTTP 500: failed"),
        ]
    )
    delays: list[float] = []
    result = run_quiet(
        workflow="record-chain-append.yml",
        repository="owner/repo",
        max_attempts=3,
        base_delay_seconds=1,
        runner=runner,
        sleeper=delays.append,
    )
    assert result == 1
    assert len(runner.calls) == 3
    assert delays == [1, 2]


if __name__ == "__main__":
    test_build_command_keeps_inputs_as_separate_arguments()
    test_http_500_retries_then_succeeds()
    test_http_429_and_network_timeout_are_retryable()
    test_permission_and_validation_failures_do_not_retry()
    test_persistent_transient_failure_is_bounded()
    print("PASS: GitHub workflow dispatch retries are bounded and selective")
