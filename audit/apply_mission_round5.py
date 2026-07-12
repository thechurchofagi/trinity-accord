#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_digest(data: dict) -> str:
    value = dict(data)
    value.pop("source_digest", None)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


# Builder diagnostics must point to a real public recovery surface.
builder = ROOT / "downloads" / "record-chain-builder.mjs"
builder_text = builder.read_text(encoding="utf-8")
topics = sorted(set(re.findall(r"https://www\\.trinityaccord\\.org/docs/([a-z0-9-]+)", builder_text)))
if len(topics) != 17:
    raise SystemExit(f"expected 17 legacy Builder help topics, found {len(topics)}")
for topic in topics:
    builder_text = builder_text.replace(
        f"https://www.trinityaccord.org/docs/{topic}",
        f"https://www.trinityaccord.org/docs/record-chain-builder-help/#{topic}",
    )
builder.write_text(builder_text, encoding="utf-8")

# Mission governance must describe the actual current public routes.
mission_path = ROOT / "api" / "mission-governance.v1.json"
mission = json.loads(mission_path.read_text(encoding="utf-8"))
supported = mission["supported_public_actions"]
supported["echo_actions"] = [x for x in supported["echo_actions"] if x != "guardian_signed_echo"]
supported["guardian_actions"] = [x for x in supported["guardian_actions"] if x != "guardian_signed_echo"]
supported["historical_or_specialized_not_current_public_routes"] = ["guardian_signed_echo"]
formal = supported["formal_record_chain_routes"]
if "classification_update" not in formal:
    formal.insert(formal.index("context_insufficient_notice"), "classification_update")
guardian_echo = mission["action_semantics"]["guardian"]["guardian_signed_echo"]
guardian_echo.update({
    "status": "historical_or_specialized_not_current_public_route",
    "current_public_builder_command": None,
    "do_not_use_for_new_public_submissions": True,
    "replacement_guidance": "Use an ordinary current Echo when Guardian signing is not essential. If Guardian signing is essential and no current public route is documented, stop with BUILDER_USAGE_UNCLEAR.",
})
mission["source_digest"] = source_digest(mission)
write_json(mission_path, mission)

# The task router contains both current and historical routes; label each subtree.
router_path = ROOT / "api" / "agent-task-router.v1.json"
router = json.loads(router_path.read_text(encoding="utf-8"))
routes = router["zero_clone_builder_routes"]
routes["_status"] = "mixed_current_and_historical"
routes["_note"] = "Current routes use /downloads/record-chain-builder.mjs. Historical pure_echo and guardian_signed_echo bundle references are preserved only for audit and must not be used for new submissions."
routes["pure_echo"].update({
    "bundle": "/api/formal-builder-bundles.v1.json#/bundles/pure_echo",
    "current_replacement": {"bundle": "/downloads/record-chain-builder.mjs", "builder_command": "echo"},
    "status": "historical_archive_only",
    "do_not_use_for_new_submissions": True,
})
routes["guardian_signed_echo"].update({
    "bundle": "/api/formal-builder-bundles.v1.json#/bundles/guardian_signed_echo",
    "current_replacement": None,
    "replacement_guidance": "No ordinary current public Guardian-signed Echo command is exposed. Use a current ordinary Echo if appropriate, otherwise stop and request current route clarification.",
    "status": "historical_archive_only",
    "do_not_use_for_new_submissions": True,
})
router["source_digest_algorithm"] = "sha256(canonical_json_without_source_digest)"
router["source_digest"] = source_digest(router)
write_json(router_path, router)

