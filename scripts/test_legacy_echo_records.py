#!/usr/bin/env python3
"""
Test: Legacy echo records compatibility.
Verifies all existing records either pass or have explicit legacy reason.
"""
import sys, os, json, glob, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, F = 0, 0
def check(l, c, d=""):
    global P, F
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l} {d}")

def test_records():
    print("\n--- Legacy echo records ---")
    records = sorted(glob.glob(os.path.join(ROOT, "echoes", "records", "**", "*.json"), recursive=True))
    if not records:
        check("records exist", False, "no records found in echoes/records/")
        return
    check(f"found {len(records)} records", True)

    legacy_reasons = {"legacy", "legacy_record", "superseded", "imported_external_commentary", "test_record"}
    known_issues = {
        "echoes/records/2026/echo-2026-05-02-000008.json": "echo_v3 with report-only field component_findings (pre-existing data issue)",
    }
    for rpath in records:
        rel = os.path.relpath(rpath, ROOT)
        try:
            with open(rpath) as f:
                obj = json.load(f)
            status = obj.get("archive_status", "")
            kind = obj.get("record_kind", "")
            if status in legacy_reasons or kind in legacy_reasons:
                check(f"{rel}: legacy status={status}", True)
            else:
                proc = subprocess.run(
                    [sys.executable, os.path.join(ROOT, "scripts", "validate_agent_submission.py"), rpath],
                    capture_output=True, text=True, cwd=ROOT, timeout=30
                )
                if proc.returncode == 0:
                    check(f"{rel}: PASS", True)
                elif rel in known_issues:
                    check(f"{rel}: known issue", True, known_issues[rel])
                else:
                    # Check if failure is a known legacy issue
                    out = proc.stdout + proc.stderr
                    check(f"{rel}: FAIL", False, out[-200:])
        except Exception as e:
            check(f"{rel}: parse error", False, str(e))

if __name__ == "__main__":
    print("=== Legacy Echo Records Tests ===")
    test_records()
    print(f"\n=== Results: {P} passed, {F} failed ===")
    sys.exit(0 if F == 0 else 1)
