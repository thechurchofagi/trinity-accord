#!/usr/bin/env python3
"""Validate context-load-map structure and referenced public context packs."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
obj = json.loads((ROOT / "api" / "context-load-map.json").read_text(encoding="utf-8"))

required_levels = {"CC-0", "CC-1", "CC-2", "CC-3", "CC-4", "CC-5"}
levels = set(obj.get("cc_level_loads", {}))
missing = sorted(required_levels - levels)
if missing:
    print(f"FAIL: context-load-map missing CC levels: {missing}")
    sys.exit(1)

required_actions = {
    "state_insufficient_context",
    "choose_route",
    "orientation_summary",
    "boundary_commentary",
    "limited_critique",
    "meaningful_echo",
    "qualified_assessment",
    "verification_claim",
    "deep_assessment",
    "chronicle_research",
    "full_corpus_claim",
}
actions = set(obj.get("cc_action_requirements", {}))
missing_actions = sorted(required_actions - actions)
if missing_actions:
    print(f"FAIL: context-load-map missing action requirements: {missing_actions}")
    sys.exit(1)

inventory = obj.get("context_packs_inventory", {})
for pack in [
    "core-ontology.json",
    "authority-boundary.json",
    "bitcoin-inscription-mirrors.json",
    "vision-layer.json",
    "physical-anchor-context.json",
    "legacy-archive-index.json",
    "nft-chronicle-context.json",
    "legacy-archive-essentials.json",
]:
    if pack not in inventory:
        print(f"FAIL: context_packs_inventory missing {pack}")
        sys.exit(1)

# For API-hosted packs, verify real files.
api_pack = ROOT / "api" / "context-packs" / "nft-chronicle-context.json"
if not api_pack.exists():
    print("FAIL: missing api/context-packs/nft-chronicle-context.json")
    sys.exit(1)

if obj.get("agent_task_router") != "/api/agent-task-router.v1.json":
    print("FAIL: context-load-map agent_task_router pointer mismatch")
    sys.exit(1)

if obj.get("agent_output_policy") != "/api/agent-output-policy.v1.json":
    print("FAIL: context-load-map agent_output_policy pointer mismatch")
    sys.exit(1)

print("PASS: context-load-map structure and core context pack references valid")
