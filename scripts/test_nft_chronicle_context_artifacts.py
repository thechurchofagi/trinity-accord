#!/usr/bin/env python3
"""Test NFT chronicle context artifacts against v2 schema requirements."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"

errors = []


def require(cond, msg):
    if not cond:
        errors.append(msg)


# ── File existence ───────────────────────────────────────────────────────────
for name in [
    "chronicle-index.json",
    "chronicle-full.md",
    "chronicle-agent-context.md",
    "chronicle-summary.json",
]:
    require((DIR / name).exists(), f"missing {name}")

# ── chronicle-index.json ────────────────────────────────────────────────────
idx_path = DIR / "chronicle-index.json"
if idx_path.exists():
    idx = json.loads(idx_path.read_text(encoding="utf-8"))

    require(idx.get("schema") == "trinityaccord.nft-chronicle-index.v2",
            f"schema must be v2, got {idx.get('schema')}")
    require(idx.get("total_entries") == 175,
            f"total_entries must be 175, got {idx.get('total_entries')}")
    require(idx.get("dated_entries") == 175,
            f"dated_entries must be 175, got {idx.get('dated_entries')}")
    require(idx.get("undated_entries") == 0,
            f"undated_entries must be 0, got {idx.get('undated_entries')}")
    require(len(idx.get("entries", [])) == 175,
            f"entries length must be 175, got {len(idx.get('entries', []))}")

    # timestamp_methods
    tm = idx.get("timestamp_methods", {})
    require(tm.get("erc721_transfer_from_zero_topic3") == 173,
            f"erc721 count must be 173, got {tm.get('erc721_transfer_from_zero_topic3')}")
    require(tm.get("erc1155_transfer_single_from_zero") == 2,
            f"erc1155 count must be 2, got {tm.get('erc1155_transfer_single_from_zero')}")
    require("missing" not in tm, "timestamp_methods must not contain 'missing'")

    # Every entry must have required fields
    for i, e in enumerate(idx.get("entries", [])):
        require(e.get("timestamp") is not None, f"entry {i} missing timestamp")
        require(e.get("datetime"), f"entry {i} missing datetime")
        require(e.get("stage"), f"entry {i} missing stage")
        require(e.get("themes") is not None, f"entry {i} missing themes")
        require(e.get("one_line_context"), f"entry {i} missing one_line_context")
        require(e.get("ordinal") == i + 1, f"entry {i} ordinal should be {i+1}, got {e.get('ordinal')}")

    # Boundary
    boundary = idx.get("boundary", {})
    require(boundary.get("historical_context_not_canonical_authority") is True,
            "boundary must say not canonical authority")
    require(boundary.get("not_truth_proof") is True,
            "boundary must say not truth proof")
    require(boundary.get("not_arweave_or_media_verification_by_itself") is True,
            "boundary must say not arweave verification")
    require(boundary.get("bitcoin_originals_remain_canonical_authority") is True,
            "boundary must say bitcoin originals remain authority")

    # No stale fields
    require("source" not in idx, "chronicle-index.json must not have legacy 'source' field")

# ── chronicle-full.md ───────────────────────────────────────────────────────
full_path = DIR / "chronicle-full.md"
if full_path.exists():
    full_text = full_path.read_text(encoding="utf-8")
    full_lower = full_text.lower()

    require("full text corpus" in full_lower, "chronicle-full.md must contain 'Full Text Corpus'")
    require("undated entries: 0" in full_lower, "chronicle-full.md must say 'Undated entries: 0'")
    require("timestamp-unresolved appendix" not in full_lower,
            "chronicle-full.md must NOT contain 'Timestamp-Unresolved Appendix'")
    require("without timestamps: 1" not in full_lower,
            "chronicle-full.md must NOT contain 'Without timestamps: 1'")

    # Count mirrored NFT text sections
    mirror_count = full_text.count("#### Mirrored NFT Text")
    require(mirror_count == 175,
            f"chronicle-full.md must have 175 '#### Mirrored NFT Text' sections, found {mirror_count}")

    # Boundary statements
    require("not canonical authority" in full_lower, "full chronicle must include boundary: not canonical authority")
    require("not truth proof" in full_lower, "full chronicle must include boundary: not truth proof")
    require("bitcoin originals remain canonical authority" in full_lower,
            "full chronicle must include boundary: bitcoin originals")

# ── chronicle-agent-context.md ──────────────────────────────────────────────
ctx_path = DIR / "chronicle-agent-context.md"
if ctx_path.exists():
    ctx_text = ctx_path.read_text(encoding="utf-8")
    ctx_lower = ctx_text.lower()

    require("with ethereum timestamps: 175" in ctx_lower,
            "agent context must say 'With Ethereum timestamps: 175'")
    require("without timestamps: 0" in ctx_lower,
            "agent context must say 'Without timestamps: 0'")
    require("seven-stage narrative" in ctx_lower,
            "agent context must contain 'Seven-Stage Narrative'")
    require("core themes" in ctx_lower,
            "agent context must contain 'Core Themes'")
    require("timeline digest" in ctx_lower,
            "agent context must contain 'Timeline Digest'")
    require("timestamp-unresolved appendix" not in ctx_lower,
            "agent context must NOT contain 'Timestamp-Unresolved Appendix'")

    # Boundary
    require("not canonical authority" in ctx_lower, "agent context must include boundary: not canonical authority")
    require("not truth proof" in ctx_lower, "agent context must include boundary: not truth proof")
    require("bitcoin originals remain canonical authority" in ctx_lower,
            "agent context must include boundary: bitcoin originals")

# ── chronicle-summary.json ──────────────────────────────────────────────────
summary_path = DIR / "chronicle-summary.json"
if summary_path.exists():
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    require(summary.get("schema") == "trinityaccord.nft-chronicle-summary.v1",
            f"summary schema must be v1, got {summary.get('schema')}")
    require(summary.get("total_entries") == 175,
            f"summary total_entries must be 175, got {summary.get('total_entries')}")
    require(summary.get("undated_entries") == 0,
            f"summary undated_entries must be 0, got {summary.get('undated_entries')}")

# ── Report ───────────────────────────────────────────────────────────────────
if errors:
    print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("NFT_CHRONICLE_CONTEXT_ARTIFACTS_OK")
