#!/usr/bin/env python3
"""Structural compatibility audit for the disabled A3U candidate.

This reuses frozen completed-map proofs; it does not certify semantic truth.
"""
import argparse, gzip, hashlib, json
from collections import defaultdict, deque
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads(args.base.read_text())
    ledger = json.loads(args.ledger.read_text())
    extension = json.loads(args.extension.read_text())

    base_nodes = {item["id"] for item in base["nodes"]}
    new_nodes = {item["id"] for item in extension["nodes"]}
    all_nodes = base_nodes | new_nodes
    unresolved = []
    graph = defaultdict(set)
    indegree = {node: 0 for node in all_nodes}
    for rule in base["rules"] + extension["rules"]:
        refs = list(rule["all_of"]) + [rule["conclusion"]]
        if any(ref not in all_nodes for ref in refs):
            unresolved.append(rule["id"])
        for premise in rule["all_of"]:
            conclusion = rule["conclusion"]
            if premise in all_nodes and conclusion in all_nodes and conclusion not in graph[premise]:
                graph[premise].add(conclusion)
                indegree[conclusion] += 1
    for ctx in base["context_links"] + extension["context_links"]:
        for field in ("from", "to"):
            ref = ctx.get(field, ctx.get({"from": "source", "to": "target"}[field]))
            ref_type = ctx.get(field + "_type", ctx.get({"from": "source_type", "to": "target_type"}[field], "node"))
            nonnode = ref_type in ("source_reference", "module_reference", "module", "external_source") or (field == "from" and bool(ctx.get("external_source")))
            if ref not in all_nodes and not nonnode:
                unresolved.append(ctx["id"])
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for child in graph[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    checks = {
        "base_release": base["version"] == "UCT-MAP-v1.1.2",
        "base_counts": tuple(len(base[key]) for key in ("nodes", "rules", "context_links")) == (913, 424, 261),
        "suspended_rules": len(base["suspended_historical_rule_ids"]) == 10,
        "review_count": len(ledger["items"]) == 1608,
        "base_hash": sha(args.base) == "0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612",
        "ledger_hash": sha(args.ledger) == "0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687",
        "candidate_disabled": extension["integration_status"] == "PENDING_CHECKPOINT_DISABLED" and not extension["enabled_as_established_premise"],
        "completed_release_unchanged": extension["release_effect"].startswith("NONE"),
        "candidate_counts": tuple(len(extension[key]) for key in ("nodes", "rules", "context_links")) == (7, 3, 5),
        "unique_new_nodes": len(new_nodes) == len(extension["nodes"]),
        "no_node_collision": not base_nodes & new_nodes,
        "typed_scoped_nodes": all(all(node.get(field) for field in ("kind", "statement", "scope", "quantifier", "status")) for node in extension["nodes"]),
        "all_rules_are_conjunctive": all(len(rule["all_of"]) >= 2 for rule in extension["rules"]),
        "same_instance_guards": all(rule["same_instance_required"] and rule["binding"] for rule in extension["rules"]),
        "proof_and_alternative_fields": all(rule["proof_location"] and rule["alternative_route_semantics"] for rule in extension["rules"]),
        "references_resolve": not unresolved,
        "combined_dag_acyclic": visited == len(all_nodes),
        "c1_axiom_preserved": any(link["to"] == "A:C1" and link["type"] == "AXIOM_STATUS_PRESERVED" for link in extension["context_links"]),
        "no_new_basal_gate": any(link["to"] == "A:U1" and link["type"] == "NON_GATE_CONTEXT" for link in extension["context_links"]),
        "actual_use_evidence_separated": any(link["to"] == "R166:EVIDENCE_LEVEL_LADDER" for link in extension["context_links"]),
        "actual_application_open": all(not node["enabled_as_established_premise"] for node in extension["nodes"]),
        "assistant_verdict_absent": all("current assistant" not in node["statement"].lower() for node in extension["nodes"])
    }

    coverage = []
    for kind in ("nodes", "rules", "context_links"):
        for item in base[kind]:
            encoded = json.dumps(item, sort_keys=True, ensure_ascii=False).encode()
            coverage.append({
                "id": item["id"],
                "kind": kind,
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "scope": "FROZEN_BASE_UNCHANGED; structural references checked; prior proof/review inherited",
                "semantic_status": "NO_NEW_END_TO_END_SEMANTIC_PROOF",
                "current_effect": "NONE_FROM_DISABLED_A3U"
            })
    review_ids = [item.get("id", item.get("item_id")) for item in ledger["items"]]
    result = {
        "schema": "uct-a3u-map-audit/1",
        "base_sha256": sha(args.base),
        "ledger_sha256": sha(args.ledger),
        "counts": {"nodes": 913, "rules": 424, "contexts": 261, "suspended": 10, "review_items": len(review_ids)},
        "candidate_counts": {"nodes": 7, "rules": 3, "contexts": 5},
        "checks": checks,
        "all_structural_checks_pass": all(checks.values()),
        "unresolved": unresolved,
        "semantic_adoption": "OPEN; FULL_NEW_SEMANTIC_REPROOF_NOT_COMPLETED",
        "inherited_coverage": "Every completed node/rule/context has stable-ID content-hash coverage; frozen proofs are reused, not newly reproved.",
        "affected_rederivation": "A3P's downstream-endpoint gate is narrowed: endpoint independence and region controls do not discharge causal exclusion. C1/U1, evidence/use separation and all open review items remain unchanged.",
        "integration": "PENDING_CHECKPOINT_DISABLED"
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    coverage_payload = {"items": coverage, "review_item_ids": review_ids, "semantic_limit": result["semantic_adoption"]}
    args.output.with_name("WHOLE_MAP_COVERAGE.json.gz").write_bytes(gzip.compress((json.dumps(coverage_payload, separators=(",", ":")) + "\n").encode(), mtime=0))
    print(json.dumps({"structural_pass": result["all_structural_checks_pass"], "checks": len(checks), "covered_objects": len(coverage), "review_items": len(review_ids), "semantic_adoption": "OPEN"}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
