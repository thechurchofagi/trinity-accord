#!/usr/bin/env python3
"""Guardian Stage 2 first-contact join path must expose real CLI flags."""
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

stage2 = (((guardian or {}).get("join_path") or {}).get("stage_2_active_registry_listing") or {})
if not isinstance(stage2, dict):
    print("FAIL: stage_2_active_registry_listing missing")
    sys.exit(1)

required_flags = {
    "--agent-name",
    "--provider",
    "--source-issue",
    "--guardian-id",
    "--public-key-sha256",
    "--label",
    "--guardian-type",
    "--application-mode",
    "--out",
}

flags = set(stage2.get("required_cli_flags", []))
missing = sorted(required_flags - flags)
if missing:
    print(f"FAIL: Stage 2 first-contact missing required_cli_flags: {missing}")
    sys.exit(1)

old = set(stage2.get("required_fields", []))
if old:
    print(f"FAIL: Stage 2 first-contact still uses required_fields instead of required_cli_flags: {sorted(old)}")
    sys.exit(1)

if stage2.get("must_follow_post_submit_readback") is not True:
    print("FAIL: Stage 2 first-contact must require post-submit readback")
    sys.exit(1)

print("PASS: Guardian Stage 2 first-contact uses CLI flags")
