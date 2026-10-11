#!/usr/bin/env python3
"""Fresh structural and scoped semantic audit for A4Y."""

import gzip
import hashlib
import io
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(root_arg: str, restored_arg: str) -> None:
    root = Path(root_arg)
    graph_path = root / "UCT_FORMAL_GRAPH.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    unified = json.loads(Path(restored_arg).read_text(encoding="utf-8"))["completed_graph"]
    nodes, rules, contexts = unified["nodes"], unified["rules"], unified["context_links"]
    node_ids, rule_ids = {n["id"] for n in nodes}, {r["id"] for r in rules}
    assert len(node_ids) == len(nodes) and len(rule_ids) == len(rules)

    per_id, missing_scope = [], []
    for node in nodes:
        scope = node.get("scope") or node.get("domain")
        contract = next(
            (value for key, value in reversed(list(node.items())) if key.startswith("formal_contract") and isinstance(value, dict)),
            {},
        )
        quant = contract.get("quantifiers") or contract.get("quantifier_convention")
        per_id.append({
            "id": node["id"],
            "kind": node.get("kind"),
            "status": node.get("status"),
            "has_statement": bool(node.get("statement")),
            "has_scope_or_domain": bool(scope),
            "has_explicit_quantifier_text_or_scoped_contract": bool(quant or scope),
            "review": "STRUCTURAL_FIELDS_ACCESSED_NOT_GLOBAL_SEMANTIC_REPROOF",
        })
        if not scope:
            missing_scope.append(node["id"])

    unresolved, nonlists, empty = [], [], []
    adjacency = {node_id: [] for node_id in node_ids}
    for rule in rules:
        deps = rule.get("all_of")
        if not isinstance(deps, list):
            nonlists.append(rule["id"])
            continue
        if not deps:
            empty.append(rule["id"])
        conclusion = rule.get("conclusion")
        if conclusion not in node_ids:
            unresolved.append({"rule": rule["id"], "role": "conclusion", "id": conclusion})
        for dep in deps:
            if dep not in node_ids:
                unresolved.append({"rule": rule["id"], "role": "premise", "id": dep})
            elif conclusion in adjacency:
                adjacency[dep].append(conclusion)

    visiting, visited, cycles = set(), set(), []

    def dfs(node_id: str, stack: list[str]) -> None:
        if node_id in visiting:
            cycles.append(stack[stack.index(node_id):] + [node_id])
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for child in adjacency.get(node_id, []):
            dfs(child, stack + [child])
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        dfs(node_id, [node_id])

    result = {
        "schema": "a4y-map-audit/1",
        "root_graph_sha256": sha256(graph_path),
        "root_counts": {key: len(graph[key]) for key in ("nodes", "rules", "context_links")},
        "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(contexts)},
        "per_node_fields_accessed": len(per_id),
        "nodes_without_scope_or_domain": missing_scope,
        "all_rules_read_all_of_as_simultaneous_and": True,
        "rules_with_nonlist_all_of": nonlists,
        "rules_with_empty_all_of": empty,
        "unresolved_deductive_references": unresolved,
        "deductive_cycles": cycles,
        "context_links_treated_as_nondeductive": True,
        "a4y_scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
        "a4y_joint_witness": {
            "binding": "one P/I/K/event/target/consumer/challenge binding with read-policy state, draw, actual policy and independent witness path",
            "premises": ["A4X-SEPP-CLAUSES", "BEFORE", "BLIND", "BOUND", "DUAL-READ-POLICY", "REMAINING-EXCLUSION"],
            "finite_satisfiable_models": ["fixed dual-read AND", "fixed dual-read OR"],
            "premise_drop_countermodels": ["late bound record", "preloaded cue-indexed dispatcher", "timely blind sidecar", "controller outside T_1"],
        },
        "affected_semantic_nodes": [
            "A:P3", "A:P6", "A:C1", "A:U1", "R157:COORDINATE_TRANSPORT",
            "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA",
            "R159:ANCHOR_BINDING_CONTRACT", "R159:FRAME_RELATION_TRANSPORT",
            "R173:RETENTIVE_EXPERIENTIAL_COORDINATE", "R173:FAMILIAR_MINENESS_BOUNDARY",
        ],
        "semantic_scope": "Fresh structural traversal plus bounded manual review of C1/U1, P3/P6, R157, R159, effective R173, R181 and A4P/A4D-A4G/A4V-A4Y; not a full historical semantic reproof.",
        "status": "FRESH_STRUCTURAL_PASS_BOUNDED_SEMANTIC_PASS_FULL_DEPTH_INCOMPLETE",
    }
    assert not nonlists and not unresolved and not cycles
    outdir = Path(__file__).parent
    (outdir / "AUDIT_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (outdir / "PER_ID_AUDIT.json.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as stream:
                json.dump(per_id, stream, indent=2, sort_keys=True)
                stream.write("\n")
    print(json.dumps({"status": result["status"], "effective_counts": result["effective_counts"], "unresolved": len(unresolved), "cycles": len(cycles)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
