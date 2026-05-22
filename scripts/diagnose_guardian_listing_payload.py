#!/usr/bin/env python3
"""Diagnose Guardian Active Registry Listing payloads."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from guardian_reroute_guidance import payload_is_guardian_listing, stale_gateway_message
from guardian_gateway_contract import (
    GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES,
    missing_capabilities,
)


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def fetch_json(url: str) -> tuple[dict | None, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}: {exc.reason}"
    except Exception as exc:
        return None, str(exc)


def normalize_gateway_capabilities(data: dict | None) -> list[str]:
    if not isinstance(data, dict):
        return []

    values = []
    for key in [
        "supports_gateway_capabilities",
        "gateway_capabilities",
        "capabilities",
        "supported_capabilities",
    ]:
        v = data.get(key)
        if isinstance(v, list):
            values.extend(str(x) for x in v)

    profiles = data.get("supports_payload_profiles")
    if isinstance(profiles, list):
        values.extend(f"payload_profile.{p}" for p in profiles)

    canonical = data.get("authorship_canonical_version")
    if canonical:
        values.append(f"authorship_canonical.{canonical}")

    return sorted(set(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("--gateway-base-url", default=None)
    parser.add_argument("--require-gateway-compatible", action="store_true")
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
    print(f"gateway_contract_version: {payload.get('gateway_contract_version')}")
    print(f"authorship_canonical_version: {payload.get('authorship_canonical_version')}")
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

    # Gateway runtime compatibility check
    gateway_compatible = None

    if args.gateway_base_url:
        base = args.gateway_base_url.rstrip("/")
        print("\nGateway runtime compatibility:")

        version, version_err = fetch_json(f"{base}/gateway/version")
        caps, caps_err = fetch_json(f"{base}/gateway/capabilities")

        if version_err:
            print(f"  /gateway/version: unavailable ({version_err})")
        else:
            print(f"  /gateway/version: {json.dumps(version, ensure_ascii=False)}")

        if caps_err:
            print(f"  /gateway/capabilities: unavailable ({caps_err})")
            gateway_compatible = False
            missing = GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES
        else:
            runtime_caps = normalize_gateway_capabilities(caps)
            missing = missing_capabilities(runtime_caps)
            gateway_compatible = not missing
            print(f"  runtime_capabilities: {json.dumps(runtime_caps, ensure_ascii=False)}")
            if missing:
                print("  GATEWAY_VERSION_STALE_FOR_GUARDIAN_LISTING")
                print(f"  missing_capabilities: {json.dumps(missing, ensure_ascii=False)}")
            else:
                print("  gateway_capability_status: compatible")

    if is_guardian and rc == 0 and rc2 == 0:
        if args.require_gateway_compatible and gateway_compatible is False:
            print("\nREMOTE_STATUS: FAIL")
            print("Gateway is missing required Guardian Stage 2 capabilities.")
            print("Do not submit. Do not edit payload. Redeploy/update Gateway.")
            return 2

        print("\nLOCAL_STATUS: PASS")
        print(stale_gateway_message())
        print("Submit this exact generated file. Do not edit it. Do not rebuild with build_agent_declared_echo_payload.py.")
        return 0

    print("\nLOCAL_STATUS: FAIL")
    print("Fix local validation first. Rerun scripts/build_guardian_listing_request_payload.py rather than editing signed JSON.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
