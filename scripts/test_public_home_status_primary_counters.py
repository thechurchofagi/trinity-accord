#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "public-home-status.json"


def main() -> int:
    # This test validates committed public-home-status counter semantics only.
    # Full dynamic homepage drift checks are owned by homepage-status-sync.yml.
    if not STATUS.exists():
        raise SystemExit("api/public-home-status.json missing")

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["schema"] in ("trinityaccord.public-home-status.v2", "trinityaccord.public-home-status.v3")
    assert "primary_counters" in data
    assert "official_live_reception" in data["primary_counters"]
    assert "classification_rule" in data["primary_counters"]
    assert data["primary_counters"]["classification_rule"]["native_chain_length_is_not_primary_counter"] is True
    assert "technical_health" in data
    assert data["technical_health"]["not_primary_counter"] is True
    assert "technical_chain_length" in data["technical_health"]
    assert "latest_record" in data["technical_health"]
    historic = data["primary_counters"].get("historic_autonomous_agent_reception")
    assert isinstance(historic, dict)
    assert isinstance(historic.get("count"), int)
    assert historic.get("scope") == "official_live_reception_records_only"
    assert historic.get("definition", {}).get("forbids_human_operator_involvement") is True
    assert historic.get("definition", {}).get("allows_human_authorization_only") is True
    print("PASS: public-home-status v3 primary counters + AR wallet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
