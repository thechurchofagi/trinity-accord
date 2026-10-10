#!/usr/bin/env python3
"""Whole frozen-map structural traversal for A3V; not a semantic reproof."""
from pathlib import Path
from collections import defaultdict, deque
import argparse, gzip, hashlib, json

p = argparse.ArgumentParser()
p.add_argument("--base", type=Path, required=True)
p.add_argument("--ledger", type=Path, required=True)
p.add_argument("--extension", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
g = json.loads(a.base.read_text())
l = json.loads(a.ledger.read_text())
e = json.loads(a.extension.read_text())
sha = lambda x: hashlib.sha256(x.read_bytes()).hexdigest()
ids = {n["id"] for n in g["nodes"]}
edges = defaultdict(set)
indeg = dict.fromkeys(ids, 0)
unresolved = []
for rule in g["rules"]:
    assert isinstance(rule["all_of"], list) and rule["all_of"]
    for premise in rule["all_of"]:
        if premise not in ids or rule["conclusion"] not in ids:
            unresolved.append(rule["id"])
        elif rule["conclusion"] not in edges[premise]:
            edges[premise].add(rule["conclusion"])
            indeg[rule["conclusion"]] += 1
for context in g["context_links"]:
    for field, alternative in (("from", "source"), ("to", "target")):
        ref = context.get(field, context.get(alternative))
        typ = context.get(field + "_type", context.get(alternative + "_type", "node"))
        external = typ in ("source_reference", "module_reference", "module", "external_source") or (field == "from" and context.get("external_source"))
        if ref not in ids and not external:
            unresolved.append(context["id"])
queue = deque(x for x, degree in indeg.items() if not degree)
seen = 0
while queue:
    x = queue.popleft()
    seen += 1
    for y in edges[x]:
        indeg[y] -= 1
        if not indeg[y]:
            queue.append(y)
refs = [ref for app in e["applications"] for ref in app["completed_node_refs"]]
checks = {
    "counts": tuple(len(g[k]) for k in ("nodes", "rules", "context_links")) == (913, 424, 261),
    "suspended": len(g["suspended_historical_rule_ids"]) == 10,
    "review_count": len(l["items"]) == 1608,
    "base_hash": sha(a.base) == "0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612",
    "ledger_hash": sha(a.ledger) == "0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687",
    "all_of_refs_and_context_refs": not unresolved,
    "dag": seen == len(ids),
    "completed_refs": all(ref in ids for ref in refs),
    "disabled_zero_graph_delta": not e["enabled"] and not e["nodes"] and not e["rules"] and not e["context_links"],
    "joint_actual_premises_open": all(not app["actual_premises_discharged"] for app in e["applications"]),
    "foundation_unchanged": e["foundation_effect"] == "NONE",
}
coverage = []
for kind in ("nodes", "rules", "context_links"):
    for item in g[kind]:
        coverage.append({
            "id": item["id"], "kind": kind,
            "sha256": hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest(),
            "scope": "UNCHANGED_FROZEN_OBJECT_NOT_FRESH_SEMANTIC_REPROOF",
        })
out = {
    "schema": "uct-a3v-map-audit/1",
    "checks": checks,
    "all_structural_checks_pass": all(checks.values()),
    "covered_objects": len(coverage),
    "review_items": len(l["items"]),
    "candidate_counts": {"nodes": 0, "rules": 0, "contexts": 0},
    "semantic_status": "AUDIT_INCOMPLETE",
    "affected_contracts": [
        "C1/U1 actual token and same-signature transport",
        "R172 online action use", "R173 retentive binding", "R175 target separation",
        "R177 source/feature separation", "R200 semantic firewall (disabled)",
        "A3O fixed route grain", "A3Q actual selector ancestry", "A3R sufficient SPC contract", "R173 competition-independent transport",
    ],
    "inference_effect": "PMd LiveJoin is not discharged. Integrated option influence is not distinct-token participation; SPC is not a premise of inherited R173 transport; H bridge remains open.",
    "unresolved": unresolved,
}
a.output.write_text(json.dumps(out, indent=2) + "\n")
a.output.with_name("WHOLE_MAP_COVERAGE.json.gz").write_bytes(gzip.compress(json.dumps({
    "items": coverage,
    "review_ids": [item.get("id", item.get("item_id")) for item in l["items"]],
    "semantic_status": "AUDIT_INCOMPLETE",
}, separators=(",", ":")).encode(), mtime=0))
print(json.dumps({"pass": all(checks.values()), "covered": len(coverage), "reviews": len(l["items"])}))
assert all(checks.values()), checks
