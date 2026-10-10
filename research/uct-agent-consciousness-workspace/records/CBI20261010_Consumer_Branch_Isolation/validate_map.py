#!/usr/bin/env python3
"""Scoped structural compatibility audit; passing is not semantic proof."""

import argparse
from collections import defaultdict, deque
import gzip
import hashlib
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--ledger", required=True)
    p.add_argument("--extension", required=True)
    p.add_argument("--records", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    base, ledger, ext = load(a.base), load(a.ledger), load(a.extension)
    base_ids = {x["id"] for x in base["nodes"]}
    candidate_ids = {x["id"] for x in ext["nodes"]}
    all_ids = base_ids | candidate_ids
    disabled_ids = set()
    for path in Path(a.records).glob("*/MAP_EXTENSION.json"):
        try:
            disabled_ids |= {x["id"] for x in load(path).get("nodes", [])}
        except (OSError, json.JSONDecodeError, KeyError):
            pass

    unresolved_rules = []
    edges = defaultdict(set)
    indegree = {x: 0 for x in all_ids}
    for rule in base["rules"] + ext["rules"]:
        refs = rule.get("all_of", []) + [rule.get("conclusion")]
        if any(x not in all_ids for x in refs):
            unresolved_rules.append(rule["id"])
            continue
        for source in rule["all_of"]:
            if rule["conclusion"] not in edges[source]:
                edges[source].add(rule["conclusion"])
                indegree[rule["conclusion"]] += 1
    queue = deque(x for x, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        source = queue.popleft(); visited += 1
        for target in edges[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)

    unresolved_contexts = []
    for link in ext["context_links"]:
        for key in ("from", "to"):
            if link[key] not in all_ids | disabled_ids:
                unresolved_contexts.append({"id": link["id"], "side": key, "ref": link[key]})

    required = ("kind", "statement", "scope", "quantifier", "status", "proof_location", "counterexamples_and_limits")
    checks = {
        "base_identity": base.get("version") == "UCT-MAP-v1.1.2",
        "base_counts": (len(base["nodes"]), len(base["rules"]), len(base["context_links"])) == (913, 424, 261),
        "suspended_count": len(base["suspended_historical_rule_ids"]) == 10,
        "review_count": len(ledger["items"]) == 1608,
        "base_hash": digest(a.base) == "0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612",
        "ledger_hash": digest(a.ledger) == "0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687",
        "candidate_disabled": ext.get("enabled") is False and ext.get("status") == "PENDING_CHECKPOINT_DISABLED",
        "candidate_counts": (len(ext["nodes"]), len(ext["rules"]), len(ext["context_links"])) == (7, 4, 5),
        "candidate_ids_unique": len(candidate_ids) == len(ext["nodes"]),
        "no_base_collision": not base_ids & candidate_ids,
        "candidate_contracts_complete": all(all(node.get(k) for k in required) for node in ext["nodes"]),
        "rule_refs_resolve": not unresolved_rules,
        "context_refs_resolve": not unresolved_contexts,
        "all_of_conjunctive_nonempty": all(rule.get("all_of") for rule in ext["rules"]),
        "same_instance_and_binding_explicit": all("same_instance_required" in rule and rule.get("binding") for rule in ext["rules"]),
        "proof_route_explicit": all(rule.get("proof_location") and rule.get("alternative_route_semantics") for rule in ext["rules"]),
        "combined_dag_acyclic": visited == len(all_ids),
        "c1_axiom_status_preserved": any(x["to"] == "A:C1" and x["type"] == "AXIOM_STATUS_PRESERVED" for x in ext["context_links"]),
        "no_agent_verdict": any(x["to"] == "D:UCT_INTERPRETATION" and x["type"] == "NO_CONSCIOUSNESS_OR_FEAR_INFERENCE" for x in ext["context_links"]),
        "actual_application_open": ext["nodes"][-1]["status"] == "CONDITIONAL_APPLICATION_OPEN"
    }
    coverage = []
    for kind in ("nodes", "rules", "context_links"):
        for item in base[kind]:
            canonical = json.dumps(item, sort_keys=True, ensure_ascii=False).encode()
            coverage.append({"id": item["id"], "kind": kind, "sha256": hashlib.sha256(canonical).hexdigest(), "status": "FROZEN_BASE_TRAVERSED_NOT_INDEPENDENTLY_REPROVED"})
    result = {
        "schema": "uct-cbi-map-audit/1",
        "base_counts": {"nodes": 913, "rules": 424, "contexts": 261, "suspended": 10, "review_items": 1608},
        "candidate_counts": {"nodes": 7, "rules": 4, "contexts": 5},
        "checks": checks,
        "all_structural_checks_pass": all(checks.values()),
        "unresolved_rule_refs": unresolved_rules,
        "unresolved_context_refs": unresolved_contexts,
        "semantic_limit": "No global theory proof, actual installation, phenomenal bridge, or reviewer closure.",
        "integration": "PENDING_CHECKPOINT_DISABLED"
    }
    Path(a.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path(a.output).with_name("WHOLE_MAP_COVERAGE.json.gz").write_bytes(gzip.compress(json.dumps({"items": coverage, "limit": result["semantic_limit"]}, separators=(",", ":")).encode() + b"\n", mtime=0))
    print(json.dumps({"structural_pass": result["all_structural_checks_pass"], "checks": len(checks), "covered_objects": len(coverage), "review_items": 1608}))
    if not result["all_structural_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

