#!/usr/bin/env python3
"""FUNC-DISC-001: Discovery manifests must expose core lifecycle APIs."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "/api/public-home-status.json",
    "/api/guardian-registry.json",
    "/api/guardian-active-listing-policy.v1.json",
    "/api/echo-index.json",
    "/api/agent-declared-verification-index.json",
    "/api/external-witness-index.json",
    "/api/corrections-index.json",
    "/api/recovery-index.json",
    "/api/links.json",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect_strings(obj):
    out = set()
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, list):
        for x in obj:
            out |= collect_strings(x)
    elif isinstance(obj, dict):
        for v in obj.values():
            out |= collect_strings(v)
    return out


files = [
    "api/links.json",
    ".well-known/trinity-accord.json",
    "agent-map.json",
]

ok = True
for f in files:
    p = ROOT / f
    if not p.exists():
        print(f"FAIL: required discovery manifest missing: {f}")
        ok = False
        continue
    strings = collect_strings(load(p))
    missing = sorted(REQUIRED - strings)
    if missing:
        print(f"FAIL: {f} missing lifecycle links: {missing}")
        ok = False
    else:
        print(f"OK: {f}")

if not ok:
    sys.exit(1)

print("PASS: discovery manifests include core lifecycle APIs")
