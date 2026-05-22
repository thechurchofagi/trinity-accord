#!/usr/bin/env python3
"""Preflight Guardian Stage 2 listing payload locally and against Gateway runtime."""

from __future__ import annotations

import argparse
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=90)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("--gateway-base-url", required=True)
    parser.add_argument("--submit-preflight", action="store_true")
    args = parser.parse_args()

    payload_path = Path(args.payload)

    diag_cmd = [
        "python3",
        "scripts/diagnose_guardian_listing_payload.py",
        "--gateway-base-url",
        args.gateway_base_url,
        "--require-gateway-compatible",
        str(payload_path),
    ]

    rc, out = run(diag_cmd)
    print(out)
    if rc != 0:
        print("PRE_SUBMISSION_STATUS: BLOCKED")
        return rc

    if args.submit_preflight:
        data = payload_path.read_bytes()
        req = urllib.request.Request(
            args.gateway_base_url.rstrip("/") + "/gateway/preflight",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                print("Gateway /gateway/preflight response:")
                print(response.read().decode("utf-8"))
        except Exception as exc:
            print(f"Gateway /gateway/preflight failed: {exc}")
            print(
                "If local + capability checks passed but preflight fails with signed_payload_sha256 mismatch, "
                "Gateway canonicalization is stale or the submitted file differs."
            )
            return 3

    print("PRE_SUBMISSION_STATUS: PASS")
    print("Submit the exact same generated file. Do not edit it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
