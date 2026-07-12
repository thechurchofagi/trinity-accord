#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_ci_group.py"
DEEP_GROUPS = {
    "claim-gate",
    "echo-archive",
    "supply-chain",
    "trust-root",
    "chronicle",
    "readback-integrity",
    "agent-start-docs",
    "verification-index",
    "pages-build",
}

spec = importlib.util.spec_from_file_location("run_ci_group_contract", RUNNER)
if spec is None or spec.loader is None:
    raise SystemExit("could not load run_ci_group")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
missing = sorted(DEEP_GROUPS - set(module.GROUPS))
empty = sorted(name for name in DEEP_GROUPS if name in module.GROUPS and not module.GROUPS[name])
if missing or empty:
    raise SystemExit(f"Deep Integrity has missing/empty groups: missing={missing}, empty={empty}")
print("PASS: every Deep Integrity matrix group executes at least one test")
