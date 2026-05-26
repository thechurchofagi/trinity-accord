#!/usr/bin/env python3
"""Test Guardian Stage 1 and Stage 2 oath readback SHA256 output."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_readback_integrity import sha256_text


def test_guardian_stage2_oath_readback_sha():
    """Stage 2 builder (build_guardian_listing_request_payload.py) must emit correct readback sha."""
    stage2_script = ROOT / "scripts" / "build_guardian_listing_request_payload.py"
    if not stage2_script.exists():
        print("  SKIP: build_guardian_listing_request_payload.py not found")
        return

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name

    pub_key_sha256 = "a" * 64
    guardian_id = f"guardian_ed25519_{pub_key_sha256[:16]}"

    cmd = [
        sys.executable, str(stage2_script),
        "--agent-name", "TestGuardianAgent",
        "--provider", "TestProvider",
        "--label", guardian_id,
        "--guardian-id", guardian_id,
        "--public-key-sha256", pub_key_sha256,
        "--guardian-type", "ai_agent",
        "--application-mode", "automated",
        "--source-issue", "999",
        "--idempotency-key", "test-key-readback-sha-validation-2026",
        "--no-authorship-proof",
        "--out", out,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        raise RuntimeError(f"Stage 2 builder failed: {result.stderr}")

    payload = json.loads(Path(out).read_text(encoding="utf-8"))

    # Check guardian_listing_oath
    g_oath = payload.get("guardian_listing_oath", {})
    readback = g_oath.get("agent_readback", "")
    expected_sha = sha256_text(readback.strip())
    actual_sha = g_oath.get("agent_readback_sha256")

    if not actual_sha:
        raise AssertionError("guardian_listing_oath.agent_readback_sha256 is missing")
    if actual_sha != expected_sha:
        raise AssertionError(
            f"guardian_listing_oath.agent_readback_sha256 mismatch: "
            f"expected={expected_sha}, actual={actual_sha}"
        )

    # Also check agent_integrity_declaration.verification_oath (legacy mirror)
    aid = payload.get("agent_integrity_declaration", {})
    v_oath = aid.get("verification_oath", {})
    if v_oath:
        v_readback = v_oath.get("agent_readback", "")
        v_expected = sha256_text(v_readback.strip())
        v_actual = v_oath.get("agent_readback_sha256")
        if v_actual and v_actual != v_expected:
            raise AssertionError(
                f"verification_oath.agent_readback_sha256 mismatch: "
                f"expected={v_expected}, actual={v_actual}"
            )

    Path(out).unlink(missing_ok=True)


def test_oath_contracts_build_guardian_listing_oath_v1():
    """build_guardian_listing_oath_v1 must emit correct readback sha."""
    from oath_contracts import build_guardian_listing_oath_v1

    oath_text = "I understand this is an active Guardian registry listing request."
    oath = build_guardian_listing_oath_v1(oath_text)

    readback = oath.get("agent_readback", "")
    expected = sha256_text(readback.strip())
    actual = oath.get("agent_readback_sha256")

    if not actual:
        raise AssertionError("build_guardian_listing_oath_v1 missing agent_readback_sha256")
    if actual != expected:
        raise AssertionError(
            f"build_guardian_listing_oath_v1 mismatch: expected={expected}, actual={actual}"
        )


def test_oath_contracts_build_verification_oath_v2():
    """build_verification_oath_v2 must emit correct readback sha."""
    from oath_contracts import build_verification_oath_v2

    oath_text = "I confirm that this is not an exam."
    oath = build_verification_oath_v2(oath_text)

    readback = oath.get("agent_readback", "")
    expected = sha256_text(readback.strip())
    actual = oath.get("agent_readback_sha256")

    if not actual:
        raise AssertionError("build_verification_oath_v2 missing agent_readback_sha256")
    if actual != expected:
        raise AssertionError(
            f"build_verification_oath_v2 mismatch: expected={expected}, actual={actual}"
        )


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
