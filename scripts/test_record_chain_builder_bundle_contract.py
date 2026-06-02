#!/usr/bin/env python3
"""Test: Record-Chain builder bundle contract compliance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
BUNDLE = ROOT / "api" / "record-chain-builder-bundles.v1.json"


def main() -> None:
    errors = []

    # Test 1: Builder file exists
    if not BUILDER.exists():
        errors.append("downloads/record-chain-builder.mjs: NOT FOUND")
        print("FAIL:\n" + "\n".join(f"  {e}" for e in errors))
        sys.exit(1)

    # Test 2: Bundle exists
    if not BUNDLE.exists():
        errors.append("api/record-chain-builder-bundles.v1.json: NOT FOUND")
    else:
        bundle = json.loads(BUNDLE.read_text())
        builder_info = bundle.get("canonical_builder", {})

        # Test 3: SHA256 matches
        actual_sha = hashlib.sha256(BUILDER.read_bytes()).hexdigest()
        expected_sha = builder_info.get("sha256", "")
        if actual_sha != expected_sha:
            errors.append(
                f"SHA256 mismatch: actual={actual_sha[:16]}... expected={expected_sha[:16]}..."
            )

        # Test 4: Size matches
        actual_size = BUILDER.stat().st_size
        expected_size = builder_info.get("size_bytes", 0)
        if actual_size != expected_size:
            errors.append(f"Size mismatch: actual={actual_size} expected={expected_size}")

    # Test 5: Builder --help exits 0
    result = subprocess.run(
        ["node", str(BUILDER), "help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        errors.append(f"builder --help exit code: {result.returncode}")

    # Test 6: Builder can create context-insufficient without network
    tmp = Path("/tmp/trinity-test-ci.json")
    result = subprocess.run(
        [
            "node", str(BUILDER), "context-insufficient",
            "--actor-label", "Test",
            "--provider", "Test",
            "--out", str(tmp),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        errors.append(f"context-insufficient build failed: {result.stderr[:200]}")
    elif tmp.exists():
        data = json.loads(tmp.read_text())
        if data.get("schema") != "trinityaccord.record-chain-submission.v1":
            errors.append(f"wrong submission schema: {data.get('schema')}")
        tmp.unlink()

    # Test 7: Builder can create echo with authorship proof
    tmp_echo = Path("/tmp/trinity-test-echo.json")
    tmp_key = Path("/tmp/trinity-test-key")
    # Get canonical oath first
    oath_result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        capture_output=True, text=True, timeout=10,
    )
    if oath_result.returncode != 0:
        errors.append(f"print-oath failed: {oath_result.stderr[:200]}")
    else:
        canonical_oath = oath_result.stdout
        result = subprocess.run(
            [
                "node", str(BUILDER), "echo",
                "--actor-label", "Test",
                "--provider", "Test",
                "--title", "Test",
                "--body", "Test",
                "--context-level", "CC-3",
                "--readback", canonical_oath,
                "--generate-authorship-key",
                "--key-dir", str(tmp_key),
                "--out", str(tmp_echo),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"echo build failed: {result.stderr[:200]}")
        elif tmp_echo.exists():
            data = json.loads(tmp_echo.read_text())
            if data.get("authorship_proof") is None:
                errors.append("echo: authorship_proof is None")
            elif data["authorship_proof"].get("algorithm") != "ed25519":
                errors.append(f"echo: wrong algorithm: {data['authorship_proof'].get('algorithm')}")
            # Verify oath data present
            oath = data.get("record_draft", {}).get("submission_oath_verification", {})
            if not oath:
                errors.append("echo: missing submission_oath_verification")
            elif oath.get("readback_was_not_auto_filled_by_builder") is not True:
                errors.append("echo: readback_was_not_auto_filled_by_builder not true")
            tmp_echo.unlink()

    if errors:
        print("FAIL: Builder bundle contract errors:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("PASS: All builder bundle contract tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()

    # Test 8: Embedded oath policy SHA256 matches api/record-chain-oath-policy.v1.json
    oath_policy_path = ROOT / "api" / "record-chain-oath-policy.v1.json"
    if oath_policy_path.exists():
        builder_text = BUILDER.read_text(encoding="utf-8")
        if "OATH_POLICY_SHA256" not in builder_text:
            errors.append("builder missing OATH_POLICY_SHA256 constant")
        else:
            import re as _re
            m = _re.search(r'OATH_POLICY_SHA256\s*=\s*"([a-f0-9]{64})"', builder_text)
            if m:
                embedded_sha = m.group(1)
                policy = json.loads(oath_policy_path.read_text(encoding="utf-8"))
                canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                actual_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                if embedded_sha != actual_sha:
                    errors.append(
                        f"embedded OATH_POLICY_SHA256 mismatch: embedded={embedded_sha[:16]}... actual={actual_sha[:16]}..."
                    )
            else:
                errors.append("cannot parse OATH_POLICY_SHA256 from builder")
    else:
        errors.append("api/record-chain-oath-policy.v1.json: NOT FOUND")
