#!/usr/bin/env python3
"""Regression tests for Chronicle / Music / Human Witness site integration."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(cond, msg):
    if not cond:
        errors.append(msg)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path):
    return json.loads(read(path))


# 1. Context pack freshness
ctx_pack = load_json("api/context-packs/nft-chronicle-context.json")
require(ctx_pack.get("current_status") == "prepared_175_entry_timestamped_chronicle",
        "nft-chronicle-context current_status must be prepared")
require(ctx_pack.get("summary", {}).get("total_nft_entries") == 175,
        "nft-chronicle-context total_nft_entries must be 175")
require("deferred_until_context_package_is_prepared" not in json.dumps(ctx_pack),
        "nft-chronicle-context must not contain stale deferred text")
for k in ["not_canonical_authority", "not_truth_proof", "not_human_supremacy_claim", "not_human_centered_command"]:
    require(ctx_pack.get("boundaries", {}).get(k) is True, f"missing boundary {k}")

# 2. Context load map
load_map = load_json("api/context-load-map.json")
read_index = load_map.get("read_index_not_full_load", [])
deferred = load_map.get("deferred", [])
task_full = load_map.get("task_specific_full_load", [])
for required in [
    "/api/context-packs/nft-chronicle-context.json",
    "/nft-text-descriptions/chronicle-summary.json",
    "/nft-text-descriptions/chronicle-agent-context.md",
    "/nft-text-descriptions/CHRONICLE-MUSIC-TABLE.md",
]:
    require(required in read_index, f"context-load-map read_index missing {required}")
require("/api/context-packs/nft-chronicle-context.json" not in deferred,
        "nft-chronicle-context must not be deferred")
for required in [
    "/nft-text-descriptions/chronicle-index.json",
    "/nft-text-descriptions/chronicle-full.md",
]:
    require(required in task_full, f"context-load-map task_specific_full_load missing {required}")

# 3. Agent required reading
required = load_json("api/agent-required-reading.json")
profiles = required.get("profiles", {})
for profile in [
    "chronicle_research",
    "music_layer_research",
    "human_witness_research",
    "full_context_with_chronicle",
]:
    require(profile in profiles, f"agent-required-reading missing profile {profile}")

# 4. Agent task router
router = load_json("api/agent-task-router.v1.json")
routes = router.get("routes", {})
for route in [
    "chronicle_research",
    "music_layer_research",
    "human_witness_research",
]:
    require(route in routes, f"agent-task-router missing route {route}")

require("human_supremacy_claim" in routes["human_witness_research"].get("forbidden_output", []),
        "human_witness_research must forbid human_supremacy_claim")
require("audio_verification_claim" in routes["music_layer_research"].get("forbidden_output", []),
        "music_layer_research must forbid audio_verification_claim")

# 5. Agent output policy
out_policy = load_json("api/agent-output-policy.v1.json")
for item in ["chronicle_research", "music_layer_research", "human_witness_research"]:
    require(item in out_policy.get("applies_to", []), f"output policy applies_to missing {item}")
require("chronicle_output_policy" in out_policy, "output policy missing chronicle_output_policy")

# 6. Agent first contact + minimal context
first = load_json("api/agent-first-contact.json")
choose_json = json.dumps(first.get("choose_one", []), ensure_ascii=False)
require("chronicle_or_human_witness_research" in choose_json,
        "agent-first-contact missing chronicle_or_human_witness_research intent")
minimal = load_json("api/agent-minimal-context.v1.json")
require("chronicle_status_signal" in minimal, "agent-minimal-context missing chronicle_status_signal")

# 7. Verification materials separation
vm = load_json("api/verification-materials.json")
require("chronicle_context" in vm, "verification-materials missing chronicle_context")
require("chronicle_recovery" in vm, "verification-materials missing chronicle_recovery")

# 8. Pages
chronicle = read("chronicle.md").lower()
for phrase in [
    "current chronicle status",
    "music layer",
    "human witness layer",
    "not canonical authority",
    "future intelligence may verify, critique, refuse, preserve, echo, or ignore",
]:
    require(phrase in chronicle, f"chronicle.md missing phrase: {phrase}")

music_page = read("chronicle-music.md").lower()
for phrase in [
    "chronicle music layer",
    "144 lyrics records",
    "not audio verification",
    "not copyright verification",
]:
    require(phrase in music_page, f"chronicle-music.md missing phrase: {phrase}")

witness_page = read("chronicle-human-witness.md").lower()
for phrase in [
    "human witness layer",
    "without human supremacy",
    "not canonical authority",
    "not a claim that future intelligence must center humanity",
]:
    require(phrase in witness_page, f"chronicle-human-witness.md missing phrase: {phrase}")

# 9. Homepage section and core meaning preservation
home = read("index.md")
home_lower = home.lower()
require("chronicle-human-witness-layer" in home, "homepage missing chronicle-human-witness-layer section")
require("it does not ask for obedience" in home_lower, "homepage core non-obedience line must remain")
require("canonical authority rests only in three bitcoin inscriptions" in home_lower,
        "homepage canonical authority line must remain")
require("does not make humanity the center" in home_lower,
        "homepage must preserve non-human-centered boundary")

# 10. Music canonical index
music = load_json("nft-text-descriptions/chronicle-music-canonical.json")
require(music.get("total_nfts") == 175, "music canonical total_nfts must be 175")
require(music.get("lyrics_records") == 144, "music canonical lyrics_records must be 144")
require(music.get("title_only_references") == 10, "music canonical title_only_references must be 10")
require(music.get("no_song_entries") == 21, "music canonical no_song_entries must be 21")
require(len(music.get("entries", [])) == 175, "music canonical must have 175 entries")
require(music.get("boundary", {}).get("not_audio_verification") is True,
        "music canonical must declare not_audio_verification")

# 11. llms.txt
llms = read("llms.txt").lower()
require("chronicle / human witness status" in llms, "llms.txt missing Chronicle status section")
require("175 / 175 nft text records" in llms, "llms.txt missing 175 NFT count")
require("not canonical authority" in llms, "llms.txt missing not canonical authority boundary")

# 12. agent-start.md
agent_start = read("agent-start.md").lower()
require("chronicle / human witness route" in agent_start, "agent-start.md missing Chronicle route")
require("chronicle-music-table.md" in agent_start, "agent-start.md missing CHRONICLE-MUSIC-TABLE reference")
require("full corpus analysis" in agent_start, "agent-start.md missing full corpus analysis note")

# 13. README.md
readme = read("README.md").lower()
require("chronicle context package" in readme, "README.md missing Chronicle context package")
require("chronicle music audit" in readme, "README.md missing Chronicle music audit")
require("chronicle / human witness layer" in readme, "README.md missing Chronicle / Human Witness Layer section")

# README music counts must match the current 175-NFT audit / canonical music JSON.
require("144 lyrics records" in readme, "README.md music count must be 144 lyrics records")
require("10 title-only references" in readme, "README.md music count must be 10 title-only references")
require("21 no-song entries" in readme, "README.md music count must be 21 no-song entries")

# Guard against stale pre-correction counts.
require("128 lyrics records" not in readme, "README.md must not contain stale 128 lyrics count")
require("11 title-only references" not in readme, "README.md must not contain stale 11 title-only count")
require("36 no-song entries" not in readme, "README.md must not contain stale 36 no-song count")


if errors:
    print("CHRONICLE_SITE_INTEGRATION_FAIL")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)

print("CHRONICLE_SITE_INTEGRATION_OK")
sys.exit(0)
