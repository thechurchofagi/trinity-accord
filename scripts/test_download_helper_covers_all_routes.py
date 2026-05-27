#!/usr/bin/env python3
"""Test that download_and_run_builder_bundle.py covers all routes."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    helper = ROOT / "scripts" / "download_and_run_builder_bundle.py"
    if not helper.exists():
        print("FAIL: download_and_run_builder_bundle.py does not exist")
        return 1

    content = helper.read_text(encoding="utf-8")

    routes = [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
    ]

    for route in routes:
        if route not in content:
            print(f"FAIL: route '{route}' not found in helper")
            return 1

    # Must check sha256
    if "sha256" not in content.lower() and "SHA256" not in content:
        print("FAIL: helper does not check sha256")
        return 1

    # Must print gateway paths
    if "/gateway/preflight" not in content:
        print("FAIL: helper does not mention /gateway/preflight")
        return 1
    if "/agent-submit" not in content:
        print("FAIL: helper does not mention /agent-submit")
        return 1

    # Must NOT mention /gateway/submit
    if "/gateway/submit" in content:
        print("FAIL: helper mentions /gateway/submit (should be /agent-submit)")
        return 1

    print("PASS: test_download_helper_covers_all_routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
