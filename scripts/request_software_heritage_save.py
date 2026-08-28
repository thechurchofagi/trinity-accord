#!/usr/bin/env python3
"""Request and record a Software Heritage Save Code Now archival visit."""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://archive.softwareheritage.org/api/1/"
DEFAULT_ORIGIN = "https://github.com/thechurchofagi/trinity-accord"
TERMINAL = {"succeeded", "failed"}


def request_json(url: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(
        url,
        method=method,
        headers={
            "Accept": "application/json",
            "User-Agent": "Trinity-Accord-Preservation/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def submit(origin: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"visit_type": "git", "origin_url": origin})
    value = request_json(f"{API_BASE}origin/save/?{query}", method="POST")
    if not isinstance(value, dict):
        raise SystemExit("Software Heritage returned a non-object save response")
    return value


def status_url(value: dict[str, Any]) -> str:
    request_url = value.get("request_url")
    if isinstance(request_url, str) and request_url:
        return urllib.parse.urljoin(API_BASE, request_url)
    request_id = value.get("id")
    if not isinstance(request_id, int):
        raise SystemExit("Software Heritage save response has no request identifier")
    return f"{API_BASE}origin/save/{request_id}/"


def poll(
    initial: dict[str, Any], *, timeout_seconds: int, poll_seconds: int
) -> dict[str, Any]:
    current = initial
    if current.get("save_request_status") == "rejected":
        return current
    url = status_url(current)
    deadline = time.monotonic() + max(0, timeout_seconds)
    while time.monotonic() < deadline:
        task = str(current.get("save_task_status") or "")
        if task in TERMINAL:
            return current
        time.sleep(max(1, poll_seconds))
        value = request_json(url)
        if not isinstance(value, dict):
            raise SystemExit("Software Heritage returned a non-object status response")
        current = value
    return current


def validate(value: dict[str, Any], origin: str) -> None:
    if value.get("origin_url") != origin:
        raise SystemExit("Software Heritage response origin mismatch")
    request_status = value.get("save_request_status")
    if request_status not in {"accepted", "pending", "rejected"}:
        raise SystemExit(f"unexpected Software Heritage request status: {request_status}")
    task_status = value.get("save_task_status")
    if task_status == "succeeded":
        swhid = value.get("snapshot_swhid")
        if not isinstance(swhid, str) or not swhid.startswith("swh:1:snp:"):
            raise SystemExit("successful Software Heritage visit lacks snapshot SWHID")


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--poll-seconds", type=int, default=20)
    args = parser.parse_args()

    value = submit(args.origin)
    value = poll(
        value,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    validate(value, args.origin)
    write(Path(args.output), value)
    print(json.dumps(value, sort_keys=True))

    if value.get("save_request_status") == "rejected":
        return 2
    if value.get("save_task_status") == "failed":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
