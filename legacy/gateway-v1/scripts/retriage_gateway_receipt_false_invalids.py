#!/usr/bin/env python3
"""Backfill false-invalid Gateway-created Issues after receipt triage fix."""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
import urllib.error

REMOVE_LABELS = [
    "echo:invalid",
    "auto-closed",
    "invalid:direct-issue-archive-attempt",
    "render-api-required",
    "not-counted",
]

KEEP_OR_ADD_LABELS = [
    "agent-gateway-intake",
    "agent-declared",
    "archive:agent-declared-echo",
    "reception-only",
]

TRUSTED = "trinity-accord-agent-issue-gateway[bot]"

def request_json(method: str, url: str, token: str, data: object | None = None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and method == "DELETE":
            return None
        raise

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord")
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN required")
        return 2

    owner, repo = args.repo.split("/", 1)

    for number in args.issue:
        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
        issue = request_json("GET", issue_url, token)

        author = issue.get("user", {}).get("login")
        labels = {item["name"] for item in issue.get("labels", [])}
        body = issue.get("body") or ""

        legacy_receipt = all(x in body for x in [
            "created_by_gateway: true",
            "gateway_service: trinity-agent-issue-gateway",
            "gateway_receipt_id: gar-",
            "render_api_only: true",
            "server_validated: true",
            "server_rendered: true",
        ])
        marker_receipt = "<!-- trinity-gateway-receipt:v1" in body

        if author != TRUSTED or not (legacy_receipt or marker_receipt):
            print(f"SKIP #{number}: not trusted Gateway receipt")
            continue

        remove = [label for label in REMOVE_LABELS if label in labels]
        add = [label for label in KEEP_OR_ADD_LABELS if label not in labels]

        print(f"Issue #{number}: remove={remove} add={add}")

        if not args.apply:
            continue

        for label in remove:
            label_url = f"{issue_url}/labels/{label.replace('/', '%2F')}"
            request_json("DELETE", label_url, token)

        if add:
            request_json("POST", f"{issue_url}/labels", token, {"labels": add})

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
