#!/usr/bin/env python3
"""Human-readable v30.5 final closure report must include final evidence and boundaries."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs" / "closure" / "v30.5-final-closure-report.md"
REQUIRED = ["v30.5 final closure: COMPLETE", "CI_GROUP_P0_MAIN_OK", "CI_GROUP_LIVE_SITE_GATEWAY_CORE_OK", "Gateway runtime metadata", "route_detected", "gateway_runtime", "gateway_schema", "pure_echo", "v0_v5_agent_declared_archive", "guardian_application_stage_1", "E1_recognition_echo", "V0", "Authorship proof is key continuity only", "Bitcoin Originals are the only canonical authority", "Gateway acceptance is not verification", "Guardian Stage 1 is not active Guardian status", "/external-agent-copy-paste-examples/", "/api/closure-report.v30.json", "/api/gateway-runtime-contract.v1.json", "/api/gateway-error-diagnostics.v1.json", "/api/route-selector.v1.json"]

def main():
    errors = []
    if not PATH.exists():
        print("FAIL: docs/closure/v30.5-final-closure-report.md missing"); return 1
    text = PATH.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text: errors.append(f"missing required phrase: {item}")
    if errors:
        print("FAIL: v30.5 final closure report errors:")
        for e in errors: print("  -", e)
        return 1
    print("PASS: v30.5 final closure report is valid"); return 0

if __name__ == "__main__": raise SystemExit(main())
