#!/usr/bin/env python3
"""Rebuild agent-declared-verification-index.json from GitHub Issues.

Scans closed Issues containing a trinity-issue-intake code block, filters for
agent_declared_verification_archive records with archive_ready=true, and
generates the canonical index file.

Usage:
    python3 scripts/build_agent_declared_verification_index_from_issues.py [--repo owner/repo] [--dry-run]

Requires: gh CLI authenticated with repo read access.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "api" / "agent-declared-verification-index.json"

# Fields to extract from the trinity-issue-intake block
INTAKE_FIELDS = [
    "agent_name_or_model",
    "system_or_provider",
    "agent_declared_protocol_level",
    "requested_archive_kind",
    "archive_ready",
    "auto_archive_action",
]

# Additional fields we want to preserve if present
EXTRA_FIELDS = [
    "record_intent",
    "evidence_requirement_mode",
    "claim_gate_mode",
    "claim_gate_status",
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "test_record",
]

# Label patterns that indicate test records
TEST_LABEL_PATTERNS = ["test-record", "test_record", "smoke-test"]


def run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {result.stderr.strip()}")
    return result.stdout


def parse_intake_block(body: str) -> dict[str, str] | None:
    """Extract key-value pairs from a trinity-issue-intake code block."""
    if not body:
        return None
    match = re.search(r"```trinity-issue-intake\s*\n(.*?)```", body, re.DOTALL)
    if not match:
        return None

    block = match.group(1)
    result = {}
    for line in block.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Skip list items (lines starting with -)
        if line.startswith("-"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key in (INTAKE_FIELDS + EXTRA_FIELDS):
                result[key] = value
    return result if result else None


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() in ("true", "1", "yes")


def fetch_issues(repo: str | None, limit: int = 200) -> list[dict]:
    """Fetch closed issues via gh CLI."""
    args = [
        "issue", "list",
        "--state", "closed",
        "--limit", str(limit),
        "--json", "number,title,body,closedAt,createdAt,url,labels",
    ]
    if repo:
        args.extend(["--repo", repo])

    output = run_gh(args)
    return json.loads(output)


def build_index(issues: list[dict], repo: str = "", include_test: bool = False) -> dict:
    """Build the index from parsed issue data."""
    records = []

    for issue in issues:
        body = issue.get("body", "")
        intake = parse_intake_block(body)
        if not intake:
            continue

        # Filter: must be agent_declared_verification_archive
        if intake.get("requested_archive_kind") != "agent_declared_verification_archive":
            continue

        # Filter: must be archive_ready=true
        if parse_bool(intake.get("archive_ready")) is not True:
            continue

        # Filter: must be auto_archive action
        if intake.get("auto_archive_action") != "auto_archive_agent_declared_verification":
            continue

        # Determine if this is a test record
        labels = [l.get("name", "") if isinstance(l, dict) else str(l) for l in issue.get("labels", [])]
        is_test_label = any(
            any(pat in lbl.lower() for pat in TEST_LABEL_PATTERNS)
            for lbl in labels
        )
        # Also check intake block for explicit test_record field
        is_test_intake = parse_bool(intake.get("test_record")) is True
        is_test = is_test_label or is_test_intake

        if is_test and not include_test:
            continue

        # Build counts flags - default based on test status
        counts_verifiability = parse_bool(intake.get("counts_toward_home_verifiability"))
        counts_reception = parse_bool(intake.get("counts_toward_home_reception"))

        # Defaults: non-test records count toward verifiability
        if counts_verifiability is None:
            counts_verifiability = not is_test
        if counts_reception is None:
            counts_reception = not is_test

        record = {
            "issue_number": issue["number"],
            "issue_url": issue.get("url", f"https://github.com/{repo}/issues/{issue['number']}"),
            "agent_name_or_model": intake.get("agent_name_or_model", "unknown"),
            "system_or_provider": intake.get("system_or_provider", "unknown"),
            "agent_declared_protocol_level": intake.get("agent_declared_protocol_level", "V4"),
            "requested_archive_kind": "agent_declared_verification_archive",
            "archive_ready": True,
            "auto_archive_action": "auto_archive_agent_declared_verification",
            "counts_toward_home_verifiability": counts_verifiability,
            "counts_toward_home_reception": counts_reception,
            "test_record": is_test,
            "created_at": issue.get("createdAt", ""),
        }
        records.append(record)

    # Sort by issue number
    records.sort(key=lambda r: r["issue_number"])

    return {
        "schema": "trinityaccord.agent-declared-verification-index.v1",
        "description": (
            "Index of agent-declared verification archives created through the Gateway. "
            "Records are added when a V0-V5 agent-declared Issue is successfully created and auto-archived. "
            "This index is rebuilt from closed GitHub Issues by CI."
        ),
        "generated_from": [
            "/api/agent-issue-gateway-payload-schema.v1.json"
        ],
        "rebuild_source": "github_issues",
        "rebuild_timestamp": datetime.now(timezone.utc).isoformat(),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub repo (owner/repo). Auto-detected if in a git dir.")
    parser.add_argument("--dry-run", action="store_true", help="Print index without writing.")
    parser.add_argument("--include-test", action="store_true", help="Include test records.")
    parser.add_argument("--limit", type=int, default=200, help="Max issues to fetch.")
    args = parser.parse_args()

    # Auto-detect repo
    repo = args.repo
    if not repo:
        try:
            remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            if remote.returncode == 0:
                url = remote.stdout.strip()
                # Extract owner/repo from URL
                m = re.search(r"(?:github\.com[:/])([^/]+/[^/]+?)(?:\.git)?$", url)
                if m:
                    repo = m.group(1)
        except Exception:
            pass

    if not repo:
        print("Error: --repo required or run from a git directory", file=sys.stderr)
        return 1

    print(f"Fetching closed issues from {repo}...", file=sys.stderr)
    issues = fetch_issues(repo, limit=args.limit)
    print(f"Fetched {len(issues)} issues.", file=sys.stderr)

    index = build_index(issues, repo=repo, include_test=args.include_test)
    record_count = len(index["records"])
    non_test = sum(1 for r in index["records"] if not r["test_record"])
    print(f"Found {record_count} agent-declared verification archive records ({non_test} non-test).", file=sys.stderr)

    output = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    if args.dry_run:
        print(output)
    else:
        INDEX_PATH.write_text(output, encoding="utf-8")
        print(f"Wrote {INDEX_PATH.relative_to(ROOT)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
