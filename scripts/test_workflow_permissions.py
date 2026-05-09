#!/usr/bin/env python3
"""
Test: Workflow permissions and security.
Verifies workflow permissions are minimal and no shell injection vectors.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, F = 0, 0
def check(l, c, d=""):
    global P, F
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l} {d}")

def test_triage_workflow():
    print("\n--- echo-triage.yml ---")
    p = os.path.join(ROOT, ".github", "workflows", "echo-triage.yml")
    with open(p) as f: c = f.read()
    check("has issues: write", "issues: write" in c)
    check("has contents: read", "contents: read" in c)
    check("no contents: write at top level", not c.split("jobs:")[0].strip().endswith("contents: write"))
    check("uses --event-json", "--event-json" in c)
    check("uses GITHUB_EVENT_PATH", "GITHUB_EVENT_PATH" in c)
    check("no ISSUE_TITLE env", "ISSUE_TITLE:" not in c or "github.event.issue.title" not in c)

def test_human_review_workflow():
    print("\n--- echo-human-review-action.yml ---")
    p = os.path.join(ROOT, ".github", "workflows", "echo-human-review-action.yml")
    with open(p) as f: c = f.read()
    # Top-level permissions (may be write for archive commit)
    check("has permissions section", "permissions:" in c)
    check("has issues: write", "issues: write" in c)
    # Close job should NOT have git push
    if "close:" in c:
        parts = c.split("close:")
        close_section = parts[-1] if len(parts) > 1 else ""
        check("close job has no git push", "git push" not in close_section)
        check("close job has no git commit", "git commit" not in close_section)

if __name__ == "__main__":
    print("=== Workflow Permissions Tests ===")
    test_triage_workflow()
    test_human_review_workflow()
    print(f"\n=== Results: {P} passed, {F} failed ===")
    sys.exit(0 if F == 0 else 1)
