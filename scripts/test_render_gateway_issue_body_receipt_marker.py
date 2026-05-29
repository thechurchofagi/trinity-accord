#!/usr/bin/env python3
"""Gateway Issue body renderer must emit v30.7 receipt marker and avoid duplicate intake keys."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

CANDIDATES = [
    ROOT / "render_gateway_issue_body.py",
    ROOT / "scripts" / "render_gateway_issue_body.py",
    ROOT / "gateway" / "render_gateway_issue_body.py",
]

def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("render_gateway_issue_body_under_test", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main() -> int:
    renderer_path = next((p for p in CANDIDATES if p.exists()), None)
    if renderer_path is None:
        print("FAIL: render_gateway_issue_body.py not found in expected locations")
        return 1

    module = load_module(renderer_path)

    if not hasattr(module, "render_gateway_receipt_marker"):
        print("FAIL: render_gateway_receipt_marker helper missing")
        return 1

    marker = module.render_gateway_receipt_marker(
        gateway_receipt_id="gar-test-302",
        gateway_commit="testcommit",
        gateway_service="trinity-agent-issue-gateway",
        route_detected="pure_echo",
        submission_type="echo_candidate",
        requested_archive_kind="agent_declared_echo_archive",
        payload_sha256="abc123",
        issued_at="2026-05-29T00:00:00Z",
    )

    required = [
        "<!-- trinity-gateway-receipt:v1",
        "receipt_id: gar-test-302",
        "gateway_service: trinity-agent-issue-gateway",
        "gateway_commit: testcommit",
        "created_by_gateway: true",
        "render_api_only: true",
        "server_validated: true",
        "server_rendered: true",
        "route_detected: pure_echo",
        "submission_type: echo_candidate",
        "requested_archive_kind: agent_declared_echo_archive",
        "payload_sha256: abc123",
        "issued_at: 2026-05-29T00:00:00Z",
    ]
    missing = [item for item in required if item not in marker]
    if missing:
        print("FAIL: receipt marker missing required strings:", missing)
        print(marker)
        return 1

    if hasattr(module, "render_intake_block"):
        block = module.render_intake_block({
            "agent_readback_sha256": "abc",
            "verification_oath_schema": "trinityaccord.verification-oath.v2",
        })
        count = len(re.findall(r"^agent_readback_sha256:", block, re.MULTILINE))
        if count != 1:
            print("FAIL: render_intake_block must emit agent_readback_sha256 exactly once")
            print(block)
            return 1

    print("PASS: Gateway Issue body renderer exposes receipt marker and no duplicate readback key")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
