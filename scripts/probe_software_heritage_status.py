#!/usr/bin/env python3
"""Query Software Heritage save requests and the repository's latest visit."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

from scripts.archive_public_web import (
    DEFAULT_REPOSITORY,
    query_software_heritage_latest_visit,
    query_software_heritage_save_request,
    utc_now,
    write_result,
)


def query_or_error(query, *args) -> dict:
    try:
        return {"ok": True, "response": query(*args)}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "http_status": error.code,
            "error": str(error),
            "response_body": body[:2000],
        }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        return {"ok": False, "http_status": None, "error": f"{type(error).__name__}: {error}"}


def request_is_complete(item: dict) -> bool:
    response = item.get("response", {})
    return bool(
        item.get("ok")
        and response.get("save_task_status") == "succeeded"
        and response.get("visit_status") == "full"
        and response.get("snapshot_swhid")
    )


def latest_visit_is_complete(item: dict) -> bool:
    response = item.get("response", {})
    return bool(
        item.get("ok")
        and response.get("status") == "full"
        and response.get("snapshot")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--request-id", type=int, action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        raise SystemExit("timeout-seconds must be positive")
    if any(request_id <= 0 for request_id in args.request_id):
        raise SystemExit("request IDs must be positive")

    requests = [
        {
            "request_id": request_id,
            **query_or_error(
                query_software_heritage_save_request,
                request_id,
                args.timeout_seconds,
            ),
        }
        for request_id in args.request_id
    ]
    latest = query_or_error(
        query_software_heritage_latest_visit,
        args.repository,
        args.timeout_seconds,
    )
    complete = (
        any(request_is_complete(item) for item in requests)
        or latest_visit_is_complete(latest)
    )
    result = {
        "schema": "trinityaccord.software-heritage-status.v1",
        "generated_at": utc_now(),
        "repository": args.repository,
        "save_requests": requests,
        "latest_visit": latest,
        "archive_complete": complete,
    }
    write_result(args.output, result)
    print(json.dumps({"archive_complete": complete}, sort_keys=True))
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
