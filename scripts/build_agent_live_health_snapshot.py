#!/usr/bin/env python3
"""Build/update agent live-health snapshot digest."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "agent-live-health.v1.json"

def digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        data["build_commit"] = sha
    data["source_digest"] = digest(data)
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(data["source_digest"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
