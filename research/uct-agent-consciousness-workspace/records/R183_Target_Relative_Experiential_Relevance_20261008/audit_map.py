#!/usr/bin/env python3
"""Full structural traversal plus targeted semantic-scope checks for R183."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "UCT_FORMAL_GRAPH.json"
CORE = ROOT / "records/CORE20261008_Target_Relative_Support/MAP_EXTENSION.json"
EI = ROOT / "records/EI20261008_Architecture_Dependence/MAP_EXTENSION.json"
R183 = Path(__file__).resolve().parent / "MAP_EXTENSION.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest_ids(ids):
    return hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()


def duplicates(values):
    return sorted(k for k, v in Counter(values).items() if v > 1)


def cycle_nodes(nodes, rules):
    graph = defaultdict(set)
    for rule in rules:
        for premise in rule.get("all_of", []):
            graph[premise].add(rule["conclusion"])
    state = {}
    stack = []
    found = set()

    def visit(n):
        state[n] = 1
        stack.append(n)
        for m in graph.get(n, ()):
            if state.get(m, 0) == 0:
                visit(m)
            elif state.get(m) == 1:
                found.update(stack[stack.index(m):])
        stack.pop()
        state[n] = 2

    for n in nodes:
        if state.get(n, 0) == 0:
            visit(n)
    return sorted(found)


def main():
    base, core, ei, r183 = map(read, (BASE, CORE, EI, R183))
    base_nodes = base["nodes"]
    base_rules = base["rules"]
    base_contexts = base["context_links"]
    base_ids = [n["id"] for n in base_nodes]
    base_rule_ids = [r["id"] for r in base_rules]
    base_id_set = set(base_ids)

    missing_base_node_fields = {
        f: sorted(n.get("id", "<missing-id>") for n in base_nodes if f not in n)
        for f in ("id", "kind", "statement", "scope", "status")
    }
    missing_base_rule_fields = {
        f: sorted(r.get("id", "<missing-id>") for r in base_rules if f not in r)
        for f in ("id", "all_of", "conclusion", "statement")
    }
    unresolved_base_rule_refs = []
    for rule in base_rules:
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]:
            if ref not in base_id_set:
                unresolved_base_rule_refs.append([rule.get("id"), ref])
    unresolved_base_context_refs = []
    for i, link in enumerate(base_contexts):
        for side in ("from", "to"):
            if link.get(side) not in base_id_set:
                unresolved_base_context_refs.append([i, side, link.get(side)])

    core_ids = [n["id"] for n in core["nodes"]]
    core_rule_ids = [r["id"] for r in core["rules"]]
    effective_ids = base_id_set | set(core_ids)
    effective_rules = base_rules + core["rules"]
    unresolved_core_refs = []
    for rule in core["rules"]:
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]:
            if ref not in effective_ids:
                unresolved_core_refs.append([rule["id"], ref])

    r183_ids = [n["id"] for n in r183["nodes"]]
    r183_rule_ids = [r["id"] for r in r183["rules"]]
    r183_all_ids = effective_ids | set(r183_ids)
    unresolved_r183_refs = []
    for rule in r183["rules"]:
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]:
            if ref not in r183_all_ids:
                unresolved_r183_refs.append([rule["id"], ref])

    relevant_base_ids = ["A:C1", "A:C1_OI", "A:U1", "A:P3", "C:FIXED_J", "C:P1", "C:P2_FULL", "C:P7"]
    relevant_base_rule_ids = ["a01", "a03", "c01", "c03", "c12"]
    relevant_core_ids = ["CORE20261008:CONTRACT", "CORE20261008:FAMILY", "CORE20261008:MINIMA", "CORE20261008:REQUIRED_INTERSECTION", "CORE20261008:MONOTONE", "CORE20261008:ACTUAL_BRIDGE", "CORE20261008:EXPERIENTIAL_APPLICATION"]
    relevant_ei_ids = ["EI20261008:CONTRACT", "EI20261008:NONTRANSPORT", "EI20261008:CORE_FAMILY", "EI20261008:ACTUAL_BRIDGE", "EI20261008:STRUCTURAL_INTERPRETATION"]
    assert all(i in base_id_set for i in relevant_base_ids)
    assert all(i in set(base_rule_ids) for i in relevant_base_rule_ids)
    assert all(i in set(core_ids) for i in relevant_core_ids)
    assert all(i in {n["id"] for n in ei["nodes"]} for i in relevant_ei_ids)

    result = {
        "schema": "uct-r183-map-audit-v1",
        "base": {
            "sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
            "revision": base["revision"],
            "nodes_traversed": len(base_nodes),
            "rules_traversed": len(base_rules),
            "context_links_traversed": len(base_contexts),
            "node_id_order_sha256": digest_ids(base_ids),
            "rule_id_order_sha256": digest_ids(base_rule_ids),
            "duplicate_node_ids": duplicates(base_ids),
            "duplicate_rule_ids": duplicates(base_rule_ids),
            "missing_node_field_counts": {k: len(v) for k, v in missing_base_node_fields.items()},
            "missing_node_fields": missing_base_node_fields,
            "missing_rule_field_counts": {k: len(v) for k, v in missing_base_rule_fields.items()},
            "missing_rule_fields": missing_base_rule_fields,
            "unresolved_rule_references": unresolved_base_rule_refs,
            "unresolved_context_references": unresolved_base_context_refs,
            "deductive_cycle_nodes": cycle_nodes(base_ids, base_rules),
        },
        "effective_core_layer": {
            "nodes_traversed": len(core_ids),
            "rules_traversed": len(core_rule_ids),
            "duplicate_ids_against_base": sorted(set(core_ids) & base_id_set),
            "duplicate_rule_ids_against_base": sorted(set(core_rule_ids) & set(base_rule_ids)),
            "unresolved_rule_references": unresolved_core_refs,
        },
        "r183_pending_layer": {
            "nodes_traversed": len(r183_ids),
            "rules_traversed": len(r183_rule_ids),
            "duplicate_ids_against_effective": sorted(set(r183_ids) & effective_ids),
            "duplicate_rule_ids_against_effective": sorted(set(r183_rule_ids) & (set(base_rule_ids) | set(core_rule_ids))),
            "unresolved_rule_references": unresolved_r183_refs,
            "all_rules_have_nonempty_all_of": all(bool(r.get("all_of")) for r in r183["rules"]),
            "enabled_as_established_premises": r183["enabled_as_established_premises"],
        },
        "targeted_semantic_scope": {
            "base_nodes_read": relevant_base_ids,
            "base_rules_read": relevant_base_rule_ids,
            "core_nodes_read": relevant_core_ids,
            "ei_pending_nodes_read_as_nonpremise_witnesses": relevant_ei_ids,
            "fixed_sources_read": ["UCT I v1.2 §§2-4", "UCT III v1.0 §§5,7", "TA25 §§3-5"],
            "review_items_preserved_open": ["QC-20261008-10", "IA-QC11", "QC-20261008-12", "QC-20261008-13"],
        },
        "semantic_audit": {
            "status": "AUDIT_INCOMPLETE",
            "full_structural_traversal_completed": True,
            "full_per_item_semantic_reproof_completed": False,
            "exact_unreviewed_base_node_count": len(base_nodes) - len(relevant_base_ids),
            "exact_unreviewed_base_rule_count": len(base_rules) - len(relevant_base_rule_ids),
            "exact_unreviewed_base_context_count": len(base_contexts),
            "reason": "Every base item was structurally traversed, but only the named affected source/claim slice received current-round semantic rereading. Structural validity and acyclicity are not semantic proof.",
        },
    }
    assert not result["base"]["duplicate_node_ids"]
    assert not result["base"]["duplicate_rule_ids"]
    assert not unresolved_base_rule_refs
    assert not unresolved_base_context_refs
    assert not result["base"]["deductive_cycle_nodes"]
    assert not unresolved_core_refs
    assert not unresolved_r183_refs
    assert not result["effective_core_layer"]["duplicate_ids_against_base"]
    assert not result["r183_pending_layer"]["duplicate_ids_against_effective"]
    assert result["r183_pending_layer"]["enabled_as_established_premises"] is False
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
