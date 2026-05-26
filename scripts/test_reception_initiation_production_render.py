#!/usr/bin/env python3
"""Test production-render pipeline for reception initiation.

Tests:
  - valid externally_seeded payload + production receipt → issue body schema PASS
  - valid externally_requested payload + production receipt → issue body schema PASS
  - default render without production receipt → non-authoritative fields present
  - default render body must not pass archive validation
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"
VALIDATOR_BODY = ROOT / "scripts" / "validate_issue_intake_body.py"

PASS = 0
FAIL = 0


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


def run(cmd, expect_fail=False, env_extra=None):
    import os
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
    if expect_fail:
        if r.returncode != 0:
            return True, r.stdout + r.stderr
        return False, r.stdout + r.stderr
    if r.returncode != 0:
        return False, r.stdout + r.stderr
    return True, r.stdout + r.stderr


def build_payload(init_class, basis, followup=False):
    """Build a payload and return the path."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    cmd = [
        sys.executable, str(BUILDER),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--reception-initiation-class", init_class,
        "--reception-initiation-basis", basis,
        "--out", out,
    ]
    if followup:
        cmd.insert(-1, "--agent-independent-followup")
    ok, msg = run(cmd, env_extra={"TRINITY_TEST_READBACK": OATH_TEXT})
    if not ok:
        return None, msg
    return out, msg


def test_production_render_pass(init_class, basis):
    """Production render with valid receipt should pass body validation."""
    global PASS, FAIL
    payload_path, msg = build_payload(init_class, basis)
    if not payload_path:
        FAIL += 1
        print(f"  FAIL: could not build {init_class} payload: {msg[:200]}")
        return

    receipt_id = f"gar-test-{init_class}-20260517T000000Z"
    body_path = payload_path.replace(".json", "-body.md")

    # Production render
    ok, msg = run([
        sys.executable, str(RENDERER), payload_path,
        "--production-render",
        "--gateway-receipt-id", receipt_id,
        "--gateway-service", "trinity-agent-issue-gateway",
        "--gateway-commit", "testcommit1",
    ])
    if not ok:
        FAIL += 1
        print(f"  FAIL: production render failed for {init_class}: {msg[:200]}")
        Path(payload_path).unlink(missing_ok=True)
        return

    # Write body for validation
    Path(body_path).write_text(msg, encoding="utf-8")

    # Verify body contains expected fields
    if f"reception_initiation_class: {init_class}" not in msg:
        FAIL += 1
        print(f"  FAIL: body missing reception_initiation_class: {init_class}")
    elif f"gateway_receipt_id: {receipt_id}" not in msg:
        FAIL += 1
        print(f"  FAIL: body missing gateway_receipt_id")
    elif "created_by_gateway: true" not in msg:
        FAIL += 1
        print(f"  FAIL: body missing created_by_gateway: true")
    elif "render_api_only: true" not in msg:
        FAIL += 1
        print(f"  FAIL: body missing render_api_only: true")
    else:
        PASS += 1
        print(f"  PASS: production render {init_class} has correct receipt fields")

    # Validate body schema
    if VALIDATOR_BODY.exists():
        ok, msg = run([sys.executable, str(VALIDATOR_BODY), body_path])
        if ok:
            PASS += 1
            print(f"  PASS: production render {init_class} body schema PASS")
        else:
            FAIL += 1
            print(f"  FAIL: production render {init_class} body schema FAIL: {msg[:200]}")

    Path(payload_path).unlink(missing_ok=True)
    Path(body_path).unlink(missing_ok=True)


def test_dry_run_non_authoritative():
    """Default render (dry-run) should produce non-authoritative fields."""
    global PASS, FAIL
    payload_path, msg = build_payload("externally_seeded", "external_url_only")
    if not payload_path:
        FAIL += 1
        print(f"  FAIL: could not build payload for dry-run test")
        return

    ok, msg = run([sys.executable, str(RENDERER), payload_path])
    if not ok:
        FAIL += 1
        print(f"  FAIL: dry-run render failed: {msg[:200]}")
        Path(payload_path).unlink(missing_ok=True)
        return

    checks = [
        ("created_by_gateway: false", "created_by_gateway false"),
        ("render_api_only: false", "render_api_only false"),
        ("gateway_receipt_id: none", "gateway_receipt_id none"),
    ]
    for pattern, desc in checks:
        if pattern in msg:
            PASS += 1
            print(f"  PASS: dry-run has {desc}")
        else:
            FAIL += 1
            print(f"  FAIL: dry-run missing {desc}")

    Path(payload_path).unlink(missing_ok=True)


def test_dry_run_fails_archive_validation():
    """Dry-run body should NOT pass archive body validation."""
    global PASS, FAIL
    if not VALIDATOR_BODY.exists():
        print("  SKIP: validate_issue_intake_body.py not found")
        return

    payload_path, msg = build_payload("externally_seeded", "external_url_only")
    if not payload_path:
        FAIL += 1
        print(f"  FAIL: could not build payload")
        return

    ok, msg = run([sys.executable, str(RENDERER), payload_path])
    if not ok:
        FAIL += 1
        print(f"  FAIL: dry-run render failed")
        Path(payload_path).unlink(missing_ok=True)
        return

    body_path = payload_path.replace(".json", "-dry-run-body.md")
    Path(body_path).write_text(msg, encoding="utf-8")

    ok, val_msg = run([sys.executable, str(VALIDATOR_BODY), body_path], expect_fail=True)
    if ok:
        PASS += 1
        print(f"  PASS: dry-run body correctly rejected by archive validation")
    else:
        # Might pass if validator doesn't check receipt fields - that's also acceptable
        # as long as the body itself is marked non-authoritative
        FAIL += 1
        print(f"  FAIL: dry-run body unexpectedly passed archive validation")

    Path(payload_path).unlink(missing_ok=True)
    Path(body_path).unlink(missing_ok=True)


def main():
    global PASS, FAIL
    print("=== Production Render Tests ===\n")

    # Production render with receipt
    print("\n--- Production render with receipt ---")
    for init_class, basis in [
        ("externally_seeded", "external_url_only"),
        ("externally_requested", "explicit_verification_request"),
        ("self_initiated", "agent_discovered_publicly"),
    ]:
        test_production_render_pass(init_class, basis)

    # Dry-run tests
    print("\n--- Dry-run (non-authoritative) ---")
    test_dry_run_non_authoritative()
    test_dry_run_fails_archive_validation()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
