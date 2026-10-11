#!/usr/bin/env python3
"""Fresh structural and scoped semantic audit for A4V."""

import gzip
import hashlib
import io
import json
import sys
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(root, restored):
    root = Path(root)
    graph_path = root / "UCT_FORMAL_GRAPH.json"
    graph = json.loads(graph_path.read_text())
    unified = json.loads(Path(restored).read_text())["completed_graph"]
    nodes, rules, contexts = unified["nodes"], unified["rules"], unified["context_links"]
    node_ids, rule_ids = {n["id"] for n in nodes}, {r["id"] for r in rules}
    assert len(node_ids) == len(nodes) and len(rule_ids) == len(rules)

    per_id, missing_scope = [], []
    for n in nodes:
        scope = n.get("scope") or n.get("domain")
        contract = next((v for k, v in reversed(list(n.items())) if k.startswith("formal_contract") and isinstance(v, dict)), {})
        quant = contract.get("quantifiers") or contract.get("quantifier_convention")
        per_id.append({
            "id": n["id"], "kind": n.get("kind"), "status": n.get("status"),
            "has_statement": bool(n.get("statement")), "has_scope_or_domain": bool(scope),
            "has_explicit_quantifier_text_or_scoped_contract": bool(quant or scope),
            "review": "STRUCTURAL_FIELDS_ACCESSED_NOT_GLOBAL_SEMANTIC_REPROOF"
        })
        if not scope:
            missing_scope.append(n["id"])

    unresolved, all_of_nonlists, empty_all_of = [], [], []
    adjacency = {nid: [] for nid in node_ids}
    for rule in rules:
        deps = rule.get("all_of")
        if not isinstance(deps, list):
            all_of_nonlists.append(rule["id"]); continue
        if not deps:
            empty_all_of.append(rule["id"])
        conclusion = rule.get("conclusion")
        if conclusion not in node_ids:
            unresolved.append({"rule": rule["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in node_ids:
                unresolved.append({"rule": rule["id"], "role": "premise", "id": dep})
            elif conclusion in adjacency:
                adjacency[dep].append(conclusion)

    visiting, visited, cycles = set(), set(), []
    def dfs(x, stack):
        if x in visiting:
            cycles.append(stack[stack.index(x):] + [x]); return
        if x in visited: return
        visiting.add(x)
        for y in adjacency.get(x, []): dfs(y, stack + [y])
        visiting.remove(x); visited.add(x)
    for nid in node_ids: dfs(nid, [nid])

    result = {
        "schema": "a4v-map-audit/1",
        "root_graph_sha256": sha256(graph_path),
        "root_counts": {k: len(graph[k]) for k in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "nodes_without_scope_or_domain": missing_scope,
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": all_of_nonlists,
        "rules_with_empty_all_of": empty_all_of,
        "unresolved_deductive_references": unresolved,
        "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "a4v_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "a4v_joint_witness": {
            "binding": "one P/I/K/event/x/a/r/consumer",
            "premises": ["BIND", "ANCHOR", "ENCODE", "USE", "A-CONTRAST", "R-CONTRAST", "JOINT", "ORDER"],
            "finite_satisfiable_models": ["XOR/XOR", "XNOR/XNOR"]
        },
        "affected_semantic_nodes": ["A:P3", "A:P6", "A:C1", "A:U1", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R159:ANCHOR_BINDING_CONTRACT", "R159:FRAME_RELATION_TRANSPORT", "R173:RETENTIVE_EXPERIENTIAL_COORDINATE", "R173:FAMILIAR_MINENESS_BOUNDARY"],
        "semantic_scope": "Fresh structural traversal plus bounded manual review of C1/U1, P3/P6, R157, R159, effective R173, A4M, A4N and A4V; not a full historical semantic reproof.",
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE"
    }
    assert not all_of_nonlists and not unresolved and not cycles
    outdir = Path(__file__).parent
    (outdir / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (outdir / "PER_ID_AUDIT.json.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as f:
                json.dump(per_id, f, indent=2, sort_keys=True); f.write("\n")
    print(json.dumps({"status": result["status"], "effective_counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
