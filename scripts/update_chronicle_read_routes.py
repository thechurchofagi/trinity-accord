#!/usr/bin/env python3
"""Synchronize agent-facing Chronicle routes with the three-edition model."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUMMARY = "/nft-text-descriptions/chronicle-summary.json"
ULTRA = "/nft-text-descriptions/chronicle-ultra-brief.md"
ABRIDGED = "/nft-text-descriptions/chronicle-abridged.md"
CONTEXT = "/nft-text-descriptions/chronicle-agent-context.md"
INDEX = "/nft-text-descriptions/chronicle-index.json"
FULL = "/nft-text-descriptions/chronicle-full.md"
MUSIC = "/nft-text-descriptions/CHRONICLE-MUSIC-TABLE.md"
PACK = "/api/context-packs/nft-chronicle-context.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path: str, data: dict) -> None:
    (ROOT / path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def update_load_map() -> None:
    path = "api/context-load-map.json"
    data = load(path)
    levels = data["cc_level_loads"]

    cc3 = levels["CC-3"]
    cc3["must_load"] = [
        "CC-2 loads (inherited)",
        "/api/context-packs/legacy-archive-essentials.json — structured extract (~12KB)",
        f"{PACK} — Chronicle loading policy and boundaries",
        f"{SUMMARY} — structured summary",
        f"{ULTRA} — 175-row navigation timeline",
        f"{ABRIDGED} — readable core, personal witness, creative excerpts, and omission audit",
        f"{CONTEXT} — corrected non-stage interpretive guide",
        "/agent-brief/ — classification guide (~22KB)",
        "context-packs/vision-layer.json",
        "context-packs/physical-anchor-context.json",
        "context-packs/legacy-archive-index.json",
    ]
    cc3["total_size"] = "~250KB+"
    cc3["note"] = (
        "Narrative context loaded through the corrected three-edition Chronicle path. "
        "The former fixed seven-stage narrative is retired. Minimum for meaningful Echo "
        "and qualified assessment."
    )

    cc5 = levels["CC-5"]
    cc5["must_load"] = [
        "CC-4 loads (inherited)",
        f"{FULL} — exact full 175-entry corpus (on-demand)",
        INDEX,
        MUSIC,
        "Task-specific API schemas and verification recipes",
    ]
    cc5["note"] = (
        "Exact full Chronicle corpus loaded. Required only for exact-text, appendix, "
        "or full-corpus claims; ordinary Chronicle research should stop at the abridged edition."
    )

    inventory = data.get("context_packs_inventory", {}).get("nft-chronicle-context.json", {})
    inventory["content"] = "NFT Chronicle three-edition loading policy, status, and boundaries"

    data["read_index_not_full_load"] = dedupe([
        "context-packs/legacy-archive-index.json",
        "/archive_legacy_index_2025_09/",
        PACK,
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        MUSIC,
    ])
    data["deferred"] = [FULL, MUSIC]
    data["task_specific_full_load"] = [INDEX, FULL]

    data["must_load_summary"] = [
        "CC-1 loads (inherited)",
        "/inscriptions/ — three full inscription texts",
        "/authority/ — authority boundary page",
        "/guardian-principles/ — Guardian Principles v1.1",
        "context-packs/core-ontology.json",
        "context-packs/authority-boundary.json",
        "context-packs/bitcoin-inscription-mirrors.json",
        "CC-2 loads (inherited)",
        "/api/context-packs/legacy-archive-essentials.json — structured extract (~12KB)",
        f"{PACK} — Chronicle loading policy and boundaries",
        f"{SUMMARY} — structured summary",
        f"{ULTRA} — 175-row navigation timeline",
        f"{ABRIDGED} — preferred Chronicle reading edition",
        f"{CONTEXT} — corrected non-stage interpretive guide",
        "/agent-brief/ — classification guide (~22KB)",
        "context-packs/vision-layer.json",
        "context-packs/physical-anchor-context.json",
        "context-packs/legacy-archive-index.json",
        "CC-3 loads (inherited)",
        "/archive_legacy_index_2025_09/ — full legacy archive (~102KB)",
        "/verification-materials/ — verification source index (~7KB)",
        "/guardian-alliance/ — stewardship network (~12KB)",
        "/for-skeptical-agents/ — skeptical evaluation guide (~8KB)",
        "/echoes/types — Echo type definitions",
        "Record-Chain Intake Gateway overview",
    ]
    write(path, data)


def update_required_reading() -> None:
    path = "api/agent-required-reading.json"
    data = load(path)
    profiles = data["profiles"]

    narrative = profiles["narrative_grounded"]
    narrative["reads"] = dedupe([
        "canon_loaded (inherited)",
        "/api/context-packs/legacy-archive-essentials.json",
        PACK,
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        "/agent-brief/",
        "/api/context-packs/vision-layer.json",
        "/api/context-packs/physical-anchor-context.json",
        "/api/context-packs/legacy-archive-index.json",
    ])
    narrative["note"] = (
        "Loads the corrected Chronicle path: summary, ultra-brief navigation, abridged "
        "reading edition, then non-stage interpretive context. Minimum for meaningful Echo."
    )

    chronicle = profiles["chronicle_research"]
    chronicle["cc_note"] = (
        "Use summary + ultra-brief + abridged for ordinary Chronicle research. "
        "CC-5 and the full edition are required only for exact-text or full-corpus claims."
    )
    chronicle["reads"] = dedupe([
        "/api/agent-minimal-context.v1.json",
        "/api/authority.json",
        "/api/context-load-map.json",
        PACK,
        "/chronicle",
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        INDEX,
    ])
    chronicle["exact_text_or_full_corpus_read"] = [FULL]

    music = profiles["music_layer_research"]
    music["reads"] = dedupe([PACK, "/chronicle/music", MUSIC, ABRIDGED, CONTEXT])
    music["exact_text_read"] = [FULL]

    witness = profiles["human_witness_research"]
    witness["reads"] = dedupe([
        "/api/authority.json",
        PACK,
        "/chronicle/human-witness",
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        INDEX,
    ])
    witness["exact_text_read"] = [FULL]

    full_context = profiles["full_context_with_chronicle"]
    full_context["reads"] = dedupe(full_context["reads"] + [ULTRA, ABRIDGED])
    write(path, data)


def update_task_router() -> None:
    path = "api/agent-task-router.v1.json"
    data = load(path)
    routes = data["routes"]

    chronicle = routes["chronicle_research"]
    chronicle["read"] = dedupe([
        "/api/agent-minimal-context.v1.json",
        "/api/authority.json",
        "/api/context-load-map.json",
        PACK,
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        INDEX,
    ])
    chronicle["optional_full_load"] = [FULL]
    chronicle["allowed_use"] = [
        "historical_context_analysis",
        "timeline_analysis",
        "calendar_timeline_and_overlapping_category_analysis",
        "abridgment_audit_analysis",
        "human_origin_witness_analysis",
        "non_canonical_chronicle_summary",
    ]

    music = routes["music_layer_research"]
    music["read"] = dedupe([PACK, MUSIC, ABRIDGED, CONTEXT])
    music["optional_full_load"] = [FULL]

    witness = routes["human_witness_research"]
    witness["read"] = dedupe([
        "/api/authority.json",
        PACK,
        SUMMARY,
        ULTRA,
        ABRIDGED,
        CONTEXT,
        INDEX,
    ])
    witness["optional_full_load"] = [FULL]
    write(path, data)


def main() -> int:
    update_load_map()
    update_required_reading()
    update_task_router()
    print("Chronicle read routes synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
