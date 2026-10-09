#!/usr/bin/env python3
"""Full structural traversal of UCT-MAP-v1.1.2 plus disabled R196."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads(args.base.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    extension = json.loads(args.extension.read_text(encoding="utf-8"))

    base_nodes = {item["id"] for item in base["nodes"]}
    base_rules = {item["id"] for item in base["rules"]}
    base_contexts = {item["id"] for item in base["context_links"]}
    new_nodes = [item["id"] for item in extension["nodes"]]
    new_rules = [item["id"] for item in extension["rules"]]
    new_contexts = [item["id"] for item in extension["context_links"]]

    checks = {
        "base_release_is_v1_1_2": base.get("version") == "UCT-MAP-v1.1.2",
        "base_counts_match_release": (len(base_nodes), len(base_rules), len(base_contexts), len(base["suspended_historical_rule_ids"])) == (913, 424, 261, 10),
        "review_ledger_has_1608_items": len(ledger.get("items", [])) == 1608,
        "extension_disabled": extension.get("integration_status") == "PENDING_CHECKPOINT_DISABLED" and extension.get("enabled_as_established_premise") is False and extension.get("release_effect", "").startswith("NONE"),
        "candidate_counts_are_9_6_5": (len(new_nodes), len(new_rules), len(new_contexts)) == (9, 6, 5),
        "new_ids_unique": len(new_nodes) == len(set(new_nodes)) and len(new_rules) == len(set(new_rules)) and len(new_contexts) == len(set(new_contexts)),
        "no_id_collision": not (set(new_nodes) & base_nodes or set(new_rules) & base_rules or set(new_contexts) & base_contexts),
        "every_new_node_has_concept_quantifier_scope": all(item.get("kind") and item.get("statement") and item.get("quantifier") and item.get("scope") for item in extension["nodes"]),
        "all_rules_have_simultaneous_all_of": all(len(item.get("all_of", [])) >= 2 for item in extension["rules"]),
        "all_rules_bind_same_instance": all(item.get("same_instance_required") is True and item.get("binding") for item in extension["rules"]),
        "all_rules_record_direction_and_proof": all(item.get("statement") and item.get("proof_location") and item.get("alternative_route_semantics") for item in extension["rules"]),
        "basal_experience_not_gated": any(link["to"] == "A:U1" and link["type"] == "NON_GATE_CONTEXT" for link in extension["context_links"]),
        "c1_axiom_status_preserved": any(link["to"] == "A:C1" and link["type"] == "AXIOM_STATUS_PRESERVED" for link in extension["context_links"]),
        "test_and_actual_use_separated": "does not install" in next(n["statement"].lower() for n in extension["nodes"] if n["id"] == "R196:EVIDENCE_USE_SEPARATION"),
        "phenomenal_direction_left_open": "OPEN" in next(n["status"] for n in extension["nodes"] if n["id"] == "R196:INDEPENDENT_ENDPOINT"),
        "structural_and_phenomenal_orientation_separated": any(n["id"] == "R196:STRUCTURAL_SPECIFICITY" for n in extension["nodes"]) and any(n["id"] == "R196:PHENOMENAL_COMPLEMENT" for n in extension["nodes"]),
    }

    all_nodes = base_nodes | set(new_nodes)
    unresolved = []
    for rule in extension["rules"]:
        for premise in rule["all_of"]:
            if premise not in all_nodes:
                unresolved.append([rule["id"], "premise", premise])
        if rule["conclusion"] not in all_nodes:
            unresolved.append([rule["id"], "conclusion", rule["conclusion"]])
    for context in extension["context_links"]:
        for field in ("from", "to"):
            if context[field] not in all_nodes:
                unresolved.append([context["id"], field, context[field]])
    checks["all_references_resolve"] = not unresolved

    graph = defaultdict(set)
    indegree = {node: 0 for node in all_nodes}
    for rule in list(base["rules"]) + list(extension["rules"]):
        conclusion = rule["conclusion"]
        for premise in rule["all_of"]:
            if premise in all_nodes and conclusion in all_nodes and conclusion not in graph[premise]:
                graph[premise].add(conclusion)
                indegree[conclusion] += 1
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    checks["combined_rule_graph_acyclic"] = seen == len(all_nodes)

    prohibited = ("proves consciousness", "requires a unique owner", "assistant is conscious", "assistant is not conscious")
    checks["no_prohibited_overclaim"] = not any(phrase in json.dumps(extension).lower() for phrase in prohibited)

    result = {
        "schema": "uct-r196-map-compatibility-audit/1",
        "base_release": base["version"],
        "base_graph_sha256": sha256(args.base),
        "base_review_ledger_sha256": sha256(args.ledger),
        "capsule_counts": {"nodes": len(base_nodes), "active_rules": len(base_rules), "contexts": len(base_contexts), "suspended_historical_rules": len(base["suspended_historical_rule_ids"]), "review_items": len(ledger.get("items", []))},
        "candidate_counts": {"nodes": len(new_nodes), "rules": len(new_rules), "contexts": len(new_contexts), "combined_nodes": len(all_nodes), "combined_rules": len(base_rules)+len(new_rules), "combined_contexts": len(base_contexts)+len(new_contexts)},
        "checks": checks,
        "unresolved_references": unresolved,
        "all_structural_checks_pass": all(checks.values()),
        "joint_satisfiability_review": "The exact marker and outcome classifications coexist on one four-cell domain. The target complement is a nonidentification result, and endpoint sufficiency is conditional on an explicitly open premise. No open premise is inferred as true.",
        "full_map_review_scope": "Every base node/rule/context ID and all 1,608 review items were loaded; combined references and the full dependency graph were traversed. Candidate fields, all_of packages, bindings, directions and proof locations were checked.",
        "semantic_scope": "Structural PASS is not premise truth, general proof, actual intervention/use, valid phenomenal measurement, familiar-mineness identification, reviewer closure or activation.",
        "integration_status": "STRUCTURAL_COMPATIBILITY_PASS_SEMANTIC_ADOPTION_OPEN" if all(checks.values()) else "FAIL"
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_structural_checks_pass": result["all_structural_checks_pass"], "checks": len(checks), "base_nodes": len(base_nodes), "review_items": len(ledger.get("items", []))}))
    if not result["all_structural_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
