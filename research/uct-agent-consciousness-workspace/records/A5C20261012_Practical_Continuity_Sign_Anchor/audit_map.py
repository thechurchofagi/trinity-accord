#!/usr/bin/env python3
"""Fresh structural and bounded semantic audit for A5C."""

import gzip
import hashlib
import io
import json
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(root_arg, restored_arg):
    root = Path(root_arg)
    graph_path = root / "UCT_FORMAL_GRAPH.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    effective = json.loads(Path(restored_arg).read_text(encoding="utf-8"))["completed_graph"]
    nodes, rules, contexts = effective["nodes"], effective["rules"], effective["context_links"]
    node_ids = {node["id"] for node in nodes}
    assert len(node_ids) == len(nodes)

    per_id = []
    for node in nodes:
        scope = node.get("scope") or node.get("domain")
        contract = next((v for k, v in reversed(list(node.items())) if k.startswith("formal_contract") and isinstance(v, dict)), {})
        per_id.append({
            "id": node["id"], "kind": node.get("kind"), "status": node.get("status"),
            "has_statement": bool(node.get("statement")), "has_scope_or_domain": bool(scope),
            "has_explicit_quantifier_text_or_scoped_contract": bool(contract.get("quantifiers") or contract.get("quantifier_convention") or scope),
            "review": "STRUCTURAL_FIELDS_ACCESSED_NOT_GLOBAL_SEMANTIC_REPROOF",
        })

    unresolved, nonlists, empty = [], [], []
    adjacency = {node_id: [] for node_id in node_ids}
    for rule in rules:
        deps = rule.get("all_of")
        if not isinstance(deps, list):
            nonlists.append(rule["id"]); continue
        if not deps: empty.append(rule["id"])
        conclusion = rule.get("conclusion")
        if conclusion not in node_ids: unresolved.append({"rule": rule["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in node_ids: unresolved.append({"rule": rule["id"], "role": "premise", "id": dep})
            elif conclusion in adjacency: adjacency[dep].append(conclusion)

    visiting, visited, cycles = set(), set(), []
    def dfs(node, stack):
        if node in visiting:
            cycles.append(stack[stack.index(node):] + [node]); return
        if node in visited: return
        visiting.add(node)
        for child in adjacency.get(node, []): dfs(child, stack + [child])
        visiting.remove(node); visited.add(node)
    for node_id in node_ids: dfs(node_id, [node_id])

    result = {
        "schema": "a5c-map-audit/1",
        "root_graph_sha256": sha(graph_path), "restored_effective_graph_sha256": sha(restored_arg),
        "root_counts": {key: len(graph[key]) for key in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": nonlists, "rules_with_empty_all_of": empty,
        "unresolved_deductive_references": unresolved, "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "a5c_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "a5c_joint_satisfiability": {
            "orientation_witness": {"transport": "S_c=S_t", "orientations_without_anchor": [[0,0],[1,1]], "with_positive_anchor": [[0,0]]},
            "route_witness": {"joint_edges": [[0,0],[1,0],[0,1],[1,1]], "distributed_edges": [[0,0],[1,1]], "different_orbits": True},
            "actuality_claimed": False,
        },
        "affected_semantic_nodes": ["A:P3", "A:P6", "A:C1", "A:U1", "A:PHEN_TARGET", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R166:EVIDENCE_LEVEL_LADDER", "R172:EXPERIENCE_INTERNAL_ACTION_COORDINATE", "R173:FAMILIAR_MINENESS_BOUNDARY"],
        "semantic_scope": "Fresh structural traversal plus bounded manual review of C1/U1, P3/P6, R157, R166, R172, effective R173, R181, R197, R203, A3Y/A3Z and A4V-A5B; not a full historical semantic reproof.",
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE",
    }
    assert not nonlists and not unresolved and not cycles and not empty
    out = Path(__file__).parent
    (out / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "PER_ID_AUDIT.json.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8") as stream:
                json.dump(per_id, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"status": result["status"], "effective_counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
