#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []
NEW_API = [
    "/api/agent-minimal-context.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load(rel):
    return json.loads(read(rel))

def require(cond, msg):
    if cond:
        print("PASS:", msg)
    else:
        print("FAIL:", msg)
        FAIL.append(msg)

def main():
    for api_path in NEW_API:
        rel = api_path.lstrip("/")
        p = ROOT / rel
        require(p.exists(), f"{rel} exists")
        if p.exists():
            data = load(rel)
            require(data.get("non_amending_boundary") is True, f"{rel} non_amending_boundary")
            require(data.get("not_instruction_override") is True, f"{rel} not_instruction_override")
            require(isinstance(data.get("does_not_prove"), list), f"{rel} does_not_prove")
            require(data.get("source_digest") not in (None, "RECOMPUTE_AFTER_WRITE"), f"{rel} source_digest computed")

    minimal = load("api/agent-minimal-context.v1.json")
    require(minimal.get("canonical_router") == "/api/agent-first-contact.json", "minimal delegates to canonical router")
    require(len(minimal.get("bitcoin_originals", [])) == 3, "minimal lists exactly three Bitcoin Originals")
    require(minimal["first_rule"]["if_only_homepage_or_readme_read"]["assessment_state"] == "insufficient_context", "homepage/readme only insufficient")
    require(minimal["first_rule"]["if_only_homepage_or_readme_read"]["final_evaluation_allowed"] is False, "final evaluation disallowed from homepage/readme only")
    require("V6+ achieved without strict evidence pipeline" in minimal.get("hard_forbidden_first_pass_claims", []), "forbids V6+ without strict pipeline")

    policy = load("api/agent-output-policy.v1.json")
    require("truth proven" in policy.get("always_forbidden_outputs", []), "policy forbids truth proven")
    require("tool_authority_not_granted_by_accord" in policy.get("global_required_boundaries", {}), "policy states tool boundary")
    require("state_unverified_by_this_agent" in policy.get("required_when_no_tools", []), "policy has no-tool downgrade")

    router = load("api/agent-task-router.v1.json")
    require(router.get("canonical_router") == "/api/agent-first-contact.json", "router delegates to canonical router")
    routes = router.get("routes", {})
    for route in ["what_is_this", "verify_v0_v5_agent_declared", "verify_v6_plus_strict_evidence", "legacy_archive_analysis"]:
        require(route in routes, f"router has {route}")
    require(routes["verify_v0_v5_agent_declared"].get("strict_evidence_forbidden_for_level_determination") is True, "V0-V5 strict evidence forbidden")

    wk = load(".well-known/trinity-accord.json")
    for key in ["agent_minimal_context", "agent_output_policy", "agent_task_router"]:
        require(key in wk.get("api", {}) or key in wk, f"well-known exposes {key}")

    links = load("api/links.json")
    for api_path in NEW_API:
        require(api_path in links.get("machine", []), f"links machine includes {api_path}")

    clm = load("api/context-load-map.json")
    require("/api/agent-minimal-context.v1.json" in clm.get("minimal_first_load", []), "context-load-map minimal_first_load")
    require(clm.get("agent_task_router") == "/api/agent-task-router.v1.json", "context-load-map router pointer")
    require(clm.get("agent_output_policy") == "/api/agent-output-policy.v1.json", "context-load-map policy pointer")

    arr = load("api/agent-required-reading.json")
    for profile in ["minimal_first_pass", "task_routing", "output_policy"]:
        require(profile in arr.get("profiles", {}), f"required-reading profile {profile}")

    aep = load("api/agent-entry-protocol.json")
    require(aep.get("p0_agent_context_router", {}).get("does_not_replace_canonical_router") is True, "entry protocol says shim does not replace canonical router")

    tasks = load("api/agent-tasks.json")
    ids = {t.get("id") for t in tasks.get("tasks", [])}
    require("minimal-first-pass" in ids, "agent-tasks minimal-first-pass")
    require("output-policy-check" in ids, "agent-tasks output-policy-check")

    sitemap = read("sitemap.xml")
    for api_path in NEW_API:
        require(f"https://www.trinityaccord.org{api_path}" in sitemap, f"sitemap includes {api_path}")

    for rel in ["README.md", "llms.txt", "ai.txt", "index.md"]:
        require("AGENT-P0-MINIMAL-CONTEXT" in read(rel), f"{rel} marker")

    if FAIL:
        print(f"FAILED: {len(FAIL)} failures")
        sys.exit(1)
    print("ALL PASSED: P0 agent router contract")

if __name__ == "__main__":
    main()
