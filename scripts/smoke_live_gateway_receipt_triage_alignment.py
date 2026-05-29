#!/usr/bin/env python3
"""Live smoke test: Gateway receipt triage alignment.

Creates a live canary Issue via GitHub API, triggers triage workflow,
verifies receipt recognition and label assignment.

Requires env:
  TRINITY_LIVE_GATEWAY_RECEIPT_TRIAGE=I_UNDERSTAND_THIS_CREATES_A_LIVE_ISSUE
  GITHUB_TOKEN with issues:write + actions:read scope
  GITHUB_REPO (default: thechurchofagi/trinity-accord)

Safety:
  - Env guard prevents accidental execution
  - Test issue is closed and labeled for cleanup after verification
  - Idempotent: re-running cleans up previous canary issues
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


# --- Config ---
ENV_GUARD = "TRINITY_LIVE_GATEWAY_RECEIPT_TRIAGE"
ENV_GUARD_VALUE = "I_UNDERSTAND_THIS_CREATES_A_LIVE_ISSUE"
TOKEN_ENV = "GITHUB_TOKEN"
REPO_ENV = "GITHUB_REPO"
DEFAULT_REPO = "thechurchofagi/trinity-accord"
SITE_URL = "https://www.trinityaccord.org"

TRIAGE_WAIT_SECONDS = 120
TRIAGE_POLL_INTERVAL = 10

# Labels that a valid Gateway issue MUST NOT have
FORBIDDEN_LABELS = [
    "echo:invalid",
    "invalid:direct-issue-archive-attempt",
    "not-counted",
]

# Labels that a valid Gateway issue SHOULD have
EXPECTED_GATEWAY_LABELS = [
    "agent-gateway-intake",
    "agent-declared",
]

CANARY_TITLE_PREFIX = "[smoke-test] Gateway receipt triage canary"


# --- Helpers ---
def api_request(method: str, path: str, token: str, repo: str, body: dict | None = None) -> dict | list:
    """Make a GitHub API request."""
    url = f"https://api.github.com/repos/{repo}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "trinity-smoke-test",
        },
    )
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"API {method} {path} failed ({e.code}): {error_body}") from e


def fetch_url(url: str) -> tuple[int, str]:
    """Fetch a URL and return (status_code, body)."""
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-smoke-test"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else ""


def find_canary_issues(token: str, repo: str) -> list[dict]:
    """Find existing canary issues from previous runs."""
    issues = api_request("GET", "/issues?state=all&per_page=100&sort=created&direction=desc", token, repo)
    return [i for i in issues if i["title"].startswith(CANARY_TITLE_PREFIX)]


def cleanup_canary_issues(token: str, repo: str) -> None:
    """Close any leftover canary issues from previous runs."""
    for issue in find_canary_issues(token, repo):
        if issue["state"] == "open":
            api_request("PATCH", f"/issues/{issue['number']}", token, repo, {
                "state": "closed",
                "state_reason": "not_planned",
            })
            print(f"  Cleaned up previous canary #{issue['number']}")


def build_canary_body() -> str:
    """Build an issue body with a v1 receipt marker + archive intent.

    This simulates what a properly-functioning Gateway SHOULD produce.
    Since the triage checks trusted actor, this non-bot issue will be
    treated as a direct submission — which is the expected rejection path.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<!-- trinity-gateway-receipt:v1
receipt_id: gar-smoke-test-{int(time.time())}
gateway_service: trinity-agent-issue-gateway
gateway_commit: smoke-test
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
route_detected: pure_echo
submission_type: echo_candidate
requested_archive_kind: agent_declared_echo_archive
payload_sha256: smoke-test-placeholder
issued_at: {now}
-->

```trinity-issue-intake
echo_type: E1_recognition_echo
requested_archive_kind: agent_declared_echo_archive
record_intent: auto_archive_candidate
archive_ready: true
auto_archive_action: auto_archive_agent_declared_echo
system_or_provider: smoke-test
agent_name_or_model: smoke-test
agent_readback_sha256: smoke-test
```

