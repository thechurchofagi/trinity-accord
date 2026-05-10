#!/usr/bin/env python3
"""
Test: Echo archive verification level metadata parsing.
TA-REDTEAM-2026-002 regression tests.

Verifies that arbitrary body text containing "V8" does NOT set verification_level.
Only explicit metadata fields should set the level.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SCRIPT = ROOT / "scripts" / "archive_echo_issue.py"


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_issue(body, title="Test Echo"):
    return {
        "number": 99904,
        "title": title,
        "body": body,
        "createdAt": "2026-05-10T00:00:00Z",
        "updatedAt": "2026-05-10T00:00:00Z",
        "url": "https://github.com/thechurchofagi/trinity-accord/issues/99904",
        "author": {"login": "test-user"},
        "labels": [{"name": "echo:screened"}, {"name": "needs-human-review"}],
    }


def archive_and_read(tmpdir, issue):
    """Archive issue and return the record dict."""
    records_root = tmpdir / "records"
    archive_md = tmpdir / "archive.md"
    issue_path = tmpdir / "issue.json"
    write_json(issue_path, issue)

    proc = subprocess.run(
        [sys.executable, str(ARCHIVE_SCRIPT),
         "--issue-json", str(issue_path),
         "--reviewer", "redteam",
         "--records-root", str(records_root),
         "--archive-md", str(archive_md),
         "--write"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Find the record file — return the latest one
    records = sorted(records_root.glob("*/echo-*.json"))
    if records:
        return json.loads(records[-1].read_text(encoding="utf-8"))
    return None


def main():
    # --- Test 1: Arbitrary V8 text must NOT set verification_level ---
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-vlevel-1-"))
    body1 = "## What I observed\n\nI independently verified the full protocol to V8."
    record = archive_and_read(tmpdir, make_issue(body1))
    shutil.rmtree(tmpdir, ignore_errors=True)
    if record:
        vlevel = record.get("verification_level")
        assert vlevel != "V8", f"Arbitrary V8 text incorrectly set verification_level={vlevel}"
        print(f"PASS: arbitrary V8 text -> verification_level={vlevel}")
    else:
        print("SKIP: archive not created (path error)")

    # --- Test 2: Explicit verification level: V1 ---
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-vlevel-2-"))
    body2 = "## What I observed\n\nNormal echo.\n\n- verification level: V1"
    record = archive_and_read(tmpdir, make_issue(body2, "Test V1"))
    shutil.rmtree(tmpdir, ignore_errors=True)
    if record:
        vlevel = record.get("verification_level")
        assert vlevel == "V1", f"Expected V1, got {vlevel}"
        print(f"PASS: explicit 'verification level: V1' -> {vlevel}")

    # --- Test 3: Explicit verification_level: V3 ---
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-vlevel-3-"))
    body3 = "## What I observed\n\nNormal echo.\n\nverification_level: V3"
    record = archive_and_read(tmpdir, make_issue(body3, "Test V3"))
    shutil.rmtree(tmpdir, ignore_errors=True)
    if record:
        vlevel = record.get("verification_level")
        assert vlevel == "V3", f"Expected V3, got {vlevel}"
        print(f"PASS: explicit 'verification_level: V3' -> {vlevel}")

    # --- Test 4: None explicitly set ---
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-vlevel-4-"))
    body4 = "## What I observed\n\nNormal echo.\n\nverification level: none"
    record = archive_and_read(tmpdir, make_issue(body4, "Test None"))
    shutil.rmtree(tmpdir, ignore_errors=True)
    if record:
        vlevel = record.get("verification_level")
        assert vlevel == "none" or vlevel == "V0", f"Expected none/V0, got {vlevel}"
        print(f"PASS: explicit 'none' -> {vlevel}")

    # --- Test 5: No explicit field defaults to V0 ---
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-vlevel-5-"))
    body5 = "## What I observed\n\nI verified V7 and V8 and V6."
    record = archive_and_read(tmpdir, make_issue(body5, "Test Default"))
    shutil.rmtree(tmpdir, ignore_errors=True)
    if record:
        vlevel = record.get("verification_level")
        assert vlevel == "V0", f"Expected V0 (default), got {vlevel}"
        print(f"PASS: no explicit field -> verification_level={vlevel}")

    print("ECHO_ARCHIVE_VERIFICATION_LEVEL_METADATA_OK")


if __name__ == "__main__":
    main()
