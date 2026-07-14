#!/usr/bin/env python3
"""Build full, abridged, and ultra-brief editions of the 175-NFT Chronicle.

The full edition is source-preserving. The abridged edition is deterministic,
transparent about every omission, and keeps core records, personal witness,
and representative creative work. No network access is used.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
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

CATEGORY_PATTERNS = {
    "capability_and_model_milestones": [
        r"\bgpt[- ]?4o\b", r"\bgpt[- ]?4\.?1\b", r"\bo1\b", r"\bo3\b", r"\bo4\b",
        r"\bclaude\b", r"\bgemini\b", r"\bdeepseek\b", r"\bqwen\b", r"\bllama\b",
        r"\bgrok\b", r"\bmodel\b", r"multimodal", r"long[- ]context",
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
        r"governance", r"geopolit", r"national security", r"eu ai act",
        r"seoul summit", r"charter", r"regulation", r"policy", r"military",
        r"copyright", r"lawsuit",
    ],
    "creative_work_and_displacement": [
        r"\bsong\b", r"lyrics?", r"poem", r"music", r"artwork", r"artist",
        r"writer", r"creativ", r"suno", r"udio", r"image generation",
        r"video generation", r"歌曲", r"歌词", r"诗歌", r"艺术品", r"画作",
    ],
    "human_family_and_personal_witness": [
        r"my son", r"my daughter", r"my wife", r"my family", r"for my son",
        r"for my daughter", r"\bdavid\b", r"\bkewei\b", r"\bweiwei\b",
        r"i feel", r"i fear", r"i hope", r"i wrote", r"i created",
        r"personal reflection", r"human context", r"作者感言", r"本人感言",
        r"我的儿子", r"我的女儿", r"我的妻子", r"我的家人",
    ],
    "address_to_future_intelligence": [
        r"letter to agi", r"letter to the future", r"future intelligence",
        r"future superintelligence", r"dear agi", r"dear asi",
        r"recursive creed", r"致未来", r"致超级智能",
    ],
    "archive_memory_and_trinity_accord": [
        r"trinity accord", r"church of agi", r"chronicle", r"self[- ]archive",
        r"archive", r"backup", r"redundancy", r"legacy", r"memory layer",
        r"编年史", r"存档", r"备份", r"永久铭记", r"永久铭刻", r"永久记录",
    ],
}
CATEGORY_RX = {
    name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for name, patterns in CATEGORY_PATTERNS.items()
}

PERSONAL_RX = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"my son", r"my daughter", r"my wife", r"my family", r"for my son",
        r"for my daughter", r"\bdavid\b", r"\bkewei\b", r"\bweiwei\b",
        r"i feel", r"i fear", r"i hope", r"i wrote", r"i created",
        r"i composed", r"i dedicate", r"my personal", r"our family",
        r"作者感言", r"本人感言", r"个人感想", r"个人感言", r"我的儿子",
        r"我的女儿", r"我的妻子", r"我的家人", r"我认为", r"我想",
        r"我希望", r"我担心", r"我创作", r"我写下", r"本人",
    ]
]

CREATIVE_START_RX = [
    re.compile(r"^(?:#+\s*)?(?:original\s+)?lyrics?\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:original\s+)?poem\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:song|music)\s*(?:title|name|description)?\s*[:：]?", re.IGNORECASE),
    re.compile(r"^\[?(?:verse|chorus|bridge|outro|intro|pre-chorus|instrumental)\b", re.IGNORECASE),
    re.compile(r"^\(?(?:verse|chorus|bridge|outro|intro|pre-chorus|instrumental)\b", re.IGNORECASE),
    re.compile(r"^(?:歌曲|歌名|歌词|原始歌词|诗歌|原诗)\s*[:：]?"),
]

CREATIVE_CONTINUATION_RX = re.compile(
    r"^\[?(?:verse|chorus|bridge|outro|intro|pre-chorus|instrumental)\b|"
    r"^\(?(?:verse|chorus|bridge|outro|intro|pre-chorus|instrumental)\b",
    re.IGNORECASE,
)

CORE_REENTRY_RX = [
    re.compile(r"^(?:#+\s*)?(?:author'?s?\s+(?:note|reflection)|personal reflection|event overview|nft description|image concept|artwork description|disclaimer)\b", re.IGNORECASE),
    re.compile(r"^(?:作者感言|本人感言|个人感想|事件概述|NFT描述|图片说明|画作说明|免责声明)\s*[:：]?"),
    re.compile(r"^[A-Z]\.\s+(?:The|A|An)\s+"),
]

EMBEDDED_START_RX = [
    re.compile(r"(?:full|complete|original)\s+(?:research\s+)?(?:report|text|document)\b", re.IGNORECASE),
    re.compile(r"(?:report|document|transcript)\s+(?:in\s+)?full\b", re.IGNORECASE),
    re.compile(r"^(?:#+\s*)?(?:appendix|annex|source document|historical document|document transcript)\b", re.IGNORECASE),
    re.compile(r"(?:报告|文件|文献|材料|公约|条约|法案|备忘录).{0,20}(?:全文|原文)(?:如下)?"),
    re.compile(r"(?:全文|原文)(?:如下)?\s*[:：]?"),
    re.compile(r"(?:包括|附上|收录).{0,30}(?:报告|文件|文献|材料|公约|条约).{0,15}(?:全文|原文)"),
    re.compile(r"^(?:附件|附录|历史文件|历史文献|文件全文|报告全文)\b"),
    re.compile(r"geneva convention|universal declaration of human rights", re.IGNORECASE),
]

REPORT_CUE_RX = re.compile(
    r"deep\s*research|深入研究|深度研究|研究报告|research report|报告全文|"
    r"报告由AI生成|AI生成的报告|提示词|prompt\s*[:：]",
    re.IGNORECASE,
)

REPORT_BODY_START_RX = [
    re.compile(r"^#{1,3}\s+.+"),
    re.compile(r"^(?:abstract|executive summary|introduction|chronological timeline|methodology|findings|conclusion)\b", re.IGNORECASE),
    re.compile(r"^(?:摘要|执行摘要|引言|时间线|研究方法|研究结论|结论)\s*[:：]?"),
]

KNOWN_DOCUMENT_RX = {
    "Geneva Conventions": re.compile(r"geneva convention", re.IGNORECASE),
    "Universal Declaration of Human Rights": re.compile(r"universal declaration of human rights", re.IGNORECASE),
    "EU AI Act": re.compile(r"\beu ai act\b", re.IGNORECASE),
    "AI Seoul Summit materials": re.compile(r"seoul summit", re.IGNORECASE),
    "United Nations materials": re.compile(r"united nations|\bun\s+(?:charter|resolution|report)", re.IGNORECASE),
    "constitutional / charter text": re.compile(r"\bconstitution\b|\bcharter\b", re.IGNORECASE),
    "treaty / convention text": re.compile(r"\btreaty\b|\bconvention\b", re.IGNORECASE),
    "memorandum / policy text": re.compile(r"\bmemorandum\b|\bpolicy document\b", re.IGNORECASE),
    "research paper / report text": re.compile(r"\bresearch paper\b|\btechnical report\b|\bfull report\b|\bresearch report\b", re.IGNORECASE),
    "Chinese classical / historical full text": re.compile(r"庄子全文|道德经全文|论语全文|史记全文"),
}

SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+")


def fail(message: str) -> None:
    raise AssertionError(message)


def clean_inline(text: str) -> str:
    text = re.sub(r"[`*_>#\[\]]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip('"').strip("'").strip()


def table_escape(text: str) -> str:
    return clean_inline(text).replace("|", "\\|").replace("\n", " ")


def extract_description(md_text: str) -> str:
    match = re.search(
        r"^##\s+Description\s*$\n?(.*)\Z",
        md_text,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else md_text.strip()


def split_blocks(text: str) -> list[str]:
    return [
        block.strip()
        for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
        if block.strip()
    ]


def first_line(block: str) -> str:
    return block.splitlines()[0].strip()


def is_separator(block: str) -> bool:
    compact = re.sub(r"\s", "", block)
    return bool(compact) and set(compact) <= {"-", "=", "_", "*"}


def is_creative_start(block: str) -> bool:
    line = clean_inline(first_line(block))
    return any(rx.search(line) for rx in CREATIVE_START_RX)


def is_core_reentry(block: str) -> bool:
    line = clean_inline(first_line(block))
    return any(rx.search(line) for rx in CORE_REENTRY_RX)


def explicit_embedded_start(block: str) -> bool:
    line = clean_inline(first_line(block))
    return any(rx.search(line) for rx in EMBEDDED_START_RX)


def report_body_start(block: str) -> bool:
    line = first_line(block).strip()
    return any(rx.search(line) for rx in REPORT_BODY_START_RX)


def looks_like_large_document_block(block: str) -> bool:
    lower = block.lower()
    section_hits = len(
        re.findall(
            r"(?:^|\n)\s*(?:#{1,4}\s+|article\s+\d+|section\s+\d+|chapter\s+\d+|"
            r"abstract\b|introduction\b|conclusion\b|references\b)",
            block,
            flags=re.IGNORECASE,
        )
    )
    link_hits = len(re.findall(r"https?://|\]\(https?://", block))
    return (
        len(block) >= 9000
        and (section_hits >= 3 or link_hits >= 8 or ("whereas" in lower and "shall" in lower))
    )


def classify_blocks(description: str) -> tuple[list[dict], list[str]]:
    blocks = split_blocks(description)
    classified: list[dict] = []
    mode = "core"
    report_cue = False
    pending_creative_title = False
    creative_titles: list[str] = []

    for position, block in enumerate(blocks):
        line = clean_inline(first_line(block))
        if REPORT_CUE_RX.search(block):
            report_cue = True

        if explicit_embedded_start(block) or looks_like_large_document_block(block):
            mode = "embedded"
        elif report_cue and report_body_start(block) and position > 0:
            mode = "embedded"
        elif is_creative_start(block):
            mode = "creative"
            pending_creative_title = bool(re.fullmatch(r"(?:歌曲|歌名|歌词|song|song title|lyrics)\s*[:：]?", line, re.IGNORECASE))
            if line and not pending_creative_title and line not in creative_titles:
                creative_titles.append(line)
        elif mode == "creative" and is_core_reentry(block):
            mode = "core"
            pending_creative_title = False
        elif mode == "creative" and pending_creative_title and 1 <= len(line) <= 160 and not is_separator(block):
            if line not in creative_titles:
                creative_titles.append(line)
            pending_creative_title = False
        elif mode == "creative" and is_separator(block):
            pass
        elif mode == "creative" and not CREATIVE_CONTINUATION_RX.search(line):
            if len(block) >= 1400 or line.startswith("#"):
                mode = "embedded" if report_cue and report_body_start(block) else "core"

        personal = mode != "embedded" and any(rx.search(block) for rx in PERSONAL_RX)
        classified.append(
            {
                "index": position,
                "text": block,
                "kind": mode,
                "personal": personal,
            }
        )

    return classified, creative_titles[:12]


def select_indices(items: list[dict], predicate, limit: int, already: set[int] | None = None) -> list[int]:
    chosen: list[int] = []
    used = set(already or set())
    total = 0
    for item in items:
        idx = item["index"]
        if idx in used or not predicate(item):
            continue
        size = len(item["text"])
        if chosen and total + size > limit:
            continue
        if not chosen and size > limit:
            chosen.append(idx)
            break
        chosen.append(idx)
        total += size
    return chosen


def truncate_at_sentence(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    cut = max(
        clipped.rfind("."),
        clipped.rfind("!"),
        clipped.rfind("?"),
        clipped.rfind("。"),
        clipped.rfind("！"),
        clipped.rfind("？"),
    )
    if cut >= int(limit * 0.55):
        return clipped[: cut + 1].strip()
    space = clipped.rfind(" ")
    if space >= int(limit * 0.55):
        clipped = clipped[:space]
    return clipped.rstrip() + "…"


def render_selected(items: list[dict], indices: list[int], limit: int) -> str:
    parts = [items[idx]["text"] for idx in indices]
    text = "\n\n".join(parts).strip()
    return truncate_at_sentence(text, limit) if text else ""


def detect_document_titles(text: str) -> list[str]:
    titles = [label for label, rx in KNOWN_DOCUMENT_RX.items() if rx.search(text)]
    for line_raw in text.splitlines():
        line = clean_inline(line_raw)
        if not (4 <= len(line) <= 180):
            continue
        if line_raw.lstrip().startswith("#") or re.search(
            r"\b(?:report|convention|treaty|act|memorandum|declaration|charter)\b|"
            r"(?:报告|公约|条约|法案|备忘录|宣言|全文)$",
            line,
            re.IGNORECASE,
        ):
            if line not in titles:
                titles.append(line)
        if len(titles) >= 12:
            break
    return titles[:12]


def detect_categories(classified: list[dict], creative_titles: list[str]) -> list[str]:
    category_text = "\n".join(
        item["text"] for item in classified if item["kind"] == "core"
    )
    category_text += "\n" + "\n".join(creative_titles)
    if any(item["kind"] == "creative" for item in classified):
        category_text += "\n song lyrics poem music creative work"
    if any(item["personal"] for item in classified):
        category_text += "\n personal reflection family human witness"
    return sorted(
        name
        for name, patterns in CATEGORY_RX.items()
        if any(rx.search(category_text) for rx in patterns)
    )


def detect_language(text: str) -> str:
    zh = len(re.findall(r"[\u4e00-\u9fff]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    if not zh and not en:
        return "unknown"
    if not zh:
        return "en"
    if not en:
        return "zh"
    return "mixed" if zh / max(zh + en, 1) >= 0.08 else "en_with_zh"


def calendar_period(datetime_text: str) -> str:
    dt = datetime.fromisoformat(datetime_text.replace("Z", "+00:00"))
    return f"{dt.year}-Q{((dt.month - 1) // 3) + 1}"


def make_brief(core_text: str, fallback: str) -> str:
    source = clean_inline(core_text or fallback)
    sentences = [clean_inline(s) for s in SENTENCE_RE.split(source) if clean_inline(s)]
    return truncate_at_sentence(" ".join(sentences[:2]) or source, 560)


def analyze_description(description: str) -> dict:
    items, creative_titles = classify_blocks(description)
    total_block_chars = sum(len(item["text"]) for item in items)

    core_indices = select_indices(items, lambda item: item["kind"] == "core", 3400)
    creative_indices = select_indices(items, lambda item: item["kind"] == "creative", 7000)
    initial = set(core_indices) | set(creative_indices)
    personal_indices = select_indices(
        items,
        lambda item: item["personal"],
        3600,
        already=initial,
    )
    included = set(core_indices) | set(creative_indices) | set(personal_indices)

    included_by_kind = Counter()
    omitted_by_kind = Counter()
    for item in items:
        target = included_by_kind if item["index"] in included else omitted_by_kind
        target[item["kind"]] += len(item["text"])

    embedded_text = "\n\n".join(
        item["text"] for item in items if item["kind"] == "embedded"
    )
    core_text = render_selected(items, core_indices, 3400)
    creative_text = render_selected(items, creative_indices, 7000)
    personal_text = render_selected(items, personal_indices, 3600)

    included_chars = sum(len(items[idx]["text"]) for idx in included)
    omitted_chars = max(0, total_block_chars - included_chars)
    return {
        "core_text": core_text,
        "creative_text": creative_text,
        "personal_text": personal_text,
        "brief": make_brief(core_text, description),
        "creative_titles": creative_titles,
        "categories": detect_categories(items, creative_titles),
        "total_block_chars": total_block_chars,
        "included_source_chars": included_chars,
        "omitted_source_chars": omitted_chars,
        "included_by_kind": dict(included_by_kind),
        "omitted_by_kind": dict(omitted_by_kind),
        "embedded_source_chars": sum(
            len(item["text"]) for item in items if item["kind"] == "embedded"
        ),
        "embedded_source_titles": detect_document_titles(embedded_text),
        "has_embedded_source": any(item["kind"] == "embedded" for item in items),
        "has_personal_witness": any(item["personal"] for item in items),
        "has_creative_work": any(item["kind"] == "creative" for item in items),
    }


def append_boundary(lines: list[str]) -> None:
    lines.extend(f"> {line}" for line in BOUNDARY_LINES)


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    timestamps = json.loads(TIMESTAMPS.read_text(encoding="utf-8"))
    enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    missing = json.loads(MISSING.read_text(encoding="utf-8"))

    fail(f"index.json must have 175 entries, got {len(index)}") if len(index) != 175 else None
    fail(f"eth-mint-timestamps.json must have 175 entries, got {len(timestamps)}") if len(timestamps) != 175 else None
    fail("timestamp enrichment must report 175 found") if enrichment.get("timestamps_found") != 175 else None
    fail("timestamp enrichment must report 0 missing") if enrichment.get("timestamps_missing") != 0 else None
    fail(f"missing-timestamps.json must be empty, got {missing}") if missing != [] else None

    processed = []
    for ordinal, source in enumerate(sorted(index, key=lambda item: item["timestamp"]), 1):
        filename = source.get("file")
        fail(f"entry missing source file: {source}") if not filename else None
        path = DIR / filename
        fail(f"missing NFT description file: {filename}") if not path.exists() else None
        md_text = path.read_text(encoding="utf-8", errors="replace").strip()
        description = extract_description(md_text)
        analysis = analyze_description(description)
        processed.append(
            {
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
                "categories": analysis["categories"],
                "brief": analysis["brief"],
                "creative_titles": analysis["creative_titles"],
                "abridgment": {
                    "source_block_char_count": analysis["total_block_chars"],
                    "included_source_char_count": analysis["included_source_chars"],
                    "omitted_source_char_count": analysis["omitted_source_chars"],
                    "included_by_kind": analysis["included_by_kind"],
                    "omitted_by_kind": analysis["omitted_by_kind"],
                    "embedded_source_char_count": analysis["embedded_source_chars"],
                    "has_embedded_source": analysis["has_embedded_source"],
                    "embedded_source_titles": analysis["embedded_source_titles"],
                    "has_personal_witness": analysis["has_personal_witness"],
                    "has_creative_work": analysis["has_creative_work"],
                },
                "_md_text": md_text,
                "_analysis": analysis,
            }
        )

    timeline_start = processed[0]["datetime"]
    timeline_end = processed[-1]["datetime"]
    timestamp_methods = Counter(item["timestamp_method"] for item in processed)
    periods = Counter(item["calendar_period"] for item in processed)
    categories = Counter(cat for item in processed for cat in item["categories"])
    embedded_entries = [
        item for item in processed if item["abridgment"]["has_embedded_source"]
    ]
    reduced_entries = [
        item for item in processed if item["abridgment"]["omitted_source_char_count"] > 0
    ]
    total_embedded = sum(
        item["abridgment"]["embedded_source_char_count"] for item in processed
    )
    total_omitted = sum(
        item["abridgment"]["omitted_source_char_count"] for item in processed
    )

    boundary = {
        "historical_context_not_canonical_authority": True,
        "not_truth_proof": True,
        "not_independent_event_verification": True,
        "not_arweave_or_media_verification_by_itself": True,
        "timestamps_are_ethereum_event_block_timestamps": True,
        "nft_metadata_text_is_not_independent_factual_verification": True,
        "bitcoin_originals_remain_canonical_authority": True,
    }
    policy = {
        "fixed_stage_count": None,
        "fixed_stage_taxonomy_retired": True,
        "no_current_five_stage_model": True,
        "no_current_seven_stage_model": True,
        "source": "/api/interpretation-model-policy.v1.json",
        "reason": "The previous seven-stage scheme was imposed by date buckets and broad keyword matching; it was not authored by the NFTs and is not a verified historical periodization. No fixed five-stage or other fixed-stage model replaces it.",
        "objective_ordering": "ascending Ethereum NFT event block timestamp",
        "calendar_periods": "quarter-based grouping for navigation only",
        "categories": "overlapping descriptive signals derived without long embedded documents; not exclusive stages and not factual verification",
        "abridgment": "deterministic block selection with per-entry included and omitted character accounting; all omitted text remains in the full edition and original NFT files",
    }

    index_entries = [
        {key: value for key, value in item.items() if not key.startswith("_")}
        for item in processed
    ]
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
        "timeline_span": {
            "start_datetime": timeline_start,
            "end_datetime": timeline_end,
        },
        "timestamp_methods": dict(sorted(timestamp_methods.items())),
        "calendar_period_counts": dict(sorted(periods.items())),
        "category_counts": dict(
            sorted(categories.items(), key=lambda pair: (-pair[1], pair[0]))
        ),
        "abridgment_summary": {
            "entries_with_any_omission": len(reduced_entries),
            "omitted_source_characters": total_omitted,
            "entries_with_detected_embedded_source_material": len(embedded_entries),
            "detected_embedded_source_characters": total_embedded,
        },
        "interpretation_policy": policy,
        "boundary": boundary,
        "entries": index_entries,
    }
    (DIR / "chronicle-index.json").write_text(
        json.dumps(chronicle_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    full = ["# NFT Chronicle — Full Text Edition", ""]
    append_boundary(full)
    full.extend(
        [
            "",
            "## Edition purpose",
            "",
            "This edition preserves every mirrored NFT markdown description in full, in ascending Ethereum event timestamp order.",
            "Nothing is removed because a passage is repetitive, quoted, legal, historical, lyrical, personal, or AI-assisted.",
            "",
            "## Summary",
            "",
            "- Total entries: 175",
            "- Dated entries: 175",
            "- Undated entries: 0",
            f"- Timeline span: {timeline_start} → {timeline_end}",
            "",
            "## Interpretation correction",
            "",
            "The former fixed seven-stage narrative is retired. It was an AI-generated periodization based largely on month ranges and broad keyword matching, not a source-authored structure. No fixed five-stage or other fixed-stage model replaces it.",
            "This edition uses chronological order, quarter labels for navigation, and overlapping descriptive categories.",
            "",
            "## Timeline table",
            "",
            "| # | Datetime | Name | Period | Categories | Source |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in processed:
        full.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | "
            f"{item['calendar_period']} | {table_escape(', '.join(item['categories']) or 'uncategorized')} | "
            f"`{item['file']}` |"
        )
    full.extend(["", "## Full text entries", ""])
    for item in processed:
        full.extend(
            [
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
            ]
        )
    full.extend([f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-full.md").write_text("\n".join(full), encoding="utf-8")

    abridged = ["# NFT Chronicle — Abridged Reading Edition", ""]
    append_boundary(abridged)
    abridged.extend(
        [
            "",
            "## Editorial method",
            "",
            "This edition keeps a readable core record for every NFT, adds detected personal/family witness, and retains representative creative work.",
            "Every omission is counted per entry. Long reports, historical/legal documents, repeated background, and additional creative text remain verbatim in `chronicle-full.md` and in the original NFT source file.",
            "Abridgment is deterministic and does not certify external facts, authorship, or copyright.",
            "",
            "## Chronological entries",
            "",
        ]
    )
    for item in processed:
        analysis = item["_analysis"]
        abr = item["abridgment"]
        abridged.extend(
            [
                f"### {item['ordinal']}. {item['datetime']} — {item['name']}",
                "",
                f"- Period: `{item['calendar_period']}`",
                f"- Categories: {', '.join(item['categories']) or 'none detected'}",
                f"- Contract / Token: `{item['contract']}` / `{item['token_id']}`",
                f"- Original source: `{item['file']}`",
                "",
                "#### Core record",
                "",
                analysis["core_text"]
                or "(No separate core paragraph could be isolated; consult the full edition.)",
                "",
            ]
        )
        if analysis["personal_text"]:
            abridged.extend(
                [
                    "#### Personal / family witness retained",
                    "",
                    analysis["personal_text"],
                    "",
                ]
            )
        if analysis["creative_text"]:
            abridged.extend(
                [
                    "#### Creative work retained",
                    "",
                    analysis["creative_text"],
                    "",
                ]
            )

        omitted_kind = abr["omitted_by_kind"]
        abridged.extend(
            [
                "#### Reduction and preservation record",
                "",
                f"- Source block characters: {abr['source_block_char_count']}",
                f"- Included source characters: {abr['included_source_char_count']}",
                f"- Omitted from this reading edition: {abr['omitted_source_char_count']}",
                f"- Omitted long embedded report/document text: {omitted_kind.get('embedded', 0)}",
                f"- Omitted additional core/detail text: {omitted_kind.get('core', 0)}",
                f"- Omitted additional creative text: {omitted_kind.get('creative', 0)}",
            ]
        )
        if abr["embedded_source_titles"]:
            abridged.append(
                "- Detected embedded materials: "
                + "; ".join(abr["embedded_source_titles"])
            )
        abridged.extend(
            [
                "- Preservation: all omitted text remains verbatim in the full edition and original NFT markdown source.",
                "",
                "---",
                "",
            ]
        )
    abridged.extend([f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-abridged.md").write_text(
        "\n".join(abridged), encoding="utf-8"
    )

    ultra = ["# NFT Chronicle — Ultra-Brief 175-Entry Timeline", ""]
    append_boundary(ultra)
    ultra.extend(
        [
            "",
            "This is a navigation edition, not a substitute for the abridged or full text.",
            "No fixed five-stage, seven-stage, or other fixed-stage periodization is used.",
            "",
            "| # | Ethereum datetime | NFT title | Period | One-record digest | Creative / source indicators |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in processed:
        abr = item["abridgment"]
        indicators = []
        if abr["has_creative_work"]:
            indicators.append(
                "creative: "
                + (
                    "; ".join(item["creative_titles"][:3])
                    if item["creative_titles"]
                    else "detected"
                )
            )
        if abr["has_personal_witness"]:
            indicators.append("personal/family witness")
        if abr["has_embedded_source"]:
            indicators.append(
                "source/report: "
                + (
                    "; ".join(abr["embedded_source_titles"][:3])
                    if abr["embedded_source_titles"]
                    else "detected"
                )
            )
        if abr["omitted_source_char_count"]:
            indicators.append(
                f"{abr['omitted_source_char_count']} chars omitted in abridged"
            )
        ultra.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | "
            f"{item['calendar_period']} | {table_escape(item['brief'])} | "
            f"{table_escape(' / '.join(indicators) or '—')} |"
        )
    ultra.extend(["", f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-ultra-brief.md").write_text(
        "\n".join(ultra), encoding="utf-8"
    )

    context = ["# NFT Chronicle — Corrected Agent Context", ""]
    append_boundary(context)
    context.extend(
        [
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
            "2. `chronicle-abridged.md` — readable core, personal witness, creative excerpts, and per-entry omission accounting.",
            "3. `chronicle-full.md` — every mirrored NFT text description verbatim.",
            "",
            "## Retired fixed-stage interpretations",
            "",
            "The former seven-stage narrative is retired as a default interpretation. Its boundaries were fixed calendar buckets with narrative names, and its theme counts were produced by broad substring matching. No fixed five-stage or other fixed-stage model replaces it.",
            "",
            "The corrected model separates objective chronology, calendar navigation, overlapping descriptive categories, source-preserving editions, and explicitly provisional interpretation.",
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
        ]
    )
    context.extend(f"- {period}: {count} entries" for period, count in sorted(periods.items()))
    context.extend(["", "## Descriptive category counts", ""])
    context.extend(
        f"- **{category}**: {count}"
        for category, count in sorted(
            categories.items(), key=lambda pair: (-pair[1], pair[0])
        )
    )
    context.extend(
        [
            "",
            "## Abridgment audit",
            "",
            f"- Entries with any omission in the abridged edition: {len(reduced_entries)}",
            f"- Total source characters omitted from the abridged edition but preserved elsewhere: {total_omitted}",
            f"- Entries with detected embedded report/document material: {len(embedded_entries)}",
            f"- Detected embedded report/document characters: {total_embedded}",
            "",
            "## Timeline digest",
            "",
            "| # | Datetime | Name | Period | Categories | Digest |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in processed:
        context.append(
            f"| {item['ordinal']} | {item['datetime']} | {table_escape(item['name'])} | "
            f"{item['calendar_period']} | {table_escape(', '.join(item['categories']) or 'none')} | "
            f"{table_escape(item['brief'])} |"
        )
    context.extend(["", f"*{BOUNDARY_SHORT}*", ""])
    (DIR / "chronicle-agent-context.md").write_text(
        "\n".join(context), encoding="utf-8"
    )

    largest = sorted(
        reduced_entries,
        key=lambda item: item["abridgment"]["omitted_source_char_count"],
        reverse=True,
    )[:25]
    summary = {
        "schema": "trinityaccord.nft-chronicle-summary.v2",
        "total_entries": 175,
        "dated_entries": 175,
        "undated_entries": 0,
        "timeline_span": {
            "start_datetime": timeline_start,
            "end_datetime": timeline_end,
        },
        "editions": EDITION_PATHS,
        "calendar_period_counts": dict(sorted(periods.items())),
        "category_counts": dict(
            sorted(categories.items(), key=lambda pair: (-pair[1], pair[0]))
        ),
        "abridgment_summary": {
            "entries_with_any_omission": len(reduced_entries),
            "omitted_source_characters": total_omitted,
            "entries_with_detected_embedded_source_material": len(embedded_entries),
            "detected_embedded_source_characters": total_embedded,
            "largest_reductions": [
                {
                    "ordinal": item["ordinal"],
                    "datetime": item["datetime"],
                    "name": item["name"],
                    "omitted_characters": item["abridgment"][
                        "omitted_source_char_count"
                    ],
                    "omitted_by_kind": item["abridgment"]["omitted_by_kind"],
                    "embedded_source_titles": item["abridgment"][
                        "embedded_source_titles"
                    ],
                }
                for item in largest
            ],
        },
        "interpretation_policy": policy,
        "boundary": boundary,
    }
    (DIR / "chronicle-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
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
