#!/usr/bin/env python3
"""Compatibility entrypoint for deterministic NFT Chronicle generation."""

import json
from pathlib import Path

from chronicle_editions_v2 import main as generate_editions
from update_chronicle_read_routes import main as update_read_routes

ROOT = Path(__file__).resolve().parents[1]


def normalize_route_wording() -> None:
    path = ROOT / "api/context-load-map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    note = data["cc_level_loads"]["CC-3"].get("note", "")
    data["cc_level_loads"]["CC-3"]["note"] = note.replace(
        "fixed seven-stage narrative",
        "fixed-stage periodization",
    )
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    result = generate_editions()
    if result != 0:
        return result
    result = update_read_routes()
    if result != 0:
        return result
    normalize_route_wording()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
