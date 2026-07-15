#!/usr/bin/env python3
"""Validate the three-edition, 175-entry NFT Chronicle artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
GENERATED = [
    "chronicle-index.json",
    "chronicle-full.md",
    "chronicle-abridged.md",
    "chronicle-ultra-brief.md",
    "chronicle-agent-context.md",
    "chronicle-summary.json",
]

errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


for name in GENERATED:
    require((DIR / name).exists(), f"missing {name}")

idx_path = DIR / "chronicle-index.json"
idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}
require(idx.get("schema") == "trinityaccord.nft-chronicle-index.v3", f"index schema must be v3, got {idx.get('schema')}")
require(idx.get("total_entries") == 175, "index total_entries must be 175")
require(idx.get("dated_entries") == 175, "index dated_entries must be 175")
require(idx.get("undated_entries") == 0, "index undated_entries must be 0")
entries = idx.get("entries", [])
require(len(entries) == 175, f"index entries must contain 175 items, got {len(entries)}")

methods = idx.get("timestamp_methods", {})
require(methods.get("erc721_transfer_from_zero_topic3") == 173, "ERC-721 timestamp count must be 173")
require(methods.get("erc1155_transfer_single_from_zero") == 2, "ERC-1155 timestamp count must be 2")
require("missing" not in methods, "timestamp methods must not contain missing")

policy = idx.get("interpretation_policy", {})
require(policy.get("fixed_stage_taxonomy_retired") is True, "fixed seven-stage taxonomy must be retired")
require(policy.get("no_current_five_stage_model") is True, "no fixed five-stage replacement may be current")
require(policy.get("fixed_stage_count") is None, "current fixed stage count must be null")
require("seven" in policy.get("reason", "").lower(), "retirement reason must identify the former seven-stage scheme")
require("character accounting" in policy.get("abridgment", ""), "abridgment policy must require character accounting")
require(idx.get("calendar_period_counts"), "calendar period counts missing")
require(idx.get("category_counts") is not None, "category counts missing")
require(idx.get("editions", {}).get("abridged") == "nft-text-descriptions/chronicle-abridged.md", "abridged edition path missing")
require(idx.get("editions", {}).get("ultra_brief") == "nft-text-descriptions/chronicle-ultra-brief.md", "ultra-brief edition path missing")
require(idx.get("abridgment_summary", {}).get("entries_with_any_omission", 0) > 0, "abridgment summary must report reduced entries")

required_abridgment_fields = [
    "source_block_char_count",
    "included_source_char_count",
    "omitted_source_char_count",
    "included_by_kind",
    "omitted_by_kind",
    "embedded_source_char_count",
    "has_embedded_source",
    "embedded_source_titles",
    "has_personal_witness",
    "has_creative_work",
]
for position, entry in enumerate(entries, 1):
    require(entry.get("ordinal") == position, f"entry {position} has wrong ordinal")
    require(entry.get("timestamp") is not None, f"entry {position} missing timestamp")
    require(entry.get("datetime"), f"entry {position} missing datetime")
    require(entry.get("calendar_period"), f"entry {position} missing calendar period")
    require(isinstance(entry.get("categories"), list), f"entry {position} categories must be a list")
    require(entry.get("brief"), f"entry {position} missing brief digest")
    require(isinstance(entry.get("creative_titles"), list), f"entry {position} creative_titles must be a list")
    abridgment = entry.get("abridgment", {})
    for field in required_abridgment_fields:
        require(field in abridgment, f"entry {position} abridgment missing {field}")
    source_chars = abridgment.get("source_block_char_count", -1)
    included_chars = abridgment.get("included_source_char_count", -1)
    omitted_chars = abridgment.get("omitted_source_char_count", -1)
    require(source_chars >= 0 and included_chars >= 0 and omitted_chars >= 0, f"entry {position} has invalid character accounting")
    require(included_chars + omitted_chars == source_chars, f"entry {position} character accounting does not balance")
    require(sum(abridgment.get("included_by_kind", {}).values()) == included_chars, f"entry {position} included-by-kind does not balance")
    require(sum(abridgment.get("omitted_by_kind", {}).values()) == omitted_chars, f"entry {position} omitted-by-kind does not balance")
    require("stage" not in entry, f"entry {position} must not retain old fixed stage")
    require("themes" not in entry, f"entry {position} must not retain old broad theme field")
    require("one_line_context" not in entry, f"entry {position} must not retain old one_line_context field")

boundary = idx.get("boundary", {})
require(boundary.get("historical_context_not_canonical_authority") is True, "index boundary must say non-canonical")
require(boundary.get("not_truth_proof") is True, "index boundary must say not truth proof")
require(boundary.get("bitcoin_originals_remain_canonical_authority") is True, "index boundary must preserve Bitcoin authority")

full_path = DIR / "chronicle-full.md"
if full_path.exists():
    full = full_path.read_text(encoding="utf-8")
    lower = full.lower()
    require("full text edition" in lower, "full edition heading missing")
    require(full.count("#### Mirrored NFT Text — Unabridged") == 175, "full edition must contain 175 unabridged text sections")
    require("former fixed seven-stage narrative is retired" in lower, "full edition must state seven-stage retirement")
    require("not canonical authority" in lower, "full edition boundary missing")
    for position, entry in enumerate(entries, 1):
        source_path = DIR / entry.get("file", "")
        require(source_path.exists(), f"entry {position} source markdown missing")
        if source_path.exists():
            source_text = source_path.read_text(encoding="utf-8", errors="replace").strip()
            require(source_text in full, f"entry {position} source text is not preserved verbatim in full edition")

abridged_path = DIR / "chronicle-abridged.md"
if abridged_path.exists():
    abridged = abridged_path.read_text(encoding="utf-8")
    lower = abridged.lower()
    require("abridged reading edition" in lower, "abridged heading missing")
    require(abridged.count("#### Core record") == 175, "abridged edition must contain 175 core-record sections")
    require(abridged.count("#### Reduction and preservation record") == 175, "abridged edition must contain 175 reduction records")
    require("all omitted text remains verbatim" in lower, "abridged edition must explain preservation of every omission")
    require("not canonical authority" in lower, "abridged edition boundary missing")

ultra_path = DIR / "chronicle-ultra-brief.md"
if ultra_path.exists():
    ultra = ultra_path.read_text(encoding="utf-8")
    lower = ultra.lower()
    require("ultra-brief 175-entry timeline" in lower, "ultra-brief heading missing")
    data_rows = [line for line in ultra.splitlines() if line.startswith("| ")][1:]
    require(len(data_rows) == 175, f"ultra-brief timeline must have 175 rows, got {len(data_rows)}")
    require("a fixed-stage periodization is used" not in lower, "ultra-brief edition must not reinstate a fixed-stage periodization")

ctx_path = DIR / "chronicle-agent-context.md"
if ctx_path.exists():
    context = ctx_path.read_text(encoding="utf-8")
    lower = context.lower()
    require("corrected agent context" in lower, "agent context correction heading missing")
    require("with ethereum timestamps: 175" in lower, "agent context must state 175 timestamped entries")
    require("without timestamps: 0" in lower, "agent context must state zero untimestamped entries")
    require("retired fixed-stage interpretations" in lower, "agent context must explain retirement of fixed-stage interpretations")
    require("overlapping interpretive arcs" in lower, "agent context must use overlapping arcs")
    require("abridgment audit" in lower, "agent context must expose the abridgment audit")
    require("## seven-stage narrative" not in lower, "agent context must not retain old seven-stage section")

summary_path = DIR / "chronicle-summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
require(summary.get("schema") == "trinityaccord.nft-chronicle-summary.v2", f"summary schema must be v2, got {summary.get('schema')}")
require(summary.get("total_entries") == 175, "summary total_entries must be 175")
require(summary.get("undated_entries") == 0, "summary undated_entries must be 0")
require(summary.get("interpretation_policy", {}).get("fixed_stage_taxonomy_retired") is True, "summary must retire fixed stages")
require(summary.get("editions", {}).get("full") == "nft-text-descriptions/chronicle-full.md", "summary full edition path missing")
require(summary.get("abridgment_summary", {}).get("omitted_source_characters", 0) > 0, "summary must report omitted characters")

if all((DIR / name).exists() for name in GENERATED):
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", *[str(DIR / name) for name in GENERATED]],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    require(result.returncode == 0, "generated Chronicle editions drift from committed files")

if errors:
    print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_OK")
