#!/usr/bin/env python3
"""Structural compatibility audit for the disabled R189 map candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--extension", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    ext = json.loads(args.extension.read_text(encoding="utf-8"))

    base_nodes = {n["id"] for n in base["nodes"]}
    base_rules = {r["id"] for r in base["rules"]}
    base_contexts = {c["id"] for c in base["context_links"]}
    new_nodes = [n["id"] for n in ext["nodes"]]
    new_rules = [r["id"] for r in ext["rules"]]
    new_contexts = [c["id"] for c in ext["context_links"]]

    checks = {}
    checks["base_release_is_v1_1_2"] = base.get("version") == "UCT-MAP-v1.1.2"
    checks["base_counts_match_release"] = (
        len(base_nodes), len(base_rules), len(base_contexts), len(base["suspended_historical_rule_ids"])
    ) == (913, 424, 261, 10)
    checks["review_ledger_has_1608_items"] = len(ledger) == 1608 if isinstance(ledger, list) else len(ledger.get("items", [])) == 1608
    checks["extension_disabled"] = (
        ext.get("integration_status") == "PENDING_CHECKPOINT_DISABLED"
        and ext.get("enabled_as_established_premise") is False
        and ext.get("release_effect", "").startswith("NONE")
    )
    checks["new_ids_unique"] = (
        len(new_nodes) == len(set(new_nodes))
        and len(new_rules) == len(set(new_rules))
        and len(new_contexts) == len(set(new_contexts))
    )
    checks["no_id_collision"] = not (
        set(new_nodes) & base_nodes or set(new_rules) & base_rules or set(new_contexts) & base_contexts
    )
    checks["all_new_nodes_scoped"] = all(n.get("scope") and n.get("statement") for n in ext["nodes"])
    checks["all_rules_have_nonempty_all_of"] = all(r.get("all_of") for r in ext["rules"])
    checks["all_rules_same_instance"] = all(r.get("same_instance_required") is True for r in ext["rules"])
    checks["all_rules_have_binding_and_proof"] = all(r.get("binding") and r.get("proof_location") for r in ext["rules"])

    all_nodes = base_nodes | set(new_nodes)
    unresolved = []
    for rule in ext["rules"]:
        for premise in rule["all_of"]:
            if premise not in all_nodes:
                unresolved.append([rule["id"], "premise", premise])
        if rule["conclusion"] not in all_nodes:
            unresolved.append([rule["id"], "conclusion", rule["conclusion"]])
    for link in ext["context_links"]:
        for field in ("from", "to"):
            if link[field] not in all_nodes:
                unresolved.append([link["id"], field, link[field]])
    checks["all_references_resolve"] = not unresolved

    graph = defaultdict(set)
    indegree = {node: 0 for node in all_nodes}
    for rule in list(base["rules"]) + list(ext["rules"]):
        for premise in rule["all_of"]:
            if premise in all_nodes and rule["conclusion"] in all_nodes and rule["conclusion"] not in graph[premise]:
                graph[premise].add(rule["conclusion"])
                indegree[rule["conclusion"]] += 1
    queue = deque(sorted(k for k, d in indegree.items() if d == 0))
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for target in graph[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    checks["combined_rule_graph_acyclic"] = seen == len(all_nodes)

    payload = {
        "schema": "uct-r189-map-compatibility-audit/1",
        "base_release": base["version"],
        "base_graph_sha256": sha256(args.base),
        "base_review_ledger_sha256": sha256(args.ledger),
        "base_counts": {
            "nodes": len(base_nodes),
            "active_rules": len(base_rules),
            "contexts": len(base_contexts),
            "suspended_historical_rules": len(base["suspended_historical_rule_ids"]),
        },
        "candidate_counts": {
            "nodes": len(new_nodes),
            "rules": len(new_rules),
            "contexts": len(new_contexts),
            "combined_nodes": len(all_nodes),
            "combined_rules": len(base_rules) + len(new_rules),
            "combined_contexts": len(base_contexts) + len(new_contexts),
        },
        "checks": checks,
        "unresolved_references": unresolved,
        "all_structural_checks_pass": all(checks.values()),
        "semantic_scope": "Compatibility traversal of the exact 1,608-item reviewed baseline plus manual affected-family review. This does not re-prove all inherited mathematics, validate premise truth, or make R189 active.",
        "integration_status": "STRUCTURAL_COMPATIBILITY_PASS_SEMANTIC_ADOPTION_OPEN" if all(checks.values()) else "FAIL",
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not payload["all_structural_checks_pass"]:
        raise SystemExit("map compatibility audit failed")


if __name__ == "__main__":
    main()
