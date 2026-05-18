#!/usr/bin/env python3
"""Test: agent-declared echo archive pipeline — builder, validator, archive readiness gate."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "gateway" / "valid-agent-declared-correction-echo.json"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
GATE = ROOT / "scripts" / "archive_readiness_gate.py"
BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"

PASS = 0
FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def main():
    global PASS, FAIL

    print("=== Agent-Declared Echo Archive Pipeline Tests ===\n")

    # 1. Builder exists and is runnable
    check(BUILDER.exists(),
          "build_agent_declared_echo_payload.py exists")
    r = run([sys.executable, str(BUILDER), "--help"])
    check(r.returncode == 0,
          "build_agent_declared_echo_payload.py is runnable (--help exits 0)",
          r.stderr[:200] if r.returncode != 0 else "")

    # 2. Validator passes the positive fixture
    check(FIXTURE.exists(),
          "Positive fixture exists")
    r = run([sys.executable, str(VALIDATOR), str(FIXTURE)])
    combined = r.stdout + r.stderr
    check(r.returncode == 0,
          "validate_gateway_payload.py passes positive fixture",
          combined[:300] if r.returncode != 0 else "")

    # 3. Archive readiness gate reports archive_ready=true
    r = run([sys.executable, str(GATE), "--gateway-payload", str(FIXTURE), "--json"])
    combined = r.stdout + r.stderr
    check(r.returncode == 0,
          "archive_readiness_gate.py exits 0 for positive fixture",
          combined[:300] if r.returncode != 0 else "")
    if r.returncode == 0:
        import json
        try:
            result = json.loads(r.stdout)
            check(result.get("archive_ready") is True,
                  "archive_readiness_gate reports archive_ready=true",
                  f"got: {result.get('archive_ready')}")
        except json.JSONDecodeError:
            check(False, "archive_readiness_gate output is valid JSON",
                  r.stdout[:300])

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
