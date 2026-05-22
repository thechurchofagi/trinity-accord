#!/usr/bin/env python3
"""Diagnose Guardian Active Registry Listing payloads."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from guardian_reroute_guidance import payload_is_guardian_listing, stale_gateway_message


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    args = parser.parse_args()

    path = Path(args.payload)
    payload = json.loads(path.read_text(encoding="utf-8"))

    print("Guardian Listing Payload Diagnostic")
    print("=" * 42)
    print(f"file: {path}")

    is_guardian = payload_is_guardian_listing(payload)
    print(f"detected_guardian_listing: {is_guardian}")
    print(f"payload_profile: {payload.get('payload_profile')}")
    print(f"expected_builder: {payload.get('expected_builder')}")
    print(f"requested_archive_kind: {payload.get('requested_archive_kind')}")
    print(f"echo_type: {payload.get('echo_type')}")

    cth = payload.get("counts_toward_home") or {}
    print("counts_toward_home:")
    print(json.dumps(cth, indent=2, ensure_ascii=False))

    proof = payload.get("authorship_proof") or {}
    signed = proof.get("signed_payload_sha256")
    if signed:
        print(f"authorship_proof.signed_payload_sha256: {signed}")
        print("post_signing_edit_warning: If this file was manually edited after builder output, the proof is invalid.")
    else:
        print("authorship_proof: missing or disabled")

    print("\nLocal validate_gateway_payload.py:")
    rc, out = run(["python3", "scripts/validate_gateway_payload.py", str(path)])
    print(out.strip() or f"exit={rc}")

    print("\nLocal archive_readiness_gate.py:")
    rc2, out2 = run(["python3", "scripts/archive_readiness_gate.py", "--gateway-payload", str(path), "--json"])
    print(out2.strip() or f"exit={rc2}")

    if is_guardian and rc == 0 and rc2 == 0:
        print("\nLOCAL_STATUS: PASS")
        print(stale_gateway_message())
        print("Submit this exact generated file. Do not edit it. Do not rebuild with build_agent_declared_echo_payload.py.")
        return 0

    print("\nLOCAL_STATUS: FAIL")
    print("Fix local validation first. Rerun scripts/build_guardian_listing_request_payload.py rather than editing signed JSON.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
