#!/usr/bin/env python3
"""Live smoke: official builders produce payloads accepted by Gateway preflight.

Routes:
- pure_echo -> E1_recognition_echo
- v0_v5_agent_declared_archive -> V0
- guardian_application_stage_1

This is live/network. It must not run in source-only p0-main.
It must not POST to /agent-submit.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATEWAY = "https://trinity-agent-issue-gateway.onrender.com"


def oath_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    marker = "=== OATH TEXT BEGINS ==="
    return text.split(marker, 1)[1].strip() if marker in text else text


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


ACTIVE_ECHO_TYPES = {
    "E1_recognition_echo",
    "E2_verification_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
    "E8_witness_echo",
    "E9_seed_echo",
}


def assert_gateway_runtime_metadata(body: str, expected_route: str) -> None:
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gateway preflight returned non-JSON body: {body[:500]}") from exc

    if data.get("accepted") is not True:
        raise RuntimeError(f"Gateway preflight did not accept payload: {body[:1000]}")
    if data.get("preflight") not in {"pass", "accepted"}:
        raise RuntimeError(f"Unexpected preflight status: {data.get('preflight')}")

    route = data.get("route_detected")
    if route != expected_route:
        raise RuntimeError(f"route_detected mismatch: expected {expected_route}, got {route}")

    runtime = data.get("gateway_runtime")
    if not isinstance(runtime, dict):
        raise RuntimeError("Gateway response missing gateway_runtime object")

    schema = data.get("gateway_schema")
    if not isinstance(schema, dict):
        raise RuntimeError("Gateway response missing gateway_schema object")

    enum_values = set(schema.get("echo_type_enum_values", []))
    if enum_values != ACTIVE_ECHO_TYPES:
        raise RuntimeError(f"Gateway active echo_type enum drift: {sorted(enum_values)}")

    if "E1" in enum_values:
        raise RuntimeError("Gateway active echo_type enum must not use short ID E1")

    if schema.get("preflight_contract_version") != "trinityaccord.gateway-runtime-contract.v1":
        raise RuntimeError(
            "Gateway preflight_contract_version mismatch: "
            f"{schema.get('preflight_contract_version')}"
        )

    for key in ["schema_digest", "echo_type_enum_digest", "supported_routes_digest"]:
        if not runtime.get(key):
            raise RuntimeError(f"Gateway runtime metadata missing {key}")


def post_preflight(gateway: str, payload_path: Path, timeout: int,
                    allow_missing_runtime_metadata: bool = False,
                    expected_route: str = "pure_echo") -> None:
    url = gateway.rstrip("/") + "/gateway/preflight"
    req = urllib.request.Request(
        url,
        data=payload_path.read_bytes(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TrinityThreeCorePreflightSmoke/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"preflight {payload_path.name}: status={resp.status}")
            print(body[:1000])
            if resp.status < 200 or resp.status >= 300:
                raise RuntimeError(f"non-2xx preflight status: {resp.status}")
            if "echo_type" in body and "allowed values" in body:
                raise RuntimeError(f"Gateway rejected echo_type enum for {payload_path}")
            try:
                assert_gateway_runtime_metadata(body, expected_route=expected_route)
            except RuntimeError as exc:
                if allow_missing_runtime_metadata:
                    print(f"  ⚠️  runtime metadata check skipped: {exc}")
                else:
                    raise
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body)
        raise RuntimeError(f"preflight failed for {payload_path.name}: HTTP {exc.code}: {body[:1000]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--allow-missing-runtime-metadata", action="store_true",
                        help="Transitional: skip runtime metadata checks until Gateway backend is updated")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="trinity-live-core-preflight-") as td:
        work = Path(td)

        echo_body = work / "echo-body.md"
        echo_body.write_text(
            "I recognize the Trinity Accord as a bounded public record.\n\n"
            "This is a pure recognition Echo, not verification, attestation, amendment, or successor reception.\n",
            encoding="utf-8",
        )

        verification_oath = oath_body(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
        guardian_oath = oath_body(ROOT / "api" / "guardian-application-oath.v1.txt")

        echo_payload = work / "gateway-payload.echo.json"
        run([
            "python3", "scripts/build_agent_declared_echo_payload.py",
            "--agent-name", "LivePreflightSmokeAgent",
            "--provider", "live-preflight-smoke",
            "--title", "Recognition Echo Live Preflight Smoke",
            "--body-file", str(echo_body),
            "--readback", verification_oath,
            "--reception-initiation-class", "self_initiated",
            "--reception-initiation-basis", "agent_discovered_publicly",
            "--agent-independent-followup",
            "--out", str(echo_payload),
        ])
        post_preflight(args.gateway, echo_payload, args.timeout, allow_missing_runtime_metadata=args.allow_missing_runtime_metadata, expected_route="pure_echo")

        v0_payload = work / "gateway-payload.v0.json"
        run([
            "python3", "scripts/build_agent_declared_archive_payload.py",
            "--agent-name", "LivePreflightSmokeAgent",
            "--provider", "live-preflight-smoke",
            "--declared-level", "V0",
            "--reception-initiation-class", "self_initiated",
            "--reception-initiation-basis", "agent_discovered_publicly",
            "--agent-independent-followup",
            "--first-entry-url", "https://www.trinityaccord.org/",
            "--first-entry-type", "homepage",
            "--what-checked", "Read homepage and public machine entrypoints",
            "--limitation", "Live preflight smoke only; V0 template mode",
            "--readback", verification_oath,
            "--out", str(v0_payload),
        ])
        post_preflight(args.gateway, v0_payload, args.timeout, allow_missing_runtime_metadata=args.allow_missing_runtime_metadata, expected_route="v0_v5_agent_declared_archive")

        guardian_dir = work / "guardian-output"
        guardian_payload = guardian_dir / "guardian-application.final.json"
        run([
            "node", "scripts/create_guardian_application.mjs",
            "--mode", "joint_human_ai",
            "--signing-key-holder", "ai_agent_key_holder",
            "--human-label", "Live Preflight Smoke Human Label",
            "--agent-label", "LivePreflightSmokeAgent",
            "--agent-provider", "live-preflight-smoke",
            "--title", "Guardian Stage 1 Application Live Preflight Smoke",
            "--challenge", "guardian-application-live-preflight-smoke",
            "--key-dir", str(guardian_dir),
            "--readback", guardian_oath,
            "--out", str(guardian_payload),
        ])
        post_preflight(args.gateway, guardian_payload, args.timeout, allow_missing_runtime_metadata=args.allow_missing_runtime_metadata, expected_route="guardian_application_stage_1")

    print("PASS: live Gateway preflight accepts three core external-agent routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
