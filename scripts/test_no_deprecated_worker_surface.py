#!/usr/bin/env python3
"""
P3 Test: No deprecated worker surface at top level.
Verifies deprecated worker is moved to archive/deprecated/.
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label} {detail}")


def test_no_top_level_worker():
    """trinity-echo-worker should not exist at top level."""
    print("\n--- Top-level worker ---")
    check("No top-level trinity-echo-worker/",
          not os.path.isdir(os.path.join(ROOT, "trinity-echo-worker")))


def test_worker_in_deprecated():
    """Worker should be in archive/deprecated/."""
    print("\n--- Deprecated location ---")
    check("archive/deprecated/trinity-echo-worker/ exists",
          os.path.isdir(os.path.join(ROOT, "archive", "deprecated", "trinity-echo-worker")))

    deprecated_path = os.path.join(ROOT, "archive", "deprecated", "trinity-echo-worker")
    if os.path.isdir(deprecated_path):
        check("Has DEPRECATED.md",
              os.path.exists(os.path.join(deprecated_path, "DEPRECATED.md")))


def test_no_wrangler_deploy_workflow():
    """No workflow should deploy the worker."""
    print("\n--- No deploy workflow ---")
    workflow_dir = os.path.join(ROOT, ".github", "workflows")
    if os.path.exists(workflow_dir):
        for fname in os.listdir(workflow_dir):
            fpath = os.path.join(workflow_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                check(f"{fname} has no wrangler deploy",
                      "wrangler deploy" not in content)


if __name__ == "__main__":
    print("=== P3 Deprecated Worker Surface Tests ===")
    test_no_top_level_worker()
    test_worker_in_deprecated()
    test_no_wrangler_deploy_workflow()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
