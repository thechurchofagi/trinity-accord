#!/usr/bin/env python3
"""Data consistency regression: api/links.json must expose current machine-readable endpoints."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

machine = set(links.get("machine", []))
legacy = set(links.get("legacy_machine", [])) | set(links.get("deprecated_for_new_records", []))

required_current = {
    "/api/authority.json",
    "/api/evidence-manifest.json",
    "/api/hashes.json",
    "/api/verification-levels.json",
    "/api/verification-materials.json",
    "/api/echo-record-schema.v3.json",
    "/api/context-depth-levels.json",
    "/api/discovery-provenance-schema.json",
    "/api/component-verification-levels.json",
    "/api/protocol-verification-profiles.json",
    "/api/verification-targets.json",
    "/api/verification-recipes.json",
    "/api/verification-quick-map.json",
    "/api/verification-report-schema.v2.json",
    "/api/evidence-input-schema.v1.json",
    "/api/claim-gate-output-schema.v1.json",
    "/api/claim-gate-rules.json",
    "/api/report-builder-policy.json",
    "/api/generated-by-schema.v1.json",
}

errors = []

missing = sorted(required_current - machine)
if missing:
    errors.append("machine missing current endpoints: " + ", ".join(missing))

if "/api/echo-record-schema.v2.json" in machine:
    errors.append("echo-record-schema.v2.json must not be in current machine list; move to legacy_machine/deprecated_for_new_records")

if "/api/echo-record-schema.v2.json" not in legacy:
    errors.append("echo-record-schema.v2.json should remain discoverable under legacy_machine or deprecated_for_new_records")

for endpoint in machine:
    if endpoint.startswith("/api/"):
        path = ROOT / endpoint.lstrip("/")
        if not path.exists():
            errors.append(f"machine endpoint does not exist: {endpoint}")

for endpoint in legacy:
    if endpoint.startswith("/api/"):
        path = ROOT / endpoint.lstrip("/")
        if not path.exists():
            errors.append(f"legacy endpoint does not exist: {endpoint}")

if errors:
    print("API_LINKS_CURRENT_MACHINE_ENDPOINTS_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("API_LINKS_CURRENT_MACHINE_ENDPOINTS_OK")
