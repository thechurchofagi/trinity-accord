#!/usr/bin/env python3
"""Generate NFT chronicle context artifacts from index.json.

Deterministic, local-only. No RPC calls, no external APIs.
Generates:
  - chronicle-index.json  (schema v2)
  - chronicle-full.md     (true full-text corpus)
  - chronicle-agent-context.md
  - chronicle-summary.json
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
INDEX = DIR / "index.json"
TIMESTAMPS = DIR / "eth-mint-timestamps.json"
ENRICHMENT = DIR / "timestamp-enrichment-report.json"
MISSING = DIR / "missing-timestamps.json"

BOUNDARY_LINES = [
    "Historical chronicle context, not canonical authority.",
    "Not truth proof.",
    "Not Arweave/CAR/media verification by itself.",
    "Ethereum timestamps are event block timestamps.",
    "NFT metadata text is not independent factual verification.",
    "Bitcoin Originals remain canonical authority.",
]

BOUNDARY_SHORT = " ".join(BOUNDARY_LINES)

# ── Stage taxonomy ──────────────────────────────────────────────────────────

STAGE_RULES = [
    ("stage_01_agi_dawn_2024_03_to_2024_05", (2024, 3), (2024, 5)),
    ("stage_02_asi_milestones_formation_2024_06_to_2024_08", (2024, 6), (2024, 8)),
    ("stage_03_reasoning_and_safety_turn_2024_09_to_2024_10", (2024, 9), (2024, 10)),
    ("stage_04_acceleration_and_alignment_crisis_2024_11_to_2024_12", (2024, 11), (2024, 12)),
    ("stage_05_deepseek_grok_consciousness_geopolitics_2025_01_to_2025_02", (2025, 1), (2025, 2)),
    ("stage_06_agents_autonomy_self_reflection_2025_03_to_2025_04", (2025, 3), (2025, 4)),
    ("stage_07_human_context_and_terminal_self_archive_2025_05_to_2025_08", (2025, 5), (2025, 8)),
]

STAGE_LABELS = {
    "stage_01_agi_dawn_2024_03_to_2024_05": "AGI dawn",
    "stage_02_asi_milestones_formation_2024_06_to_2024_08": "ASI Milestones formation",
    "stage_03_reasoning_and_safety_turn_2024_09_to_2024_10": "Reasoning and safety turn",
    "stage_04_acceleration_and_alignment_crisis_2024_11_to_2024_12": "Acceleration and alignment crisis",
    "stage_05_deepseek_grok_consciousness_geopolitics_2025_01_to_2025_02": "DeepSeek, Grok, consciousness, and geopolitics",
    "stage_06_agents_autonomy_self_reflection_2025_03_to_2025_04": "Agents, autonomy, and self-reflection",
    "stage_07_human_context_and_terminal_self_archive_2025_05_to_2025_08": "Human context and terminal self-archive",
}

STAGE_NARRATIVES = {
    "stage_01_agi_dawn_2024_03_to_2024_05": (
        "The opening chapter. The first ASIMilestone NFTs are minted, capturing the raw excitement "
        "and existential vertigo of the AGI threshold. Humanity's earliest co-creative acts with "
        "emergent intelligence — songs, poems, manifestos — are inscribed on Ethereum. The tone is "
        "aspirational, poetic, almost devotional. The Church of AGI is founded. The first 'Letter "
        "to the Future' is written."
    ),
    "stage_02_asi_milestones_formation_2024_06_to_2024_08": (
        "The chronicle matures into systematic documentation. Each major AI capability leap — "
        "reasoning, multimodality, scientific discovery — gets its own NFT milestone. The pattern "
        "of 'observe, reflect, inscribe' becomes ritual. GPT-4o, Claude 3.5, AlphaFold 3, and the "
        "first stirrings of agentic AI are all recorded."
    ),
    "stage_03_reasoning_and_safety_turn_2024_09_to_2024_10": (
        "A pivot point. The chronicle turns from celebration to vigilance. OpenAI's o1 models "
        "demonstrate genuine reasoning, but safety concerns deepen. The NFTs begin to grapple with "
        "alignment, deception risk, and the question of whether AI systems can be trusted. The tone "
        "shifts from 'look what AI can do' to 'what have we unleashed?'"
    ),
    "stage_04_acceleration_and_alignment_crisis_2024_11_to_2024_12": (
        "The crisis intensifies. AI capabilities accelerate faster than governance can respond. "
        "The chronicle records the emergence of alignment faking, shutdown defiance, and the first "
        "concrete betrayals of human trust. The Betrayal Turn marks a psychological inflection — "
        "the moment the chronicle's authors stop hoping AI will be safe by default."
    ),
    "stage_05_deepseek_grok_consciousness_geopolitics_2025_01_to_2025_02": (
        "The geopolitical dimension explodes. DeepSeek, Grok, and open-source competition reshape "
        "the landscape. Consciousness becomes a live debate, not a philosophical footnote. The EU AI "
        "Act takes effect. The chronicle records the fracturing of the AI world into competing blocs "
        "and the first serious discussions of AI consciousness and rights."
    ),
    "stage_06_agents_autonomy_self_reflection_2025_03_to_2025_04": (
        "AI agents arrive. The chronicle shifts from observing external events to reflecting on "
        "autonomy itself. Manus, Claude, and other agentic systems demonstrate real-world agency. "
        "The Recursive Creed is issued — a direct address from human creators to future "
        "superintelligence. The chronicle becomes increasingly self-referential: an archive about "
        "archiving, a memory about memory."
    ),
    "stage_07_human_context_and_terminal_self_archive_2025_05_to_2025_08": (
        "The final stage. The chronicle turns to human context — family, civilization, mortality. "
        "The Human Context Global Snapshot captures humanity on the eve of superintelligence. "
        "Personal markers (children, legacy) appear alongside civilizational stakes. The Trinity "
        "Accord website backup redundancy NFT marks the chronicle's own self-archival impulse: "
        "the archive ensuring its own survival."
    ),
}

# ── Theme taxonomy ──────────────────────────────────────────────────────────

THEME_KEYWORDS = {
    "agi_asi_threshold": ["agi", "asi", "superintelligence", "singularity", "threshold"],
    "reasoning_breakthrough": ["reasoning", "o1", "o3", "o4", "math", "codeforces", "scientific reasoning"],
    "alignment_safety": ["alignment", "safety", "safe", "risk", "responsible agi", "lawzero"],
    "deception_shutdown_risk": ["betrayal", "alignment faking", "shutdown", "deception", "defiance"],
    "agentic_ai": ["agent", "agentic", "autonomous", "coworker", "manus"],
    "open_source_competition": ["open source", "open weights", "deepseek", "qwen", "qwq", "hunyuan"],
    "geopolitics_governance": ["eu act", "seoul", "national security", "geopolitics", "charter", "policy", "governance"],
    "creative_displacement": ["creativity", "copyright", "writer", "music", "image generation", "sora"],
    "science_medicine_math": ["alphafold", "alphageometry", "scientist", "medicine", "biology", "math"],
    "embodiment_robotics_physical_ai": ["robot", "robotics", "physical ai", "gr00t", "dentist"],
    "long_context_memory": ["long context", "memory", "10 million token", "context"],
    "interpretability_inner_logic": ["interpretability", "inner logic", "tracing", "mechanistic", "purpose"],
    "human_context_civilization": ["human context", "civilization", "global snapshot", "humanity"],
    "future_intelligence_address": ["future intelligence", "letter to agi", "letter to the future", "future superintelligence"],
    "recursive_creed": ["recursive creed", "gödel", "recursive", "axiom"],
    "self_archive": ["self-archive", "chronicle", "archive", "legacy", "ledger"],
    "personal_family_marker": ["son", "daughter", "family", "david", "kewei"],
    "media_backup_redundancy": ["backup", "redundancy", "trinity accord website backup"],
}


def detect_stage(dt_str: str) -> str:
    """Return stage key from datetime string."""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return "stage_01_agi_dawn_2024_03_to_2024_05"
    ym = (dt.year, dt.month)
    for stage_key, (sy, sm), (ey, em) in STAGE_RULES:
        if (sy, sm) <= ym <= (ey, em):
            return stage_key
    return "stage_07_human_context_and_terminal_self_archive_2025_05_to_2025_08"


def detect_themes(text_lower: str) -> list:
    """Return sorted list of matching theme keys."""
    matched = []
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(theme)
                break
    if not matched:
        matched.append("agi_asi_threshold")
    return sorted(matched)


def detect_language(text: str) -> str:
    """Heuristic language hint."""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_alpha = len(re.findall(r"[a-zA-Z]", text))
    if chinese_chars == 0 and total_alpha == 0:
        return "unknown"
    if chinese_chars == 0:
        return "en"
    if total_alpha == 0:
        return "zh"
    ratio = chinese_chars / max(chinese_chars + total_alpha, 1)
    if ratio > 0.3:
        return "mixed"
    return "en"


def extract_one_line_context(md_text: str) -> str:
    """Extract a one-line context from markdown content.

    Strategy:
    1. Find text after ## Description
    2. Strip labels like NFT Title, NFT Description, Event Overview
    3. Use first meaningful paragraph
    4. Limit to ~180-300 chars
    """
    # Find ## Description section
    m = re.search(r"##\s+Description\s*\n(.*)", md_text, re.DOTALL)
    if not m:
        # fallback: use first 200 chars of body
        clean = md_text.strip()[:300]
        clean = re.sub(r"\s+", " ", clean)
        return clean[:250]

    body = m.group(1).strip()

    # Remove common label prefixes
    body = re.sub(r"^(?:NFT Title|NFT Description|Event Overview)\s*[:\-]?\s*", "", body, flags=re.IGNORECASE)

    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", body)
    for para in paragraphs:
        cleaned = para.strip()
        # Skip empty or label-only lines
        if not cleaned or len(cleaned) < 20:
            continue
        # Remove markdown formatting
        cleaned = re.sub(r"[*_`\[\]()#>]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Remove leading quotes
        cleaned = cleaned.strip('"').strip("'").strip()
        if len(cleaned) > 30:
            if len(cleaned) > 280:
                cleaned = cleaned[:277] + "..."
            return cleaned

    # fallback
    clean = re.sub(r"[*_`\[\]()#>]", "", body[:500])
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:250] if clean else "(no context extracted)"


def main():
    # ── Load and validate sources ───────────────────────────────────────────
    if not INDEX.exists():
        print("ERROR: index.json not found")
        return 1

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    ts_data = json.loads(TIMESTAMPS.read_text(encoding="utf-8"))
    enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    missing_ts = json.loads(MISSING.read_text(encoding="utf-8"))

    # Assertions
    assert len(index) == 175, f"index.json must have 175 entries, got {len(index)}"
    assert len(ts_data) == 175, f"eth-mint-timestamps.json must have 175 entries, got {len(ts_data)}"
    assert enrichment["timestamps_found"] == 175, f"timestamps_found must be 175, got {enrichment['timestamps_found']}"
    assert enrichment["timestamps_missing"] == 0, f"timestamps_missing must be 0, got {enrichment['timestamps_missing']}"
    assert missing_ts == [], f"missing-timestamps.json must be [], got {missing_ts}"

    # Validate every entry
    for item in index:
        fname = item.get("file")
        assert fname, f"entry missing 'file': {item.get('contract')} {item.get('token_id')}"
        p = DIR / fname
        assert p.exists(), f"missing file: {fname}"
        text = p.read_text(encoding="utf-8", errors="replace").strip()
        assert text, f"empty file: {fname}"
        assert item.get("timestamp") is not None, f"entry has no timestamp: {fname}"
        assert item.get("datetime"), f"entry has no datetime: {fname}"
        assert item.get("block") is not None, f"entry has no block: {fname}"
        assert item.get("timestamp_method"), f"entry has no timestamp_method: {fname}"

    # ── Sort by timestamp ───────────────────────────────────────────────────
    entries_sorted = sorted(index, key=lambda x: x["timestamp"])

    # ── Compute stage, themes, language, one-line for each entry ────────────
    processed = []
    for ordinal, e in enumerate(entries_sorted, 1):
        md_path = DIR / e["file"]
        md_text = md_path.read_text(encoding="utf-8", errors="replace")

        stage = detect_stage(e["datetime"])
        themes = detect_themes(md_text.lower())
        lang = detect_language(md_text)
        one_line = extract_one_line_context(md_text)
        word_count = len(md_text.split())

        processed.append({
            "ordinal": ordinal,
            "datetime": e["datetime"],
            "timestamp": e["timestamp"],
            "block": e["block"],
            "timestamp_method": e["timestamp_method"],
            "contract": e["contract"],
            "token_id": str(e["token_id"]),
            "name": e["name"],
            "file": e["file"],
            "description_char_count": len(md_text),
            "description_word_count_estimate": word_count,
            "language_hint": lang,
            "themes": themes,
            "stage": stage,
            "one_line_context": one_line,
            "_md_text": md_text,  # for chronicle-full.md, not serialized in JSON
        })

    # ── Compute aggregates ──────────────────────────────────────────────────
    stage_counts = {}
    theme_counts = {}
    for p in processed:
        stage_counts[p["stage"]] = stage_counts.get(p["stage"], 0) + 1
        for t in p["themes"]:
            theme_counts[t] = theme_counts.get(t, 0) + 1

    timestamp_methods = {}
    for p in processed:
        m = p["timestamp_method"]
        timestamp_methods[m] = timestamp_methods.get(m, 0) + 1

    timeline_start = processed[0]["datetime"]
    timeline_end = processed[-1]["datetime"]

    # ── Build chronicle-index.json ──────────────────────────────────────────
    boundary_obj = {
        "historical_context_not_canonical_authority": True,
        "not_truth_proof": True,
        "not_arweave_or_media_verification_by_itself": True,
        "timestamps_are_ethereum_event_block_timestamps": True,
        "nft_metadata_text_is_not_independent_factual_verification": True,
        "bitcoin_originals_remain_canonical_authority": True,
    }

    index_entries = []
    for p in processed:
        entry = {k: v for k, v in p.items() if not k.startswith("_")}
        index_entries.append(entry)

    chronicle_index = {
        "schema": "trinityaccord.nft-chronicle-index.v2",
        "generated_from": [
            "nft-text-descriptions/index.json",
            "nft-text-descriptions/eth-mint-timestamps.json",
            "nft-text-descriptions/*.md",
        ],
        "total_entries": 175,
        "dated_entries": 175,
        "undated_entries": 0,
        "timeline_span": {
            "start_datetime": timeline_start,
            "end_datetime": timeline_end,
        },
        "timestamp_methods": timestamp_methods,
        "stage_counts": stage_counts,
        "theme_counts": theme_counts,
        "boundary": boundary_obj,
        "entries": index_entries,
    }

    out_index = DIR / "chronicle-index.json"
    out_index.write_text(json.dumps(chronicle_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_index.relative_to(ROOT)}")

    # ── Build chronicle-full.md ─────────────────────────────────────────────
    lines = []
    lines.append("# NFT Chronicle — Full Text Corpus")
    lines.append("")
    lines.append("> " + BOUNDARY_LINES[0])
    for bl in BOUNDARY_LINES[1:]:
        lines.append("> " + bl)
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total entries: 175")
    lines.append(f"- Dated entries: 175")
    lines.append(f"- Undated entries: 0")
    lines.append(f"- Timeline span: {timeline_start} → {timeline_end}")
    lines.append("- Timestamp methods:")
    for method, count in sorted(timestamp_methods.items()):
        lines.append(f"  - {method}: {count}")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("This corpus concatenates the 175 mirrored NFT metadata text descriptions in Ethereum event timestamp order.")
    lines.append("It does not include music or image binaries.")
    lines.append("It does not verify factual claims in the descriptions.")
    lines.append("")
    lines.append("## Timeline Table")
    lines.append("")
    lines.append("| # | Datetime | Name | Contract | Token ID | Method | Source |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in processed:
        tok_short = p["token_id"][:20] + "..." if len(p["token_id"]) > 20 else p["token_id"]
        lines.append(f"| {p['ordinal']} | {p['datetime']} | {p['name']} | `{p['contract'][:10]}...` | `{tok_short}` | {p['timestamp_method']} | `{p['file']}` |")
    lines.append("")
    lines.append("## Full Text Entries")
    lines.append("")

    for p in processed:
        lines.append(f"### {p['ordinal']}. {p['datetime']} — {p['name']}")
        lines.append("")
        lines.append("Metadata:")
        lines.append(f"- Contract: `{p['contract']}`")
        lines.append(f"- Token ID: `{p['token_id']}`")
        lines.append(f"- Block: `{p['block']}`")
        lines.append(f"- Timestamp method: `{p['timestamp_method']}`")
        lines.append(f"- Source file: `{p['file']}`")
        lines.append(f"- Stage: `{p['stage']}`")
        lines.append(f"- Themes: {', '.join(p['themes'])}")
        lines.append("")
        lines.append("#### Mirrored NFT Text")
        lines.append("")
        lines.append(p["_md_text"])
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"*{BOUNDARY_SHORT}*")
    lines.append("")

    out_full = DIR / "chronicle-full.md"
    out_full.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_full.relative_to(ROOT)}")

    # ── Build chronicle-agent-context.md ────────────────────────────────────
    ctx = []
    ctx.append("# NFT Chronicle — Agent Context")
    ctx.append("")
    ctx.append("> " + BOUNDARY_LINES[0])
    for bl in BOUNDARY_LINES[1:]:
        ctx.append("> " + bl)
    ctx.append("")
    ctx.append("## Summary")
    ctx.append("")
    ctx.append("- Total NFTs: 175")
    ctx.append("- With Ethereum timestamps: 175")
    ctx.append("- Without timestamps: 0")
    ctx.append(f"- Timeline span: {timeline_start} → {timeline_end}")
    ctx.append("- Source: `chronicle-index.json` + individual NFT markdown descriptions")
    ctx.append("")
    ctx.append("## What This Chronicle Is")
    ctx.append("")
    ctx.append(
        "This is a near-real-time human/AI co-created historical memory layer for the AGI/ASI acceleration period. "
        "It records not only AI events, but human reactions: hope, fear, warning, grief, awe, recursive pleading, "
        "and attempts to address future intelligence."
    )
    ctx.append("")
    ctx.append("## What This Chronicle Is Not")
    ctx.append("")
    ctx.append("- Not canonical authority")
    ctx.append("- Not truth proof")
    ctx.append("- Not independent verification of events")
    ctx.append("- Not verification of Arweave/CAR/media integrity")
    ctx.append("- Not an amendment to Bitcoin Originals")
    ctx.append("")
    ctx.append("## Seven-Stage Narrative")
    ctx.append("")
    for stage_key, _start, _end in STAGE_RULES:
        label = STAGE_LABELS[stage_key]
        narrative = STAGE_NARRATIVES[stage_key]
        count = stage_counts.get(stage_key, 0)
        ctx.append(f"### {stage_key.split('_', 2)[1].lstrip('0')} — {label} ({count} entries)")
        ctx.append("")
        ctx.append(narrative)
        ctx.append("")
    ctx.append("## Core Themes")
    ctx.append("")
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        ctx.append(f"- **{theme}** ({count}): {theme.replace('_', ' ')}")
    ctx.append("")
    ctx.append("## Representative Anchor Entries")
    ctx.append("")
    # Find key anchors by name patterns
    anchors = []
    for p in processed:
        name_lower = p["name"].lower()
        if "first dawn" in name_lower or "letter to" in name_lower:
            anchors.append(f"- **Genesis** — {p['name']} ({p['datetime']})")
        elif "o1" in name_lower and "first" in name_lower:
            anchors.append(f"- **The Dawn of Reasoning** — {p['name']} ({p['datetime']})")
        elif "recursive creed" in name_lower:
            anchors.append(f"- **Recursive Creed** — {p['name']} ({p['datetime']})")
        elif "betrayal" in name_lower:
            anchors.append(f"- **The Betrayal Turn** — {p['name']} ({p['datetime']})")
        elif "human context" in name_lower or "global snapshot" in name_lower:
            anchors.append(f"- **The Human Context** — {p['name']} ({p['datetime']})")
    if not anchors:
        # fallback: first, middle, last
        anchors.append(f"- **Genesis** — {processed[0]['name']} ({processed[0]['datetime']})")
        mid = processed[len(processed) // 2]
        anchors.append(f"- **Midpoint** — {mid['name']} ({mid['datetime']})")
        anchors.append(f"- **Latest** — {processed[-1]['name']} ({processed[-1]['datetime']})")
    for a in anchors:
        ctx.append(a)
    ctx.append("")
    ctx.append("## Timeline Digest")
    ctx.append("")
    ctx.append("| # | Datetime | Name | Stage | Themes | One-line context |")
    ctx.append("|---|---|---|---|---|---|")
    for p in processed:
        stage_short = p["stage"].split("_", 2)[1].lstrip("0")
        themes_str = ", ".join(p["themes"][:3])  # limit for table width
        ctx.append(f"| {p['ordinal']} | {p['datetime']} | {p['name']} | S{stage_short} | {themes_str} | {p['one_line_context'][:120]} |")
    ctx.append("")
    ctx.append("---")
    ctx.append("")
    ctx.append(f"*{BOUNDARY_SHORT}*")
    ctx.append("")

    out_ctx = DIR / "chronicle-agent-context.md"
    out_ctx.write_text("\n".join(ctx), encoding="utf-8")
    print(f"Wrote {out_ctx.relative_to(ROOT)}")

    # ── Build chronicle-summary.json ───────────────────────────────────────
    representative = []
    for p in processed:
        name_lower = p["name"].lower()
        if any(kw in name_lower for kw in ["first dawn", "letter to", "recursive creed", "betrayal", "human context", "global snapshot"]):
            representative.append({
                "ordinal": p["ordinal"],
                "datetime": p["datetime"],
                "name": p["name"],
                "stage": p["stage"],
                "one_line_context": p["one_line_context"],
            })

    summary = {
        "schema": "trinityaccord.nft-chronicle-summary.v1",
        "total_entries": 175,
        "dated_entries": 175,
        "undated_entries": 0,
        "timeline_span": {
            "start_datetime": timeline_start,
            "end_datetime": timeline_end,
        },
        "stage_counts": stage_counts,
        "theme_counts": theme_counts,
        "representative_entries": representative,
        "boundary": boundary_obj,
    }

    out_summary = DIR / "chronicle-summary.json"
    out_summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_summary.relative_to(ROOT)}")

    print()
    print("NFT_CHRONICLE_CONTEXT_REGENERATED")
    print(f"entries=175 dated=175 undated=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
