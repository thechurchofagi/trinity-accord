#!/usr/bin/env python3
"""External-agent docs must align with the current Record-Chain submission flow."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CURRENT_FILES = {
    "external-agent-quickstart.md": ROOT / "external-agent-quickstart.md",
    "guardian-join.md": ROOT / "guardian-join.md",
    "guardian-routes.md": ROOT / "guardian-routes.md",
}

REQUIRED_CURRENT_SNIPPETS = [
    "/downloads/record-chain-builder.mjs",
    "/api/record-chain-intake-gateway.v1.json",
]

FORBIDDEN_ACTIVE_SNIPPETS = [
    "/gateway/preflight",
    "/agent-submit",
    "/api/formal-builder-bundles.v1.json",
    "/api/external-agent-operation-examples.v1.json",
    "download_and_run_builder_bundle.py",
]


def main() -> int:
    errors: list[str] = []

    for label, path in CURRENT_FILES.items():
        if not path.exists():
            errors.append(f"{label}: file missing")
            continue

        text = path.read_text(encoding="utf-8")
        for required in REQUIRED_CURRENT_SNIPPETS:
            if required not in text:
                errors.append(f"{label}: missing current submission snippet: {required}")
        for forbidden in FORBIDDEN_ACTIVE_SNIPPETS:
            if forbidden in text:
                errors.append(f"{label}: retired submission snippet remains active: {forbidden}")

    if errors:
        print("FAIL: external-agent docs current-flow alignment errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external-agent docs align with the current Record-Chain flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
