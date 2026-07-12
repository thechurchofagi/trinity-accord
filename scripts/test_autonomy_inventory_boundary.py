#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "public-home-status.json"


def main() -> None:
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    signal = data.get("current_record_chain_autonomy_signal", {})
    errors = []
    if signal.get("scope") != "current_record_chain_only":
        errors.append("autonomy inventory scope changed unexpectedly")
    if signal.get("inventory_scope") != "all_current_native_records_including_non_official_test_and_maintenance_records":
        errors.append("autonomy inventory does not disclose inclusion of non-official/test/maintenance records")
    if signal.get("not_official_live_reception_counter") is not True:
        errors.append("raw autonomy inventory can be mistaken for official-live reception")
    if signal.get("does_not_establish_autonomous_external_agent_discovery") is not True:
        errors.append("raw autonomy inventory lacks the strict discovery boundary")
    eligible = signal.get("eligible_records")
    official = signal.get("official_live_eligible_records")
    if not isinstance(eligible, int) or not isinstance(official, int) or not (0 <= official <= eligible):
        errors.append("official-live autonomy inventory count is invalid")
    if signal.get("includes_non_official_records") is not (official != eligible):
        errors.append("includes_non_official_records is inconsistent with counts")
    strict = data.get("primary_counters", {}).get("historic_autonomous_agent_reception", {})
    if strict.get("scope") != "official_live_reception_records_only":
        errors.append("strict autonomous reception counter is not clearly separated")
    if errors:
        raise SystemExit("FAIL:\n- " + "\n- ".join(errors))
    print("PASS: raw native autonomy inventory cannot be mistaken for strict official-live autonomous reception")


if __name__ == "__main__":
    main()
