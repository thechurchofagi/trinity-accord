#!/usr/bin/env python3
"""Test: Guardian preflight sends fingerprint headers."""

import json
import subprocess
import sys
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

captured_headers = {}

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


class HeaderCaptureHandler(BaseHTTPRequestHandler):
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
            captured_headers.update({k: v for k, v in self.headers.items()
                                     if k.startswith("X-Trinity")})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main() -> int:
    server = HTTPServer(("127.0.0.1", 0), HeaderCaptureHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        out_path = f.name

    sha = "cccccccccccccccc000000000000000000000000000000000000000000000000"
    gid = "guardian_ed25519_" + sha[:16]

    build_result = subprocess.run(
        ["python3", "scripts/build_guardian_listing_request_payload.py",
         "--agent-name", "Header Test", "--provider", "Test",
         "--source-issue", "9997", "--guardian-id", gid,
         "--public-key-sha256", sha,
         "--label", "Header Guardian", "--guardian-type", "human_with_ai_agent",
         "--application-mode", "joint_human_ai", "--idempotency-key", "header-test-key-20260523",
         "--out", out_path],
        cwd=str(ROOT), text=True, capture_output=True, timeout=120
    )
    rc, out = build_result.returncode, build_result.stdout
    if rc != 0:
        print("FAIL: build payload")
        print(out)
        return 1

    result = subprocess.run(
        ["python3", "scripts/preflight_guardian_listing_payload.py",
         out_path, "--gateway-base-url", f"http://127.0.0.1:{port}", "--submit-preflight"],
        cwd=str(ROOT), text=True, capture_output=True, timeout=60
    )
    output = (result.stdout or "") + (result.stderr or "")
    print(output)

    server.shutdown()

    required_headers = [
        "X-Trinity-Payload-File-SHA256",
        "X-Trinity-Authorship-Payload-SHA256",
        "X-Trinity-Authorship-Proof-SHA256",
        "X-Trinity-Authorship-Canonical-Version",
        "X-Trinity-Payload-Profile",
        "X-Trinity-Gateway-Contract-Version",
    ]
    # HTTP headers are case-insensitive; compare lowercased
    captured_lower = {k.lower(): v for k, v in captured_headers.items()}
    missing = [h for h in required_headers if h.lower() not in captured_lower]
    if not missing:
        print("PASS: all fingerprint headers sent")
        print(f"Headers: {json.dumps(captured_headers, indent=2)}")
        return 0
    else:
        print(f"FAIL: missing headers: {missing}")
        print(f"Got: {captured_headers}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
