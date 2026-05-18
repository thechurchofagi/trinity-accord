#!/usr/bin/env python3
"""Test: preflight/submit render mode consistency in server.js and agent-submit.md."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "examples" / "github-app-backend" / "server.js"
AGENT_SUBMIT = ROOT / "agent-submit.md"

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
    doc = AGENT_SUBMIT.read_text()

    print("=== Preflight/Submit Render Mode Consistency Tests ===\n")

    # 1. renderArgs.push("--production-render") exists
    check("--production-render" in src,
          "server.js contains renderArgs.push(\"--production-render\")")

    # 2. --production-render is NOT inside an if (createIssue block
    # Find all occurrences and verify none are inside createIssue guards
    lines = src.split("\n")
    production_render_in_create_issue = False
    in_create_issue = False
    for line in lines:
        if "if (createIssue" in line or "if(createIssue" in line:
            in_create_issue = True
        if in_create_issue and "--production-render" in line:
            production_render_in_create_issue = True
        if in_create_issue and line.strip() == "}":
            in_create_issue = False
    check(not production_render_in_create_issue,
          "--production-render NOT inside an if(createIssue) block")

    # 3. preflight_receipt_id in preflight response
    check("preflight_receipt_id" in src,
          "server.js has preflight_receipt_id in preflight response")

    # 4. receipt_scope in preflight response
    check("receipt_scope" in src,
          "server.js has receipt_scope in preflight response")

    # 5. preflight_equivalent in submit response
    check("preflight_equivalent" in src,
          "server.js has preflight_equivalent in submit response")

    # 6. SERVER_GENERATED_FIELDS constant
    check("SERVER_GENERATED_FIELDS" in src,
          "server.js has SERVER_GENERATED_FIELDS constant")

    # 7. mentionsServerGeneratedField function
    check("mentionsServerGeneratedField" in src,
          "server.js has mentionsServerGeneratedField function")

    # 8. GATEWAY_INTERNAL_RENDER_VALIDATION_ERROR
    check("GATEWAY_INTERNAL_RENDER_VALIDATION_ERROR" in src,
          "server.js has GATEWAY_INTERNAL_RENDER_VALIDATION_ERROR")

    # 9. agent-submit.md warns about server-generated fields
    check("server-generated" in doc.lower() or "server_generated" in doc.lower() or "server generated" in doc.lower(),
          "agent-submit.md warns about server-generated fields")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
