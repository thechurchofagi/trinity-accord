#!/usr/bin/env python3
"""Fresh structural traversal and bounded semantic audit for A5E."""

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
    for n in nodes:
        scope = n.get("scope") or n.get("domain")
        contracts = [v for k, v in n.items() if k.startswith("formal_contract") and isinstance(v, dict)]
        contract = contracts[-1] if contracts else {}
        per_id.append({
            "id": n["id"], "kind": n.get("kind"), "status": n.get("status"),
            "has_statement": bool(n.get("statement")), "has_scope_or_domain": bool(scope),
            "has_quantifier_or_scoped_contract": bool(scope or contract.get("quantifiers") or contract.get("quantifier_convention")),
            "review": "FIELDS_ACCESSED; NOT_GLOBAL_SEMANTIC_REPROOF"
        })

    unresolved, nonlists, empty = [], [], []
    adjacency = {i: [] for i in ids}
    for r in rules:
        deps = r.get("all_of")
        if not isinstance(deps, list):
            nonlists.append(r["id"]); continue
        if not deps: empty.append(r["id"])
        conclusion = r.get("conclusion")
        if conclusion not in ids: unresolved.append({"rule": r["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in ids: unresolved.append({"rule": r["id"], "role": "premise", "id": dep})
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
    for i in ids: dfs(i, [i])

    result = {
        "schema": "a5e-map-audit/1",
        "root_graph_sha256": sha(graph_path),
        "restored_effective_graph_sha256": sha(restored_arg),
        "root_counts": {k: len(root_graph[k]) for k in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": nonlists,
        "rules_with_empty_all_of": empty,
        "unresolved_deductive_references": unresolved,
        "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "context_endpoint_schema_differences_or_unresolved": context_unresolved,
        "a5e_joint_satisfiability": {
            "automorphism_case": {"ACTUAL_TOKEN_BINDING": 1, "COMPLETE_RELEVANT_K": 1, "G_IS_K_AUTOMORPHISM": 1, "H_IS_K_DEFINABLE": 1, "PARAMETERS_TRANSPORTED_IF_ANY": 1, "H_INVARIANT": 1},
            "grounded_asymmetry_case": {"ACTUAL_TOKEN_BINDING": 1, "COMPLETE_RELEVANT_K": 1, "G_IS_K_AUTOMORPHISM": 0, "GROUNDED_ASYMMETRIC_ANCHOR": 1, "TARGET_COVARIES_OR_CHANGES": 1},
            "extra_bridge_case": {"G_IS_K_AUTOMORPHISM": 1, "H_REVERSES": 1, "H_IS_K_DEFINABLE": 0, "EXTRA_BRIDGE_REQUIRED": 1},
            "actuality_claimed": False
        },
        "a5e_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "affected_semantic_nodes": ["A:P3", "A:P6", "A:C1", "A:U1", "A:PHEN_TARGET", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R166:EVIDENCE_LEVEL_LADDER", "R172:EXPERIENCE_INTERNAL_ACTION_COORDINATE", "R173:FAMILIAR_MINENESS_BOUNDARY"],
        "manual_semantic_checks": [
            "No inference from finite view, abstract symmetry or checker output to actual installation",
            "All automorphism premises refer to one object, interval, complete signature and parameter assignment",
            "Parameter-free invariance and parameterized covariance are not conflated",
            "No converse from invariance to definability is asserted",
            "No role-swap comparison is called an automorphism after a grounded anchor is changed",
            "C1 transport is conditional and not inferred backward from report or target naming",
            "Orbit law constrains structural content but does not identify H_pc, evidence sign or a unique owner"
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
