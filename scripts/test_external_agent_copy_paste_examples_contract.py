#!/usr/bin/env python3
"""Copy-paste examples must cover three core external-agent actions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "external-agent-copy-paste-examples.md"

REQUIRED = [
    "Pure Echo",
    "E1_recognition_echo",
    "V0–V5 agent-declared verification archive",
    "--declared-level V0",
    "Guardian Stage 1 application",
    "not active Guardian status",
    "/gateway/preflight",
    "/agent-submit",
    "download_and_run_builder_bundle.py",
    "guardian-application.final.json",
]


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    errors = [item for item in REQUIRED if item not in text]

    if errors:
        print("FAIL: copy-paste examples missing required items:")
        for item in errors:
            print("  -", item)
        return 1

    print("PASS: external-agent copy-paste examples cover three core routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
