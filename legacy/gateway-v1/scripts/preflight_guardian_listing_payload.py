#!/usr/bin/env python3
"""Preflight Guardian Stage 2 listing payload locally and against Gateway runtime."""

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

from agent_authorship_common import authorship_debug_fingerprint


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=90)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def classify_gateway_preflight_error(error_json: dict) -> None:
    code = error_json.get("error_code")

    if code == "GATEWAY_VERSION_STALE_FOR_GUARDIAN_LISTING":
        print("CLASSIFICATION: gateway_runtime_stale")
        print("ACTION: update/redeploy Gateway. Do not edit or re-sign payload.")
        return

    if code == "AUTHORED_PAYLOAD_DIGEST_MISMATCH":
        print("CLASSIFICATION: authorship_digest_mismatch")
        signed = error_json.get("signed_payload_sha256") or error_json.get("signed_payload_sha256_from_proof")
        computed = error_json.get("computed_payload_sha256") or error_json.get("computed_payload_sha256_by_gateway")
        received = error_json.get("received_raw_body_sha256")
        local_file = error_json.get("x_trinity_payload_file_sha256")

        print(f"  signed_payload_sha256: {signed}")
        print(f"  computed_payload_sha256_by_gateway: {computed}")
        print(f"  received_raw_body_sha256: {received}")
        print(f"  x_trinity_payload_file_sha256: {local_file}")

        if received and local_file and received != local_file:
            print("LIKELY_CAUSE: submitted bytes differ from local file or transport wrapped/modified body.")
        elif signed and computed and signed != computed:
            print("LIKELY_CAUSE: Gateway canonicalization differs from local contract, or payload changed after signing.")
        else:
            print("LIKELY_CAUSE: insufficient Gateway diagnostic fields; ask Gateway to return computed digest and payload keys.")

        print("ACTION: do not strip fields or re-sign manually. Compare exact file, raw body hash, and Gateway canonical fields.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("--gateway-base-url", required=True)
    parser.add_argument("--submit-preflight", action="store_true")
    args = parser.parse_args()

    payload_path = Path(args.payload)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    fingerprint = authorship_debug_fingerprint(payload, str(payload_path))

    print("Local submission fingerprint:")
    print(json.dumps(fingerprint, indent=2, ensure_ascii=False))

    if fingerprint.get("authorship_digest_matches_proof") is False:
        print("PRE_SUBMISSION_STATUS: BLOCKED")
        print("Local payload digest does not match authorship_proof.signed_payload_sha256.")
        print("Rerun scripts/build_guardian_listing_request_payload.py. Do not submit this file.")
        return 4

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
        proof = payload.get("authorship_proof") or {}
        headers = {
            "Content-Type": "application/json",
            "X-Trinity-Payload-File-SHA256": fingerprint.get("payload_file_sha256") or "",
            "X-Trinity-Authorship-Payload-SHA256": fingerprint["local_authorship_payload_sha256"],
            "X-Trinity-Authorship-Proof-SHA256": proof.get("signed_payload_sha256") or "",
            "X-Trinity-Authorship-Canonical-Version": fingerprint["authorship_canonical_version"],
            "X-Trinity-Payload-Profile": str(fingerprint.get("payload_profile") or ""),
            "X-Trinity-Gateway-Contract-Version": str(fingerprint.get("gateway_contract_version") or ""),
        }
        req = urllib.request.Request(
            args.gateway_base_url.rstrip("/") + "/gateway/preflight",
            data=data,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                print("Gateway /gateway/preflight response:")
                print(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"Gateway /gateway/preflight failed: HTTP {exc.code} {exc.reason}")
            if body:
                print("Gateway error body:")
                print(body)
                try:
                    classify_gateway_preflight_error(json.loads(body))
                except Exception:
                    pass
            return 3
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
