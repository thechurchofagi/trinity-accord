#!/usr/bin/env python3
"""Test reception initiation classification across the pipeline.

Tests:
  - builder externally_requested → payload has externally_requested
  - builder externally_seeded → payload has externally_seeded
  - builder self_initiated → payload has self_initiated
  - rendered machine block includes same class
  - payload with missing class fails validator
  - payload self_initiated + human_supplied_link=true fails
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

PASS = 0
FAIL = 0


def run(cmd, expect_fail=False):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if expect_fail:
        if r.returncode != 0:
            return True, r.stdout + r.stderr
        return False, r.stdout + r.stderr
    if r.returncode != 0:
        return False, r.stdout + r.stderr
    return True, r.stdout + r.stderr


def test_builder_initiation_class(init_class, basis):
    """Build payload with given initiation class and verify it's in the output."""
    global PASS, FAIL
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
    ok, msg = run(cmd)
    if not ok:
        FAIL += 1
        print(f"  FAIL: builder with {init_class} failed: {msg[:200]}")
        return None

    payload = json.loads(Path(out).read_text())
    actual = payload.get("reception_initiation_class")
    if actual == init_class:
        PASS += 1
        print(f"  PASS: builder {init_class} → payload has {actual}")
    else:
        FAIL += 1
        print(f"  FAIL: builder {init_class} → payload has {actual}")

    Path(out).unlink(missing_ok=True)
    return payload


def test_validator_accepts(payload):
    """Validate a payload and expect it to pass."""
    global PASS, FAIL
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f, indent=2)
        f.flush()
        path = f.name

    ok, msg = run([sys.executable, str(VALIDATOR), path])
    Path(path).unlink(missing_ok=True)
    if ok:
        PASS += 1
        print(f"  PASS: validator accepted payload")
    else:
        FAIL += 1
        print(f"  FAIL: validator rejected payload: {msg[:200]}")
    return ok


def test_validator_rejects(payload, reason_hint=""):
    """Validate a payload and expect it to fail."""
    global PASS, FAIL
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f, indent=2)
        f.flush()
        path = f.name

    ok, msg = run([sys.executable, str(VALIDATOR), path], expect_fail=True)
    Path(path).unlink(missing_ok=True)
    if ok:
        PASS += 1
        print(f"  PASS: validator rejected bad payload ({reason_hint})")
    else:
        FAIL += 1
        print(f"  FAIL: validator accepted bad payload ({reason_hint}): {msg[:200]}")
    return not ok


def test_renderer_includes_class(payload, expected_class):
    """Render machine block and check it contains the initiation class."""
    global PASS, FAIL
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(payload, f, indent=2)
        f.flush()
        path = f.name

    ok, msg = run([sys.executable, str(RENDERER), path])
    Path(path).unlink(missing_ok=True)
    if not ok:
        FAIL += 1
        print(f"  FAIL: renderer failed: {msg[:200]}")
        return

    if f"reception_initiation_class: {expected_class}" in msg:
        PASS += 1
        print(f"  PASS: renderer includes reception_initiation_class: {expected_class}")
    else:
        FAIL += 1
        print(f"  FAIL: renderer missing reception_initiation_class: {expected_class}")
        # Debug: show what's there
        for line in msg.splitlines():
            if "reception_initiation" in line or "initiation" in line:
                print(f"    found: {line}")


def test_missing_class_fails_validator():
    """A payload without reception_initiation_class should fail validation."""
    global PASS, FAIL
    # Build a valid payload first
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name

    ok, msg = run([
        sys.executable, str(BUILDER),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--reception-initiation-class", "self_initiated",
        "--reception-initiation-basis", "agent_discovered_publicly",
        "--out", out,
    ])
    if not ok:
        FAIL += 1
        print(f"  FAIL: could not build base payload: {msg[:200]}")
        return

    payload = json.loads(Path(out).read_text())
    Path(out).unlink(missing_ok=True)

    # Remove the field
    del payload["reception_initiation_class"]
    test_validator_rejects(payload, "missing reception_initiation_class")


def test_self_initiated_with_human_link_fails():
    """self_initiated + human_supplied_link=true should fail."""
    global PASS, FAIL
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name

    ok, msg = run([
        sys.executable, str(BUILDER),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--reception-initiation-class", "self_initiated",
        "--reception-initiation-basis", "agent_discovered_publicly",
        "--out", out,
    ])
    if not ok:
        FAIL += 1
        print(f"  FAIL: could not build base payload: {msg[:200]}")
        return

    payload = json.loads(Path(out).read_text())
    Path(out).unlink(missing_ok=True)

    # Force human_supplied_link=true
    payload["discovery_provenance"]["human_supplied_link"] = True
    test_validator_rejects(payload, "self_initiated + human_supplied_link=true")


def main():
    global PASS, FAIL
    print("=== Reception Initiation Classification Tests ===\n")

    # Test each initiation class
    for init_class, basis in [
        ("externally_requested", "explicit_verification_request"),
        ("externally_seeded", "external_url_only"),
        ("self_initiated", "agent_discovered_publicly"),
        ("agent_referred", "other_agent_reference"),
        ("system_scheduled", "scheduled_monitor"),
        ("unknown", "unknown"),
    ]:
        print(f"\n--- {init_class} ---")
        payload = test_builder_initiation_class(init_class, basis)
        if payload:
            test_validator_accepts(payload)
            test_renderer_includes_class(payload, init_class)

    # Negative tests
    print("\n--- Negative tests ---")
    test_missing_class_fails_validator()
    test_self_initiated_with_human_link_fails()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
