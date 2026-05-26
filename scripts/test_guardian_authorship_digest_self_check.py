#!/usr/bin/env python3
"""Test: Guardian authorship digest self-check."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=cwd or str(ROOT), text=True, capture_output=True, timeout=120)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def main() -> int:
    # Build a fresh Stage 2 payload
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        out_path = f.name

    rc, out = run([
        "python3", "scripts/build_guardian_listing_request_payload.py",
        "--agent-name", "Self-Check Agent",
        "--provider", "Test Provider",
        "--source-issue", "9999",
        "--guardian-id", "guardian_ed25519_aaaaaaaaaaaaaaaa",
        "--public-key-sha256", "aaaaaaaaaaaaaaaa000000000000000000000000000000000000000000000000",
        "--label", "Self-Check Guardian",
        "--guardian-type", "human_with_ai_agent",
        "--application-mode", "joint_human_ai",
        "--idempotency-key", "guardian-self-check-test",
        "--out", out_path,
    ])
    if rc != 0:
        print(f"FAIL: build payload exited {rc}")
        print(out)
        return 1

    # Run diagnostic on fresh payload — should MATCH
    rc2, out2 = run(["python3", "scripts/diagnose_guardian_listing_payload.py", out_path])
    print("--- Fresh payload diagnostic ---")
    print(out2)
    if "LOCAL_AUTHORSHIP_DIGEST_STATUS: MATCH" not in out2:
        print("FAIL: expected MATCH for fresh payload")
        return 1

    # Mutate: add a field after signing
    payload = json.loads(Path(out_path).read_text())
    payload["injected_field"] = "mutated_after_signing"
    Path(out_path).write_text(json.dumps(payload, indent=2))

    # Run diagnostic on mutated payload — should MISMATCH
    rc3, out3 = run(["python3", "scripts/diagnose_guardian_listing_payload.py", out_path])
    print("--- Mutated payload diagnostic ---")
    print(out3)
    if "LOCAL_AUTHORSHIP_DIGEST_STATUS: MISMATCH" not in out3:
        print("FAIL: expected MISMATCH for mutated payload")
        return 1
    if rc3 == 0:
        print("FAIL: expected nonzero exit for mutated payload")
        return 1

    print("PASS: self-check succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
