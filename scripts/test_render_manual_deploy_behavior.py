#!/usr/bin/env python3
"""Behavioral regressions for the Render manual deployment helper."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_manual_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_manual_deploy_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load render_manual_deploy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke(
    service: dict[str, Any],
    request_result: Any | Callable[..., Any],
    *,
    deploy: bool = True,
    commit_id: str = "",
    wait: bool = False,
) -> tuple[int, str, str, int]:
    module = load_module()
    request_calls = 0

    module.find_service = lambda _token, _name: dict(service)

    def fake_request(*args, **kwargs):
        nonlocal request_calls
        request_calls += 1
        if callable(request_result):
            return request_result(*args, **kwargs)
        return request_result

    module.request = fake_request
    module.time.sleep = lambda _seconds: None
    old_argv = sys.argv
    old_render = os.environ.get("RENDER")
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        os.environ["RENDER"] = "test-token"
        sys.argv = [str(MODULE_PATH), "--service", "example-service"]
        if deploy:
            sys.argv.append("--deploy")
        if commit_id:
            sys.argv += ["--commit-id", commit_id]
        sys.argv += ["--deploy-id-recovery-timeout", "0"]
        if wait:
            sys.argv += [
                "--wait",
                "--wait-timeout",
                "5",
                "--poll-seconds",
                "0",
            ]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = module.main()
            except SystemExit as exc:
                code = int(exc.code or 0)
    finally:
        sys.argv = old_argv
        if old_render is None:
            os.environ.pop("RENDER", None)
        else:
            os.environ["RENDER"] = old_render
    return code, stdout.getvalue(), stderr.getvalue(), request_calls


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    suspended = {
        "id": "srv-suspended",
        "name": "example-service",
        "suspended": "suspended",
        "suspenders": ["user"],
    }
    code, stdout, stderr, calls = invoke(suspended, {})
    require(code == 1, "suspended service deployment must fail")
    require(calls == 0, "suspended service must fail before POSTing a deploy")
    require("suspended" in stdout.lower() and "no deployment was created" in stderr.lower(), "suspension failure must be explicit")

    active = {
        "id": "srv-active",
        "name": "example-service",
        "suspended": "not_suspended",
        "suspenders": [],
        "autoDeploy": "no",
    }
    def accepted_without_id(path: str, _token: str, method: str = "GET", body: dict | None = None):
        if method == "POST":
            return {}
        if path.endswith("/deploys?limit=20"):
            return []
        return {}

    code, _stdout, stderr, calls = invoke(active, accepted_without_id)
    require(
        code == 1 and calls == 2,
        "missing deploy ID without an exact recoverable candidate must fail after POST and one list read",
    )
    require(
        "no unique exact-commit deploy" in stderr.lower(),
        "missing deploy ID recovery failure must be explicit",
    )

    code, stdout, stderr, calls = invoke(active, {"deploy": {"id": "dep-confirmed"}})
    require(code == 0 and calls == 1, "confirmed deploy response must succeed")
    require(not stderr, "confirmed deploy should not write stderr")
    require("deploy_id=dep-confirmed" in stdout, "confirmed deploy ID must be reported")

    exact_commit = "a" * 40
    observed_calls: list[tuple[str, str, dict[str, Any]]] = []

    def exact_live(path: str, _token: str, method: str = "GET", body: dict | None = None):
        observed_calls.append((path, method, dict(body or {})))
        if method == "POST":
            return {
                "id": "dep-exact",
                "status": "build_in_progress",
                "commit": {"id": exact_commit},
            }
        return {
            "id": "dep-exact",
            "status": "live",
            "commit": {"id": exact_commit},
        }

    code, stdout, stderr, calls = invoke(
        active,
        exact_live,
        commit_id=exact_commit,
        wait=True,
    )
    require(code == 0 and calls == 2, "exact deploy must POST once and poll until live")
    require(not stderr, "exact live deploy should not write stderr")
    require(
        observed_calls[0][2].get("commitId") == exact_commit,
        "Render POST must bind the exact commitId",
    )
    require(
        f"RENDER_DEPLOY_LIVE service=example-service deploy_id=dep-exact commit_id={exact_commit}"
        in stdout,
        "exact live commit proof must be reported",
    )

    wrong_commit = "b" * 40

    def mismatched_live(path: str, _token: str, method: str = "GET", body: dict | None = None):
        return {
            "id": "dep-wrong",
            "status": "live",
            "commit": {"id": wrong_commit},
        }

    code, _stdout, stderr, _calls = invoke(
        active,
        mismatched_live,
        commit_id=exact_commit,
        wait=True,
    )
    require(code == 1, "commit mismatch must fail closed")
    require(
        "commit" in stderr.lower()
        and ("mismatch" in stderr.lower() or "unexpected" in stderr.lower()),
        "commit mismatch must be explicit",
    )

    auto_deploying = dict(active, autoDeploy="yes")
    code, _stdout, stderr, calls = invoke(
        auto_deploying,
        {},
        commit_id=exact_commit,
        wait=True,
    )
    require(
        code == 1 and calls == 0 and "autodeploy" in stderr.lower(),
        "exact deploy must refuse actual Render autodeploy drift before POST",
    )

    code, _stdout, stderr, calls = invoke(
        active,
        {},
        commit_id="A" * 40,
        wait=True,
    )
    require(
        code == 1 and calls == 0 and "lowercase" in stderr.lower(),
        "non-lowercase commit IDs must be rejected before POST",
    )

    code, stdout, stderr, calls = invoke(suspended, {}, deploy=False)
    require(code == 0 and calls == 0 and not stderr, "dry-run should disclose suspended service without attempting a deploy")
    require("dry_run" in stdout.lower(), "dry-run result must be explicit")

    print("PASS: Render helper proves the exact commit reaches live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
