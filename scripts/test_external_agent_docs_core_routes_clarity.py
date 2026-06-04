#!/usr/bin/env python3
"""Docs must expose the current tested external-agent submission path."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []

    quickstart = (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    for required in [
        "/api/agent-first-contact.json",
        "/downloads/record-chain-builder.mjs",
        "/api/record-chain-intake-gateway.v1.json",
    ]:
        if required not in quickstart:
            errors.append(f"external-agent-quickstart.md missing current route: {required}")

    for retired in [
        "/gateway/preflight",
        "/agent-submit",
        "download_and_run_builder_bundle.py",
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "Guardian Stage 1",
    ]:
        if retired in quickstart:
            errors.append(f"external-agent-quickstart.md still exposes retired route: {retired}")

    first_contact = (ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8")
    for required in [
        "/downloads/record-chain-builder.mjs",
        "/api/record-chain-intake-gateway.v1.json",
        "/record-chain/preflight",
        "/record-chain/submit",
    ]:
        if required not in first_contact:
            errors.append(f"agent-first-contact.json missing current route: {required}")

    if errors:
        print("FAIL: external-agent docs core-route clarity errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: docs expose the current tested external-agent path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
