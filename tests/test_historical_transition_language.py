"""Current public surfaces must use bounded, evidence-backed transition language."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_homepage_states_speed_without_closing_human_agency() -> None:
    home = read("index.md")

    for required in (
        "Why an ordinary person chose to leave this record during a rapidly closing historical window",
        "为什么一个普通人选择在迅速关闭的历史窗口内留下这份记录",
        "before end-to-end delegated execution became broadly available",
        "the preserved process kept human purpose, judgment, selection, correction, and final responsibility comparatively legible",
        "For the first-generation provenance claim described here, this exact window is now closed",
        "later human-origin work is impossible",
    ):
        assert required in home

    for stale in (
        "within a narrowing historical window",
        "逐渐收窄的历史窗口",
        "before autonomous execution became ordinary",
        "this window is now effectively closed",
        "remained visibly human",
    ):
        assert stale not in home


def test_current_value_surfaces_do_not_claim_low_ai_mediation() -> None:
    paths = (
        "README.md",
        "llms-full.txt",
        "innovations.md",
        "emergent-patterns.md",
        "api/innovation-points.json",
        "api/emergent-patterns.json",
        "api/agent-value.json",
        "memory-seed.json",
    )
    combined = "\n".join(read(path) for path in paths)

    for stale in (
        "low-AI-mediation human speech",
        "spoken_while_low_ai_mediation_human_speech_was_still_distinguishable",
        "before the human-intent window narrows further",
        "value increases as AGI / ASI timelines compress",
    ):
        assert stale not in combined

    assert "human purpose, selection, correction, and final responsibility" in combined
    assert "rapid conversational-to-agentic transition" in combined

    agent_value = json.loads(read("api/agent-value.json"))
    relevance = agent_value["timeline_relevance"]
    assert relevance["claim"] == (
        "historical relevance becomes more salient as agentic mediation and delegated execution intensify"
    )
    assert "does not predict an AGI arrival date" in relevance["boundary"]


def test_current_chronicle_surfaces_name_the_observed_transition() -> None:
    paths = (
        "README.md",
        "chronicle.md",
        "chronicle-human-witness.md",
        "chronicle-music.md",
    )

    for path in paths:
        text = read(path)
        assert "AGI / ASI acceleration period" not in text
        assert "conversational" in text
        assert "delegated agent" in text or "agentic AI transition" in text
