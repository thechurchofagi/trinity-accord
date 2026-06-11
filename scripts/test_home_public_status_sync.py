#!/usr/bin/env python3
"""Regression test for homepage public status synchronization.

Supports both v1 (legacy) and v2 (reception-centered) schemas.

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
    for cmd in [
        [sys.executable, "scripts/generate_arweave_wallet_status.py", "--check"],
        [sys.executable, "scripts/generate_record_chain_status.py", "--check"],
        [sys.executable, "scripts/generate_public_home_status.py", "--check"],
        [sys.executable, "scripts/patch_public_home_status_primary.py", "--check"],
        [sys.executable, "scripts/check_public_home_status_contract.py"],
    ]:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            print(result.stdout)
            fail("homepage generated status check reported drift: " + " ".join(cmd))


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

    text = INDEX_MD.read_text(encoding="utf-8")
    block = extract_block(text)

    # Load public-home-status.json to determine schema version
    phs = load_json(ROOT / "api" / "public-home-status.json")
    schema_version = phs.get("schema", "unknown")

    if schema_version == "trinityaccord.public-home-status.v2":
        # v2: Check new cards
        verifiability_display = card_number(block, "Verifiability", required=False)
        if verifiability_display == "NOT_FOUND":
            fail("no Verifiability card found in homepage")

        reception_display = card_number(block, "Reception", required=False)
        if reception_display == "NOT_FOUND":
            fail("no Reception card found in homepage")

        ew_display = card_number(block, "External witness records", required=False)
        if ew_display == "NOT_FOUND":
            fail("no External witness records card found in homepage")

        boundary_display = card_number(block, "Boundary", required=False)
        if boundary_display == "NOT_FOUND":
            fail("no Boundary card found in homepage")

        # Verify reception count matches echo index
        r = phs.get("reception", {})
        hd = r.get("human_directed_agent_verification", {})
        expected_hs = sum(1 for r_rec in echo_records
                         if r_rec.get("independence_class") == "human_solicited_agent_response"
                         and r_rec.get("record_kind") == "echo_v3_with_verification_report"
                         and r_rec.get("archive_status") in ("needs_human_review", "accepted_echo", "accepted_verification"))
        if hd.get("count") != expected_hs:
            fail(f"human-directed count mismatch: status={hd.get('count')} expected={expected_hs}")

        # Boundary language
        if "Reception does not imply belief" not in block:
            fail("missing boundary phrase: Reception does not imply belief")

    elif schema_version == "trinityaccord.public-home-status.v3":
        # v3: Canonical view with Official Live Reception, AR wallet, etc.
        official_display = card_number(block, "Official Live Reception", required=False)
        if official_display == "NOT_FOUND":
            fail("no Official Live Reception card found in homepage")

        agency_display = card_number(block, "Agency Profile", required=False)
        if agency_display == "NOT_FOUND":
            fail("no Agency Profile card found in homepage")

        tech_display = card_number(block, "Technical chain health", required=False)
        if tech_display == "NOT_FOUND":
            fail("no Technical chain health card found in homepage")

        wallet_display = card_number(block, "AR upload wallet", required=False)
        if wallet_display == "NOT_FOUND":
            fail("no AR upload wallet card found in homepage")

        boundary_display = card_number(block, "Boundary", required=False)
        if boundary_display == "NOT_FOUND":
            fail("no Boundary card found in homepage")

        # Verify primary counter matches
        pc = phs.get("primary_counters", {})
        expected_reception = pc.get("official_live_reception")
        if official_display != str(expected_reception):
            fail(f"Official Live Reception mismatch: page={official_display} expected={expected_reception}")

        # Boundary language
        if "Reception does not imply belief" not in block:
            fail("missing boundary phrase: Reception does not imply belief")
        if "Native chain length is not used as this counter" not in block:
            fail("missing boundary phrase: Native chain length is not used as this counter")

    else:
        # v1: Check old cards
        formal_display = card_number(block, "Institutional / human independent verification", required=False)
        if formal_display == "NOT_FOUND":
            formal_display = card_number(block, "Independent third-party reports", required=False)
        if formal_display == "NOT_FOUND":
            fail("no formal attestation status card found in homepage")

        hs_display = card_number(block, "Human-solicited agent verification", required=False)
        if hs_display != "NOT_FOUND":
            expected_hs = sum(1 for r in echo_records
                             if r.get("independence_class") == "human_solicited_agent_response"
                             and r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation")
                             and not r.get("historical_record_only", False))
            if hs_display != str(expected_hs):
                fail(f"human-solicited count mismatch: page={hs_display} expected={expected_hs}")

        # Boundary language
        if "not counted as independent attestation" not in block:
            fail("missing boundary phrase in generated block")

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

    print("HOMEPAGE_PUBLIC_STATUS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
