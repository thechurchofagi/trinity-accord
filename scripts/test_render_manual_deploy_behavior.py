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
    old_argv = sys.argv
    old_render = os.environ.get("RENDER")
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        os.environ["RENDER"] = "test-token"
        sys.argv = [str(MODULE_PATH), "--service", "example-service"]
        if deploy:
            sys.argv.append("--deploy")
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
    }
    code, _stdout, stderr, calls = invoke(active, {})
    require(code == 1 and calls == 1, "missing deploy ID must fail after one POST")
    require("without returning a deploy id" in stderr.lower(), "missing deploy ID failure must be explicit")

    code, stdout, stderr, calls = invoke(active, {"deploy": {"id": "dep-confirmed"}})
    require(code == 0 and calls == 1, "confirmed deploy response must succeed")
    require(not stderr, "confirmed deploy should not write stderr")
    require("deploy_id=dep-confirmed" in stdout, "confirmed deploy ID must be reported")

    code, stdout, stderr, calls = invoke(suspended, {}, deploy=False)
    require(code == 0 and calls == 0 and not stderr, "dry-run should disclose suspended service without attempting a deploy")
    require("dry_run" in stdout.lower(), "dry-run result must be explicit")

    print("PASS: Render helper fails closed on suspended or unconfirmed deploys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