This is a live smoke test issue for Gateway receipt triage alignment verification.
Created by automated smoke test at {now}.
"""


def wait_for_triage(issue_number: int, token: str, repo: str) -> dict:
    """Wait for the triage workflow to process the issue."""
    print(f"  Waiting for triage workflow on #{issue_number} (up to {TRIAGE_WAIT_SECONDS}s)...")
    deadline = time.time() + TRIAGE_WAIT_SECONDS

    while time.time() < deadline:
        # Check for triage comment
        comments = api_request("GET", f"/issues/{issue_number}/comments?per_page=10", token, repo)
        triage_comment = None
        for c in comments:
            if c.get("body", "").find("trinity-echo-triage") >= 0:
                triage_comment = c
                break

        if triage_comment:
            # Also get current labels
            issue = api_request("GET", f"/issues/{issue_number}", token, repo)
            return {
                "triaged": True,
                "labels": [l["name"] for l in issue.get("labels", [])],
                "comment_body": triage_comment.get("body", ""),
                "state": issue.get("state"),
            }

        time.sleep(TRIAGE_POLL_INTERVAL)

    # Timeout — get current state anyway
    issue = api_request("GET", f"/issues/{issue_number}", token, repo)
    return {
        "triaged": False,
        "labels": [l["name"] for l in issue.get("labels", [])],
        "comment_body": "",
        "state": issue.get("state"),
    }


# --- Test Cases ---
def test_receipt_contract_live() -> bool:
    """Verify the receipt contract API endpoint is live."""
    print("\n[1/5] Receipt contract API is live...")
    status, body = fetch_url(f"{SITE_URL}/api/gateway-receipt-contract.v1.json")
    if status != 200:
        print(f"  FAIL: HTTP {status}")
        return False

    data = json.loads(body)
    if data.get("schema") != "trinityaccord.gateway-receipt-contract.v1":
        print(f"  FAIL: unexpected schema: {data.get('schema')}")
        return False

    if "trinity-accord-agent-issue-gateway[bot]" not in data.get("trusted_gateway_actors", []):
        print("  FAIL: Gateway bot not in trusted_gateway_actors")
        return False

    print(f"  PASS: contract v{data.get('version')} online, trusted actors configured")
    return True


def test_existing_gateway_issues_have_receipt(token: str, repo: str) -> bool:
    """Verify recent Gateway bot issues have receipt markers or legacy receipt."""
    print("\n[2/5] Existing Gateway bot issues have valid receipt...")
    issues = api_request("GET", "/issues?state=all&per_page=10&sort=created&direction=desc", token, repo)

    gateway_issues = [
        i for i in issues
        if i.get("user", {}).get("login") == "trinity-accord-agent-issue-gateway[bot]"
    ]

    if not gateway_issues:
        print("  SKIP: no recent Gateway bot issues found")
        return True

    passed = 0
    failed = 0
    for issue in gateway_issues[:5]:
        body = issue.get("body", "") or ""
        has_new_marker = "trinity-gateway-receipt:v1" in body
        has_legacy = "created_by_gateway: true" in body
        has_valid_receipt = has_new_marker or has_legacy

        forbidden_found = [
            l["name"] for l in issue.get("labels", [])
            if l["name"] in FORBIDDEN_LABELS
        ]

        ok = has_valid_receipt and not forbidden_found
        status_str = "PASS" if ok else "FAIL"
        print(f"  #{issue['number']}: {status_str} (new_marker={has_new_marker}, legacy={has_legacy}, forbidden_labels={forbidden_found})")
        if ok:
            passed += 1
        else:
            failed += 1

    if failed:
        print(f"  FAIL: {failed}/{passed + failed} Gateway issues have issues")
        return False

    print(f"  PASS: {passed} Gateway issues verified")
    return True


def test_triage_rejects_forged_receipt(token: str, repo: str) -> bool:
    """Create a canary issue with receipt marker, verify triage rejects it.

    Since the issue is NOT created by the Gateway bot, triage should:
    - Detect archive intent
    - NOT recognize the receipt marker (untrusted actor)
    - Apply: echo:invalid, auto-closed, invalid:direct-issue-archive-attempt, etc.
    """
    print("\n[3/5] Triage rejects non-Gateway receipt marker (canary)...")

    # Cleanup previous canaries
    cleanup_canary_issues(token, repo)

    # Create canary issue
    body = build_canary_body()
    result = api_request("POST", "/issues", token, repo, {
        "title": f"{CANARY_TITLE_PREFIX} {int(time.time())}",
        "body": body,
    })
    issue_number = result["number"]
    print(f"  Created canary issue #{issue_number}")

    # Wait for triage
    triage = wait_for_triage(issue_number, token, repo)

    if not triage["triaged"]:
        print(f"  WARNING: Triage did not complete within {TRIAGE_WAIT_SECONDS}s")
        print(f"  Current labels: {triage['labels']}")
        if not triage["labels"]:
            print("  FAIL: No labels applied (triage may not have triggered)")
            return False

    labels = triage["labels"]

    # For non-Gateway issues with archive intent, triage SHOULD apply these
    expected_rejection_labels = [
        "echo:invalid",
        "invalid:direct-issue-archive-attempt",
        "not-counted",
    ]

    missing = [l for l in expected_rejection_labels if l not in labels]
    if missing:
        print(f"  FAIL: Missing expected rejection labels: {missing}")
        print(f"  Got labels: {labels}")
        return False

    # Verify the issue was closed
    if triage["state"] != "closed":
        print(f"  FAIL: Expected state=closed, got state={triage['state']}")
        return False

    print(f"  PASS: Triage correctly rejected non-Gateway receipt (labels={labels}, state={triage['state']})")
    return True


def test_gateway_bot_not_getting_rejection_labels(token: str, repo: str) -> bool:
    """Verify Gateway bot issues do NOT receive rejection labels.

    This is the key acceptance path test — checks that the triage
    correctly distinguishes Gateway bot from regular users.
    """
    print("\n[4/5] Gateway bot issues NOT getting rejection labels...")
    issues = api_request("GET", "/issues?state=all&per_page=20&sort=created&direction=desc", token, repo)

    gateway_issues = [
        i for i in issues
        if i.get("user", {}).get("login") == "trinity-accord-agent-issue-gateway[bot]"
    ]

    if not gateway_issues:
        print("  SKIP: no recent Gateway bot issues")
        return True

    violations = []
    for issue in gateway_issues[:10]:
        labels = [l["name"] for l in issue.get("labels", [])]
        forbidden = [l for l in labels if l in FORBIDDEN_LABELS]
        if forbidden:
            violations.append((issue["number"], forbidden))

    if violations:
        for num, labels in violations:
            print(f"  FAIL: Gateway issue #{num} has forbidden labels: {labels}")
        return False

    print(f"  PASS: {len(gateway_issues[:10])} Gateway issues have no forbidden labels")
    return True


def test_receipt_verifier_exists(token: str, repo: str) -> bool:
    """Verify the receipt verifier script and tests exist."""
    print("\n[5/5] Receipt verifier and tests exist...")
    try:
        verifier = api_request("GET", "/contents/scripts/gateway_receipt_verifier.py", token, repo)
        tests = api_request("GET", "/contents/scripts/test_gateway_receipt_verifier.py", token, repo)
        regression = api_request("GET", "/contents/scripts/test_issue_299_gateway_receipt_regression.py", token, repo)
        print(f"  PASS: gateway_receipt_verifier.py, test_gateway_receipt_verifier.py, test_issue_299_gateway_receipt_regression.py all present")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


# --- Main ---
def main() -> int:
    # Env guard
    if os.environ.get(ENV_GUARD) != ENV_GUARD_VALUE:
        print("SKIP: live gateway receipt triage smoke not enabled")
        print(f"Set {ENV_GUARD}={ENV_GUARD_VALUE} to run")
        return 0

    token = os.environ.get(TOKEN_ENV)
    if not token:
        print(f"ERROR: {TOKEN_ENV} not set")
        return 1

    repo = os.environ.get(REPO_ENV, DEFAULT_REPO)

    print(f"Live Gateway Receipt Triage Smoke Test")
    print(f"Repo: {repo}")
    print(f"Site: {SITE_URL}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Guard: {ENV_GUARD}={ENV_GUARD_VALUE}")

    results = {}
    results["receipt_contract_live"] = test_receipt_contract_live()
    results["gateway_issues_have_receipt"] = test_existing_gateway_issues_have_receipt(token, repo)
    results["triage_rejects_forged"] = test_triage_rejects_forged_receipt(token, repo)
    results["gateway_bot_no_rejection_labels"] = test_gateway_bot_not_getting_rejection_labels(token, repo)
    results["verifier_exists"] = test_receipt_verifier_exists(token, repo)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results.items():
        status_str = "PASS" if passed else "FAIL"
        print(f"  {status_str}: {name}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\nAll checks passed. v30.7 live receipt triage alignment: PASS")
        return 0
    else:
        print("\nSome checks failed. See above for details.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
