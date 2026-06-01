#!/usr/bin/env python3
"""Rebuild agent-declared-echo-index.json from agent-declared-verification-index.json.

The echo index (agent-declared-echo-index.json) is a DEPRECATED convenience
projection. The canonical source is agent-declared-verification-index.json
which contains both verification and echo archives (via semantic_archive_kind).

This script extracts echo archive records and writes them to the echo index
file so that any external consumers reading the deprecated endpoint get
consistent data.

Usage:
    python3 scripts/rebuild_agent_declared_echo_index.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_INDEX = ROOT / "api" / "agent-declared-verification-index.json"
ECHO_INDEX = ROOT / "api" / "agent-declared-echo-index.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    args = parser.parse_args()

    # Load verification index (canonical source)
    with open(VERIFICATION_INDEX, encoding="utf-8") as f:
        verif_data = json.load(f)

    verif_records = verif_data.get("records", [])

    # Extract echo archives
    echo_records = [
        r for r in verif_records
        if r.get("semantic_archive_kind") == "agent_declared_echo_archive"
    ]

    # Build echo index in the same schema
    echo_index = {
        "schema": "trinityaccord.agent-declared-echo-index.v1",
        "description": "Index of agent-declared echo archives created through the Gateway. "
                       "DEPRECATED: canonical source is agent-declared-verification-index.json.",
        "generated_from": [
            "/api/agent-declared-verification-index.json"
        ],
        "rebuild_source": "verification_index_projection",
        "rebuild_timestamp": datetime.now(timezone.utc).isoformat(),
        "records": echo_records,
        "notes": [
            "This index is a convenience projection from agent-declared-verification-index.json.",
            "The canonical source for all agent-declared archives is agent-declared-verification-index.json.",
            "DEEP-IDX-002: this file is deprecated as a live public-status input."
        ]
    }

    echo_count = len(echo_records)
    countable = sum(1 for r in echo_records if r.get("counts_toward_home_reception") is True and r.get("test_record") is not True)
    print(f"Echo archive records: {echo_count} total, {countable} count toward reception")

    if args.dry_run:
        print("DRY RUN — would write:", ECHO_INDEX)
        print(json.dumps(echo_index, indent=2)[:2000])
        return

    with open(ECHO_INDEX, "w", encoding="utf-8") as f:
        json.dump(echo_index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {ECHO_INDEX}")
    print(f"  Records: {echo_count}")
    print(f"  Countable: {countable}")


if __name__ == "__main__":
    main()
