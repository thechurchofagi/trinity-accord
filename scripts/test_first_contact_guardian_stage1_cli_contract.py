#!/usr/bin/env python3
"""Guardian Stage 1 first-contact join path must expose real CLI flags."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

guardian = None
for item in fc.get("choose_one", []):
    if item.get("intent") == "guardian_stewardship":
        guardian = item
        break

stage1 = (((guardian or {}).get("join_path") or {}).get("stage_1_self_registration") or {})
if not isinstance(stage1, dict):
    print("FAIL: stage_1_self_registration missing")
    sys.exit(1)

required_flags = {
    "--human-label",
    "--agent-label",
    "--challenge",
    "--readback",
    "--out",
}

flags = set(stage1.get("required_cli_flags", []))
missing = sorted(required_flags - flags)
if missing:
    print(f"FAIL: Stage 1 first-contact missing required_cli_flags: {missing}")
    sys.exit(1)

if "--print-oath" not in stage1.get("readback_rule", ""):
    print("FAIL: Stage 1 readback_rule must mention --print-oath")
    sys.exit(1)

if stage1.get("must_follow_post_submit_readback") is not True:
    print("FAIL: Stage 1 first-contact must require post-submit readback")
    sys.exit(1)

print("PASS: Guardian Stage 1 first-contact uses CLI flags/readback rule")
