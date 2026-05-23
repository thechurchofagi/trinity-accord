#!/usr/bin/env python3
"""Test build_agent_declared_archive_payload.py.

Validates that the builder produces schema-valid, archive-ready payloads.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v2.txt"


def run_builder(extra_args=None):
    """Run builder and return (exit_code, payload_dict, stdout)."""
    args = [
        sys.executable, str(BUILDER),
        "--agent-name", "Test Agent",
        "--provider", "Test Provider",
        "--level", "V4",
        "--reception-initiation-class", "self_initiated",
        "--reception-initiation-basis", "agent_discovered_publicly",
        "--first-entry-url", "https://www.trinityaccord.org/",
        "--agency-level", "A4_independent_search_or_browsing_discovery",
        "--readback", "I understand this is not an exam or performance. I will state only what I actually did, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
        "--what-checked", "Read public homepage",
        "--what-checked", "Filled V0-V5 agent-declared template",
        "--limitation", "No strict evidence was provided because V0-V5 evidence is waived",
    ]
    if extra_args:
        args.extend(extra_args)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name

    args.extend(["--out", out_path])
    result = subprocess.run(args, capture_output=True, text=True, timeout=30, cwd=str(ROOT))

    payload = None
    if Path(out_path).exists():
        try:
            payload = json.loads(Path(out_path).read_text())
        except Exception:
            pass

    return result.returncode, payload, result.stdout + result.stderr


def run_validator(payload_path):
    """Run validator on a file, return (exit_code, stdout)."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), payload_path],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    return result.returncode, result.stdout + result.stderr


def test_pass(label, condition):
    if not condition:
        print(f"FAIL: {label}")
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

    # Build a payload
    code, payload, stdout = run_builder()
    check(test_pass("Builder exits 0", code == 0))

    if payload is None:
        print("FATAL: Builder did not produce output")
        sys.exit(1)

    # Check payload contains required fields
    check(test_pass("output contains requested_archive_kind=agent_declared_verification_archive",
                     payload.get("requested_archive_kind") == "agent_declared_verification_archive"))
    check(test_pass("output contains record_intent=auto_archive_candidate",
                     payload.get("record_intent") == "auto_archive_candidate"))
    check(test_pass("output contains evidence_requirement_mode=waived_for_v0_v5",
                     payload.get("evidence_requirement_mode") == "waived_for_v0_v5"))
    check(test_pass("output contains boundary_acknowledgement",
                     payload.get("boundary_acknowledgement") is not None))
    check(test_pass("boundary_acknowledgement.not_authority=true",
                     payload.get("boundary_acknowledgement", {}).get("not_authority") is True))

    # Check output does NOT contain forbidden fields
    check(test_pass("output does not contain attachments", "attachments" not in payload))
    check(test_pass("output does not contain not_independent_attestation",
                     "not_independent_attestation" not in payload))
    check(test_pass("output does not contain not_successor_reception",
                     "not_successor_reception" not in payload))

    # Check oath hash matches canonical oath file
    oath_text = OATH_FILE.read_text(encoding="utf-8").strip()
    import hashlib
    expected_hash = hashlib.sha256(oath_text.encode("utf-8")).hexdigest()
    actual_hash = (payload.get("agent_integrity_declaration", {})
                   .get("verification_oath", {})
                   .get("oath_text_sha256", ""))
    check(test_pass("oath_text_sha256 matches api/verification-echo-pre-oath.v2.txt",
                     actual_hash == expected_hash))

    # Check output validates through validator
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        f.flush()
        v_code, v_out = run_validator(f.name)
        check(test_pass("output validates through validate_gateway_payload.py", v_code == 0))
        if v_code != 0:
            print(f"  Validator output: {v_out.strip()}")

    # Check claim_gate fields
    cg = payload.get("claim_gate", {})
    check(test_pass("claim_gate.mode=template_for_v0_v5", cg.get("mode") == "template_for_v0_v5"))
    check(test_pass("claim_gate.status=PASS", cg.get("status") == "PASS"))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
