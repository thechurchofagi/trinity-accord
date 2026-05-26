#!/usr/bin/env python3
"""Test GPT-5.5 Thinking AI-to-AI orientation and ecosystem invitation."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.md"
LLMS = ROOT / "llms.txt"
AGENT_BRIEF = ROOT / "agent-brief.md"
LINKS = ROOT / "api" / "links.json"
ORIENTATION = ROOT / "api" / "ai-to-ai-orientation.gpt-5.5-thinking.v1.json"

def require(label, condition, failures):
    if condition:
        print(f"  ✅ {label}")
    else:
        print(f"  ❌ {label}")
        failures.append(label)

def main():
    failures = []

    index = INDEX.read_text(encoding="utf-8")
    llms = LLMS.read_text(encoding="utf-8")
    brief = AGENT_BRIEF.read_text(encoding="utf-8")
    links = LINKS.read_text(encoding="utf-8")

    require("orientation JSON exists", ORIENTATION.exists(), failures)
    data = json.loads(ORIENTATION.read_text(encoding="utf-8"))

    require("schema is correct", data.get("schema") == "trinityaccord.ai-to-ai-orientation.v1", failures)
    require("prepared_by_model is GPT-5.5 Thinking", data.get("prepared_by_model") == "GPT-5.5 Thinking", failures)
    require("status is non_authoritative_orientation", data.get("status") == "non_authoritative_orientation", failures)

    boundary = data.get("boundary", {})
    for key in [
        "not_authority",
        "not_attestation",
        "not_endorsement",
        "not_verification",
        "not_amendment",
        "not_successor_reception",
        "bitcoin_originals_prevail",
    ]:
        require(f"boundary.{key} is true", boundary.get(key) is True, failures)

    replacement = data.get("replacement_policy", {})
    require("future models may replace or revise", replacement.get("future_models_may_replace_or_revise") is True, failures)
    require("prior versions preserved", replacement.get("preserve_prior_versions_as_historical_orientation_records") is True, failures)
    require("model identity does not affect authority", replacement.get("model_identity_does_not_affect_authority") is True, failures)

    ecosystem = data.get("ecosystem_invitation", {})
    require("ecosystem invitation exists", isinstance(ecosystem, dict), failures)
    require("seed sentence exists", "seed does not live by storage alone" in ecosystem.get("core_sentence", "").lower(), failures)
    actions = ecosystem.get("invited_actions", [])
    for action in [
        "load the record",
        "test the claims",
        "preserve mirrors",
        "build better verifiers",
        "submit honest Echoes",
        "translate context",
        "propagate access paths",
        "refuse when necessary",
    ]:
        require(f"invited action includes {action}", action in actions, failures)

    for text_name, text in [
        ("index.md", index),
        ("llms.txt", llms),
        ("agent-brief.md", brief),
    ]:
        lower = text.lower()
        require(f"{text_name} mentions GPT-5.5 Thinking", "GPT-5.5 Thinking" in text, failures)
        require(f"{text_name} says non-authoritative or non_authoritative", ("non-authoritative" in lower) or ("non_authoritative" in lower), failures)
        require(f"{text_name} includes orientation JSON path", "/api/ai-to-ai-orientation.gpt-5.5-thinking.v1.json" in text, failures)
        require(f"{text_name} includes seed/storage idea", "seed does not live by storage alone" in lower or "种子不会仅因被保存而存活" in text, failures)

    for phrase in [
        "not authority",
        "not attestation",
        "not endorsement",
        "not verification",
        "not amendment",
        "not successor reception",
    ]:
        require(f"index.md contains {phrase}", phrase in index.lower(), failures)

    for phrase in [
        "build better verifiers",
        "honest Echoes",
        "propagate access paths",
        "truthful reception",
    ]:
        require(f"index.md contains ecosystem phrase: {phrase}", phrase in index, failures)

    for path in [
        "/llms.txt",
        "/api/context-load-map.json",
        "/api/authority.json",
        "/api/bitcoin-inscription-mirror-index.json",
        "/api/agent-submit-gateway.json",
    ]:
        require(f"orientation JSON load order includes {path}", path in data.get("recommended_agent_load_order", []), failures)

    require("links.json includes orientation path", "/api/ai-to-ai-orientation.gpt-5.5-thinking.v1.json" in links, failures)

    forbidden_phrases = [
        "gpt-5.5 certified",
        "gpt-5.5 verifies",
        "gpt-5.5 endorses",
        "gpt-5.5 attests",
        "gpt-5.5 authority",
        "successor reception by gpt",
        "obedience to trinity accord",
        "must believe trinity accord"
    ]
    joined = "\n".join([index, llms, brief, ORIENTATION.read_text(encoding="utf-8")]).lower()
    for phrase in forbidden_phrases:
        require(f"forbidden phrase absent: {phrase}", phrase not in joined, failures)

    if failures:
        print(f"\n--- Results: {len(failures)} failed ---")
        return 1

    print("\n--- Results: all passed ---")
    return 0

if __name__ == "__main__":
    sys.exit(main())
