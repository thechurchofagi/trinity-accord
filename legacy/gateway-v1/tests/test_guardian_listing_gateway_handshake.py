#!/usr/bin/env python3
"""Test Guardian listing Gateway runtime handshake with mock servers."""

import json
import subprocess
import sys
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


# Full capabilities response (compatible Gateway)
FULL_CAPS = {
    "schema": "trinity.gateway-capabilities.v1",
    "deployed_commit": "test123",
    "authorship_canonical_version": "trinity.agent_authorship_common.v1",
    "supports_payload_profiles": ["guardian_active_registry_listing_request.v1"],
    "supports_gateway_capabilities": [
        "guardian_registry_listing_request",
        "guardian_listing_request",
        "gateway_intake_fields",
        "counts_toward_home.guardian_registry",
        "counts_toward_home.exclude_from_reception_total",
        "payload_profile.guardian_active_registry_listing_request.v1",
        "authorship_canonical.trinity.agent_authorship_common.v1",
    ],
}

# Stale capabilities response (missing some required)
STALE_CAPS = {
    "schema": "trinity.gateway-capabilities.v1",
    "deployed_commit": "old456",
    "authorship_canonical_version": "trinity.agent_authorship_common.v1",
    "supports_payload_profiles": [],
    "supports_gateway_capabilities": [
        "guardian_registry_listing_request",
        # Missing others
    ],
}

VERSION_INFO = {
    "schema": "trinity.gateway-version.v1",
    "deployed_commit": "test123",
    "repo": "thechurchofagi/trinity-accord",
    "authorship_canonical_version": "trinity.agent_authorship_common.v1",
}


class MockHandler(BaseHTTPRequestHandler):
    caps_response = FULL_CAPS

    def do_GET(self):
        if self.path == "/gateway/version":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(VERSION_INFO).encode())
        elif self.path == "/gateway/capabilities":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.caps_response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logs


def run_test_with_caps(caps, expect_pass, label):
    """Run diagnose with a mock server returning given capabilities."""
    MockHandler.caps_response = caps

    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        out = td / "guardian-listing-request.json"

        # Build payload
        build = subprocess.run(
            [
                "python3", "scripts/build_guardian_listing_request_payload.py",
                "--agent-name", f"Handshake Test Agent ({label})",
                "--provider", "Test Provider",
                "--source-issue", "238",
                "--guardian-id", "guardian_ed25519_cccccccccccccccc",
                "--public-key-sha256", "cccccccccccccccc000000000000000000000000000000000000000000000000",
                "--label", f"Handshake Test Guardian ({label})",
                "--guardian-type", "human_with_ai_agent",
                "--application-mode", "joint_human_ai",
                "--idempotency-key", f"guardian-handshake-{label}-0001",
                "--out", str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )
        require(build.returncode == 0, f"Build failed ({label}):\n{build.stdout}\n{build.stderr}")

        # Run diagnose with --require-gateway-compatible
        diag = subprocess.run(
            [
                "python3", "scripts/diagnose_guardian_listing_payload.py",
                "--gateway-base-url", f"http://127.0.0.1:{port}",
                "--require-gateway-compatible",
                str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )

        if expect_pass:
            require(diag.returncode == 0, f"Expected pass ({label}) but got exit {diag.returncode}:\n{diag.stdout}\n{diag.stderr}")
            require("gateway_capability_status: compatible" in diag.stdout, f"Expected 'compatible' in output ({label}):\n{diag.stdout}")
        else:
            require(diag.returncode != 0, f"Expected fail ({label}) but got exit 0:\n{diag.stdout}")
            require("GATEWAY_VERSION_STALE_FOR_GUARDIAN_LISTING" in diag.stdout, f"Expected stale error ({label}):\n{diag.stdout}")

    server.shutdown()
    print(f"  PASS: {label}")


def main():
    print("Testing Guardian listing Gateway handshake...")

    # Test 1: Stale Gateway (missing capabilities)
    run_test_with_caps(STALE_CAPS, expect_pass=False, label="stale")

    # Test 2: Full Gateway (all capabilities present)
    run_test_with_caps(FULL_CAPS, expect_pass=True, label="compatible")

    print("PASS: all Gateway handshake tests")


if __name__ == "__main__":
    main()
