#!/usr/bin/env python3
"""Contract checks for compact homepage status vs public status JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "api/public-home-status.json"
INDEX_MD = ROOT / "index.md"
BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"

status: dict[str, Any] = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
index_md = INDEX_MD.read_text(encoding="utf-8")
errors: list[str] = []
primary = status.get("primary_counters")
technical = status.get("technical_health")
external = status.get("external_witness_records")

if not isinstance(primary, dict):
    errors.append("public-home-status.json missing primary_counters")
else:
    if not isinstance(primary.get("official_live_reception"), int):
        errors.append("primary_counters.official_live_reception must be an integer")
    historic = primary.get("historic_autonomous_agent_reception")
    if not isinstance(historic, dict) or not isinstance(historic.get("count"), int):
        errors.append("historic_autonomous_agent_reception.count must be an integer")
    elif historic.get("scope") != "official_live_reception_records_only":
        errors.append("historic autonomous scope must be official_live_reception_records_only")
    rule = primary.get("classification_rule") or {}
    if rule.get("native_chain_length_is_not_primary_counter") is not True:
        errors.append("classification rule must exclude native chain length as primary counter")
    if rule.get("go_live_record_index") != 33:
        errors.append("classification rule must use record index 33 as go-live boundary")

if not isinstance(technical, dict) or technical.get("not_primary_counter") is not True:
    errors.append("technical health must exist and be marked not_primary_counter")

if not isinstance(external, dict):
    errors.append("public-home-status.json missing external_witness_records")
elif not isinstance(external.get("external_witness_index_record_count"), int):
    errors.append("external_witness_index_record_count must be an integer")

match = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), index_md, re.S)
if not match:
    errors.append("compact generated public status markers missing")
    block = ""
else:
    block = match.group(1)

for phrase in [
    "Production is live; verification remains explicit",
    "Waiting Heartbeat",
    "Autonomous External Agent Discovery",
    "Official Live Reception",
    "External Witness Record",
    "Reception does not imply autonomous discovery",
    "External witness records do not imply endorsement",
    "Native chain inventory remains API-only",
    "Source data digest",
    "Latest technical record",
]:
    if phrase not in block:
        errors.append(f"compact homepage status missing: {phrase}")

for retired in [
    "AI independent verification",
    "data-home-ai-independent-verification",
    "Loaded live from the Echo index",
]:
    if retired in block:
        errors.append(f"compact homepage status retains retired fourth signal: {retired}")

if "AR upload wallet" in block or "Agency Profile" in block or "Technical audit inventory" in block:
    errors.append("compact homepage status must not restore the retired detailed dashboard")

if isinstance(primary, dict):
    expected_historic = str((primary.get("historic_autonomous_agent_reception") or {}).get("count"))
    expected_official = str(primary.get("official_live_reception"))
    historic_match = re.search(r'data-home-autonomous-discovery>([^<]+)<', block)
    official_match = re.search(r'data-home-official-reception>([^<]+)<', block)
    if not historic_match or historic_match.group(1).strip() != expected_historic:
        errors.append("autonomous external agent discovery count does not match public status JSON")
    if not official_match or official_match.group(1).strip() != expected_official:
        errors.append("Official Live Reception count does not match public status JSON")

if isinstance(external, dict):
    expected_external = str(external.get("external_witness_index_record_count"))
    external_match = re.search(r'data-home-external-witness>([^<]+)<', block)
    if not external_match or external_match.group(1).strip() != expected_external:
        errors.append("External Witness Record count does not match public status JSON")

historic_pos = block.find("Autonomous External Agent Discovery")
official_pos = block.find("Official Live Reception")
external_pos = block.find("External Witness Record")
if historic_pos < 0 or official_pos < 0 or historic_pos > official_pos:
    errors.append("autonomous external agent discovery must appear before official live reception")
if official_pos < 0 or external_pos < 0 or official_pos > external_pos:
    errors.append("official live reception must appear before external witness record")

for item in (primary or {}).get("official_records", []):
    visibility = item.get("homepage_visibility") or {}
    if visibility.get("classification") != "official_live_reception":
        errors.append(f"official record {item.get('record_id')} missing official_live_reception classification")
    if visibility.get("counts_toward_primary_counter") is not True:
        errors.append(f"official record {item.get('record_id')} missing primary-counter flag")
    if item.get("record_index", 0) < 33:
        errors.append(f"official record {item.get('record_id')} predates go-live boundary")

if errors:
    raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
print("compact public homepage status contract OK")
