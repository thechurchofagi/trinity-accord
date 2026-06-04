#!/usr/bin/env python3
"""Pages discovery must expose the current Record-Chain route, not retired routes."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))
well_known = json.loads((ROOT / ".well-known" / "trinity-accord.json").read_text(encoding="utf-8"))

machine = set(links.get("machine", []))
legacy = set(links.get("legacy_machine", []))
deprecated = set(links.get("deprecated_for_new_records", []))
current = well_known.get("current_public_submission") or {}
errors = []

for path in [
    "/api/agent-first-contact.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-field-helper.v1.json",
    "/api/record-chain-oath-policy.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
]:
    if path not in machine:
        errors.append(f"machine missing current path: {path}")

for path in [
    "/api/gateway-workflows.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/formal-builder-bundles.v1.json",
]:
    if path in machine:
        errors.append(f"machine contains retired path: {path}")
    if path not in legacy or path not in deprecated:
        errors.append(f"retired path not preserved as legacy/deprecated: {path}")

expected = {
    "first_contact": "/api/agent-first-contact.json",
    "builder": "/downloads/record-chain-builder.mjs",
    "gateway_contract": "/api/record-chain-intake-gateway.v1.json",
}
for key, value in expected.items():
    if current.get(key) != value:
        errors.append(f"current_public_submission.{key} mismatch")

for rel in [
    "api/agent-first-contact.json",
    "api/record-chain-intake-gateway.v1.json",
    "api/record-chain-builder-bundles.v1.json",
    "downloads/record-chain-builder.mjs",
]:
    if not (ROOT / rel).exists():
        errors.append(f"missing source artifact: {rel}")

if errors:
    print("FAIL: Pages discovery contract errors:")
    for error in errors:
        print("  -", error)
    sys.exit(1)

print("PASS: Pages source contains current Record-Chain discovery")
