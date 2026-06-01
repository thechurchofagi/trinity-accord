#!/usr/bin/env python3
"""Gateway online smoke workflow should exist and remain manual-only."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".github" / "workflows" / "gateway-online-smoke.yml"

if not path.exists():
    print("FAIL: missing .github/workflows/gateway-online-smoke.yml")
    sys.exit(1)

data = yaml.safe_load(path.read_text(encoding="utf-8"))

on_block = data.get("on")
if isinstance(on_block, dict):
    has_dispatch = "workflow_dispatch" in on_block
else:
    text = path.read_text(encoding="utf-8")
    has_dispatch = "workflow_dispatch:" in text

if not has_dispatch:
    print("FAIL: gateway-online-smoke.yml must be workflow_dispatch-only")
    sys.exit(1)

text = path.read_text(encoding="utf-8")
if "push:" in text or "pull_request:" in text:
    print("FAIL: gateway-online-smoke.yml must not run on push or pull_request")
    sys.exit(1)

if "bash scripts/smoke_gateway_online.sh" not in text:
    print("FAIL: gateway-online-smoke.yml does not run smoke_gateway_online.sh")
    sys.exit(1)

if "contents: read" not in text:
    print("FAIL: gateway-online-smoke.yml should use contents: read")
    sys.exit(1)

print("PASS: Gateway online smoke workflow is manual-only and read-only")
