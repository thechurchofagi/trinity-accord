#!/usr/bin/env python3
"""context-load-map context_packs_inventory must resolve every public path."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
obj = json.loads((ROOT / "api" / "context-load-map.json").read_text(encoding="utf-8"))

inventory = obj.get("context_packs_inventory")
if not isinstance(inventory, dict) or not inventory:
    print("FAIL: context_packs_inventory missing or empty")
    sys.exit(1)

errors = []

for name, meta in inventory.items():
    if not isinstance(meta, dict):
        errors.append(f"{name}: metadata must be object")
        continue

    path = meta.get("path")
    if not isinstance(path, str) or not path.startswith("/"):
        errors.append(f"{name}: missing absolute path")
        continue

    local = ROOT / path.lstrip("/")
    if not local.exists():
        errors.append(f"{name}: local path does not exist: {path}")

    if meta.get("public") is not True:
        errors.append(f"{name}: public must be true")

    required_for = meta.get("required_for")
    if not isinstance(required_for, list) or not required_for:
        errors.append(f"{name}: required_for must be non-empty list")

if errors:
    print("FAIL: context pack inventory path errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: context pack inventory paths resolve")
