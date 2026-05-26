#!/usr/bin/env python3
"""Test: preflight error decision table — all errors use gatewayError() with required fields."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "examples" / "github-app-backend" / "server.js"

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
    src = SERVER.read_text()

    print("=== Preflight Error Decision Table Tests ===\n")

    # 1. All error responses use gatewayError()
    # Find all return statements with status codes (error returns)
    error_returns = re.findall(r'return\s+gatewayError\(\d+,\s*\{([^}]+)\}', src, re.DOTALL)
    check(len(error_returns) > 0,
          f"server.js uses gatewayError() for error responses (found {len(error_returns)} calls)")

    # 2. Each gatewayError call has reason, validation_stage, agent_action
    # Parse each gatewayError call more carefully
    gateway_calls = re.finditer(
        r'return\s+gatewayError\((\d+),\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\s*\)',
        src, re.DOTALL
    )
    calls_with_all_fields = 0
    total_calls = 0
    missing_calls = []

    for m in gateway_calls:
        total_calls += 1
        body = m.group(2)
        has_reason = "reason:" in body or "reason :" in body
        has_validation = "validation_stage:" in body or "validation_stage :" in body
        has_action = "agent_action:" in body or "agent_action :" in body
        if has_reason and has_validation and has_action:
            calls_with_all_fields += 1
        else:
            missing = []
            if not has_reason:
                missing.append("reason")
            if not has_validation:
                missing.append("validation_stage")
            if not has_action:
                missing.append("agent_action")
            # Get line number
            pos = m.start()
            line_num = src[:pos].count("\n") + 1
            missing_calls.append(f"line {line_num}: missing {', '.join(missing)}")

    check(total_calls > 0, f"Found {total_calls} gatewayError() calls")
    check(calls_with_all_fields == total_calls,
          f"All gatewayError() calls have reason, validation_stage, agent_action ({calls_with_all_fields}/{total_calls})",
          "; ".join(missing_calls) if missing_calls else "")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
