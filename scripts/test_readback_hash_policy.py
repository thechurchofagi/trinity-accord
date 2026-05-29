#!/usr/bin/env python3
"""agent_readback_sha256 is builder-generated, not a forbidden invented value."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

JSON_FILES = [
    "api/gateway-runtime-contract.v1.json",
    "api/route-selector.v1.json",
    "api/agent-first-contact.json",
]

def main() -> int:
    errors: list[str] = []

    for rel in JSON_FILES:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        forbidden = set(data.get("forbidden_invented_values", []))
        if "agent_readback_sha256" in forbidden:
            errors.append(f"{rel}: agent_readback_sha256 must not be in forbidden_invented_values")

        policy = data.get("readback_hash_field_policy") or {}
        if rel != "api/agent-first-contact.json":
            if policy.get("builder_generated_field") != "agent_readback_sha256":
                errors.append(f"{rel}: readback_hash_field_policy.builder_generated_field mismatch")

    text_files = [
        "index.md",
        "external-agent-copy-paste-examples.md",
        "external-agent-quickstart.md",
        "agent-start.md",
        "llms.txt",
        "ai.txt",
    ]
    for rel in text_files:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "Do not use `agent_readback_sha256`" in text or "Do not use agent_readback_sha256" in text:
            errors.append(f"{rel}: should not say builder field itself is forbidden")
        if "Do not handwrite readback hash fields" not in text and "do not handwrite readback hash fields" not in text.lower():
            errors.append(f"{rel}: missing handwrite readback hash warning")

    if errors:
        print("FAIL: readback hash policy errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: agent_readback_sha256 is builder-generated-only, not forbidden as a field")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
