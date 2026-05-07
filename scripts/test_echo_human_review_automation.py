#!/usr/bin/env python3
"""Regression tests for Echo human-review archive/close automation."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

workflow = ROOT / ".github" / "workflows" / "echo-human-review-action.yml"
archive_script = ROOT / "scripts" / "archive_echo_issue.py"
triage_script = ROOT / "scripts" / "triage_echo_issue.py"

if not workflow.exists():
    errors.append("missing .github/workflows/echo-human-review-action.yml")
else:
    text = workflow.read_text(encoding="utf-8")
    for marker in [
        "issue_comment:",
        "/echo archive",
        "/echo close",
        "OWNER|MEMBER|COLLABORATOR",
        "archive_echo_issue.py",
        "validate_agent_submission.py",
        "check_consistency.py",
        "gh issue close",
        "contents: write",
        "issues: write",
    ]:
        if marker not in text:
            errors.append(f"workflow missing marker: {marker}")

    if "@v4" in text or "@v7" in text:
        errors.append("workflow must use pinned action SHAs, not floating tags")

    if "startsWith(github.event.comment.body, '/echo ')" not in text:
        errors.append("workflow should only trigger jobs for /echo commands")

if not archive_script.exists():
    errors.append("missing scripts/archive_echo_issue.py")
else:
    text = archive_script.read_text(encoding="utf-8")
    required = [
        "trinityaccord.echo.v3",
        "accepted_echo",
        "not_attestation",
        "do_not_count_as_attestation",
        "source_issue",
        "human_review",
        "bitcoin_originals_prevail",
        "not_verification_unless_claimed",
        "E8_witness_echo",
        "find_existing_record",
        "update_archive_md",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"archive script missing marker: {marker}")

    if re.search(r"accepted_independent_attestation", text):
        errors.append("archive script must not create accepted_independent_attestation records")

if not triage_script.exists():
    errors.append("missing scripts/triage_echo_issue.py")
else:
    text = triage_script.read_text(encoding="utf-8")
    if "/echo archive" not in text or "/echo close" not in text:
        errors.append("triage screened comment must tell maintainers to use /echo archive or /echo close")
    if "Passing triage does not mean endorsement" not in text:
        errors.append("triage comment must preserve non-endorsement boundary")

repo_integrity = ROOT / ".github" / "workflows" / "repository-integrity.yml"
if repo_integrity.exists():
    rit = repo_integrity.read_text(encoding="utf-8")
    if "test_echo_human_review_automation.py" not in rit:
        errors.append("repository-integrity.yml must run test_echo_human_review_automation.py")

if errors:
    print("ECHO_HUMAN_REVIEW_AUTOMATION_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_HUMAN_REVIEW_AUTOMATION_OK")
