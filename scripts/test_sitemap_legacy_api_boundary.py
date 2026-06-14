#!/usr/bin/env python3
"""Part D: Test that sitemap either omits legacy APIs or they are fail-closed."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        ok("no sitemap.xml — nothing to check")
        return 0

    text = sitemap_path.read_text(encoding="utf-8")

    legacy_paths = [
        "record-chain-head.json",
        "record-chain-index.manifest.json",
    ]

    api_dir = ROOT / "api"

    for legacy_name in legacy_paths:
        if legacy_name in text:
            # If sitemap lists it, verify the target JSON is fail-closed
            target = api_dir / legacy_name
            if not target.exists():
                fail(f"sitemap references {legacy_name} but file missing")
            data = json.loads(target.read_text(encoding="utf-8"))
            if not data.get("historical_archive_only"):
                fail(f"sitemap references {legacy_name} but it lacks historical_archive_only flag")
            ok(f"sitemap references {legacy_name} and it is fail-closed")
        else:
            ok(f"sitemap does not reference {legacy_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
