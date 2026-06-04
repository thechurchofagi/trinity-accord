#!/usr/bin/env python3
"""Test that current docs use the Record-Chain builder and legacy docs are clearly historical."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    quickstart = ROOT / "external-agent-quickstart.md"
    zero_clone = ROOT / "zero-clone-builders.md"

    if not quickstart.exists() or not zero_clone.exists():
        print("FAIL: expected external-agent quickstart and zero-clone builder docs")
        return 1

    quickstart_text = quickstart.read_text(encoding="utf-8")
    zero_clone_text = zero_clone.read_text(encoding="utf-8")

    for required in [
        "/downloads/record-chain-builder.mjs",
        "/api/record-chain-intake-gateway.v1.json",
    ]:
        if required not in quickstart_text:
            print(f"FAIL: external-agent-quickstart.md missing current route: {required}")
            return 1

    for retired in ["/gateway/preflight", "/agent-submit"]:
        if retired in quickstart_text:
            print(f"FAIL: external-agent-quickstart.md still exposes retired route: {retired}")
            return 1

    if "Historical archive only" not in zero_clone_text:
        print("FAIL: zero-clone-builders.md is not marked historical archive only")
        return 1

    print("PASS: current quickstart and historical zero-clone docs are separated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
