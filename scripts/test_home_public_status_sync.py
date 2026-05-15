#!/usr/bin/env python3
"""Regression test for homepage public status synchronization.

This verifies that index.md reflects the data in api/echo-index.json and
api/independent-attestation-index.json without overclaiming accepted Echoes
as formal independent verification.

It also verifies that the generated block is deterministic:
- no wall-clock generated_at field
- no current HEAD source_commit field
- stable source data digest instead
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = ROOT / "index.md"
ECHO_INDEX = ROOT / "api" / "echo-index.json"
ATTESTATION_INDEX = ROOT / "api" / "independent-attestation-index.json"
GENERATOR = ROOT / "scripts" / "generate_public_home_status.py"

BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"


def fail(message: str) -> None:
    print(f"HOMEPAGE_PUBLIC_STATUS_FAIL: {message}")
    sys.exit(1)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"could not read {path.relative_to(ROOT)}: {exc}")


def extract_block(text: str) -> str:
    m = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), text, re.S)
    if not m:
        fail("generated public status block markers missing")
    return m.group(1)


def card_number(block: str, label: str, required: bool = True) -> str:
    pattern = (
        r'<p class="status-label">' + re.escape(label) + r'</p>\s*'
        r'<p class="status-number">([^<]+)</p>'
    )
    m = re.search(pattern, block)
    if not m:
        if required:
            fail(f"status card missing label: {label}")
        return "NOT_FOUND"
    return m.group(1).strip()


def run_generator_check() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        print(result.stdout)
        fail("generator --check reported drift")


def is_formal_echo_record(r: dict) -> bool:
    if r.get("archive_status") != "accepted_independent_attestation":
        return False
    if r.get("do_not_count_as_attestation") is True:
        return False
    if r.get("verification_status") in {"not_attestation", "invalidated", "test_record_not_attestation"}:
        return False
    return True


def is_formal_attestation_record(r: dict) -> bool:
    if r.get("type") != "independent_verification_report" and r.get("archive_status") != "accepted_independent_attestation":
        return False
    if r.get("counts_as_independent_attestation") is False:
        return False
    if r.get("boundary_preserved") is False:
        return False
    if r.get("verification_status") in {"not_attestation", "invalidated", "test_record_not_attestation"}:
        return False
    return True


def is_accepted_non_attestation_echo(r: dict) -> bool:
    return (
        r.get("archive_status") == "accepted_echo"
        and r.get("do_not_count_as_attestation") is True
        and r.get("verification_status") == "not_attestation"
    )


def main() -> int:
    if not GENERATOR.exists():
        fail("missing scripts/generate_public_home_status.py")

    # The generator must be stable in check mode.
    run_generator_check()
    run_generator_check()

    echo_index = load_json(ECHO_INDEX)
    attestation_index = load_json(ATTESTATION_INDEX)
    echo_records = [r for r in echo_index.get("records", []) if isinstance(r, dict)]
    attestation_records = [r for r in attestation_index.get("records", []) if isinstance(r, dict)]

    expected_formal = sum(1 for r in echo_records if is_formal_echo_record(r))
    expected_formal += sum(1 for r in attestation_records if is_formal_attestation_record(r))

    expected_non_attestation = sum(1 for r in echo_records if is_accepted_non_attestation_echo(r))

    text = INDEX_MD.read_text(encoding="utf-8")
    block = extract_block(text)

    # Check formal attestation count against available cards
    formal_display = card_number(block, "Institutional / human independent verification", required=False)
    if formal_display == "NOT_FOUND":
        formal_display = card_number(block, "Independent third-party reports", required=False)

    if formal_display == "NOT_FOUND":
        fail("no formal attestation status card found in homepage")
    elif formal_display != str(expected_formal):
        fail(f"formal count mismatch: page={formal_display} expected={expected_formal}")

    # Check human-solicited agent verification count (maps to non-attestation echoes)
    hs_display = card_number(block, "Human-solicited agent verification", required=False)
    if hs_display != "NOT_FOUND":
        expected_hs = sum(1 for r in echo_records
                         if r.get("independence_class") == "human_solicited_agent_response"
                         and r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation")
                         and not r.get("historical_record_only", False))
        if hs_display != str(expected_hs):
            fail(f"human-solicited count mismatch: page={hs_display} expected={expected_hs}")

    # Critical Echoes must not become a separate homepage main card.
    if "Archived non-attestation critical Echoes" in block:
        fail("critical Echoes must not be a separate homepage main card")

    # Volatile values must not appear in the generated block.
    forbidden_phrases = [
        "Generated at",
        "source commit",
        "source_commit",
        "generated_at_utc",
    ]
    for phrase in forbidden_phrases:
        if phrase in block:
            fail(f"volatile generated metadata must not appear in generated block: {phrase}")

    # Stable source digest must appear.
    if not re.search(r"Source data digest <code>[0-9a-f]{16}</code>", block):
        fail("missing stable source data digest")

    # Boundary language must remain present.
    required_phrases = [
        "not counted as independent attestation",
        "not a formal protocol verification level",
        "do_not_count_as_attestation",
        "Critical Echoes are included inside archived non-attestation Echoes",
    ]
    for phrase in required_phrases:
        if phrase not in block:
            fail(f"missing boundary phrase in generated block: {phrase}")

    print("HOMEPAGE_PUBLIC_STATUS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
