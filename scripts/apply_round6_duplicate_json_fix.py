#!/usr/bin/env python3
"""Remove duplicate top-level metadata from the retired Gateway workflow map."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api/gateway-workflows.v1.json"
text = path.read_text(encoding="utf-8")
old_schema = (
    '  "route_map_url": "/api/gateway-builder-route-map.v1.json",\n'
    '  "schema": "trinityaccord.gateway-workflows.v1",\n'
    '  "universal_rules": [\n'
)
new_schema = (
    '  "route_map_url": "/api/gateway-builder-route-map.v1.json",\n'
    '  "universal_rules": [\n'
)
old_version = '  ],\n  "version": "1.0.0",\n  "workflows": {\n'
new_version = '  ],\n  "workflows": {\n'
if text.count(old_schema) != 1:
    raise SystemExit("duplicate schema target missing or ambiguous")
if text.count(old_version) != 1:
    raise SystemExit("duplicate version target missing or ambiguous")
text = text.replace(old_schema, new_schema, 1).replace(old_version, new_version, 1)
path.write_text(text, encoding="utf-8")
print("ROUND6_DUPLICATE_JSON_FIXED")
