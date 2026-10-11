#!/usr/bin/env python3
"""Validate the declared A4Q interface grading; not a physical experiment."""

import json
import sys
from pathlib import Path


EXPECTED = [
    "P_same", "P_ext", "P_anchor", "P_block",
    "P_rescue", "P_closed", "P_event", "P_readout",
]


def main() -> int:
    path = Path(__file__).with_name("INTERFACE_AUDIT.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    premises = data["premises"]
    ids = [item["id"] for item in premises]
    checks = {
        "exact_eight_premises": ids == EXPECTED,
        "no_document_only_discharge": not any(item["discharged"] for item in premises),
        "joint_installation_false": data["all_eight_premises_discharged"] is False,
        "no_map_promotion": data["formal_map_promotion"] is False,
        "no_phenomenal_assignment": data["phenomenal_assignment"] is False,
        "route_grains_distinct": len(data["routes"]) == 3,
    }
    result = {
        "schema": "uct-a4q-interface-check/1.0",
        "input": path.name,
        "checks": checks,
        "pass": all(checks.values()),
        "interpretation": "The public-document audit discharges no A4P premise on an actual token; it separates a stock internal-route failure from a prospective external composite route."
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
