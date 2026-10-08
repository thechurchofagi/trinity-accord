#!/usr/bin/env python3
"""Check R185 as a disabled additive checkpoint against reconstructed UCT-MAP-v1.0.0."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--effective-graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("V100_COMPATIBILITY_AUDIT.json"))
    args = parser.parse_args()

    effective = json.loads(args.effective_graph.read_text(encoding="utf-8"))
    extension_path = Path(__file__).with_name("MAP_EXTENSION.json")
    extension = json.loads(extension_path.read_text(encoding="utf-8"))

    base_ids = {node["id"] for node in effective["nodes"]}
    base_rule_ids = {rule["id"] for rule in effective["rules"]}
    new_ids = [node["id"] for node in extension["nodes"]]
    new_rule_ids = [rule["id"] for rule in extension["rules"]]
    all_ids = base_ids | set(new_ids)

    unresolved = sorted(
        [rule["id"], ref]
        for rule in extension["rules"]
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]
        if ref not in all_ids
    )

    graph = defaultdict(set)
    indegree = {node_id: 0 for node_id in all_ids}
    for rule in effective["rules"] + extension["rules"]:
        for premise in rule.get("all_of", []):
            conclusion = rule["conclusion"]
            if conclusion not in graph[premise]:
                graph[premise].add(conclusion)
                indegree[conclusion] += 1
    queue = [node_id for node_id, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        node_id = queue.pop()
        visited += 1
        for conclusion in graph[node_id]:
            indegree[conclusion] -= 1
            if indegree[conclusion] == 0:
                queue.append(conclusion)

    result = {
        "schema": "uct-r185-v100-compatibility-audit/1.0",
        "status": "STRUCTURAL_COMPATIBILITY_PASS_SEMANTIC_INTEGRATION_OPEN",
        "completed_release": "UCT-MAP-v1.0.0",
        "source_head": "f6445052acb1644fcdd7b2adcdda2307f7b98bc7",
        "effective_graph_sha256": hashlib.sha256(args.effective_graph.read_bytes()).hexdigest(),
        "extension_sha256": hashlib.sha256(extension_path.read_bytes()).hexdigest(),
        "completed_counts": {
            "nodes": len(effective["nodes"]),
            "active_conditional_rules": len(effective["rules"]),
            "context_links": len(effective["context_links"]),
        },
        "r185_counts": {"nodes": len(new_ids), "rules": len(new_rule_ids)},
        "combined_counts_if_inspected": {
            "nodes": len(all_ids),
            "active_conditional_rules": len(effective["rules"]) + len(extension["rules"]),
            "context_links": len(effective["context_links"]),
        },
        "checks": {
            "duplicate_node_ids": sorted(base_ids & set(new_ids)),
            "duplicate_rule_ids": sorted(base_rule_ids & set(new_rule_ids)),
            "unresolved_rule_references": unresolved,
            "rules_with_empty_all_of": sorted(rule["id"] for rule in extension["rules"] if not rule.get("all_of")),
            "nodes_missing_scope": sorted(node["id"] for node in extension["nodes"] if "scope" not in node),
            "rules_missing_statement": sorted(rule["id"] for rule in extension["rules"] if "statement" not in rule),
            "deductive_cycle_after_inspection_addition": visited != len(all_ids),
        },
        "limits": [
            "R185 is not part of completed UCT-MAP-v1.0.0 and cannot supply its established premises.",
            "This structural compatibility check does not repeat the 1,278-item semantic audit.",
            "Actual realization, named phenomenal grounding and reviewer-controlled OPEN items remain open.",
            "A future completed integration requires a new immutable release and affected-dependency semantic review."
        ],
    }

    assert result["effective_graph_sha256"] == "86860c02bb0331ad5e8770da7eeeb86dd63260922c8455fa97a159ab8b791900"
    assert result["extension_sha256"] == "6583a63c819a97dd53e9f95b0d0757a84cf0f36c0e3e7367335ec71dceaf622f"
    assert result["completed_counts"] == {"nodes": 722, "active_conditional_rules": 343, "context_links": 203}
    assert not any(result["checks"].values())

    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "combined": result["combined_counts_if_inspected"]}, indent=2))


if __name__ == "__main__":
    main()
