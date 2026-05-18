#!/usr/bin/env python3
"""Test: pure echo renderer output does not leak verification-level fields."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "gateway" / "valid-agent-declared-correction-echo.json"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"

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


def main():
    global PASS, FAIL

    print("=== Pure Echo Not Verifiability Tests ===\n")

    # Render the echo fixture
    r = subprocess.run(
        [sys.executable, str(RENDERER), str(FIXTURE)],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if r.returncode != 0:
        print(f"  FAIL: Renderer failed on echo fixture")
        print(f"        stdout: {r.stdout[:300]}")
        print(f"        stderr: {r.stderr[:300]}")
        sys.exit(1)

    output = r.stdout

    # 1. Does NOT contain agent_declared_protocol_level
    check("agent_declared_protocol_level" not in output,
          "Renderer output does NOT contain agent_declared_protocol_level")

    # 2. Does NOT contain claim_gate_mode: template_for_v0_v5
    check("claim_gate_mode: template_for_v0_v5" not in output,
          "Renderer output does NOT contain claim_gate_mode: template_for_v0_v5")

    # 3. DOES contain counts_toward_home_verifiability: false
    check("counts_toward_home_verifiability: false" in output,
          "Renderer output DOES contain counts_toward_home_verifiability: false")

    # 4. DOES contain counts_toward_home_reception: true
    check("counts_toward_home_reception: true" in output,
          "Renderer output DOES contain counts_toward_home_reception: true")

    # 5. DOES contain auto_archive_action: auto_archive_agent_declared_echo
    check("auto_archive_action: auto_archive_agent_declared_echo" in output,
          "Renderer output DOES contain auto_archive_action: auto_archive_agent_declared_echo")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
