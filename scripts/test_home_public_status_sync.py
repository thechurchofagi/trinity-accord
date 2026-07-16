#!/usr/bin/env python3
"""Regression test for deterministic compact homepage public-status sync."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = ROOT / "index.md"
STATUS_PATH = ROOT / "api/public-home-status.json"
BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"


def fail(message: str) -> None:
    print(f"HOMEPAGE_PUBLIC_STATUS_FAIL: {message}")
    raise SystemExit(1)


def run_pipeline() -> None:
    for command in [
        [sys.executable, "scripts/generate_arweave_wallet_status.py"],
        [sys.executable, "scripts/generate_record_chain_status.py"],
        [sys.executable, "scripts/generate_public_home_status.py"],
        [sys.executable, "scripts/patch_public_home_status_primary.py"],
        [sys.executable, "scripts/check_public_home_status_contract.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            print(result.stdout)
            fail("public status pipeline failed: " + " ".join(command))


def extract_block(text: str) -> str:
    match = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), text, re.S)
    if not match:
        fail("compact generated public status block markers missing")
    return match.group(1)


def main() -> int:
    run_pipeline()
    first_index = INDEX_MD.read_text(encoding="utf-8")
    first_status = STATUS_PATH.read_text(encoding="utf-8")
    run_pipeline()
    second_index = INDEX_MD.read_text(encoding="utf-8")
    second_status = STATUS_PATH.read_text(encoding="utf-8")

    if first_index != second_index:
        fail("compact homepage status generation is not idempotent")
    try:
        first_data = json.loads(first_status)
        second_data = json.loads(second_status)
    except json.JSONDecodeError as exc:
        fail(f"public status JSON invalid: {exc}")
    for data in (first_data, second_data):
        data.pop("generated_at", None)
    if first_data != second_data:
        fail("public status JSON generation is not semantically idempotent")

    block = extract_block(second_index)
    primary = second_data.get("primary_counters") or {}
    expected_historic = str((primary.get("historic_autonomous_agent_reception") or {}).get("count"))
    expected_official = str(primary.get("official_live_reception"))
    historic = re.search(r'data-home-autonomous-discovery>([^<]+)<', block)
    official = re.search(r'data-home-official-reception>([^<]+)<', block)
    if not historic or historic.group(1).strip() != expected_historic:
        fail("autonomous external agent discovery count mismatch")
    if not official or official.group(1).strip() != expected_official:
        fail("Official Live Reception count mismatch")

    for phrase in [
        "Reception does not imply autonomous discovery",
        "Native chain inventory remains API-only",
        "Source data digest <code>",
        "Latest technical record <code>",
    ]:
        if phrase not in block:
            fail(f"compact status missing stable boundary/metadata phrase: {phrase}")
    if any(phrase in block for phrase in ["Generated at", "source_commit", "AR upload wallet", "Agency Profile"]):
        fail("compact status contains volatile or retired detailed-dashboard content")

    print("HOMEPAGE_PUBLIC_STATUS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
