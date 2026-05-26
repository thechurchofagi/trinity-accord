#!/usr/bin/env python3
"""Test agent-declared oath summary rendering.

Tests:
  - valid payload + production render → oath summary fields present
  - oath fields have correct values (true, hash, count >= 160)
  - production render body passes issue intake validation
  - dry-run render shows oath but is non-authoritative
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
        return r.returncode != 0, r.stdout + r.stderr
    return r.returncode == 0, r.stdout + r.stderr


def build_payload():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    ok, msg = run([
        sys.executable, str(BUILDER),
        "--agent-name", "OathTestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--agent-independent-followup",
        "--what-checked", "Read public homepage",
        "--limitation", "Test oath rendering",
        "--out", out,
    ], env_extra={"TRINITY_TEST_READBACK": OATH_TEXT})
    if not ok:
        return None, msg
    return out, msg


def test_production_render_oath_fields():
    """Production render should include all oath summary fields."""
    global PASS, FAIL
    payload_path, msg = build_payload()
    if not payload_path:
        FAIL += 1
        print(f"  FAIL: could not build payload: {msg[:200]}")
        return

    body_path = payload_path.replace(".json", "-body.md")
    ok, msg = run([
        sys.executable, str(RENDERER), payload_path,
        "--production-render",
        "--gateway-receipt-id", "gar-oath-test-20260517T000000Z",
        "--gateway-service", "trinity-agent-issue-gateway",
        "--gateway-commit", "oathtest1",
    ])
    if not ok:
        FAIL += 1
        print(f"  FAIL: production render failed: {msg[:200]}")
        Path(payload_path).unlink(missing_ok=True)
        return

    Path(body_path).write_text(msg, encoding="utf-8")

    # Check oath fields
    checks = [
        ("verification_oath_present: true", "verification_oath_present"),
        ("oath_read: true", "oath_read"),
        ("oath_version:", "oath_version"),
        ("readback_required: true", "readback_required"),
        ("agent_readback_present: true", "agent_readback_present"),
        ("agent_readback_sha256:", "agent_readback_sha256"),
        ("oath_text_sha256:", "oath_text_sha256"),
        ("agent_readback_excerpt:", "agent_readback_excerpt"),
    ]
    for pattern, desc in checks:
        if pattern in msg:
            PASS += 1
            print(f"  PASS: oath field {desc} present")
        else:
            FAIL += 1
            print(f"  FAIL: oath field {desc} missing")

    # Check char count >= 160
    import re
    count_match = re.search(r"agent_readback_char_count:\s*(\d+)", msg)
    if count_match:
        count = int(count_match.group(1))
        if count >= 160:
            PASS += 1
            print(f"  PASS: agent_readback_char_count={count} >= 160")
        else:
            FAIL += 1
            print(f"  FAIL: agent_readback_char_count={count} < 160")
    else:
        FAIL += 1
        print(f"  FAIL: agent_readback_char_count not found")

    # Validate body schema
    if VALIDATOR_BODY.exists():
        ok, val_msg = run([sys.executable, str(VALIDATOR_BODY), body_path])
        if ok:
            PASS += 1
            print(f"  PASS: oath body schema PASS")
        else:
            FAIL += 1
            print(f"  FAIL: oath body schema FAIL: {val_msg[:200]}")

    Path(payload_path).unlink(missing_ok=True)
    Path(body_path).unlink(missing_ok=True)


def test_dry_run_has_oath_but_non_authoritative():
    """Dry-run should show oath fields but be non-authoritative."""
    global PASS, FAIL
    payload_path, msg = build_payload()
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

    # Oath fields should still be present
    if "verification_oath_present: true" in msg:
        PASS += 1
        print(f"  PASS: dry-run has oath fields")
    else:
        FAIL += 1
        print(f"  FAIL: dry-run missing oath fields")

    # But non-authoritative
    if "created_by_gateway: false" in msg:
        PASS += 1
        print(f"  PASS: dry-run is non-authoritative")
    else:
        FAIL += 1
        print(f"  FAIL: dry-run not marked non-authoritative")

    Path(payload_path).unlink(missing_ok=True)


def test_missing_oath_fails_payload_validation():
    """Payload without oath should fail gateway payload validation."""
    global PASS, FAIL
    payload_path, msg = build_payload()
    if not payload_path:
        FAIL += 1
        print(f"  FAIL: could not build payload")
        return

    payload = json.loads(Path(payload_path).read_text())
    Path(payload_path).unlink(missing_ok=True)

    # Remove oath
    del payload["agent_integrity_declaration"]["verification_oath"]

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f)
        bad_path = f.name

    ok, msg = run([
        sys.executable, str(ROOT / "scripts" / "validate_gateway_payload.py"), bad_path
    ], expect_fail=True)
    Path(bad_path).unlink(missing_ok=True)

    if ok:
        PASS += 1
        print(f"  PASS: missing oath rejected by payload validator")
    else:
        FAIL += 1
        print(f"  FAIL: missing oath not rejected by payload validator")


def main():
    global PASS, FAIL
    print("=== Agent-Declared Oath Rendering Tests ===\n")

    print("--- Production render oath fields ---")
    test_production_render_oath_fields()

    print("\n--- Dry-run oath but non-authoritative ---")
    test_dry_run_has_oath_but_non_authoritative()

    print("\n--- Missing oath fails validation ---")
    test_missing_oath_fails_payload_validation()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
