#!/usr/bin/env python3
"""External-agent docs must expose the current Record-Chain submission flow."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "external-agent-quickstart.md",
    ROOT / "guardian-join.md",
    ROOT / "guardian-routes.md",
]

REQUIRED = [
    "/downloads/record-chain-builder.mjs",
    "/api/record-chain-intake-gateway.v1.json",
]


def main() -> int:
    errors: list[str] = []
    for path in FILES:
        if not path.exists():
            errors.append(f"missing file: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        for required in REQUIRED:
            if required not in text:
                errors.append(f"{path.name}: missing current submission snippet: {required}")

    if errors:
        print("FAIL: external-agent docs current-flow alignment errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external-agent docs expose the current Record-Chain flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
