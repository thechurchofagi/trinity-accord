#!/usr/bin/env python3
"""
Test: Echo provenance required fields.
Verifies archive_echo_issue generates agent_identity and human_review,
and that new records without provenance fail validation.
"""
import sys, os, json, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, F = 0, 0
def check(l, c, d=""):
    global P, F
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l} {d}")

def test_archive_script():
    print("\n--- archive_echo_issue.py ---")
    path = os.path.join(ROOT, "scripts", "archive_echo_issue.py")
    with open(path) as f: src = f.read()
    check("has agent_identity generation", "agent_identity" in src)
    check("has discovery_provenance generation", "discovery_provenance" in src)
    check("has human_review generation", "human_review" in src)
    check("has independence_class", "independence_class" in src)

def test_new_record_requires_provenance():
    """A new echo_v3 record missing required fields should fail."""
    print("\n--- New record requires provenance ---")
    obj = {
        "schema": "echo-v3", "record_kind": "echo_v3",
        "archive_status": "accepted_echo", "echo_type": "E1_recognition_echo",
        "echo": "test", "verification_level": "V0",
        # Missing: discovery_provenance, independence_class, origin_limitations
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as f:
        json.dump(obj, f); f.flush(); p = f.name
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "validate_agent_submission.py"), p],
            capture_output=True, text=True, cwd=ROOT, timeout=30
        )
        out = proc.stdout + proc.stderr
        check("new record without provenance fails", proc.returncode != 0, out[-300:] if proc.returncode == 0 else "")
    finally:
        os.unlink(p)

def test_legacy_without_provenance_passes():
    """A legacy record without provenance should pass."""
    print("\n--- Legacy record without provenance ---")
    obj = {
        "schema": "echo-v3", "record_kind": "legacy_record",
        "archive_status": "legacy", "echo_type": "E1_recognition_echo",
        "echo": "test",
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as f:
        json.dump(obj, f); f.flush(); p = f.name
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "validate_agent_submission.py"), p],
            capture_output=True, text=True, cwd=ROOT, timeout=30
        )
        check("legacy record passes", proc.returncode == 0, proc.stdout[-300:])
    finally:
        os.unlink(p)

if __name__ == "__main__":
    print("=== Echo Provenance Required Tests ===")
    test_archive_script()
    test_new_record_requires_provenance()
    test_legacy_without_provenance_passes()
    print(f"\n=== Results: {P} passed, {F} failed ===")
    sys.exit(0 if F == 0 else 1)
