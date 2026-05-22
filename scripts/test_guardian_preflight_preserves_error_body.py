#!/usr/bin/env python3
"""Test: Guardian preflight preserves Gateway HTTP error body."""

import json
import subprocess
import sys
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MOCK_CAPABILITIES = {
    "supports_gateway_capabilities": [
        "guardian_registry_listing_request",
        "guardian_listing_request",
        "gateway_intake_fields",
        "counts_toward_home.guardian_registry",
        "counts_toward_home.exclude_from_reception_total",
    ],
    "supports_payload_profiles": [
        "guardian_active_registry_listing_request.v1",
    ],
    "authorship_canonical_version": "trinity.agent_authorship_common.v1",
}


class MockGatewayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/gateway/version":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"version": "test-mock-1.0"}).encode())
        elif self.path == "/gateway/capabilities":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(MOCK_CAPABILITIES).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/gateway/preflight":
            length = int(self.headers.get("Content-Length", 0))
            self.rfile.read(length)
            error_body = json.dumps({
                "ok": False,
                "error_code": "AUTHORED_PAYLOAD_DIGEST_MISMATCH",
                "signed_payload_sha256_from_proof": "aaaa",
                "computed_payload_sha256_by_gateway": "bbbb",
                "received_raw_body_sha256": "cccc",
            })
            self.send_response(422)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error_body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress logs


def main() -> int:
    server = HTTPServer(("127.0.0.1", 0), MockGatewayHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Build a payload
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        out_path = f.name

    sha = "bbbbbbbbbbbbbbbb000000000000000000000000000000000000000000000000"
    gid = "guardian_ed25519_" + sha[:16]

    rc, out = subprocess.run(
        ["python3", "scripts/build_guardian_listing_request_payload.py",
         "--agent-name", "Error Body Test", "--provider", "Test",
         "--source-issue", "9998", "--guardian-id", gid,
         "--public-key-sha256", sha,
         "--label", "Error Body Guardian", "--guardian-type", "human_with_ai_agent",
         "--application-mode", "joint_human_ai", "--idempotency-key", "error-body-test",
         "--out", out_path],
        cwd=str(ROOT), text=True, capture_output=True, timeout=120
    ).returncode
    if rc != 0:
        print("FAIL: build payload")
        print(out)
        return 1

    # Run preflight against mock Gateway
    result = subprocess.run(
        ["python3", "scripts/preflight_guardian_listing_payload.py",
         out_path, "--gateway-base-url", f"http://127.0.0.1:{port}", "--submit-preflight"],
        cwd=str(ROOT), text=True, capture_output=True, timeout=60
    )
    output = (result.stdout or "") + (result.stderr or "")
    print(output)

    server.shutdown()

    checks = [
        "Gateway error body:" in output,
        "AUTHORED_PAYLOAD_DIGEST_MISMATCH" in output,
        "CLASSIFICATION: authorship_digest_mismatch" in output,
    ]
    if all(checks):
        print("PASS: error body preserved and classified")
        return 0
    else:
        print(f"FAIL: checks {[c for c in checks if not c]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
