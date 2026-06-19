#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "api" / "context-load-map.json"

IGNORE_PREFIXES = ("CC-",)


def clean_item(value: str) -> str | None:
    s = str(value).strip()
    if not s:
        return None
    if s.startswith(IGNORE_PREFIXES) and "loads" in s:
        return None
    if s.startswith("http://") or s.startswith("https://"):
        return s
    # Strip common description suffixes.
    for sep in [" — ", " -- "]:
        if sep in s:
            s = s.split(sep, 1)[0].strip()
    # Keep only path-like entries.
    if s.startswith("/") or s.startswith("context-packs/"):
        return s
    return None


def candidate_paths(path: str) -> list[Path]:
    if path.startswith("http://") or path.startswith("https://"):
        return []

    raw = path.strip()
    no_slash = raw.lstrip("/")
    candidates: list[Path] = []

    if raw.startswith("/api/") or raw.startswith("/downloads/") or raw.startswith("/nft-text-descriptions/"):
        candidates.append(ROOT / no_slash)
    elif raw.startswith("context-packs/"):
        candidates.append(ROOT / "api" / raw)
        candidates.append(ROOT / raw)
    elif raw.startswith("/") and raw.endswith("/"):
        base = no_slash.strip("/")
        candidates.extend([
            ROOT / base,
            ROOT / f"{base}.md",
            ROOT / base / "index.md",
            ROOT / base / "index.html",
        ])
    elif raw.startswith("/"):
        candidates.append(ROOT / no_slash)
        candidates.append(ROOT / f"{no_slash}.md")

    return candidates


def main() -> int:
    if not MAP.exists():
        print("FAIL: missing api/context-load-map.json")
        return 1

    data = json.loads(MAP.read_text(encoding="utf-8"))
    items: list[str] = []

    items.extend(data.get("minimal_first_load", []) or [])

    levels = data.get("cc_level_loads", {}) or {}
    for level in ["CC-1", "CC-2", "CC-3"]:
        items.extend((levels.get(level, {}) or {}).get("must_load", []) or [])

    inv = data.get("context_packs_inventory", {}) or {}
    for spec in inv.values():
        if isinstance(spec, dict) and spec.get("path"):
            items.append(spec["path"])

    missing = []
    warnings = []
    checked = []

    for raw in items:
        item = clean_item(raw)
        if not item:
            continue
        if item.startswith("http://") or item.startswith("https://"):
            warnings.append(f"external URL not checked: {item}")
            continue
        cands = candidate_paths(item)
        if not cands:
            continue
        checked.append(item)
        if not any(p.exists() for p in cands):
            missing.append((item, [str(p.relative_to(ROOT)) for p in cands]))

    if warnings:
        for w in warnings:
            print(f"WARN: {w}")

    if missing:
        for item, cands in missing:
            print(f"FAIL: context-load-map path not found: {item}")
            print("  tried:")
            for c in cands:
                print(f"    - {c}")
        return 1

    print(f"PASS: context-load-map links ({len(checked)} local paths checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
