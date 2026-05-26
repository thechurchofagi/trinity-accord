#!/usr/bin/env python3
"""
Script audit consistency tests — ensures script counts, exit codes, and all_green rules.

Usage:
    python3 scripts/test_script_audit_consistency.py
"""
import json, sys, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate, check_script_consistency

PASS = FAIL = TOTAL = 0


def run(tid, desc, scripts, expect_failures=0, expect_blocking=0, expect_non_blocking=0, expect_limitations=0):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    try:
        failures, blocking, non_blocking, limitations = check_script_consistency(scripts)
        errs = []
        if len(failures) != expect_failures:
            errs.append(f"Expected {expect_failures} failures, got {len(failures)}: {failures}")
        if len(blocking) != expect_blocking:
            errs.append(f"Expected {expect_blocking} blocking, got {len(blocking)}: {blocking}")
        if len(non_blocking) != expect_non_blocking:
            errs.append(f"Expected {expect_non_blocking} non-blocking, got {len(non_blocking)}")
        if len(limitations) != expect_limitations:
            errs.append(f"Expected {expect_limitations} limitations, got {len(limitations)}: {limitations}")
        if errs:
            FAIL += 1; print(f"FAIL {tid}: {desc}"); [print(f"      {e}") for e in errs]
        else:
            PASS += 1; print(f"PASS {tid}: {desc}")
    except Exception as e:
        FAIL += 1; print(f"FAIL {tid}: {desc} — {e}")


_SENTINEL = object()

def s(path="scripts/v.py", exists=True, reviewed=True, executed=True, cmd="python3 v.py",
       env=_SENTINEL, exit_code=0, stdout="PASS", blocking=True):
    d = {
        "path": path, "exists": exists, "source_reviewed": reviewed, "executed": executed,
        "command": cmd,
        "exit_code": exit_code, "stdout_summary": stdout, "blocking": blocking, "result": "PASS",
    }
    if env is not _SENTINEL:
        d["environment"] = env
    else:
        d["environment"] = {"python": "3.x"}
    return d


# All pass
run("SA-01", "All scripts pass", [s(), s(path="scripts/v2.py")],
    expect_failures=0, expect_blocking=0, expect_non_blocking=0, expect_limitations=0)

# Missing script
run("SA-02", "Missing script", [s(exists=False, reviewed=False, executed=False)],
    expect_failures=0, expect_blocking=0, expect_non_blocking=0, expect_limitations=1)

# Missing command
run("SA-03", "Missing command", [s(cmd=None)],
    expect_failures=1, expect_blocking=0, expect_non_blocking=0)

# Missing environment — pass None explicitly (not via default)
run("SA-04", "Missing environment", [s(env=None)],
    expect_failures=1, expect_blocking=0, expect_non_blocking=0)

# Missing exit_code
run("SA-05", "Missing exit_code", [s(exit_code=None)],
    expect_failures=1, expect_blocking=0, expect_non_blocking=0)

# Missing stdout_summary
run("SA-06", "Missing stdout_summary", [s(stdout=None)],
    expect_failures=1, expect_blocking=0, expect_non_blocking=0)

# Blocking failure
run("SA-07", "Blocking failure", [s(exit_code=1)],
    expect_failures=0, expect_blocking=1, expect_non_blocking=0)

# Non-blocking failure
run("SA-08", "Non-blocking failure", [s(exit_code=1, blocking=False)],
    expect_failures=0, expect_blocking=0, expect_non_blocking=1)

# Mixed
run("SA-09", "Mixed blocking + non-blocking + missing",
    [s(), s(path="scripts/v2.py", exit_code=1, blocking=False),
     s(path="scripts/v3.py", exists=False, reviewed=False, executed=False)],
    expect_failures=0, expect_blocking=0, expect_non_blocking=1, expect_limitations=1)

print(f"\n{'='*60}")
print(f"Results: {PASS}/{TOTAL} passed, {FAIL}/{TOTAL} failed")
print(f"{'FINAL: PASS' if FAIL == 0 else 'FINAL: FAIL'} — script audit consistency tests.")
sys.exit(0 if FAIL == 0 else 1)
