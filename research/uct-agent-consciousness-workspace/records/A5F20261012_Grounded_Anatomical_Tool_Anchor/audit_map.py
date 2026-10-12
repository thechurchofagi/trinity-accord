#!/usr/bin/env python3
"""Fresh structural traversal and bounded semantic audit for A5F."""

import gzip, hashlib, io, json, sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(root_arg, restored_arg):
    root = Path(root_arg)
    graph_path = root / "UCT_FORMAL_GRAPH.json"
    root_graph = json.loads(graph_path.read_text(encoding="utf-8"))
    effective = json.loads(Path(restored_arg).read_text(encoding="utf-8"))["completed_graph"]
    nodes, rules, contexts = effective["nodes"], effective["rules"], effective["context_links"]
    ids = {n["id"] for n in nodes}
    assert len(ids) == len(nodes)

    per_id = []
    for node in nodes:
        scope = node.get("scope") or node.get("domain")
        contracts = [value for key, value in node.items() if key.startswith("formal_contract") and isinstance(value, dict)]
        contract = contracts[-1] if contracts else {}
        per_id.append({
            "id": node["id"], "kind": node.get("kind"), "status": node.get("status"),
            "has_statement": bool(node.get("statement")), "has_scope_or_domain": bool(scope),
            "has_quantifier_or_scoped_contract": bool(scope or contract.get("quantifiers") or contract.get("quantifier_convention")),
            "review": "FIELDS_ACCESSED; NOT_GLOBAL_SEMANTIC_REPROOF"
        })

    unresolved, nonlists, empty = [], [], []
    adjacency = {node_id: [] for node_id in ids}
    for rule in rules:
        deps = rule.get("all_of")
        if not isinstance(deps, list):
            nonlists.append(rule["id"]); continue
        if not deps: empty.append(rule["id"])
        conclusion = rule.get("conclusion")
        if conclusion not in ids: unresolved.append({"rule": rule["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in ids: unresolved.append({"rule": rule["id"], "role": "premise", "id": dep})
            elif conclusion in adjacency: adjacency[dep].append(conclusion)

    context_unresolved = []
    for link in contexts:
        for key in ("source", "target", "from", "to"):
            value = link.get(key)
            if isinstance(value, str) and value and value not in ids:
                context_unresolved.append({"context": link.get("id"), "field": key, "id": value})

    visiting, visited, cycles = set(), set(), []
    def dfs(node, stack):
        if node in visiting:
            cycles.append(stack[stack.index(node):] + [node]); return
        if node in visited: return
        visiting.add(node)
        for child in adjacency.get(node, []): dfs(child, stack + [child])
        visiting.remove(node); visited.add(node)
    for node_id in ids: dfs(node_id, [node_id])

    result = {
        "schema": "a5f-map-audit/1",
        "root_graph_sha256": sha(graph_path),
        "restored_effective_graph_sha256": sha(restored_arg),
        "root_counts": {key: len(root_graph[key]) for key in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": nonlists,
        "rules_with_empty_all_of": empty,
        "unresolved_deductive_references": unresolved,
        "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "context_endpoint_schema_differences_or_unresolved": context_unresolved,
        "a5f_joint_satisfiability": {
            "anchored_cross_case": {"ACTUAL_TOKEN_BINDING": 1, "UNIQUE_ANATOMICAL_ANCHOR": 1, "ACTUAL_GRIP": 1, "ACTUAL_EXTERNAL_SIDE": 1, "CROSS_NONISOMORPHIC": 1, "D_SIDE_FLIPS": 1},
            "anchor_free_countermodel": {"ACTUAL_TOKEN_BINDING": 1, "UNIQUE_ANATOMICAL_ANCHOR": 0, "PERFECT_MATCHING": 1, "CROSS_ISOMORPHIC": 1},
            "phenomenal_gap_case": {"PROTOCOL_RELATIONS_ACTUAL": 1, "TOJ_REPORT_OBSERVED": 1, "INDEPENDENT_H_TIP_CHANNEL": 0, "B_TIP_DISCHARGED": 0},
            "complete_biological_k_claimed": False
        },
        "a5f_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "affected_semantic_nodes": ["A:P3", "A:P6", "A:C1", "A:U1", "A:PHEN_TARGET", "R157:DEFINABLE_SELECTOR_SETUP", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R159:ANCHOR_BINDING_CONTRACT", "R159:FRAME_RELATION_TRANSPORT", "R159:SELECTED_OWNERSHIP_APPLICATION"],
        "manual_semantic_checks": [
            "Protocol-level actuality is not promoted to complete biological K",
            "Anatomical anchor, grip relation and external side share one object binding, interval and grain",
            "The non-isomorphism direction is not reversed into definability or phenomenology",
            "Temporal-order report, H_tip, ownership, agency and H_pc are not conflated",
            "C1 and R157 are used only in the organization-to-experience direction",
            "No exclusive owner or subject-count conclusion is introduced",
            "The anchor-free family supplies an explicit jointly satisfiable countermodel"
        ],
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE"
    }
    assert not nonlists and not empty and not unresolved and not cycles
    out = Path(__file__).parent
    (out / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "PER_ID_AUDIT.json.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8") as stream:
                json.dump(per_id, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"status": result["status"], "counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
