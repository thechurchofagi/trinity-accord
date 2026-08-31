#!/usr/bin/env python3
"""Publish non-authoritative live telemetry for Bitcoin checkpoint runs.

This helper intentionally has no role in checkpoint validity, Bitcoin consensus
verification, or release-manifest construction. It updates one GitHub Check Run
for the active workflow run so operators can inspect IBD progress while the
long-running Actions step is still executing.

Publishing is best-effort by design: telemetry failures emit workflow warnings
and return success so an observability outage cannot invalidate otherwise-correct
Bitcoin verification.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "trinity-accord.bitcoin-consensus-live-telemetry.v1"
CHECK_NAME = "Bitcoin Consensus Live Telemetry (non-authoritative)"
CHECK_TITLE = "Bitcoin consensus live telemetry — non-authoritative"


def _read_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read telemetry JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"telemetry JSON must be an object: {path}")
    return value


def _int_or_none(value: str | None) -> int | None:
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"expected integer, got {value!r}") from exc


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_payload(
    *,
    phase: str,
    chain: dict[str, Any],
    network: dict[str, Any],
    free_kib: int | None,
    seconds_remaining: int | None,
    observed_at: str,
    env: dict[str, str],
) -> dict[str, Any]:
    """Build the small public status object from an explicit allow-list."""

    height = chain.get("blocks")
    headers = chain.get("headers")
    header_backlog = None
    if isinstance(height, int) and isinstance(headers, int):
        header_backlog = max(headers - height, 0)

    repository = env.get("GITHUB_REPOSITORY")
    run_id = env.get("GITHUB_RUN_ID")
    return {
        "schema": SCHEMA,
        "authoritative": False,
        "purpose": "live_observability_only_not_consensus_evidence",
        "phase": phase,
        "observed_at": observed_at,
        "repository": repository,
        "run_id": run_id,
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "workflow_sha": env.get("GITHUB_SHA"),
        "workflow_job_status": env.get("BITCOIN_TELEMETRY_JOB_STATUS"),
        "run_url": (
            f"https://github.com/{repository}/actions/runs/{run_id}"
            if repository and run_id
            else None
        ),
        "bitcoin": {
            "chain": chain.get("chain"),
            "height": height,
            "headers": headers,
            "header_backlog": header_backlog,
            "best_block_hash": chain.get("bestblockhash"),
            "verification_progress": chain.get("verificationprogress"),
            "initial_block_download": chain.get("initialblockdownload"),
            "size_on_disk": chain.get("size_on_disk"),
            "pruned": chain.get("pruned"),
            "prune_height": chain.get("pruneheight"),
            "warnings": chain.get("warnings"),
        },
        "network": {
            "active": network.get("networkactive"),
            "connections": network.get("connections"),
            "connections_in": network.get("connections_in"),
            "connections_out": network.get("connections_out"),
        },
        "runner": {
            "free_kib": free_kib,
            "seconds_remaining_in_sync_window": seconds_remaining,
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    rendered = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False)
    return (
        "**NON-AUTHORITATIVE LIVE TELEMETRY.** This mutable Check Run is only an "
        "operational window into the currently running GitHub-hosted Bitcoin Core job. "
        "It is not a checkpoint, not consensus evidence, and never participates in "
        "verification decisions.\n\n"
        "```json\n"
        f"{rendered}\n"
        "```\n"
    )


def _run_gh_api(
    method: str,
    endpoint: str,
    payload: dict[str, Any],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", "api", "--method", method, endpoint, "--input", "-"],
        input=json.dumps(payload, separators=(",", ":")),
        check=False,
        capture_output=True,
        text=True,
    )


def _read_check_id(path: Path) -> int | None:
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError as exc:
        print(f"::warning::could not read live telemetry check id: {exc}")
        return None
    if not raw.isdigit():
        print("::warning::live telemetry check id file is malformed")
        return None
    return int(raw)


def _write_check_id(path: Path, check_id: int) -> bool:
    try:
        path.write_text(f"{check_id}\n", encoding="utf-8")
        return True
    except OSError as exc:
        print(f"::warning::could not persist live telemetry check id: {exc}")
        return False


def _check_output(markdown: str) -> dict[str, str]:
    return {"title": CHECK_TITLE, "summary": markdown}


def publish_check(
    markdown: str,
    *,
    env: dict[str, str],
    complete: bool,
    conclusion: str,
) -> bool:
    repo = env.get("GITHUB_REPOSITORY")
    sha = env.get("GITHUB_SHA")
    id_file_value = env.get("BITCOIN_LIVE_CHECK_RUN_ID_FILE")
    if not repo or not sha or not id_file_value:
        print(
            "::warning::live telemetry skipped: missing GITHUB_REPOSITORY, "
            "GITHUB_SHA, or BITCOIN_LIVE_CHECK_RUN_ID_FILE"
        )
        return False

    id_file = Path(id_file_value)
    check_id = _read_check_id(id_file)
    status = "completed" if complete else "in_progress"
    run_url = (
        f"https://github.com/{repo}/actions/runs/{env['GITHUB_RUN_ID']}"
        if env.get("GITHUB_RUN_ID")
        else None
    )

    if check_id is not None:
        patch: dict[str, Any] = {
            "status": status,
            "output": _check_output(markdown),
        }
        if run_url:
            patch["details_url"] = run_url
        if complete:
            patch["conclusion"] = conclusion
            patch["completed_at"] = _utc_now()
        result = _run_gh_api("PATCH", f"repos/{repo}/check-runs/{check_id}", patch)
        if result.returncode == 0:
            return True
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"::warning::live telemetry check update failed: {detail[:1000]}")
        return False

    create: dict[str, Any] = {
        "name": CHECK_NAME,
        "head_sha": sha,
        "status": status,
        "output": _check_output(markdown),
    }
    if run_url:
        create["details_url"] = run_url
    if complete:
        create["conclusion"] = conclusion
        create["completed_at"] = _utc_now()

    result = _run_gh_api("POST", f"repos/{repo}/check-runs", create)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"::warning::live telemetry check creation failed: {detail[:1000]}")
        return False

    try:
        response = json.loads(result.stdout)
        created_id = response["id"]
        if not isinstance(created_id, int):
            raise ValueError("check id is not an integer")
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"::warning::live telemetry check response is malformed: {exc}")
        return False
    return _write_check_id(id_file, created_id)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--chain-info-file")
    parser.add_argument("--network-info-file")
    parser.add_argument("--free-kib")
    parser.add_argument("--seconds-remaining")
    parser.add_argument("--complete", action="store_true")
    parser.add_argument("--conclusion", default="neutral")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = build_payload(
            phase=args.phase,
            chain=_read_json(args.chain_info_file),
            network=_read_json(args.network_info_file),
            free_kib=_int_or_none(args.free_kib),
            seconds_remaining=_int_or_none(args.seconds_remaining),
            observed_at=_utc_now(),
            env=dict(os.environ),
        )
        markdown = render_markdown(payload)
    except ValueError as exc:
        print(f"::warning::live telemetry input error: {exc}")
        return 0

    status_path = os.environ.get("BITCOIN_LIVE_TELEMETRY_JSON")
    if status_path:
        try:
            Path(status_path).write_text(
                json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"::warning::could not write local live telemetry JSON: {exc}")

    if args.dry_run:
        print(markdown, end="")
        return 0

    publish_check(
        markdown,
        env=dict(os.environ),
        complete=args.complete,
        conclusion=args.conclusion,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
