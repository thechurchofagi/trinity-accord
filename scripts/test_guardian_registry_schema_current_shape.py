#!/usr/bin/env python3
"""Validate guardian-registry.json against guardian-registry-schema.v1.json."""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def main():
    schema = json.loads((ROOT / "api" / "guardian-registry-schema.v1.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "api" / "guardian-registry.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(registry)
    print("GUARDIAN_REGISTRY_SCHEMA_CURRENT_SHAPE_OK")


if __name__ == "__main__":
    main()
