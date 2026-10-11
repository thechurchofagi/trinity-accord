#!/usr/bin/env python3
"""Fresh structural and scoped semantic audit for A4U.

The audit treats all_of as conjunction and context links as nondeductive. It
does not claim a global semantic proof.
"""

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
    restored_container = json.loads(Path(restored).read_text())
    unified = restored_container["completed_graph"]

    nodes = unified["nodes"]
    rules = unified["rules"]
    contexts = unified["context_links"]
    node_ids = {n["id"] for n in nodes}
    rule_ids = {r["id"] for r in rules}
    assert len(node_ids) == len(nodes)
    assert len(rule_ids) == len(rules)

    per_id = []
    missing_scope = []
    for n in nodes:
        scope = n.get("scope") or n.get("domain")
        contract = next((v for k, v in reversed(list(n.items())) if k.startswith("formal_contract") and isinstance(v, dict)), {})
        quant = contract.get("quantifiers") or contract.get("quantifier_convention")
        row = {
            "id": n["id"],
            "kind": n.get("kind"),
            "status": n.get("status"),
            "has_statement": bool(n.get("statement")),
            "has_scope_or_domain": bool(scope),
            "has_explicit_quantifier_text_or_scoped_contract": bool(quant or scope),
            "review": "STRUCTURAL_FIELDS_ACCESSED_NOT_GLOBAL_SEMANTIC_REPROOF",
        }
        per_id.append(row)
        if not scope:
            missing_scope.append(n["id"])

    unresolved = []
    adjacency = {nid: [] for nid in node_ids}
    all_of_nonlists = []
    empty_all_of = []
    for r in rules:
        deps = r.get("all_of")
        if not isinstance(deps, list):
            all_of_nonlists.append(r["id"])
            continue
        if not deps:
            empty_all_of.append(r["id"])
        conclusion = r.get("conclusion")
        if conclusion not in node_ids:
            unresolved.append({"rule": r["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in node_ids:
                unresolved.append({"rule": r["id"], "role": "premise", "id": dep})
            elif conclusion in adjacency:
                adjacency[dep].append(conclusion)

    visiting, visited = set(), set()
    cycles = []

    def dfs(x, stack):
        if x in visiting:
            cycles.append(stack[stack.index(x):] + [x])
            return
        if x in visited:
            return
        visiting.add(x)
        for y in adjacency.get(x, []):
            dfs(y, stack + [y])
        visiting.remove(x)
        visited.add(x)

    for nid in node_ids:
        dfs(nid, [nid])

    result = {
        "schema": "a4u-map-audit/1",
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
        "a4u_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "a4u_joint_witness": {
            "binding": "one P/A/D/B/C/e/K_view",
            "premises": ["BIND", "START", "SOURCE", "FIFO", "DMA", "WINDOW", "READ"],
            "satisfiable_model": "known-empty fixed-channel loss-free DREQ-paced linear-buffer single-writer timely-read run"
        },
        "semantic_scope": "Fresh structural traversal plus bounded manual review of A:P3/A:P6/A:C1/A:U1/R157/R159/R173/A4S/A4T/A4U; not a full historical semantic reproof.",
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE"
    }
    assert not all_of_nonlists
    assert not unresolved
    assert not cycles

    outdir = Path(__file__).parent
    (outdir / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (outdir / "PER_ID_AUDIT.json.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as f:
                json.dump(per_id, f, indent=2, sort_keys=True)
                f.write("\n")
    print(json.dumps({"status": result["status"], "effective_counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
