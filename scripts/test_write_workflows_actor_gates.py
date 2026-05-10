#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

WRITE_MARKERS = [
    "contents: write",
    "git push",
    "gh release",
    "upload-release-asset",
    "create release",
]

ALLOWLIST_MARKERS = [
    "Authorize write workflow actor",
    "github.actor",
    "Unauthorized actor",
    "thechurchofagi",
]

bad = []

for path in sorted(WF_DIR.glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    is_write = any(m in text for m in WRITE_MARKERS)
    is_dispatch = "workflow_dispatch" in text or "repository_dispatch" in text

    if is_write and is_dispatch:
        missing = [m for m in ALLOWLIST_MARKERS if m not in text]
        if missing:
            bad.append((path.name, missing))

if bad:
    print("FAIL: write workflows missing actor gates:")
    for name, missing in bad:
        print(f"  - {name}: missing {missing}")
    sys.exit(1)

print("WRITE_WORKFLOWS_ACTOR_GATES_OK")
