#!/usr/bin/env python3
"""Legacy Gateway deploy boundary contract.

trinity-agent-issue-gateway is a legacy/historical service.
It must NOT auto-deploy from main branch pushes.
Current public submission path is trinity-record-chain-gateway only.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except Exception:
    # Fallback: parse render.yaml manually
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
RENDER_YAML = ROOT / "render.yaml"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    if not RENDER_YAML.exists():
        fail("render.yaml missing")

    text = RENDER_YAML.read_text(encoding="utf-8")

    if yaml:
        data = yaml.safe_load(text)
        services = data.get("services", [])
    else:
        # Minimal manual check
        services = []

    # Check autoDeploy for legacy gateway
    if yaml and services:
        for svc in services:
            if not isinstance(svc, dict):
                continue
            name = svc.get("name", "")
            if "agent-issue-gateway" in name:
                if svc.get("autoDeploy") is not False:
                    fail(f"{name} has autoDeploy={svc.get('autoDeploy')} (must be false)")
                ok(f"{name}: autoDeploy is false")

    # Text-based fallback check: the YAML must not have autoDeploy: true
    # for agent-issue-gateway
    import re
    # Find the agent-issue-gateway service block
    in_block = False
    for line in text.splitlines():
        if "agent-issue-gateway" in line:
            in_block = True
        if in_block and "autoDeploy:" in line:
            if "true" in line.lower():
                fail("render.yaml: agent-issue-gateway has autoDeploy: true (must be false)")
            ok("render.yaml: agent-issue-gateway autoDeploy is not true")
            break

    # Verify current public submission points to record-chain gateway, not old gateway
    well_known = ROOT / ".well-known" / "trinity-accord.json"
    if well_known.exists():
        import json
        wk = json.loads(well_known.read_text(encoding="utf-8"))
        csm = wk.get("current_public_submission", {})
        # Check gateway_contract field
        contract = csm.get("gateway_contract", "")
        if "agent-issue-gateway" in contract:
            fail(f".well-known current_public_submission gateway_contract points to old gateway: {contract}")
        if "record-chain" not in contract:
            fail(f".well-known current_public_submission gateway_contract does not reference record-chain: {contract}")
        ok(f".well-known current_public_submission correctly references record-chain gateway")

    print("\n=== LEGACY GATEWAY DEPLOY BOUNDARY OK ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