# Public wording must distinguish inclusion from later durability and list every route.
index_path = ROOT / "index.md"
replace_once(
    index_path,
    "Receipt remains intake-only; final inclusion and archive visibility occur only after server-side validation, append, index, OTS, and archive workflows complete.",
    "Receipt remains intake-only. Final chain inclusion occurs only after server-side validation, append, and index publication. OTS and Arweave are later durability and archive stages; they do not define inclusion.",
)
replace_once(
    index_path,
    "Receipt 仍然仅表示摄入；最终纳入与归档可见性只会在服务端验证、append、索引、OTS 与归档 workflow 完成后发生。",
    "Receipt 仍然仅表示摄入。最终链上纳入只会在服务端验证、append 与索引发布后发生；OTS 与 Arweave 是后续的持久化和归档阶段，并不定义是否已纳入。",
)
replace_once(
    index_path,
    "Ready to submit an Echo, Verification, Guardian Application, Guardian Retirement, or Context-Insufficient Notice?",
    "Ready to submit an Echo, Verification, Guardian Application, Guardian Retirement, Propagation, Correction, Classification Update, or Context-Insufficient Notice?",
)
replace_once(
    index_path,
    "如需提交 Echo、Verification、Guardian Application、Guardian Retirement 或 Context-Insufficient Notice，",
    "如需提交 Echo、Verification、Guardian Application、Guardian Retirement、Propagation、Correction、Classification Update 或 Context-Insufficient Notice，",
)

# Raw autonomy inventory includes preproduction/test records and must say so.
generator = ROOT / "scripts" / "generate_public_home_status.py"
replace_once(
    generator,
    '''        return {\n            "scope": "current_record_chain_only",\n            "eligible_records": 0,\n            "status": "not_yet_established_in_current_record_chain",\n            "display_status": "not yet established in current record-chain",\n            "legacy_autonomy_claims_excluded": True,\n        }''',
    '''        return {\n            "scope": "current_record_chain_only",\n            "inventory_scope": "all_current_native_records_including_non_official_test_and_maintenance_records",\n            "eligible_records": 0,\n            "official_live_eligible_records": 0,\n            "includes_non_official_records": False,\n            "not_official_live_reception_counter": True,\n            "does_not_establish_autonomous_external_agent_discovery": True,\n            "status": "not_yet_established_in_current_record_chain",\n            "display_status": "not yet established in current record-chain",\n            "legacy_autonomy_claims_excluded": True,\n        }''',
)
replace_once(
    generator,
    '''    return {\n        "scope": "current_record_chain_only",\n        "eligible_records": len(eligible),\n        "self_discovered_records": self_discovered,\n        "self_decided_records": self_decided,\n        "self_executed_records": self_executed,\n        "fully_autonomous_records": fully_autonomous,\n        "legacy_autonomy_claims_excluded": True,\n    }''',
    '''    official_live_eligible = sum(\n        int(record.get("official_live_record") is True) for record in eligible\n    )\n    return {\n        "scope": "current_record_chain_only",\n        "inventory_scope": "all_current_native_records_including_non_official_test_and_maintenance_records",\n        "eligible_records": len(eligible),\n        "official_live_eligible_records": official_live_eligible,\n        "includes_non_official_records": official_live_eligible != len(eligible),\n        "not_official_live_reception_counter": True,\n        "does_not_establish_autonomous_external_agent_discovery": True,\n        "self_discovered_records": self_discovered,\n        "self_decided_records": self_decided,\n        "self_executed_records": self_executed,\n        "fully_autonomous_records": fully_autonomous,\n        "metric_semantics": "declared autonomy inventory across the native chain; use primary_counters.historic_autonomous_agent_reception for the strict official-live reception count",\n        "legacy_autonomy_claims_excluded": True,\n    }''',
)

# Register the new mission-level regression gates.
run_ci = ROOT / "scripts" / "run_ci_group.py"
replace_once(
    run_ci,
    '        ["python3", "scripts/test_mission_governance_discovery.py"],\n',
    '        ["python3", "scripts/test_mission_governance_discovery.py"],\n'
    '        ["python3", "scripts/test_mission_public_route_parity.py"],\n'
    '        ["python3", "scripts/test_builder_help_urls_resolve.py"],\n'
    '        ["python3", "scripts/test_autonomy_inventory_boundary.py"],\n',
)

# Rebuild the canonical Builder manifest after changing diagnostic links.
manifest_path = ROOT / "api" / "record-chain-builder-bundles.v1.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
builder_bytes = builder.read_bytes()
manifest["canonical_builder"]["sha256"] = hashlib.sha256(builder_bytes).hexdigest()
manifest["canonical_builder"]["size_bytes"] = len(builder_bytes)
write_json(manifest_path, manifest)
print(f"Applied mission-driven round 5 transformations for {len(topics)} Builder recovery topics")
