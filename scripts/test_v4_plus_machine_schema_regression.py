#!/usr/bin/env python3
"""Test V4+ is present in machine-block schema enum."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v4_plus_in_enum():
    schema_path = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
    schema = json.loads(schema_path.read_text())

    # Find agent_declared_protocol_level in definitions/properties with enum
    text = json.dumps(schema)
    assert '"V4+"' in text, f"V4+ not found in schema: {schema_path}"

    # More precise: check the enum array
    found = False

    def search(obj):
        nonlocal found
        if isinstance(obj, dict):
            if "agent_declared_protocol_level" in obj:
                node = obj["agent_declared_protocol_level"]
                if isinstance(node, dict) and "enum" in node:
                    if "V4+" in node["enum"]:
                        found = True
            for v in obj.values():
                search(v)
        elif isinstance(obj, list):
            for item in obj:
                search(item)

    search(schema)
    assert found, "V4+ not in agent_declared_protocol_level enum"
    print("PASS: v4_plus_in_enum")


if __name__ == "__main__":
    test_v4_plus_in_enum()
    print("\nV4+ schema regression test PASS")
