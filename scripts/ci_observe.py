#!/usr/bin/env python3
"""Observable command runner for GitHub Actions.

Posts a compact commit status that exposes the current stage/run URL, writes
machine-readable workflow telemetry, and emits periodic heartbeats while a
child process runs. Observability failures never change proof acceptance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

DEFAULT_ROOT = pathlib.Path(
    os.getenv(
        "CHRONICLE_OBSERVABILITY_DIR",
        "artifacts/chronicle-polygon-ethereum-settlement",
    )
)
STATUS_CONTEXT = os.getenv("CHRONICLE_STATUS_CONTEXT", "trinity/settlement")
HEARTBEAT_SECONDS = int(os.getenv("CHRONICLE_OBSERVABILITY_HEARTBEAT_SECONDS", "120"))
STALL_WARN_SECONDS = int(os.getenv("CHRONICLE_OBSERVABILITY_STALL_WARN_SECONDS", "600"))


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def out_root() -> pathlib.Path:
    DEFAULT_ROOT.mkdir(parents=True, exist_ok=True)
    return DEFAULT_ROOT


def telemetry(event: str, **fields) -> None:
    root = out_root()
    row = {"ts": utcnow(), "event": event, **fields}
    with (root / "WORKFLOW-OBSERVABILITY.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    print(
        "[CI-OBSERVE] "
        + event
        + (" " if fields else "")
        + " ".join(f"{k}={v}" for k, v in fields.items()),
        flush=True,
    )


def run_url() -> str:
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repo = os.getenv("GITHUB_REPOSITORY", "")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    if repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return server


def state_path() -> pathlib.Path:
    return out_root() / "CURRENT-STAGE.json"


def write_stage(state: str, stage: str, message: str) -> None:
    state_path().write_text(
        json.dumps(
            {
                "ts": utcnow(),
                "state": state,
                "stage": stage,
                "message": message,
                "run_id": os.getenv("GITHUB_RUN_ID"),
                "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
                "sha": os.getenv("GITHUB_SHA"),
                "url": run_url(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def post_status(state: str, stage: str, message: str) -> bool:
    write_stage(state, stage, message)
    repo = os.getenv("GITHUB_REPOSITORY")
    sha = os.getenv("GITHUB_SHA")
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    description = f"{stage}: {message}"
    if len(description) > 140:
        description = description[:137] + "..."
    telemetry(
        "status_update",
        state=state,
        stage=stage,
        description=description,
        run_id=os.getenv("GITHUB_RUN_ID"),
    )
    if not (repo and sha and token):
        telemetry(
            "status_skipped",
            reason="missing GITHUB_REPOSITORY/GITHUB_SHA/GH_TOKEN",
            stage=stage,
        )
        return False

    payload = json.dumps(
        {
            "state": state,
            "context": STATUS_CONTEXT,
            "description": description,
            "target_url": run_url(),
        }
    ).encode("utf-8")
    url = f"{api}/repos/{repo}/statuses/{sha}"
    last_error = None
    for attempt, delay in enumerate((0, 1, 2), start=1):
        if delay:
            time.sleep(delay)
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "accept": "application/vnd.github+json",
                "authorization": f"Bearer {token}",
                "content-type": "application/json",
                "user-agent": "trinity-accord-ci-observe/1.0",
                "x-github-api-version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                response.read()
            telemetry("status_post_ok", stage=stage, attempt=attempt, state=state)
            return True
        except Exception as exc:
            last_error = repr(exc)
            telemetry(
                "status_post_error",
                stage=stage,
                attempt=attempt,
                error=last_error,
            )
    telemetry("status_post_gave_up", stage=stage, error=last_error)
    return False


def last_debug_event(path: pathlib.Path | None) -> tuple[str | None, int | None, float | None]:
    if path is None or not path.exists():
        return None, None, None
    try:
        size = path.stat().st_size
        mtime = path.stat().st_mtime
        with path.open("rb") as fh:
            seek = min(size, 65536)
            fh.seek(-seek, os.SEEK_END)
            data = fh.read().decode("utf-8", errors="replace")
        lines = [line for line in data.splitlines() if line.strip()]
        event = None
        if lines:
            try:
                row = json.loads(lines[-1])
                event = str(row.get("event") or "unknown")
            except json.JSONDecodeError:
                event = "unparseable_last_line"
        return event, size, mtime
    except Exception as exc:
        telemetry("debug_probe_error", path=str(path), error=repr(exc))
        return "debug_probe_error", None, None


def cmd_status(args: argparse.Namespace) -> int:
    post_status(args.state, args.stage, args.message)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.command:
        raise SystemExit("missing child command after --")
    debug_file = pathlib.Path(args.debug_file) if args.debug_file else None
    started = time.monotonic()
    stage = args.stage
    post_status("pending", stage, "started")
    telemetry(
        "child_start",
        stage=stage,
        command=args.command,
        heartbeat_seconds=args.heartbeat_seconds,
        debug_file=str(debug_file) if debug_file else None,
    )
    proc = subprocess.Popen(args.command)
    last_debug_mtime = time.time()

    while True:
        try:
            rc = proc.wait(timeout=args.heartbeat_seconds)
            break
        except subprocess.TimeoutExpired:
            elapsed = int(time.monotonic() - started)
            event, size, mtime = last_debug_event(debug_file)
            if mtime is not None:
                last_debug_mtime = mtime
            stale = max(0, int(time.time() - last_debug_mtime))
            if event:
                message = f"{elapsed}s; debug={event}; bytes={size}; stale={stale}s"
            else:
                message = f"{elapsed}s; child alive; no debug file yet"
            if stale >= args.stall_warn_seconds:
                message = f"possible stall; {message}"
                telemetry(
                    "stall_warning",
                    stage=stage,
                    elapsed_seconds=elapsed,
                    stale_seconds=stale,
                    last_debug_event=event,
                )
            post_status("pending", stage, message)
            telemetry(
                "heartbeat",
                stage=stage,
                elapsed_seconds=elapsed,
                debug_event=event,
                debug_bytes=size,
                debug_stale_seconds=stale,
            )

    elapsed = int(time.monotonic() - started)
    event, size, _ = last_debug_event(debug_file)
    if rc == 0:
        post_status("pending", stage, f"completed in {elapsed}s; last={event or 'n/a'}")
        telemetry(
            "child_complete",
            stage=stage,
            exit_code=rc,
            elapsed_seconds=elapsed,
            debug_event=event,
            debug_bytes=size,
        )
        return 0

    post_status(
        "failure",
        stage,
        f"failed rc={rc} after {elapsed}s; last={event or 'n/a'}",
    )
    telemetry(
        "child_failed",
        stage=stage,
        exit_code=rc,
        elapsed_seconds=elapsed,
        debug_event=event,
        debug_bytes=size,
    )
    return rc


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="subcommand", required=True)

    s = sub.add_parser("status")
    s.add_argument("--state", required=True, choices=["pending", "success", "failure", "error"])
    s.add_argument("--stage", required=True)
    s.add_argument("--message", required=True)
    s.set_defaults(func=cmd_status)

    r = sub.add_parser("run")
    r.add_argument("--stage", required=True)
    r.add_argument("--debug-file")
    r.add_argument("--heartbeat-seconds", type=int, default=HEARTBEAT_SECONDS)
    r.add_argument("--stall-warn-seconds", type=int, default=STALL_WARN_SECONDS)
    r.add_argument("command", nargs=argparse.REMAINDER)
    r.set_defaults(func=cmd_run)
    return p


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
