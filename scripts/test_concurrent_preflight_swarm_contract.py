#!/usr/bin/env python3
"""The concurrent smoke must test the current signed preflight route and fail meaningfully."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE = (ROOT / "scripts/smoke_external_agent_concurrent_preflight_swarm.py").read_text(encoding="utf-8")
GROUPS = (ROOT / "scripts/run_ci_group.py").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


require("https://trinity-record-chain-gateway.onrender.com" in SMOKE, "smoke must use current Record-Chain Gateway")
require('PREFLIGHT_PATH = "/record-chain/preflight"' in SMOKE, "smoke must use current preflight endpoint")
require("trinity-agent-issue-gateway" not in SMOKE, "retired issue Gateway must not be used")
require('PREFLIGHT_PATH = "/gateway/preflight"' not in SMOKE, "retired preflight path must not be used")
require("signature_base64" in SMOKE, "smoke must require a real signed canonical submission")
require("response.get(\"accepted\") is not True" in SMOKE, "HTTP 2xx rejection must count as failure")
require("--min-success-ratio" in SMOKE, "smoke must enforce a success ratio")
require('"--max-failures", "20"' not in GROUPS, "CI must never allow all 20 agents to fail")
require('"--min-success-ratio", "0.9"' in GROUPS, "CI must require at least 90% success")

print("PASS: concurrent preflight swarm targets the current Gateway and cannot pass 100% failure")
