#!/usr/bin/env python3
"""Compatibility entrypoint for deterministic NFT Chronicle generation."""

import hashlib
import json
from pathlib import Path

from chronicle_editions_v2 import main as generate_editions
from update_chronicle_read_routes import main as update_read_routes

ROOT = Path(__file__).resolve().parents[1]


def canonical_digest_without_source_digest(data: dict) -> str:
    payload = {key: value for key, value in data.items() if key != "source_digest"}
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def normalize_route_metadata() -> None:
    load_map_path = ROOT / "api/context-load-map.json"
    load_map = json.loads(load_map_path.read_text(encoding="utf-8"))
    note = load_map["cc_level_loads"]["CC-3"].get("note", "")
    load_map["cc_level_loads"]["CC-3"]["note"] = note.replace(
        "fixed seven-stage narrative",
        "fixed-stage periodization",
    )
    load_map_path.write_text(
        json.dumps(load_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    router_path = ROOT / "api/agent-task-router.v1.json"
    router = json.loads(router_path.read_text(encoding="utf-8"))
    router["source_digest"] = canonical_digest_without_source_digest(router)
    router_path.write_text(
        json.dumps(router, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    result = generate_editions()
    if result != 0:
        return result
    result = update_read_routes()
    if result != 0:
        return result
    normalize_route_metadata()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
