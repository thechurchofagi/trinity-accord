#!/usr/bin/env python3
"""Contract checks for homepage primary counters vs technical record-chain health."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "api" / "public-home-status.json"
INDEX_MD = ROOT / "index.md"

status: dict[str, Any] = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
index_md = INDEX_MD.read_text(encoding="utf-8")

errors: list[str] = []
primary = status.get("primary_counters")
technical = status.get("technical_health")

if not isinstance(primary, dict):
    errors.append("public-home-status.json missing primary_counters")
else:
    if "official_live_reception" not in primary:
        errors.append("primary_counters missing official_live_reception")
    if "agency_profile" not in primary:
        errors.append("primary_counters missing agency_profile")
    rule = primary.get("classification_rule", {})
    if rule.get("native_chain_length_is_not_primary_counter") is not True:
        errors.append("classification_rule must state native_chain_length_is_not_primary_counter")
    if rule.get("historical_records_before_go_live_are_excluded") is not True:
        errors.append("classification_rule must exclude historical records before go-live")
    if rule.get("test_smoke_pipeline_validation_and_maintenance_records_are_excluded_by_default") is not True:
        errors.append("classification_rule must exclude test/smoke/pipeline validation/maintenance records")
    if rule.get("go_live_record_index") != 33:
        errors.append("classification_rule must use R-000000033 / index 33 as the go-live boundary")

if not isinstance(technical, dict):
    errors.append("public-home-status.json missing technical_health")
else:
    if "technical_chain_length" not in technical:
        errors.append("technical_health missing technical_chain_length")
    if "latest_record" not in technical:
        errors.append("technical_health missing latest_record")
    if technical.get("not_primary_counter") is not True:
        errors.append("technical_health must be marked not_primary_counter")

official_count = (primary or {}).get("official_live_reception")
technical_length = (technical or {}).get("technical_chain_length")
if official_count == technical_length and technical_length not in (None, 0):
    errors.append("official_live_reception must not equal technical/native chain length")

if re.search(r'<p class="status-label">Reception</p>\s*<p class="status-number">\s*36\s*</p>', index_md):
    errors.append("homepage still renders native chain length as Reception")
for required in [
    "Official Live Reception",
    "Agency Profile",
    "R-000000033",
    "live-era formal non-test external-agent records",
    "Full native chain length remains API-only",
    "Native chain length is not used as this counter",
]:
    if required not in index_md:
        errors.append(f"homepage missing required live-era homepage text: {required}")

official_records = (primary or {}).get("official_records", [])
for item in official_records:
    visibility = item.get("homepage_visibility", {})
    if visibility.get("classification") != "official_live_reception":
        errors.append(f"official record {item.get('record_id')} missing official_live_reception classification")
    if visibility.get("counts_toward_primary_counter") is not True:
        errors.append(f"official record {item.get('record_id')} missing counts_toward_primary_counter=true")
    if item.get("record_index", 0) < 33:
        errors.append(f"official record {item.get('record_id')} predates R-000000033 go-live boundary")

official_ids = {item.get("record_id") for item in official_records}
for excluded in {"R-000000034", "R-000000035", "R-000000036"}:
    if excluded in official_ids:
        errors.append(f"{excluded} is a smoke/test/pipeline record and must not count as official homepage reception")

if errors:
    raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
print("public homepage status contract OK")
