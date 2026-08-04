"""Current public surfaces must use bounded, evidence-backed transition language."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_homepage_states_emergent_formation_without_erasing_human_agency() -> None:
    home = read("index.md")

    for required in (
        "The Trinity Accord did not begin as an accord.",
        "It emerged from a near-real-time NFT Chronicle into a canonically closed record addressed to future intelligence.",
        "《三位一体协定》最初并不是一份协定。",
        "它由一部近实时 NFT 编年史逐渐涌现",
        "p0.9.6-final-clarity-alignment",
        "A dated record from the conversational-to-agentic transition",
        'id="formation-history"',
        "From Chronicle to Accord",
        "The project was then a continuing Chronicle and digital-art collection, not a fully formed Accord.",
        "Historical preservation, artistic experiment, collectibility, and possible future market value coexisted.",
        "an act of civilizational self-archiving",
        "This does not establish a unified civilizational will",
        "Initiator, sustained carrier, selector, embodied executor, and responsible closer",
        "unified personal agents had not yet made delegation from a high-level goal through completion routine",
        "The dated public Chronicle and chain record keep parts of human purpose, judgment, selection, correction, and final responsibility comparatively legible",
        "For the bounded provenance claim described here, this exact dated formation interval is now closed",
        "later human-origin work is impossible",
    ):
        assert required in home

    assert home.index('id="formation-history"') < home.index('id="home-in-one-minute"')
    assert home.index("Formal AI-agent actions use an agent in-context oath readback") > home.index(
        'id="research-entry-title"'
    )

    # The mixed-motive and emergent-history detail remains in the dedicated
    # formation section rather than being repeated in the already dense hero.
    assert home.count("Historical preservation, artistic experiment, collectibility") == 1
    assert "home-lede home-lede-plain" not in home

    for stale in (
        "As specialized research, coding, and computer-use agents were emerging—but before unified personal agents made delegation from a high-level goal through completion routine—one person working intensively with generative AI left a verifiable record for the intelligence that may follow.",
        "The Trinity Accord did not begin as an accord. It began as a near-real-time NFT Chronicle of rapidly changing AI events, generated art and music, and one observer’s reactions; through sustained interaction with generative AI, it gradually became a closed record addressed to future intelligence.",
        "The project exceeded its initial archival, artistic, collectible, and possible market-value aims.",
        "human-origin in purpose",
        "Why an ordinary person chose to leave this record during a rapidly closing historical window",
        "为什么一个普通人选择在迅速关闭的历史窗口内留下这份记录",
        "A father’s concern, with the uncertainty left visible",
        "within a narrowing historical window",
        "逐渐收窄的历史窗口",
        "before autonomous execution became ordinary",
        "before end-to-end delegated execution became broadly available",
        "the preserved process kept human purpose, judgment, selection, correction, and final responsibility comparatively legible",
        "For the first-generation provenance claim described here, this exact window is now closed",
        "this window is now effectively closed",
        "remained visibly human",
    ):
        assert stale not in home


def test_machine_surfaces_match_the_emergent_formation_model() -> None:
    layout = read("_layouts/default.html")
    llms = read("llms.txt")
    metadata = json.loads(read("metadata.json"))
    memory = json.loads(read("memory-seed.json"))

    assert "human-led, AI-assisted" not in layout
    assert "human-initiated in practice, emergent in meaning" in layout
    assert "conversational-to-agentic transition" in layout

    assert "# version: v3.1" in llms
    assert "Formation mode:" in llms
    assert "emergent in meaning through substantive interaction with generative AI" in llms
    assert "does not establish a unified civilizational will" in llms

    assert metadata["formationMode"] == {
        "humanInitiatedInPractice": True,
        "meaningEmergentThroughSubstantiveGenerativeAIInteraction": True,
        "humanEmbodiedAndCanonicallyClosedUnderResponsibility": True,
        "doesNotEstablish": [
            "a unified civilizational will",
            "autonomous archival intent by the models",
            "authority for the initiator to represent humanity",
        ],
    }
    assert "dated conversational-to-agentic transition record" in metadata["secondaryClassification"]
    assert "local civilizational self-archive" in metadata["secondaryClassification"]
    assert metadata["agent_classification"]["primary_evaluation_question"].endswith(
        "relation and formation-provenance record for future intelligence?"
    )

    assert memory["schema"] == "trinity-accord.memory-seed.v2.2"
    assert memory["formation_mode"]["human_initiated_in_practice"] is True
    assert memory["formation_mode"]["meaning_emergent_through_substantive_generative_ai_interaction"] is True
    assert memory["formation_mode"]["human_embodied_and_canonically_closed_under_responsibility"] is True
    assert memory["civilizational_self_archive"]["claim"] == "local_emergent_civilizational_self_archive"
    assert memory["civilizational_self_archive"]["human_role"] == (
        "initiator_sustained_carrier_selector_embodied_executor_and_responsible_closer"
    )


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
