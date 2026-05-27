#!/usr/bin/env python3
"""Agent submit Gateway contract must expose Gateway discovery for zero-manual canary."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api" / "agent-submit-gateway.json"

data = json.loads(path.read_text(encoding="utf-8"))
discovery = data.get("gateway_discovery", {})
errors = []

if not isinstance(discovery, dict):
    errors.append("gateway_discovery must be an object")
else:
    candidates = []
    if discovery.get("primary_base_url"):
        candidates.append(discovery.get("primary_base_url"))
    candidates.extend(discovery.get("base_url_candidates", []))

    if not candidates:
        errors.append("gateway_discovery must expose primary_base_url or base_url_candidates")

    for url in candidates:
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"Gateway candidate must be https URL: {url!r}")

    if discovery.get("preflight_path") != "/gateway/preflight":
        errors.append("preflight_path must be /gateway/preflight")
    if discovery.get("submit_path") != "/gateway/submit":
        errors.append("submit_path must be /gateway/submit")
    if discovery.get("canary_supported") is not True:
        errors.append("canary_supported must be true")
    if discovery.get("canary_policy") != "/api/live-canary-policy.v1.json":
        errors.append("canary_policy must point to /api/live-canary-policy.v1.json")

if errors:
    print("FAIL: Gateway discovery canary contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Gateway discovery for zero-manual canary is valid")
