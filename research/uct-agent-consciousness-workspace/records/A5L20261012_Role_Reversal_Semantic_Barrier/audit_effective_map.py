#!/usr/bin/env python3
"""Fresh structural audit of a restored UCT effective graph."""
import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("graph", type=Path)
a = p.parse_args()
raw = a.graph.read_bytes()
d = json.loads(raw)
nodes, rules, links = d["nodes"], d["rules"], d["context_links"]
node_ids = {n["id"] for n in nodes}
rule_ids = {r["id"] for r in rules}
missing_node_fields = [n.get("id", "<missing-id>") for n in nodes if not all(k in n for k in ("id", "kind", "statement", "scope"))]
bad_all_of = [r["id"] for r in rules if not isinstance(r.get("all_of"), list)]
empty_all_of = [r["id"] for r in rules if isinstance(r.get("all_of"), list) and not r["all_of"]]
unresolved = []
unresolved_context_node_refs = []
external_context_endpoints = 0
for r in rules:
    for x in r.get("all_of", []):
        if x not in node_ids:
            unresolved.append([r["id"], "premise", x])
    if r.get("conclusion") not in node_ids:
        unresolved.append([r["id"], "conclusion", r.get("conclusion")])
for x in links:
    # Context links are explicitly nondeductive and may name modules or source
    # references. Validate only endpoints typed as graph nodes.
    left, right = x.get("from", x.get("source")), x.get("to", x.get("target"))
    left_type = x.get("from_type", x.get("source_type"))
    right_type = x.get("to_type", x.get("target_type"))
    for side, endpoint, endpoint_type in (("from", left, left_type), ("to", right, right_type)):
        if endpoint_type == "node" and endpoint not in node_ids:
            unresolved_context_node_refs.append([x.get("id"), side, endpoint])
        elif endpoint_type != "node":
            external_context_endpoints += 1

# Node-level dependency graph: each simultaneous premise precedes the conclusion.
adj, indeg = defaultdict(set), {x: 0 for x in node_ids}
for r in rules:
    for premise in r.get("all_of", []):
        conclusion = r.get("conclusion")
        if premise in node_ids and conclusion in node_ids and conclusion not in adj[premise]:
            adj[premise].add(conclusion)
            indeg[conclusion] += 1
q = deque(x for x, degree in indeg.items() if degree == 0)
seen = 0
while q:
    x = q.popleft(); seen += 1
    for y in adj[x]:
        indeg[y] -= 1
        if indeg[y] == 0:
            q.append(y)
cycles = [] if seen == len(node_ids) else sorted(x for x, degree in indeg.items() if degree > 0)
out = {
    "schema": "a5l-fresh-effective-map-audit/1",
    "graph_sha256": hashlib.sha256(raw).hexdigest(),
    "counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "unique_ids": {"nodes": len(node_ids), "rules": len(rule_ids)},
    "per_node_minimal_fields_checked": len(nodes),
    "missing_minimal_node_fields": missing_node_fields,
    "rules_read_all_of_as_simultaneous_and": len(rules),
    "rules_with_nonlist_all_of": bad_all_of,
    "rules_with_empty_all_of": empty_all_of,
    "unresolved_references": unresolved,
    "unresolved_context_node_references": unresolved_context_node_refs,
    "external_or_module_context_endpoints": external_context_endpoints,
    "deductive_cycles": cycles,
    "context_links_treated_as_nondeductive": all(x.get("deductive") is False for x in links),
    "pass": not any((missing_node_fields, bad_all_of, empty_all_of, unresolved, unresolved_context_node_refs, cycles)) and len(node_ids) == len(nodes) and len(rule_ids) == len(rules)
}
print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
