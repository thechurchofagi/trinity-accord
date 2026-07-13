#!/usr/bin/env python3
"""Generate three deterministic editions of the 175-entry NFT Chronicle.

Local-only; no RPC calls or external APIs.

Outputs:
  - chronicle-index.json        structured factual/curation index (v3)
  - chronicle-full.md           all mirrored NFT text, unabridged
  - chronicle-abridged.md       core record + human witness + creative work;
                                long embedded source documents are described
  - chronicle-ultra-brief.md    one-row-per-NFT chronological digest
  - chronicle-agent-context.md  corrected reading guide (no fixed stage claims)
  - chronicle-summary.json      compact machine-readable summary (v2)
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
INDEX = DIR / "index.json"
TIMESTAMPS = DIR / "eth-mint-timestamps.json"
ENRICHMENT = DIR / "timestamp-enrichment-report.json"
MISSING = DIR / "missing-timestamps.json"

BOUNDARY_LINES = [
    "Historical chronicle context, not canonical authority.",
    "Not truth proof.",
    "Not independent verification of external events.",
    "Ethereum timestamps are NFT event block timestamps, not necessarily real-world event times.",
    "NFT metadata text may contain human recollection, AI-assisted wording, quotations, lyrics, and embedded source material.",
    "Bitcoin Originals remain canonical authority.",
]
BOUNDARY_SHORT = " ".join(BOUNDARY_LINES)

EDITION_PATHS = {
    "full": "nft-text-descriptions/chronicle-full.md",
    "abridged": "nft-text-descriptions/chronicle-abridged.md",
    "ultra_brief": "nft-text-descriptions/chronicle-ultra-brief.md",
    "agent_context": "nft-text-descriptions/chronicle-agent-context.md",
    "index": "nft-text-descriptions/chronicle-index.json",
    "summary": "nft-text-descriptions/chronicle-summary.json",
}

# These are overlapping descriptive categories, never exclusive stages.
CATEGORY_PATTERNS = {
    "capability_and_model_milestones": [
        r"\bgpt[- ]?4o\b", r"\bo1\b", r"\bo3\b", r"\bo4\b", r"\bclaude\b",
        r"\bgemini\b", r"\bdeepseek\b", r"\bqwen\b", r"\bllama\b", r"\bgrok\b",
        r"\bmodel\b", r"multimodal", r"long[- ]context",
    ],
    "reasoning_science_and_medicine": [
        r"reasoning", r"mathemat", r"scientific", r"alphafold", r"biology",
        r"medicine", r"healthcare", r"physics", r"chemistry", r"research",
    ],
    "safety_alignment_and_control": [
        r"alignment", r"ai safety", r"superalignment", r"deception", r"shutdown",
        r"betrayal", r"control problem", r"existential risk", r"responsible ai",
    ],
    "agents_autonomy_and_embodiment": [
        r"\bagent(?:ic|s)?\b", r"autonomous", r"computer use", r"robot(?:ics)?",
        r"physical ai", r"manus", r"coworker", r"embodied",
    ],
    "governance_geopolitics_and_society": [
        r"governance", r"geopolit", r"national security", r"eu ai act", r"seoul summit",
        r"charter", r"regulation", r"policy", r"military", r"copyright", r"lawsuit",
    ],
    "creative_work_and_displacement": [
        r"\bsong\b", r"lyrics?", r"poem", r"music", r"artwork", r"artist",
        r"writer", r"creativ", r"suno", r"udio", r"image generation", r"video generation",
    ],
    "human_family_and_personal_witness": [
        r"my son", r"my daughter", r"my wife", r"my family", r"for my son", r"for my daughter",
        r"\bdavid\b", r"\bkewei\b", r"\bweiwei\b", r"i feel", r"i fear", r"i hope",
        r"i wrote", r"i created", r"personal reflection", r"human context",
    ],
    "address_to_future_intelligence": [
        r"letter to agi", r"letter to the future", r"future intelligence",
        r"future superintelligence", r"dear agi", r"dear asi", r"recursive creed",
    ],
    "archive_memory_and_trinity_accord": [
        r"trinity accord", r"church of agi", r"chronicle", r"self[- ]archive",
        r"archive", r"backup", r"redundancy", r"legacy", r"memory layer",
    ],
}
COMPILED_CATEGORY_PATTERNS = {
    key: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for key, patterns in CATEGORY_PATTERNS.items()
}

CREATIVE_START_PATTERNS = [
    re.compile(r"^(?:#+\s*)?(?:original\s+)?lyrics?\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:original\s+)?poem\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:song|music|artwork|art piece|visual work)\s*(?:title|name|description)?\s*[:：]", re.IGNORECASE),
    re.compile(r"^\[(?:verse|chorus|bridge|outro|intro|pre-chorus|instrumental)", re.IGNORECASE),
    re.compile(r"^(?:歌词|原始歌词|歌曲|诗歌|原诗|画作|艺术品)\s*[:：]"),
]

EMBEDDED_SOURCE_START_PATTERNS = [
    re.compile(r"^(?:#+\s*)?(?:appendix|annex|full text|complete text|source text|source document|historical document|original document|document transcript)\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:全文|原文|附录|附件|历史文件|历史文献|文件全文)\b"),
    re.compile(r"^(?:#+\s*)?(?:(?:the\s+)?geneva convention|universal declaration of human rights|constitution|treaty|convention|declaration|memorandum|resolution|white paper)\b", re.IGNORECASE),
    re.compile(r"^(?:(?:the following|below)\s+is|(?:the\s+)?(?:full|complete|original)\s+text\s+of)\s+(?:the\s+)?(?:full|complete|original)?\s*(?:text|document)?", re.IGNORECASE),
    re.compile(r"^(?:以下|下文)为.+(?:全文|原文)"),
]

KNOWN_DOCUMENT_PATTERNS = {
    "Geneva Conventions": re.compile(r"geneva convention", re.IGNORECASE),
    "Universal Declaration of Human Rights": re.compile(r"universal declaration of human rights", re.IGNORECASE),
    "EU AI Act": re.compile(r"\beu ai act\b", re.IGNORECASE),
    "AI Seoul Summit materials": re.compile(r"seoul summit", re.IGNORECASE),
    "United Nations materials": re.compile(r"united nations|\bun\s+(?:charter|resolution|report)", re.IGNORECASE),
    "constitutional / charter text": re.compile(r"\bconstitution\b|\bcharter\b", re.IGNORECASE),
    "treaty / convention text": re.compile(r"\btreaty\b|\bconvention\b", re.IGNORECASE),
    "memorandum / policy text": re.compile(r"\bmemorandum\b|\bpolicy document\b", re.IGNORECASE),
    "research paper / report text": re.compile(r"\bresearch paper\b|\btechnical report\b|\bfull report\b", re.IGNORECASE),
}

PERSONAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"my son", r"my daughter", r"my wife", r"my family", r"for my son", r"for my daughter",
        r"\bdavid\b", r"\bkewei\b", r"\bweiwei\b", r"i feel", r"i fear", r"i hope",
        r"i wrote", r"i created", r"i composed", r"i dedicate", r"my personal", r"our family",
    ]
]

SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+")


def fail(message: str) -> None:
    raise AssertionError(message)


def clean_inline(text: str) -> str:
    text = re.sub(r"[`*_>#\[\]]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip('"').strip("'").strip()


def extract_description(md_text: str) -> str:
    match = re.search(r"^##\s+Description\s*$\n?(.*)\Z", md_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    lines = md_text.splitlines()
    body = []
    metadata_seen = False
    for line in lines:
        if line.startswith("**Contract**") or line.startswith("**Token ID**"):
            metadata_seen = True
            continue
        if metadata_seen and line.strip():
            body.append(line)
    return "\n".join(body).strip() or md_text.strip()


def split_blocks(text: str) -> list[str]:
    blocks = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        block = block.strip()
        if block:
            blocks.append(block)
    return blocks


def first_line(block: str) -> str:
    return block.splitlines()[0].strip()


def is_creative_start(block: str) -> bool:
    line = first_line(block)
    return any(pattern.search(line) for pattern in CREATIVE_START_PATTERNS)


def is_embedded_source_start(block: str) -> bool:
    line = first_line(block)
    if any(pattern.search(line) for pattern in EMBEDDED_SOURCE_START_PATTERNS):
        return True
    lower = block.lower()
    article_hits = len(re.findall(r"(?:^|\n)\s*(?:article|section|chapter)\s+\d+", block, flags=re.IGNORECASE))
    if len(block) >= 2500 and article_hits >= 3:
        return True
    if len(block) >= 3500 and ("whereas" in lower or "shall be" in lower) and article_hits >= 1:
        return True
    return False


def detect_document_titles(text: str) -> list[str]:
    found = [label for label, pattern in KNOWN_DOCUMENT_PATTERNS.items() if pattern.search(text)]
    for block in split_blocks(text):
        line = clean_inline(first_line(block))
        if not line or len(line) > 180:
            continue
        if is_embedded_source_start(block) and line not in found:
            found.append(line)
    return found[:12]


def truncate_at_sentence(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    cut = max(clipped.rfind("."), clipped.rfind("!"), clipped.rfind("?"), clipped.rfind("。"), clipped.rfind("！"), clipped.rfind("？"))
    if cut >= int(limit * 0.55):
        return clipped[: cut + 1].strip()
    space = clipped.rfind(" ")
    if space >= int(limit * 0.55):
        clipped = clipped[:space]
    return clipped.rstrip() + "…"


def select_blocks(blocks: Iterable[str], limit: int) -> str:
    selected: list[str] = []
    total = 0
    for block in blocks:
        clean = block.strip()
        if not clean:
            continue
        addition = len(clean) + (2 if selected else 0)
        if total + addition > limit:
            remaining = limit - total
            if remaining >= 180:
                selected.append(truncate_at_sentence(clean, remaining))
            break
        selected.append(clean)
        total += addition
    return "\n\n".join(selected).strip()


def detect_categories(text: str) -> list[str]:
    return sorted(
        category
        for category, patterns in COMPILED_CATEGORY_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    )


def detect_language(text: str) -> str:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_chars = len(re.findall(r"[A-Za-z]", text))
    if chinese_chars == 0 and latin_chars == 0:
        return "unknown"
    if chinese_chars == 0:
        return "en"
    if latin_chars == 0:
        return "zh"
    ratio = chinese_chars / max(chinese_chars + latin_chars, 1)
    return "mixed" if ratio >= 0.08 else "en_with_zh"


def calendar_period(datetime_text: str) -> str:
    dt = datetime.fromisoformat(datetime_text.replace("Z", "+00:00"))
    return f"{dt.year}-Q{((dt.month - 1) // 3) + 1}"


def extract_entry_layers(description: str) -> dict:
    blocks = split_blocks(description)
    core_blocks: list[str] = []
    creative_blocks: list[str] = []
    embedded_blocks: list[str] = []
    mode = "core"

    for block in blocks:
        if is_embedded_source_start(block):
            mode = "embedded"
        elif mode == "core" and is_creative_start(block):
            mode = "creative"
        elif mode == "creative" and is_embedded_source_start(block):
            mode = "embedded"

        if mode == "embedded":
            embedded_blocks.append(block)
        elif mode == "creative":
            creative_blocks.append(block)
        else:
            core_blocks.append(block)

    if not creative_blocks:
        for block in list(core_blocks):
            line = first_line(block).lower()
            if re.search(r"\b(?:lyrics?|poem|song title|original song)\b|(?:歌词|诗歌|歌曲名)", line, re.IGNORECASE):
                creative_blocks.append(block)

    non_embedded_blocks = core_blocks + creative_blocks
    personal_blocks = [
        block for block in non_embedded_blocks
        if any(pattern.search(block) for pattern in PERSONAL_PATTERNS)
    ]

    core_excerpt = select_blocks(core_blocks, 3000)
    if not core_excerpt:
        core_excerpt = select_blocks(non_embedded_blocks, 3000)
    creative_excerpt = select_blocks(creative_blocks, 12000)
    personal_excerpt = select_blocks(personal_blocks, 2600)
    embedded_text = "\n\n".join(embedded_blocks).strip()

    brief_source = core_excerpt or select_blocks(non_embedded_blocks, 1200) or description
    brief_sentences = [clean_inline(s) for s in SENTENCE_RE.split(clean_inline(brief_source)) if clean_inline(s)]
    brief = " ".join(brief_sentences[:2])
    brief = truncate_at_sentence(brief or clean_inline(brief_source), 520)

    creative_titles = []
    for block in creative_blocks:
        line = clean_inline(first_line(block))
        if 3 <= len(line) <= 180 and line not in creative_titles:
            creative_titles.append(line)
    creative_titles = creative_titles[:8]

    return {
        "core_excerpt": core_excerpt,
        "creative_excerpt": creative_excerpt,
        "personal_excerpt": personal_excerpt,
        "brief": brief,
        "creative_titles": creative_titles,
        "embedded_source_text": embedded_text,
        "embedded_source_titles": detect_document_titles(embedded_text),
        "core_char_count": sum(len(block) for block in core_blocks),
        "creative_char_count": sum(len(block) for block in creative_blocks),
        "personal_char_count": sum(len(block) for block in personal_blocks),
        "embedded_source_char_count": len(embedded_text),
        "has_embedded_source": bool(embedded_text),
    }


def boundary_markdown(lines: list[str]) -> None:
    for line in BOUNDARY_LINES:
        lines.append(f"> {line}")


def table_escape(text: str) -> str:
    return clean_inline(text).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    if not INDEX.exists():
        print("ERROR: index.json not found", file=sys.stderr)
        return 1

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    timestamps = json.loads(TIMESTAMPS.read_text(encoding="utf-8"))
    enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    missing = json.loads(MISSING.read_text(encoding="utf-8"))

    fail(f"index.json must have 175 entries, got {len(index)}") if len(index) != 175 else None
    fail(f"eth-mint-timestamps.json must have 175 entries, got {len(timestamps)}") if len(timestamps) != 175 else None
    fail("timestamp enrichment must report 175 found") if enrichment.get("timestamps_found") != 175 else None
    fail("timestamp enrichment must report 0 missing") if enrichment.get("timestamps_missing") != 0 else None
    fail(f"missing-timestamps.json must be empty, got {missing}") if missing != [] else None

    entries_sorted = sorted(index, key=lambda item: item["timestamp"])
    processed = []

    for ordinal, source in enumerate(entries_sorted, 1):
        filename = source.get("file")
        fail(f"entry missing source file: {source}") if not filename else None
        path = DIR / filename
        fail(f"missing NFT description file: {filename}") if not path.exists() else None
        md_text = path.read_text(encoding="utf-8", errors="replace").strip()
        fail(f"empty NFT description file: {filename}") if not md_text else None
        for required in ("timestamp", "datetime", "block", "timestamp_method", "contract", "token_id", "name"):
            fail(f"{filename} missing {required}") if source.get(required) is None else None

        description = extract_description(md_text)
        layers = extract_entry_layers(description)
        categories = detect_categories(description)
        processed.append({
            "ordinal": ordinal,
            "datetime": source["datetime"],
            "timestamp": source["timestamp"],
            "block": source["block"],
            "timestamp_method": source["timestamp_method"],
            "contract": source["contract"],
            "token_id": str(source["token_id"]),
            "name": source["name"],
            "file": filename,
            "description_char_count": len(description),
            "description_word_count_estimate": len(description.split()),
            "language_hint": detect_language(description),
            "calendar_period": calendar_period(source["datetime"]),
            "categories": categories,
            "brief": layers["brief"],
            "creative_titles": layers["creative_titles"],
            "abridgment": {
                "core_char_count": layers["core_char_count"],
                "creative_char_count": layers["creative_char_count"],
                "personal_char_count": layers["personal_char_count"],
                "embedded_source_char_count": layers["embedded_source_char_count"],
                "has_embedded_source": layers["has_embedded_source"],
                "embedded_source_titles": layers["embedded_source_titles"],
            },
            "_md_text": md_text,
            "_description": description,
            "_layers": layers,
        })

    timeline_start = processed[0]["datetime"]
    timeline_end = processed[-1]["datetime"]
    timestamp_methods = Counter(item["timestamp_method"] for item in processed)
    period_counts = Counter(item["calendar_period"] for item in processed)
    category_counts = Counter(category for item in processed for category in item["categories"])
    embedded_entries = [item for item in processed if item["abridgment"]["has_embedded_source"]]
    total_embedded_chars = sum(item["abridgment"]["embedded_source_char_count"] for item in processed)

    boundary_obj = {
        "historical_context_not_canonical_authority": True,
        "not_truth_proof": True,
        "not_independent_event_verification": True,
        "not_arweave_or_media_verification_by_itself": True,
        "timestamps_are_ethereum_event_block_timestamps": True,
        "nft_metadata_text_is_not_independent_factual_verification": True,
        "bitcoin_originals_remain_canonical_authority": True,
    }
    interpretation_policy = {
        "fixed_stage_taxonomy_retired": True,
        "reason": "The previous seven-stage scheme was imposed by date buckets and broad keyword matching; it was not authored by the NFTs and is not a verified historical periodization.",
        "objective_ordering": "ascending Ethereum NFT event block timestamp",
        "calendar_periods": "quarter-based grouping for navigation only",
        "categories": "overlapping descriptive signals, not exclusive stages and not factual verification",
        "abridgment": "deterministic extraction; long embedded source documents are omitted only from abridged editions and remain in the full corpus and original NFT files",
    }

    serializable_entries = []
    for item in processed:
        serializable_entries.append({key: value for key, value in item.items() if not key.startswith("_")})
    chronicle_index = {
        "schema": "trinityaccord.nft-chronicle-index.v3",
        "generated_from": [
            "nft-text-descriptions/index.json",
            "nft-text-descriptions/eth-mint-timestamps.json",
            "nft-text-descriptions/*.md",
        ],
        "editions": EDITION_PATHS,
        "total_entries": 175,
        "dated_entries": 175,
        "undated_entries": 0,
        "timeline_span": {"start_datetime": timeline_start, "end_datetime": timeline_end},
        "timestamp_methods": dict(sorted(timestamp_methods.items())),
        "calendar_period_counts": dict(sorted(period_counts.items())),
        "category_counts": dict(sorted(category_counts.items(), key=lambda pair: (-pair[1], pair[0]))),
        "embedded_source_summary": {
            "entries_with_embedded_source_material": len(embedded_entries),
            "embedded_source_characters": total_embedded_chars,
        },
        "interpretation_policy": interpretation_policy,
        "boundary": boundary_obj,
        "entries": serializable_entries,
    }
    (DIR / "chronicle-index.json").write_text(
        json.dumps(chronicle_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    full: list[str] = ["# NFT Chronicle — Full Text Edition", ""]
    boundary_markdown(full)
    full.extend([
        "",
        "## Edition purpose",
        "",
        "This edition preserves every mirrored NFT markdown description in full, in ascending Ethereum event timestamp order.",
        "Nothing is removed because a passage is repetitive, quoted, legal, historical, lyrical, personal, or AI-assisted.",
        "The only added material is navigation metadata and the boundary above.",
        "",
        "## Summary",
        "",
        "- Total entries: 175",
        "- Dated entries: 175",
        "- Undated entries: 0",
        f"- Timeline span: {timeline_start} → {timeline_end}",
        f"- Entries containing detected embedded source material: {len(embedded_entries)}",
        f"- Detected embedded-source characters retained in this edition: {total_embedded_chars}",
        "",
        "## Interpretation correction",
        "",
        "The former fixed seven-stage narrative is retired. It was an AI-generated periodization based largely on month ranges and broad keyword matching, not a source-authored structure.",
        "This edition uses only chronological order, quarter labels for navigation, and overlapping descriptive categories.",
        "",
        "## Timeline table",
        "",
        "| # | Datetime | Name | Period | Categories | Source |",
        "|---|---|---|---|---|---|",
    ])
    for item in processed:
        cats = ", ".join(item["categories"]) or "uncategorized"
        full.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | {item['calendar_period']} | {table_escape(cats)} | `{item['file']}` |"
        )
    full.extend(["", "## Full text entries", ""])
    for item in processed:
        full.extend([
            f"### {item['ordinal']}. {item['datetime']} — {item['name']}",
            "",
            "Metadata:",
            f"- Contract: `{item['contract']}`",
            f"- Token ID: `{item['token_id']}`",
            f"- Block: `{item['block']}`",
            f"- Timestamp method: `{item['timestamp_method']}`",
            f"- Calendar period: `{item['calendar_period']}`",
            f"- Descriptive categories: {', '.join(item['categories']) or 'none detected'}",
            f"- Source file: `{item['file']}`",
            "",
            "#### Mirrored NFT Text — Unabridged",
            "",
            item["_md_text"],
            "",
            "---",
            "",
        ])
    full.extend([f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-full.md").write_text("\n".join(full), encoding="utf-8")

    abridged: list[str] = ["# NFT Chronicle — Abridged Reading Edition", ""]
    boundary_markdown(abridged)
    abridged.extend([
        "",
        "## Editorial method",
        "",
        "This edition preserves the core record, personal/family witness, and creative work detected in each NFT description.",
        "Long embedded historical, legal, policy, report, or source-document text is represented by title/type and size instead of being repeated.",
        "No omitted text is lost: it remains in `chronicle-full.md` and in the individual NFT source markdown file.",
        "The abridgment is deterministic and conservative; it does not certify external facts or resolve authorship/copyright questions.",
        "",
        "## Chronological entries",
        "",
    ])
    for item in processed:
        layers = item["_layers"]
        abridged.extend([
            f"### {item['ordinal']}. {item['datetime']} — {item['name']}",
            "",
            f"- Period: `{item['calendar_period']}`",
            f"- Categories: {', '.join(item['categories']) or 'none detected'}",
            f"- Contract / Token: `{item['contract']}` / `{item['token_id']}`",
            f"- Original source: `{item['file']}`",
            "",
            "#### Core record",
            "",
            layers["core_excerpt"] or "(No separate core paragraph could be isolated; consult the full edition.)",
            "",
        ])
        if layers["personal_excerpt"] and layers["personal_excerpt"] not in layers["core_excerpt"]:
            abridged.extend(["#### Personal / family witness", "", layers["personal_excerpt"], ""])
        if layers["creative_excerpt"]:
            abridged.extend(["#### Creative work retained", "", layers["creative_excerpt"], ""])
        if layers["has_embedded_source"]:
            titles = layers["embedded_source_titles"] or ["unlabeled embedded source/document text"]
            abridged.extend([
                "#### Embedded source material summarized",
                "",
                f"- Detected material: {'; '.join(titles)}",
                f"- Omitted from this abridged edition: {layers['embedded_source_char_count']} characters",
                "- Preservation: retained verbatim in the full edition and the original NFT markdown source.",
                "",
            ])
        abridged.extend(["---", ""])
    abridged.extend([f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-abridged.md").write_text("\n".join(abridged), encoding="utf-8")

    ultra: list[str] = ["# NFT Chronicle — Ultra-Brief 175-Entry Timeline", ""]
    boundary_markdown(ultra)
    ultra.extend([
        "",
        "This is a navigation edition, not a substitute for the abridged or full text.",
        "The prior fixed seven-stage periodization is intentionally not used.",
        "",
        "| # | Ethereum datetime | NFT title | Period | One-record digest | Creative / embedded material |",
        "|---|---|---|---|---|---|",
    ])
    for item in processed:
        layers = item["_layers"]
        notes = []
        if layers["creative_titles"]:
            notes.append("creative: " + "; ".join(layers["creative_titles"][:3]))
        if layers["has_embedded_source"]:
            titles = layers["embedded_source_titles"] or ["embedded source text"]
            notes.append("source appendix: " + "; ".join(titles[:3]))
        ultra.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | {item['calendar_period']} | {table_escape(item['brief'])} | {table_escape(' / '.join(notes) or '—')} |"
        )
    ultra.extend(["", f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-ultra-brief.md").write_text("\n".join(ultra), encoding="utf-8")

    context: list[str] = ["# NFT Chronicle — Corrected Agent Context", ""]
    boundary_markdown(context)
    context.extend([
        "",
        "## Corpus facts",
        "",
        "- Total NFTs: 175",
        "- With Ethereum timestamps: 175",
        "- Without timestamps: 0",
        f"- Timeline span: {timeline_start} → {timeline_end}",
        "- Ordering: ascending Ethereum NFT event block timestamp",
        "",
        "## Three reading editions",
        "",
        "1. `chronicle-ultra-brief.md` — 175-row navigation timeline.",
        "2. `chronicle-abridged.md` — core record, personal witness, creative text, and compact references to long embedded documents.",
        "3. `chronicle-full.md` — every mirrored NFT text description verbatim.",
        "",
        "## Correction to the former seven-stage narrative",
        "",
        "The former seven-stage narrative is retired as a default interpretation. Its boundaries were fixed calendar buckets with narrative names, and its theme counts were produced by broad substring matching. That method made many categories appear far more universal than the source text justified.",
        "",
        "The corrected model separates:",
        "",
        "- objective chronology: Ethereum event timestamps and calendar quarters;",
        "- source-preserving editions: full, abridged, and ultra-brief;",
        "- overlapping descriptive categories: useful for search, but neither exclusive stages nor verified historical claims;",
        "- interpretive reading: explicitly provisional and revisable.",
        "",
        "## Overlapping interpretive arcs (non-exclusive)",
        "",
        "These are reading aids, not a periodization:",
        "",
        "1. Capability and model milestones.",
        "2. Reasoning, science, and medicine.",
        "3. Safety, alignment, governance, and control anxiety.",
        "4. Creative collaboration, cultural displacement, songs, poems, and artwork.",
        "5. Agents, autonomy, embodiment, and future-intelligence address.",
        "6. Human/family witness, memory, and Trinity Accord self-archival.",
        "",
        "## Calendar distribution",
        "",
    ])
    for period, count in sorted(period_counts.items()):
        context.append(f"- {period}: {count} entries")
    context.extend(["", "## Descriptive category counts", ""])
    for category, count in sorted(category_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        context.append(f"- **{category}**: {count}")
    context.extend([
        "",
        "## Embedded source material",
        "",
        f"- Entries with detected long source/document material: {len(embedded_entries)}",
        f"- Detected characters retained in the full edition but summarized in the abridged edition: {total_embedded_chars}",
        "- Detection is structural and conservative; absence from this count does not prove an entry contains no quotation or source material.",
        "",
        "## Timeline digest",
        "",
        "| # | Datetime | Name | Period | Categories | Digest |",
        "|---|---|---|---|---|---|",
    ])
    for item in processed:
        context.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | {item['calendar_period']} | {table_escape(', '.join(item['categories']) or 'none')} | {table_escape(item['brief'])} |"
        )
    context.extend(["", f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-agent-context.md").write_text("\n".join(context), encoding="utf-8")

    largest_embedded = sorted(
        embedded_entries,
        key=lambda item: item["abridgment"]["embedded_source_char_count"],
        reverse=True,
    )[:20]
    summary = {
        "schema": "trinityaccord.nft-chronicle-summary.v2",
        "total_entries": 175,
        "dated_entries": 175,
        "undated_entries": 0,
        "timeline_span": {"start_datetime": timeline_start, "end_datetime": timeline_end},
        "editions": EDITION_PATHS,
        "calendar_period_counts": dict(sorted(period_counts.items())),
        "category_counts": dict(sorted(category_counts.items(), key=lambda pair: (-pair[1], pair[0]))),
        "embedded_source_summary": {
            "entries_with_embedded_source_material": len(embedded_entries),
            "embedded_source_characters": total_embedded_chars,
            "largest_entries": [
                {
                    "ordinal": item["ordinal"],
                    "datetime": item["datetime"],
                    "name": item["name"],
                    "characters": item["abridgment"]["embedded_source_char_count"],
                    "titles": item["abridgment"]["embedded_source_titles"],
                }
                for item in largest_embedded
            ],
        },
        "interpretation_policy": interpretation_policy,
        "boundary": boundary_obj,
    }
    (DIR / "chronicle-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    for path in EDITION_PATHS.values():
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"NFT_CHRONICLE_GENERATION_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
