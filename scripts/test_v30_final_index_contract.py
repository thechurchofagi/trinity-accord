#!/usr/bin/env python3
"""v30 final index must point to closure, runtime, route, and external-agent artifacts."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "v30-final-index.json"

REQUIRED_MACHINE = {"/api/mission-governance.v1.json", "/api/closure-report.v30.json", "/api/gateway-runtime-contract.v1.json", "/api/gateway-error-diagnostics.v1.json", "/api/route-selector.v1.json", "/api/external-agent-operation-examples.v1.json", "/api/formal-builder-bundles.v1.json", "/api/formal-builder-bundle-signatures.v1.json"}
REQUIRED_HUMAN = {"/docs/closure/v30.5-final-closure-report.md", "/CHANGELOG.md"}
REQUIRED_ROUTES = {"pure_echo", "v0_v5_agent_declared_archive", "guardian_application_stage_1"}

def digest(data):
    clone = dict(data); clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

def public_path_exists(p):
    return (ROOT / p.lstrip("/")).exists()

def main():
    errors = []
    if not PATH.exists():
        print("FAIL: api/v30-final-index.json missing"); return 1
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "trinityaccord.v30-final-index": errors.append("schema mismatch")
    if data.get("status") != "complete": errors.append("status must be complete")
    machine = set(data.get("machine_contracts", []))
    m = sorted(REQUIRED_MACHINE - machine)
    if m: errors.append(f"missing machine contracts: {m}")
    human = set(data.get("human_reports", []))
    h = sorted(REQUIRED_HUMAN - human)
    if h: errors.append(f"missing human reports: {h}")
    routes = set(data.get("core_routes", []))
    r = sorted(REQUIRED_ROUTES - routes)
    if r: errors.append(f"missing core routes: {r}")
    for p in machine | human:
        if not public_path_exists(p): errors.append(f"referenced path does not exist: {p}")
    for g in data.get("live_guards", []):
        if not (ROOT / g).exists(): errors.append(f"live guard missing: {g}")
    expected = digest(data)
    if data.get("source_digest") != expected: errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")
    if errors:
        print("FAIL: v30 final index contract errors:")
        for e in errors: print("  -", e)
        return 1
    print("PASS: v30 final index contract is valid"); return 0

if __name__ == "__main__": raise SystemExit(main())
