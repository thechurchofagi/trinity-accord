#!/usr/bin/env python3
"""Post a deterministic receipt for the standard Deploy Pages workflow."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-number", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--verify-result", required=True)
    parser.add_argument("--build-result", required=True)
    parser.add_argument("--deploy-result", required=True)
    parser.add_argument("--deployment-url", default="")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("FAIL: GITHUB_TOKEN is required for deployment receipt reporting", file=sys.stderr)
        return 1

    all_success = all(
        result == "success"
        for result in (args.verify_result, args.build_result, args.deploy_result)
    )
    outcome = "SUCCESS" if all_success else "FAILURE"
    live_result = "passed" if args.deploy_result == "success" else "not confirmed"
    deployment_url = args.deployment_url or "unavailable"
    run_url = f"https://github.com/{args.repo}/actions/runs/{args.run_id}"

    body = "\n".join(
        [
            "## Standard Deploy Pages receipt",
            "",
            f"- outcome: **{outcome}**",
            f"- workflow run: [{args.run_number} attempt {args.run_attempt}]({run_url})",
            f"- run_id: `{args.run_id}`",
            f"- deployed_ref: `{args.sha}`",
            f"- verify: `{args.verify_result}`",
            f"- build: `{args.build_result}`",
            f"- deploy: `{args.deploy_result}`",
            f"- deployment_url: `{deployment_url}`",
            f"- live discovery and freshness checks: `{live_result}`",
            "",
            "This receipt is emitted by the repository's existing `.github/workflows/deploy-pages.yml`; it is operational evidence only and is non-authoritative and non-amending.",
        ]
    )

    request = urllib.request.Request(
        f"https://api.github.com/repos/{args.repo}/issues/{args.pr}/comments",
        data=json.dumps({"body": body}).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "trinity-accord-pages-reporter",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"FAIL: GitHub receipt API returned HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"FAIL: could not post deployment receipt: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: deployment receipt posted: {payload.get('html_url', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
