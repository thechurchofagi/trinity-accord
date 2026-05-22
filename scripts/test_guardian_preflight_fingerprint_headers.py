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
            self.wfile.write(json.dumps({
                "supports_gateway_capabilities": [
                    "guardian_active_registry_listing",
                    "guardian_listing_request_v1",
                ],
                "authorship_canonical_version": "trinity.agent_authorship_common.v1",
            }).encode())
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

    rc, out = subprocess.run(
        ["python3", "scripts/build_guardian_listing_request_payload.py",
         "--agent-name", "Header Test", "--provider", "Test",
         "--source-issue", "9997", "--guardian-id", "guardian_ed25519_headertest",
         "--public-key-sha256", "headertest00000000000000000000000000000000000000000000000000000000",
         "--label", "Header Guardian", "--guardian-type", "human_with_ai_agent",
         "--application-mode", "joint_human_ai", "--idempotency-key", "header-test",
         "--out", out_path],
        cwd=str(ROOT), text=True, capture_output=True, timeout=120
    ).returncode
    if rc != 0:
        print("FAIL: build payload")
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
    missing = [h for h in required_headers if h not in captured_headers]
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
