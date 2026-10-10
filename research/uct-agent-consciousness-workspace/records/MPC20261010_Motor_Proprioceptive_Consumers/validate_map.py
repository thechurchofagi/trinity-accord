#!/usr/bin/env python3
"""MPC scoped compatibility audit; structural checks are not semantic proof."""

import argparse
import gzip
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    base = load(args.base)
    ledger = load(args.ledger)
    extension = load(args.extension)
    base_nodes = {node["id"] for node in base["nodes"]}
    candidate_nodes = {node["id"] for node in extension["nodes"]}
    all_current_nodes = base_nodes | candidate_nodes

    # Disabled context links may cite earlier disabled candidates. Load their IDs
    # only for context resolution; they do not become deductive premises.
    disabled_node_ids = set()
    disabled_sources = {}
    for path in args.records.glob("*/MAP_EXTENSION.json"):
        try:
            item = load(path)
        except (json.JSONDecodeError, OSError):
            continue
        ids = {node.get("id") for node in item.get("nodes", []) if node.get("id")}
        disabled_node_ids |= ids
        for node_id in ids:
            disabled_sources.setdefault(node_id, str(path.relative_to(args.records.parent)))

    unresolved_rule_refs = []
    unresolved_context_refs = []
    graph = defaultdict(set)
    indegree = {node_id: 0 for node_id in all_current_nodes}
    rules = base["rules"] + extension["rules"]
    for rule in rules:
        refs = list(rule.get("all_of", [])) + [rule.get("conclusion")]
        if any(ref not in all_current_nodes for ref in refs):
            unresolved_rule_refs.append(rule["id"])
            continue
        for premise in rule["all_of"]:
            if rule["conclusion"] not in graph[premise]:
                graph[premise].add(rule["conclusion"])
                indegree[rule["conclusion"]] += 1

    inherited_unresolved_context_refs = []
    for context in base["context_links"] + extension["context_links"]:
        for side in ("from", "to"):
            ref = context.get(side, context.get({"from": "source", "to": "target"}[side]))
            ref_type = context.get(side + "_type", context.get({"from": "source_type", "to": "target_type"}[side], "node"))
            nonnode = ref_type in {"source_reference", "module_reference", "module", "external_source"}
            if ref not in (all_current_nodes | disabled_node_ids) and not nonnode:
                target = {"context": context["id"], "side": side, "ref": ref}
                if context in extension["context_links"]:
                    unresolved_context_refs.append(target)
                else:
                    inherited_unresolved_context_refs.append(target)

    queue = deque(node_id for node_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node_id = queue.popleft()
        visited += 1
        for target in graph[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)

    base_contract_missing = []
    for node in base["nodes"]:
        contract = node.get("formal_contract_R153", {})
        if not node.get("statement") or not contract.get("object_domain") or not contract.get("quantifier_convention"):
            base_contract_missing.append(node["id"])
    candidate_contract_missing = []
    for node in extension["nodes"]:
        if any(not node.get(field) for field in ("kind", "statement", "scope", "quantifier", "status", "proof_location", "counterexamples_and_limits")):
            candidate_contract_missing.append(node["id"])

    checks = {
        "base_identity": base.get("version") == "UCT-MAP-v1.1.2",
        "base_counts": (len(base["nodes"]), len(base["rules"]), len(base["context_links"])) == (913, 424, 261),
        "suspended_count": len(base["suspended_historical_rule_ids"]) == 10,
        "review_count": len(ledger["items"]) == 1608,
        "base_hash": digest(args.base) == "0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612",
        "ledger_hash": digest(args.ledger) == "0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687",
        "candidate_disabled": extension.get("status") == "PENDING_CHECKPOINT_DISABLED" and extension.get("enabled") is False,
        "candidate_counts": (len(extension["nodes"]), len(extension["rules"]), len(extension["context_links"])) == (7, 4, 5),
        "unique_candidate_ids": len(candidate_nodes) == len(extension["nodes"]),
        "no_base_collision": not (base_nodes & candidate_nodes),
        "base_nodes_traversed": len(base["nodes"]) == 913,
        "candidate_node_contracts_complete": not candidate_contract_missing,
        "rule_refs_resolve": not unresolved_rule_refs,
        "context_refs_resolve": not unresolved_context_refs,
        "all_of_nonempty": all(rule.get("all_of") for rule in extension["rules"]),
        "same_instance_fields_explicit": all("same_instance_required" in rule and rule.get("binding") for rule in extension["rules"]),
        "proof_and_route_fields_explicit": all(rule.get("proof_location") and rule.get("alternative_route_semantics") for rule in extension["rules"]),
        "combined_deductive_dag_acyclic": visited == len(all_current_nodes),
        "c1_axiom_preserved": any(link.get("to") == "A:C1" and link.get("type") == "AXIOM_STATUS_PRESERVED" for link in extension["context_links"]),
        "no_assistant_verdict": any(link.get("to") == "D:UCT_INTERPRETATION" and link.get("type") == "NO_CONSCIOUSNESS_OR_FEAR_INFERENCE" for link in extension["context_links"]),
        "actual_intake_not_inferred": extension["nodes"][-1]["status"] == "CONDITIONAL_APPLICATION_OPEN",
    }

    coverage = []
    for kind in ("nodes", "rules", "context_links"):
        for item in base[kind]:
            canonical = json.dumps(item, sort_keys=True, ensure_ascii=False)
            coverage.append({
                "id": item["id"],
                "kind": kind,
                "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                "scope": "FROZEN_BASE_UNCHANGED; concept/quantifier/scope or all_of/reference fields traversed",
                "semantic_status": "INHERITED_NOT_INDEPENDENTLY_REPROVED",
            })

    result = {
        "schema": "uct-mpc-map-audit/1",
        "base_sha256": digest(args.base),
        "review_ledger_sha256": digest(args.ledger),
        "base_counts": {"nodes": 913, "rules": 424, "contexts": 261, "suspended": 10, "review_items": 1608},
        "candidate_counts": {"nodes": 7, "rules": 4, "contexts": 5},
        "checks": checks,
        "all_structural_checks_pass": all(checks.values()),
        "unresolved_rule_refs": unresolved_rule_refs,
        "unresolved_context_refs": unresolved_context_refs,
        "inherited_release_context_exceptions": inherited_unresolved_context_refs,
        "disabled_context_targets": {link["to"]: disabled_sources.get(link["to"]) for link in extension["context_links"] if link["to"] in disabled_node_ids},
        "base_contract_missing": base_contract_missing,
        "candidate_contract_missing": candidate_contract_missing,
        "affected_rederivation": [
            "A:C1 remains an explanatory axiom; no empirical confirmation or basal gate is added.",
            "MPC:C1-C2 identify response-function ambiguity only on the frozen endpoint tensor; they do not identify actual intake events.",
            "MPC:C3 blocks output-to-use inference even after a complete response table; carrier/event instrumentation remains required.",
            "Agency, ownership, intensity/bias, precision/sensitivity and report remain separately typed endpoints.",
            "No current-assistant consciousness or fear conclusion follows.",
        ],
        "semantic_adoption": "OPEN; no independent full-history semantic re-proof, physical instantiation, or reviewer closure",
        "integration": "PENDING_CHECKPOINT_DISABLED",
    }
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compressed = args.output.with_name("WHOLE_MAP_COVERAGE.json.gz")
    compressed.write_bytes(gzip.compress((json.dumps({"items": coverage, "semantic_limit": result["semantic_adoption"]}, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8"), mtime=0))
    print(json.dumps({"structural_pass": result["all_structural_checks_pass"], "checks": len(checks), "covered_objects": len(coverage), "review_items": 1608}))
    if not result["all_structural_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
