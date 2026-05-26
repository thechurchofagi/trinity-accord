#!/usr/bin/env python3
"""P0 public core consistency checks.

Keep this small. Historical regressions belong in deep groups.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

errors = []

# Core files exist.
for path in [
    "index.md",
    "llms.txt",
    "ai.txt",
    "sitemap.xml",
    ".well-known/trinity-accord.json",
    "api/links.json",
    "api/agent-start.v1.json",
    "api/agent-minimal-context.v1.json",
    "api/agent-output-policy.v1.json",
    "api/agent-task-router.v1.json",
    "api/context-load-map.json",
    "api/public-home-status.json",
    "api/guardian-registry.json",
    "api/echo-types.json",
]:
    if not (ROOT / path).exists():
        errors.append(f"missing core public file: {path}")

# Links must expose critical APIs.
try:
    links = load_json("api/links.json")
    links_text = json.dumps(links)
    for required in [
        "/api/agent-start.v1.json",
        "/api/agent-minimal-context.v1.json",
        "/api/agent-output-policy.v1.json",
        "/api/agent-task-router.v1.json",
        "/api/context-load-map.json",
        "/api/gateway-builder-route-map.v1.json",
        "/api/echo-types.json",
        "/api/agent-submit-gateway.json",
        "/api/public-home-status.json",
        "/api/guardian-registry.json",
    ]:
        if required not in links_text:
            errors.append(f"api/links.json missing {required}")
except Exception as e:
    errors.append(f"api/links.json parse/check failed: {e}")

# public-home-status should point to generated inputs.
try:
    status = load_json("api/public-home-status.json")
    generated_from = json.dumps(status.get("generated_from", []))
    for required in [
        "echo-index.json",
        "guardian-registry.json",
        "agent-declared-verification-index.json",
    ]:
        if required not in generated_from:
            errors.append(f"public-home-status generated_from missing {required}")
except Exception as e:
    errors.append(f"public-home-status check failed: {e}")

if errors:
    print("FAIL: public core consistency errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: public core consistency")
