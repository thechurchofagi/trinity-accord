#!/usr/bin/env python3
"""Test Gateway agent-declared E2E flow.

Simulates: build payload → validate → claim gate → archive readiness → render machine block.
Asserts no strict evidence errors appear.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"


def run_script(script, args):
    result = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, timeout=60, cwd=str(ROOT)
    )
    return result.returncode, result.stdout, result.stderr


def test_pass(label, condition, detail=""):
    if not condition:
        print(f"FAIL: {label}")
        if detail:
            print(f"  {detail}")
        return False
    print(f"PASS: {label}")
    return True


def test_fail_absent(label, text, forbidden_pattern):
    if forbidden_pattern in text:
        print(f"FAIL: {label} — found forbidden pattern: {forbidden_pattern}")
        return False
    print(f"PASS: {label} (absent)")
    return True


def main():
    passed = 0
    failed = 0
    total = 0

    def check(result):
        nonlocal passed, failed, total
        total += 1
        if result:
            passed += 1
        else:
            failed += 1

    # Step 1: Build payload
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        payload_path = f.name

    code, stdout, stderr = run_script(BUILDER, [
        "--agent-name", "E2E Agent",
        "--provider", "E2E Test",
        "--level", "V4",
        "--first-entry-url", "https://www.trinityaccord.org/",
        "--readback", "I understand this is not an exam or performance. I will state only what I actually did, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
        "--what-checked", "Read homepage",
        "--what-checked", "Filled template",
        "--limitation", "Evidence waived for V0-V5",
        "--out", payload_path,
    ])
    combined = stdout + stderr

    check(test_pass("Builder succeeds", code == 0, combined))

    # Step 2: Validate payload
    v_code, v_out, v_err = run_script(VALIDATOR, [payload_path])
    check(test_pass("Validator passes", v_code == 0, v_out + v_err))

    # Step 3: Check no strict evidence errors
    check(test_fail_absent("No V4_EVIDENCE_REQUIRED_FOR_ARCHIVE", combined, "V4_EVIDENCE_REQUIRED_FOR_ARCHIVE"))
    check(test_fail_absent("No V4_REQUIRED_SCRIPT_SET_INCOMPLETE", combined, "V4_REQUIRED_SCRIPT_SET_INCOMPLETE"))
    check(test_fail_absent("No UNSOLICITED_DISCOVERY_PROOF_REQUIRED", combined, "UNSOLICITED_DISCOVERY_PROOF_REQUIRED"))
    check(test_fail_absent("No downloads/verify.py reference", combined, "downloads/verify.py"))
    check(test_fail_absent("No evidence_input_path required", combined, "evidence_input_path required"))

    # Step 4: Check payload fields
    payload = json.loads(Path(payload_path).read_text())
    check(test_pass("record_intent=auto_archive_candidate",
                     payload.get("record_intent") == "auto_archive_candidate"))
    check(test_pass("requested_archive_kind=agent_declared_verification_archive",
                     payload.get("requested_archive_kind") == "agent_declared_verification_archive"))
    check(test_pass("evidence_requirement_mode=waived_for_v0_v5",
                     payload.get("evidence_requirement_mode") == "waived_for_v0_v5"))

    # Step 5: Render machine block and check
    r_code, r_out, r_err = run_script(RENDERER, [payload_path])
    check(test_pass("Renderer succeeds", r_code == 0, r_out + r_err))

    check(test_fail_absent("No V4_EVIDENCE_REQUIRED in machine block", r_out, "V4_EVIDENCE_REQUIRED"))
    check(test_fail_absent("No V4_REQUIRED_SCRIPT_SET in machine block", r_out, "V4_REQUIRED_SCRIPT_SET"))
    check(test_fail_absent("No downloads/verify.py in machine block", r_out, "downloads/verify.py"))
    check(test_pass("Machine block has archive_ready: true", "archive_ready: true" in r_out))
    check(test_pass("Machine block has auto_archive_action", "auto_archive_action: auto_archive_agent_declared_verification" in r_out))
    check(test_pass("Machine block has CLAIM_GATE_TEMPLATE_PASS", "CLAIM_GATE_TEMPLATE_PASS" in r_out))
    check(test_pass("Machine block has EVIDENCE_WAIVED_FOR_V0_V5", "EVIDENCE_WAIVED_FOR_V0_V5" in r_out))

    # Step 6: Verify no attachments in payload
    check(test_pass("No attachments in payload", "attachments" not in payload))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All E2E tests passed.")


if __name__ == "__main__":
    main()
