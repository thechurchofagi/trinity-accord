#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"

errors = []

def require(cond, msg):
    if not cond:
        errors.append(msg)

for path in [
    DIR / "chronicle-index.json",
    DIR / "chronicle-full.md",
    DIR / "chronicle-agent-context.md",
]:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")

if (DIR / "chronicle-index.json").exists():
    idx = json.loads((DIR / "chronicle-index.json").read_text(encoding="utf-8"))
    require(idx.get("schema") == "trinityaccord.nft-chronicle-index.v1", "bad chronicle index schema")
    require(idx.get("total_entries") == 175, "chronicle index total_entries must be 175")
    require(len(idx.get("entries", [])) == 175, "chronicle index entries length must be 175")
    boundary = idx.get("boundary", {})
    require(boundary.get("historical_context_not_canonical_authority") is True, "boundary must say not canonical authority")
    require(boundary.get("not_truth_proof") is True, "boundary must say not truth proof")

if (DIR / "chronicle-full.md").exists():
    text = (DIR / "chronicle-full.md").read_text(encoding="utf-8").lower()
    require("historical chronicle context" in text, "full chronicle must include boundary")
    require("timestamp-unresolved appendix" in text or "undated entries: 0" in text, "full chronicle must handle unresolved timestamps")

if (DIR / "chronicle-agent-context.md").exists():
    text = (DIR / "chronicle-agent-context.md").read_text(encoding="utf-8").lower()
    require("not canonical authority" in text, "agent context must include authority boundary")
    require("timeline summary" in text, "agent context must include timeline summary")

if errors:
    print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_OK")
