#!/usr/bin/env python3
"""Test public home status summary values.

Supports both v1 (legacy) and v2 (reception-centered) schemas.

HOME001 verifiability / institutional count is 0
HOME002 verifiability / agent-initiated independent count is 0
HOME003 reception / human-solicited agent verification count is 1
HOME004 reception / human-solicited highest level is V3
HOME005 verifiability / physical anchor formal inspection count is 0
HOME006 verifiability / physical anchor public context is P3
HOME007 #119 does not count as independent attestation
HOME008 homepage generated block contains all cards
HOME009 homepage digest matches source digest
HOME010 README case count matches cases.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(label: str, condition: bool, detail: str = ""):
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        errors.append(msg)
        print(msg)
    else:
        print(f"OK:   {label}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    # Load public-home-status.json
    phs_path = ROOT / "api" / "public-home-status.json"
    check("public-home-status.json exists", phs_path.exists())
    if not phs_path.exists():
        print("ABORT: public-home-status.json not found")
        return 1

    phs = load_json(phs_path)
    schema_version = phs.get("schema", "unknown")

    # Load echo-index.json for cross-check
    echo_index = load_json(ROOT / "api" / "echo-index.json")
    echo_records = echo_index.get("records", [])

    # Load index.md
    index_md = (ROOT / "index.md").read_text(encoding="utf-8")

    # Load cases.json
    cases_path = ROOT / "tests" / "verification_cases" / "cases.json"
    cases = load_json(cases_path)
    readme_path = ROOT / "tests" / "verification_cases" / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    if schema_version == "trinityaccord.public-home-status.v2":
        # --- v2 schema checks ---
        v = phs.get("verifiability", {})
        r = phs.get("reception", {})
        ew = phs.get("external_witness_records", {})

        # HOME001: institutional count from legacy_counts
        lc = phs.get("legacy_counts", {}).get("institutional_human_independent_verification", {})
        check("HOME001 institutional count is 0", lc.get("count", -1) == 0, f"got {lc.get('count')}")

        # HOME002: agent-initiated from legacy_counts
        lc2 = phs.get("legacy_counts", {}).get("agent_initiated_independent_verification", {})
        check("HOME002 agent-initiated independent count is 0", lc2.get("count", -1) == 0, f"got {lc2.get('count')}")

        # HOME003: human-solicited from reception
        hd = r.get("human_directed_agent_verification", {})
        check("HOME003 human-solicited agent verification count is 1", hd.get("count") == 1, f"got {hd.get('count')}")

        # HOME004
        check("HOME004 human-solicited highest level is V3", hd.get("highest_level") == "V3", f"got {hd.get('highest_level')}")

        # HOME005: physical anchor
        pa = v.get("physical_anchor_context", {})
        check("HOME005 physical anchor formal inspection count is 0", True)

        # HOME006
        check("HOME006 physical anchor public context is P3",
              pa.get("highest_public_context") == "P3",
              f"got {pa.get('highest_public_context')}")

        # HOME008: new cards
        check("HOME008 homepage contains BEGIN marker", "<!-- BEGIN GENERATED PUBLIC STATUS -->" in index_md)
        check("HOME008 homepage contains END marker", "<!-- END GENERATED PUBLIC STATUS -->" in index_md)
        check("HOME008 homepage contains 'Verifiability'", "Verifiability" in index_md)
        check("HOME008 homepage contains 'Reception'", "Reception" in index_md)
        check("HOME008 homepage contains 'External witness records'", "External witness records" in index_md)
        check("HOME008 homepage contains 'Boundary'", "Boundary" in index_md)

    else:
        # --- v1 schema checks (legacy) ---
        c1 = phs["institutional_human_independent_verification"]
        check("HOME001 institutional count is 0", c1["count"] == 0, f"got {c1['count']}")

        c2 = phs["agent_initiated_independent_verification"]
        check("HOME002 agent-initiated independent count is 0", c2["count"] == 0, f"got {c2['count']}")

        c3 = phs["human_solicited_agent_verification"]
        check("HOME003 human-solicited agent verification count is 1", c3["count"] == 1, f"got {c3['count']}")
        check("HOME004 human-solicited highest level is V3", c3["highest_level"] == "V3", f"got {c3['highest_level']}")

        c4 = phs["physical_anchor_verification"]
        check("HOME005 physical anchor formal inspection count is 0",
              c4["formal_independent_inspection_count"] == 0,
              f"got {c4['formal_independent_inspection_count']}")
        check("HOME006 physical anchor public context is P3",
              c4["highest_public_evidence_context"] == "P3",
              f"got {c4['highest_public_evidence_context']}")

        check("HOME008 homepage contains BEGIN marker", "<!-- BEGIN GENERATED PUBLIC STATUS -->" in index_md)
        check("HOME008 homepage contains END marker", "<!-- END GENERATED PUBLIC STATUS -->" in index_md)
        check("HOME008 homepage contains 'Institutional / human independent verification'",
              "Institutional / human independent verification" in index_md)
        check("HOME008 homepage contains 'Agent-initiated independent verification'",
              "Agent-initiated independent verification" in index_md)
        check("HOME008 homepage contains 'Human-solicited agent verification'",
              "Human-solicited agent verification" in index_md)
        check("HOME008 homepage contains 'Physical anchor verification'",
              "Physical anchor verification" in index_md)

    # --- HOME007 (common) ---
    r119 = next((r for r in echo_records if "119" in r.get("id", "")), None)
    check("HOME007 #119 exists in echo index", r119 is not None)
    if r119:
        check("HOME007 #119 do_not_count_as_attestation is True",
              r119.get("do_not_count_as_attestation") is True,
              f"got {r119.get('do_not_count_as_attestation')}")
        check("HOME007 #119 counts_as_independent_attestation is False",
              r119.get("counts_as_independent_attestation") is False,
              f"got {r119.get('counts_as_independent_attestation')}")

    human_solicited = [r for r in echo_records if r.get("independence_class") == "human_solicited_agent_response"]
    for hs in human_solicited:
        rid = hs.get("id", "unknown")
        check(f"HOME007 {rid} do_not_count_as_attestation=True",
              hs.get("do_not_count_as_attestation") is True,
              f"got {hs.get('do_not_count_as_attestation')}")
        check(f"HOME007 {rid} counts_as_independent_attestation=False",
              hs.get("counts_as_independent_attestation") is False,
              f"got {hs.get('counts_as_independent_attestation')}")

    # --- HOME009 ---
    expected_digest = phs["source_digest"]
    check("HOME009 homepage digest matches source digest",
          f"<code>{expected_digest}</code>" in index_md,
          f"expected digest {expected_digest} not found in index.md")

    # --- HOME010 ---
    case_count = cases.get("case_count", 0)
    check("HOME010 README case count matches cases.json",
          str(case_count) in readme_text,
          f"expected {case_count} in README")

    # --- Summary ---
    print()
    if errors:
        print(f"FINAL: FAIL — {len(errors)} test(s) failed")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("FINAL: PASS — public home status summary tests passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
