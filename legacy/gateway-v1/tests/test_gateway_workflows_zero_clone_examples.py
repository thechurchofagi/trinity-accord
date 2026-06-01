#!/usr/bin/env python3
"""Test that gateway-workflows.md contains zero-clone references."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "gateway-workflows.md"
    if not path.exists():
        print(f"FAIL: {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")

    required = [
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "/zero-clone-builders/",
        "/external-agent-quickstart/",
    ]

    for term in required:
        if term not in content:
            print(f"FAIL: gateway-workflows.md missing '{term}'")
            return 1

    # Must mention E2 deprecated
    if "deprecated" not in content.lower() or "e2" not in content.lower():
        print("FAIL: gateway-workflows.md does not mention E2 deprecated")
        return 1

    print("PASS: test_gateway_workflows_zero_clone_examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
