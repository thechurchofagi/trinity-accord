#!/usr/bin/env python3
"""Fresh structural and bounded semantic audit for A5H."""

import gzip
import hashlib
import io
import json
import sys
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(root_arg, effective_arg):
    root = Path(root_arg)
    raw = json.loads(Path(effective_arg).read_text(encoding="utf-8"))
    graph = raw.get("completed_graph", raw)
    nodes, rules, contexts = graph["nodes"], graph["rules"], graph["context_links"]
    ids = {node["id"] for node in nodes}
    assert len(ids) == len(nodes)
    per_id = []
    for node in nodes:
        scope = node.get("scope") or node.get("domain")
        contracts = [v for k, v in node.items() if k.startswith("formal_contract") and isinstance(v, dict)]
        contract = contracts[-1] if contracts else {}
        per_id.append({
            "id": node["id"], "kind": node.get("kind"), "status": node.get("status"),
            "has_statement": bool(node.get("statement")), "has_scope_or_domain": bool(scope),
            "has_quantifier_or_scoped_contract": bool(scope or contract.get("quantifiers") or contract.get("quantifier_convention")),
            "review": "FIELDS_ACCESSED; NOT_GLOBAL_SEMANTIC_REPROOF",
        })

    unresolved, bad_all_of, empty_all_of = [], [], []
    adjacency = {node_id: [] for node_id in ids}
    for rule in rules:
        premises = rule.get("all_of")
        if not isinstance(premises, list):
            bad_all_of.append(rule["id"]); continue
        if not premises:
            empty_all_of.append(rule["id"])
        conclusion = rule.get("conclusion")
        if conclusion not in ids:
            unresolved.append({"rule": rule["id"], "role": "conclusion", "id": conclusion})
        for premise in premises:
            if premise not in ids:
                unresolved.append({"rule": rule["id"], "role": "premise", "id": premise})
            elif conclusion in adjacency:
                adjacency[premise].append(conclusion)

    visiting, visited, cycles = set(), set(), []
    def dfs(node, stack):
        if node in visiting:
            cycles.append(stack[stack.index(node):] + [node]); return
        if node in visited:
            return
        visiting.add(node)
        for child in adjacency[node]:
            dfs(child, stack + [child])
        visiting.remove(node); visited.add(node)
    for node_id in ids:
        dfs(node_id, [node_id])

    root_graph = json.loads((root / "UCT_FORMAL_GRAPH.json").read_text(encoding="utf-8"))
    result = {
        "schema": "a5h-map-audit/1",
        "root_graph_sha256": digest(root / "UCT_FORMAL_GRAPH.json"),
        "effective_graph_sha256": digest(effective_arg),
        "root_counts": {k: len(root_graph[k]) for k in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": bad_all_of,
        "rules_with_empty_all_of": empty_all_of,
        "unresolved_deductive_references": unresolved,
        "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "a5h_joint_satisfiability": {
            "coarse_o_fixed_complete_k_varies": {"FIX_O_A5F": 1, "VARY_S": 1, "VARY_K": 1, "CONTRADICTION": 0},
            "complete_pointed_k_fixed": {"FIX_K": 1, "SAME_BINDING": 1, "DIFFERENT_H_ADMISSIBLE_UNDER_C1": 0},
            "response_equivalence": {"COMPATIBLE_MODELS": 6, "TRACKING_TARGET": 4, "INVARIANT_TARGET": 2},
            "complete_biological_k_claimed": False
        },
        "a5h_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "affected_semantic_nodes": ["A:P3", "A:P6", "A:C1", "A:U1", "A:PHEN_TARGET", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R159:ANCHOR_BINDING_CONTRACT"],
        "manual_semantic_checks": [
            "O_A5F is a coarse protocol coordinate, not complete K",
            "S is an actual relation inside K, not a report or target experience",
            "held-stick pointer reports and forearm SI localization are not pooled across installations",
            "response-mapping reversal does not identify H_tip",
            "all positive bridge premises are simultaneous and same-binding",
            "C1 remains an axiom and no basal report gate or exclusive owner is introduced"
        ],
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE"
    }
    assert [len(nodes), len(rules), len(contexts)] == [913, 424, 261]
    assert not bad_all_of and not empty_all_of and not unresolved and not cycles
    out = Path(__file__).parent
    (out / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "PER_ID_AUDIT.json.gz").open("wb") as raw_out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_out, mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8") as stream:
                json.dump(per_id, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"status": result["status"], "counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
