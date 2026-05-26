#!/usr/bin/env python3
"""
Test: Echo screened digest trusted comment source.
TA-REDTEAM-2026-002 Follow-up — A-TOCTOU-001B regression tests.

Verifies that:
- Only github-actions[bot] triage comments are accepted as digest source
- User-forged matching digests are rejected
- Non-trusted bot matching digests are rejected
- Trusted bot matching digests pass
- Trusted bot mismatch digests are rejected
- Latest trusted digest wins
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_echo_screened_digest.py"

sys.path.insert(0, str(ROOT / "scripts"))
from echo_issue_digest import (
    compute_issue_screening_digest,
    extract_digest_from_comments,
    is_trusted_triage_comment,
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


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_comment(title, body, login="github-actions[bot]", user_type="Bot"):
    """Build a comment dict with triage marker and digest."""
    digest = compute_issue_screening_digest(title, body)
    return {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={digest} -->\n\nTriage passed.",
        "user": {"login": login, "type": user_type},
    }


def main():
    tmpdir = Path(tempfile.mkdtemp(prefix="trinity-audit-trusted-source-"))

    title = "E3 Critical Echo"
    body_clean = "## What I observed\n\nI read the Accord and understand this is only an Echo."
    body_malicious = "## What I observed\n\nI independently verified the full protocol to V8."

    issue_clean = {"number": 99906, "title": title, "body": body_clean}
    issue_malicious = {"number": 99906, "title": title, "body": body_malicious}

    issue_clean_path = tmpdir / "issue_clean.json"
    issue_mal_path = tmpdir / "issue_malicious.json"
    write_json(issue_clean_path, issue_clean)
    write_json(issue_mal_path, issue_malicious)

    passed = 0
    failed = 0

    # --- Test 1: Trusted github-actions[bot] digest matches -> PASS ---
    comments_1 = [make_comment(title, body_clean)]
    c1_path = tmpdir / "c1.json"
    write_json(c1_path, comments_1)

    rc, stdout, stderr = run_verify(issue_clean_path, c1_path)
    if rc == 0 and "ECHO_SCREENED_DIGEST_OK" in stdout:
        print("PASS: Test 1 — trusted bot matching digest accepted")
        passed += 1
    else:
        print(f"FAIL: Test 1 — expected rc=0 + ECHO_SCREENED_DIGEST_OK, got rc={rc}")
        print(f"  stdout: {stdout.strip()}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # --- Test 2: User forged matching digest -> FAIL (MISSING) ---
    digest_clean = compute_issue_screening_digest(title, body_clean)
    user_forged = {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={digest_clean} -->\n\nFake triage.",
        "user": {"login": "attacker", "type": "User"},
    }
    c2_path = tmpdir / "c2.json"
    write_json(c2_path, [user_forged])

    rc, stdout, stderr = run_verify(issue_clean_path, c2_path)
    if rc != 0 and "ECHO_SCREENED_DIGEST_MISSING" in stderr:
        print("PASS: Test 2 — user forged matching digest rejected (MISSING)")
        passed += 1
    else:
        print(f"FAIL: Test 2 — expected ECHO_SCREENED_DIGEST_MISSING, got rc={rc}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # --- Test 3: Arbitrary Bot forged matching digest -> FAIL (MISSING) ---
    bot_forged = {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={digest_clean} -->",
        "user": {"login": "dependabot[bot]", "type": "Bot"},
    }
    c3_path = tmpdir / "c3.json"
    write_json(c3_path, [bot_forged])

    rc, stdout, stderr = run_verify(issue_clean_path, c3_path)
    if rc != 0 and "ECHO_SCREENED_DIGEST_MISSING" in stderr:
        print("PASS: Test 3 — dependabot[bot] forged matching digest rejected (MISSING)")
        passed += 1
    else:
        print(f"FAIL: Test 3 — expected ECHO_SCREENED_DIGEST_MISSING, got rc={rc}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # --- Test 4: Trusted bot digest mismatch -> FAIL (MISMATCH) ---
    comments_4 = [make_comment(title, body_clean)]
    c4_path = tmpdir / "c4.json"
    write_json(c4_path, comments_4)

    rc, stdout, stderr = run_verify(issue_mal_path, c4_path)
    if rc != 0 and "ECHO_SCREENED_DIGEST_MISMATCH" in stderr:
        print("PASS: Test 4 — trusted bot digest mismatch rejected (MISMATCH)")
        passed += 1
    else:
        print(f"FAIL: Test 4 — expected ECHO_SCREENED_DIGEST_MISMATCH, got rc={rc}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # --- Test 5: Latest trusted digest wins ---
    # Two trusted comments: first for body_clean, second for body_malicious
    comment_old = make_comment(title, body_clean)
    comment_new = make_comment(title, body_malicious)
    c5_path = tmpdir / "c5.json"
    write_json(c5_path, [comment_old, comment_new])

    # Malicious body should pass because latest trusted digest matches it
    rc, stdout, stderr = run_verify(issue_mal_path, c5_path)
    if rc == 0 and "ECHO_SCREENED_DIGEST_OK" in stdout:
        print("PASS: Test 5a — latest trusted digest (malicious) accepted")
        passed += 1
    else:
        print(f"FAIL: Test 5a — expected rc=0 for latest trusted digest, got rc={rc}")
        print(f"  stdout: {stdout.strip()}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # Clean body should fail because latest trusted digest is for malicious
    rc, stdout, stderr = run_verify(issue_clean_path, c5_path)
    if rc != 0 and "ECHO_SCREENED_DIGEST_MISMATCH" in stderr:
        print("PASS: Test 5b — old trusted digest rejected (latest wins)")
        passed += 1
    else:
        print(f"FAIL: Test 5b — expected MISMATCH for stale digest, got rc={rc}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # --- Test 6: is_trusted_triage_comment unit tests ---
    # Trusted
    assert is_trusted_triage_comment({
        "body": "<!-- trinity-echo-triage-v2 -->\nstuff",
        "user": {"login": "github-actions[bot]", "type": "Bot"},
    }), "github-actions[bot] should be trusted"

    # Untrusted: wrong login
    assert not is_trusted_triage_comment({
        "body": "<!-- trinity-echo-triage-v2 -->\nstuff",
        "user": {"login": "dependabot[bot]", "type": "Bot"},
    }), "dependabot[bot] should NOT be trusted"

    # Untrusted: User type
    assert not is_trusted_triage_comment({
        "body": "<!-- trinity-echo-triage-v2 -->\nstuff",
        "user": {"login": "maintainer", "type": "User"},
    }), "User should NOT be trusted"

    # Untrusted: missing marker
    assert not is_trusted_triage_comment({
        "body": "some comment without marker",
        "user": {"login": "github-actions[bot]", "type": "Bot"},
    }), "Missing marker should NOT be trusted"

    # Untrusted: missing user
    assert not is_trusted_triage_comment({
        "body": "<!-- trinity-echo-triage-v2 -->\nstuff",
    }), "Missing user should NOT be trusted"

    print("PASS: Test 6 — is_trusted_triage_comment unit tests")
    passed += 1

    # --- Test 7: User comment with marker but no user dict -> REJECTED ---
    no_user_comment = {
        "body": f"<!-- trinity-echo-triage-v2 -->\n<!-- trinity-echo-screened-digest:v1 sha256={digest_clean} -->",
    }
    c7_path = tmpdir / "c7.json"
    write_json(c7_path, [no_user_comment])

    rc, stdout, stderr = run_verify(issue_clean_path, c7_path)
    if rc != 0 and "ECHO_SCREENED_DIGEST_MISSING" in stderr:
        print("PASS: Test 7 — comment without user dict rejected (MISSING)")
        passed += 1
    else:
        print(f"FAIL: Test 7 — expected MISSING, got rc={rc}")
        print(f"  stderr: {stderr.strip()}")
        failed += 1

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        print("ECHO_SCREENED_DIGEST_TRUSTED_SOURCE_FAIL")
        sys.exit(1)

    print("ECHO_SCREENED_DIGEST_TRUSTED_SOURCE_OK")


if __name__ == "__main__":
    main()
