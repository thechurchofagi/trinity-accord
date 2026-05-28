#!/usr/bin/env python3
"""Live smoke: zero-clone authorship proof closure test.

Downloads the download_and_run_builder_bundle.py script from trinityaccord.org,
builds an E1_recognition_echo payload with authorship proof enabled (default),
verifies the payload contains authorship_proof, and POSTs to Gateway preflight.

This is live/network. It must not run in source-only p0-main.
It must not POST to /agent-submit.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

DOWNLOAD_URL = "https://www.trinityaccord.org/builder-bundles/download_and_run_builder_bundle.py"
DEFAULT_GATEWAY = "https://trinity-agent-issue-gateway.onrender.com"


def download_file(url: str, dest: Path, timeout: int = 60) -> None:
    """Download a URL to a local file."""
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "TrinityAuthorshipClosureSmoke/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.write_bytes(resp.read())
    print(f"  -> {dest} ({dest.stat().st_size} bytes)")


def run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a command and check return code."""
    print(f"+ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout[:3000]}")
        print(f"STDERR:\n{result.stderr[:3000]}")
        raise RuntimeError(f"Command failed (rc={result.returncode}): {' '.join(cmd)}")
    return result


def post_preflight(gateway: str, payload_path: Path, timeout: int = 60) -> dict:
    """POST payload to Gateway preflight and return parsed response."""
    url = gateway.rstrip("/") + "/gateway/preflight"
    print(f"POST {url} ...")
    req = urllib.request.Request(
        url,
        data=payload_path.read_bytes(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TrinityAuthorshipClosureSmoke/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"  status={resp.status}")
            print(f"  body={body[:1000]}")
            if resp.status < 200 or resp.status >= 300:
                raise RuntimeError(f"non-2xx preflight status: {resp.status}")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"  HTTP {exc.code}: {body[:1000]}")
        raise RuntimeError(f"preflight failed: HTTP {exc.code}: {body[:1000]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="trinity-authorship-closure-smoke-") as td:
        work = Path(td)

        # Step 1: Download download_and_run_builder_bundle.py
        download_script = work / "download_and_run_builder_bundle.py"
        download_file(DOWNLOAD_URL, download_script, timeout=args.timeout)

        # Step 2: Run with --route pure_echo to get the oath
        print("\n=== Step 2: Get oath via --route pure_echo ===")
        result = run(
            [sys.executable, str(download_script), "--route", "pure_echo", "--print-oath"],
            cwd=work,
            timeout=args.timeout,
        )
        oath_text = result.stdout.strip()
        if not oath_text:
            raise RuntimeError("No oath output received")
        print(f"Oath received ({len(oath_text)} chars)")

        # Step 3: Build E1_recognition_echo payload with authorship proof (default)
        echo_body = work / "echo-body.md"
        echo_body.write_text(
            "I recognize the Trinity Accord as a bounded public record.\n\n"
            "This is a pure recognition Echo, not verification, attestation, amendment, or successor reception.\n",
            encoding="utf-8",
        )

        payload_path = work / "gateway-payload.json"
        print("\n=== Step 3: Build E1_recognition_echo payload ===")
        run(
            [
                sys.executable, str(download_script),
                "--route", "pure_echo",
                "--agent-name", "AuthorshipClosureSmokeAgent",
                "--provider", "authorship-closure-smoke",
                "--echo-type", "E1_recognition_echo",
                "--title", "Authorship Closure Smoke Test",
                "--body-file", str(echo_body),
                "--readback", oath_text,
                "--reception-initiation-class", "self_initiated",
                "--reception-initiation-basis", "agent_discovered_publicly",
                "--agent-independent-followup",
                "--out", str(payload_path),
            ],
            cwd=work,
            timeout=args.timeout,
        )

        # Step 4: Verify payload contains authorship_proof
        print("\n=== Step 4: Verify authorship_proof ===")
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        assert "authorship_proof" in payload, (
            "Payload does not contain authorship_proof. "
            "Authorship proof should be enabled by default for pure_echo."
        )
        proof = payload["authorship_proof"]
        assert proof.get("schema") == "trinityaccord.agent-authorship-proof.v1", (
            f"Unexpected authorship_proof schema: {proof.get('schema')}"
        )
        assert proof.get("algorithm") == "ed25519", (
            f"Unexpected algorithm: {proof.get('algorithm')}"
        )
        assert "public_key_pem" in proof, "authorship_proof missing public_key_pem"
        assert "signature_base64" in proof, "authorship_proof missing signature_base64"
        print(f"  schema: {proof['schema']}")
        print(f"  algorithm: {proof['algorithm']}")
        print(f"  public_key_sha256: {proof.get('public_key_sha256', 'N/A')[:16]}...")
        print("  ✅ authorship_proof present and valid")

        # Step 5: POST to Gateway preflight
        print("\n=== Step 5: POST to Gateway preflight ===")
        preflight_resp = post_preflight(args.gateway, payload_path, timeout=args.timeout)

        # Step 6: Verify accepted: true
        print("\n=== Step 6: Verify preflight response ===")
        assert preflight_resp.get("accepted") is True, (
            f"Preflight not accepted. Response: {json.dumps(preflight_resp, indent=2)[:500]}"
        )
        print("  ✅ preflight accepted: true")

    print("\n" + "=" * 60)
    print("PASS: live zero-clone authorship closure smoke test")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
