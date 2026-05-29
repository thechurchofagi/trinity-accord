#!/usr/bin/env python3
"""CHANGELOG must include v30.5 final closure entry."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "CHANGELOG.md"
REQUIRED = ["v30.5", "Closure Evidence and Runtime Drift Prevention", "COMPLETE", "p0-main", "live-site-gateway-core", "route_detected", "gateway_runtime", "gateway_schema", "pure_echo", "v0_v5_agent_declared_archive", "guardian_application_stage_1", "zero-clone authorship proof"]

def main():
    errors = []
    if not PATH.exists():
        print("FAIL: CHANGELOG.md missing"); return 1
    text = PATH.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text: errors.append(f"CHANGELOG missing {item}")
    if errors:
        print("FAIL: changelog v30.5 contract errors:")
        for e in errors: print("  -", e)
        return 1
    print("PASS: CHANGELOG contains v30.5 final closure entry"); return 0

if __name__ == "__main__": raise SystemExit(main())
