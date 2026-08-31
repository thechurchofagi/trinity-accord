#!/usr/bin/env python3
"""Publish non-authoritative live telemetry for Bitcoin checkpoint runs.

This helper intentionally has no role in checkpoint validity, Bitcoin consensus
verification, or release-manifest construction.  It publishes a mutable GitHub
prerelease body so operators can inspect a running IBD without waiting for the
long-running Actions step to finish.

Publishing is best-effort by design: GitHub telemetry failures are reported as
workflow warnings and return success so an observability outage cannot invalidate
or interrupt otherwise-correct Bitcoin verification.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "trinity-accord.bitcoin-consensus-live-telemetry.v1"
DEFAULT_TAG = "bitcoin-consensus-live"
TITLE = "Bitcoin Consensus Live Telemetry (non-authoritative)"


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
    """Build the small public status object.

    Only operational values are copied.  No environment dump, credentials,
    cookies, peer addresses, or debug-log content are ever included.
    """

    height = chain.get("blocks")
    headers = chain.get("headers")
    header_backlog = None
    if isinstance(height, int) and isinstance(headers, int):
        header_backlog = max(headers - height, 0)

    return {
        "schema": SCHEMA,
        "authoritative": False,
        "purpose": "live_observability_only_not_consensus_evidence",
        "phase": phase,
        "observed_at": observed_at,
        "repository": env.get("GITHUB_REPOSITORY"),
        "run_id": env.get("GITHUB_RUN_ID"),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "workflow_sha": env.get("GITHUB_SHA"),
        "run_url": (
            f"https://github.com/{env.get('GITHUB_REPOSITORY')}/actions/runs/{env.get('GITHUB_RUN_ID')}"
            if env.get("GITHUB_REPOSITORY") and env.get("GITHUB_RUN_ID")
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
        "**NON-AUTHORITATIVE LIVE TELEMETRY.** This mutable prerelease is only an "
        "operational window into the currently running GitHub-hosted Bitcoin Core job. "
        "It is not a checkpoint, not consensus evidence, and never participates in "
        "verification decisions.\n\n"
        "```json\n"
        f"{rendered}\n"
        "```\n"
    )


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def publish_markdown(markdown: str, *, tag: str, env: dict[str, str]) -> bool:
    repo = env.get("GITHUB_REPOSITORY")
    sha = env.get("GITHUB_SHA")
    if not repo or not sha:
        print("::warning::live telemetry skipped: missing GITHUB_REPOSITORY or GITHUB_SHA")
        return False

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(markdown)
        notes_path = handle.name

    try:
        edit = _run_gh(
            [
                "release",
                "edit",
                tag,
                "--repo",
                repo,
                "--title",
                TITLE,
                "--notes-file",
                notes_path,
                "--prerelease",
            ]
        )
        if edit.returncode == 0:
            return True

        create = _run_gh(
            [
                "release",
                "create",
                tag,
                "--repo",
                repo,
                "--target",
                sha,
                "--title",
                TITLE,
                "--notes-file",
                notes_path,
                "--prerelease",
            ]
        )
        if create.returncode == 0:
            return True

        # A concurrent create between edit/create is unlikely because the
        # checkpoint workflow is serialized, but one final edit makes the
        # publisher race-tolerant without making telemetry authoritative.
        retry_edit = _run_gh(
            [
                "release",
                "edit",
                tag,
                "--repo",
                repo,
                "--title",
                TITLE,
                "--notes-file",
                notes_path,
                "--prerelease",
            ]
        )
        if retry_edit.returncode == 0:
            return True

        detail = retry_edit.stderr.strip() or create.stderr.strip() or edit.stderr.strip()
        print(f"::warning::live telemetry publish failed: {detail[:1000]}")
        return False
    finally:
        try:
            Path(notes_path).unlink()
        except OSError:
            pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--chain-info-file")
    parser.add_argument("--network-info-file")
    parser.add_argument("--free-kib")
    parser.add_argument("--seconds-remaining")
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        chain = _read_json(args.chain_info_file)
        network = _read_json(args.network_info_file)
        payload = build_payload(
            phase=args.phase,
            chain=chain,
            network=network,
            free_kib=_int_or_none(args.free_kib),
            seconds_remaining=_int_or_none(args.seconds_remaining),
            observed_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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

    publish_markdown(markdown, tag=args.tag, env=dict(os.environ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
