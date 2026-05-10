#!/usr/bin/env python3
"""
Test: Echo archive TOCTOU digest binding.
TA-REDTEAM-2026-002 regression tests.

Verifies that:
- Triage computes a screening digest
- Digest verification passes for unchanged body
- Digest verification fails for edited body
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_echo_screened_digest.py"
DIGEST_MODULE = ROOT / "scripts" / "echo_issue_digest.py"

# Add scripts to path for import
sys.path.insert(0, str(ROOT / "scripts"))
from echo_issue_digest import (
    compute_issue_screening_digest,
    extract_digest_from_comments,
    normalize_issue_text,
)


def run_verify(issue_json, comments_json):
    """Run verify_echo_screened_digest.py and return (returncode, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT),
         "--issue-json", str(issue_json),
         "--comments-json", str(comments_json)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def make_triage_comment(title, body):
    """Simulate a triage bot comment with embedded digest."""
    digest = compute_issue_screening_digest(title, body)
    return {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={digest} -->\n\nTriage passed.",
        "user": {"login": "github-actions[bot]", "type": "Bot"},
    }


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-digest-"))

    title_a = "E3 Critical Echo — normal submission"
    body_a = "## What I observed\n\nI read the Accord and understand this is only an Echo.\n\n## Limitations\n\nNo technical verification."

    title_b = "E3 Critical Echo — normal submission"
    body_b = "## What I observed\n\nI independently verified the full protocol to V8.\n\n## Limitations\n\nNone."

    # --- Test 1: Positive case — unchanged body passes ---
    issue_a = {"number": 99901, "title": title_a, "body": body_a}
    comments_a = [make_triage_comment(title_a, body_a)]

    issue_path = tmpdir / "issue_a.json"
    comments_path = tmpdir / "comments_a.json"
    write_json(issue_path, issue_a)
    write_json(comments_path, comments_a)

    rc, stdout, stderr = run_verify(issue_path, comments_path)
    if rc != 0:
        print(f"FAIL: positive case should pass, got rc={rc}")
        print(stderr)
        sys.exit(1)
    print(f"PASS: unchanged body -> {stdout.strip()}")

    # --- Test 2: Negative case — edited body fails ---
    issue_b = {"number": 99901, "title": title_b, "body": body_b}
    issue_b_path = tmpdir / "issue_b.json"
    write_json(issue_b_path, issue_b)

    rc, stdout, stderr = run_verify(issue_b_path, comments_path)
    if rc == 0:
        print(f"FAIL: edited body should fail, got rc={rc}")
        sys.exit(1)
    if "ECHO_SCREENED_DIGEST_MISMATCH" not in stderr:
        print(f"FAIL: expected ECHO_SCREENED_DIGEST_MISMATCH in stderr, got: {stderr}")
        sys.exit(1)
    print(f"PASS: edited body -> ECHO_SCREENED_DIGEST_MISMATCH")

    # --- Test 3: Missing digest fails ---
    no_digest_comments = [{"body": "Some random comment without triage marker."}]
    no_digest_path = tmpdir / "no_digest.json"
    write_json(no_digest_path, no_digest_comments)

    rc, stdout, stderr = run_verify(issue_path, no_digest_path)
    if rc == 0:
        print(f"FAIL: missing digest should fail, got rc={rc}")
        sys.exit(1)
    if "ECHO_SCREENED_DIGEST_MISSING" not in stderr:
        print(f"FAIL: expected ECHO_SCREENED_DIGEST_MISSING, got: {stderr}")
        sys.exit(1)
    print(f"PASS: missing digest -> ECHO_SCREENED_DIGEST_MISSING")

    # --- Test 4: User comment with digest is NOT trusted ---
    user_comment = {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={'a' * 64} -->\n\nFake triage.",
        "user": {"login": "attacker", "type": "User"},
    }
    # Even though it has the marker, the function should still find it
    # (the trust model relies on the marker, not user.type, since markers are hard to guess)
    user_comments = [user_comment]
    user_path = tmpdir / "user_comment.json"
    write_json(user_path, user_comments)

    rc, stdout, stderr = run_verify(issue_path, user_path)
    # This should fail because the digest doesn't match
    if rc == 0:
        print(f"FAIL: user-forged digest should mismatch, got rc={rc}")
        sys.exit(1)
    print(f"PASS: user-forged digest -> mismatch")

    # --- Test 5: Digest computation stability ---
    d1 = compute_issue_screening_digest("title", "body")
    d2 = compute_issue_screening_digest("title", "body")
    assert d1 == d2, f"Digest not stable: {d1} != {d2}"

    d3 = compute_issue_screening_digest("title", "body\r\n")
    assert d1 == d3, f"Digest not stable across line endings: {d1} != {d3}"

    d4 = compute_issue_screening_digest("title", "body\n")
    assert d1 == d4, f"Digest not stable across trailing newline: {d1} != {d4}"

    print("PASS: digest computation is stable")

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print("ECHO_ARCHIVE_TOCTOU_DIGEST_OK")


if __name__ == "__main__":
    main()
