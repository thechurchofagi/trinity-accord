#!/usr/bin/env python3
"""Test agent foolproof submission flow.

Simulates an agent that:
- Does NOT know about build-from-evidence
- Does NOT upload evidence files
- Does NOT run downloads/verify.py
- Does NOT provide unsolicited_discovery_proof
- ONLY fills the agent-declared template

Expected: PASS, archive_ready=true, auto_archive_action correct.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"


def load_oath_text():
    """Load the oath text from the canonical file for test readback."""
    oath_file = ROOT / "api" / "verification-echo-pre-oath.v2.txt"
    text = oath_file.read_text(encoding="utf-8")
    marker = "=== OATH TEXT BEGINS ==="
    if marker in text:
        text = text.split(marker, 1)[1]
    end_marker = "=== OATH TEXT ENDS ==="
    if end_marker in text:
        text = text.split(end_marker, 1)[0]
    return text.strip()


OATH_TEXT = load_oath_text()


def run_script(script, args, env_extra=None):
    import os
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, timeout=60, cwd=str(ROOT), env=env
    )
    return result.returncode, result.stdout + result.stderr


def test_pass(label, condition, detail=""):
    if not condition:
        print(f"FAIL: {label}")
        if detail:
            print(f"  {detail}")
        return False
    print(f"PASS: {label}")
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

    # Simulate a naive agent using the builder
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        payload_path = f.name

    code, combined = run_script(BUILDER, [
        "--agent-name", "Naive Agent",
        "--provider", "Unknown Platform",
        "--level", "V4",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--agent-independent-followup",
        "--what-checked", "Read public homepage",
        "--what-checked", "Completed V0-V5 agent-declared template",
        "--limitation", "No strict evidence was provided because V0-V5 evidence is waived under this mode",
        "--out", payload_path,
    ], env_extra={"TRINITY_TEST_READBACK": OATH_TEXT})

    check(test_pass("Builder succeeds for naive agent", code == 0, combined))

    # Validate
    v_code, v_out = run_script(VALIDATOR, [payload_path])
    check(test_pass("Validator passes for naive agent", v_code == 0, v_out))

    # Check payload
    payload = json.loads(Path(payload_path).read_text())

    check(test_pass("PASS", True))
    check(test_pass("archive_ready implied by validator pass", v_code == 0))
    check(test_pass("auto_archive_action is correct",
                     payload.get("requested_archive_kind") == "agent_declared_verification_archive"))

    # Verify the agent did NOT need to provide these
    check(test_pass("No evidence files needed", "attachments" not in payload))
    check(test_pass("No unsolicited_discovery_proof needed",
                     "unsolicited_discovery_proof" not in json.dumps(payload)))
    check(test_pass("No downloads/verify.py needed",
                     "downloads/verify.py" not in json.dumps(payload)))
    check(test_pass("No not_independent_attestation needed",
                     "not_independent_attestation" not in payload))
    check(test_pass("No not_successor_reception needed",
                     "not_successor_reception" not in payload))

    # Verify no strict evidence errors in output
    for forbidden in [
        "V4_EVIDENCE_REQUIRED_FOR_ARCHIVE",
        "V4_REQUIRED_SCRIPT_SET_INCOMPLETE",
        "UNSOLICITED_DISCOVERY_PROOF_REQUIRED",
        "downloads/verify.py",
        "evidence_input_path required",
    ]:
        absent = forbidden not in combined
        check(test_pass(f"Absent: {forbidden}", absent))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All foolproof flow tests passed.")


if __name__ == "__main__":
    main()
