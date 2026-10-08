#!/usr/bin/env python3
"""Whole-base structural traversal and scoped semantic audit for R185."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "UCT_FORMAL_GRAPH.json"
LAYER_PATHS = [
    ("core", ROOT / "records/CORE20261008_Target_Relative_Support/MAP_EXTENSION.json"),
    ("ei_pending", ROOT / "records/EI20261008_Architecture_Dependence/MAP_EXTENSION.json"),
    ("r183_pending", ROOT / "records/R183_Target_Relative_Experiential_Relevance_20261008/MAP_EXTENSION.json"),
    ("oo_pending", ROOT / "records/OO20261008_Task_Access/MAP_EXTENSION.json"),
    ("ru_pending", ROOT / "records/RU20261008_Reliability_and_Use/MAP_EXTENSION.json"),
    ("r184_pending", ROOT / "records/R184_Target_Persistence_After_Obstruction_20261008/MAP_EXTENSION.json"),
    ("r185_pending", Path(__file__).resolve().parent / "MAP_EXTENSION.json"),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest_ids(ids):
    return hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()


def duplicates(values):
    return sorted(k for k, v in Counter(values).items() if v > 1)


def unresolved(rules, ids):
    out = []
    for rule in rules:
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]:
            if ref not in ids:
                out.append([rule.get("id"), ref])
    return out


def cycles(ids, rules):
    graph = defaultdict(set)
    for rule in rules:
        for premise in rule.get("all_of", []):
            graph[premise].add(rule["conclusion"])
    state, stack, found = {}, [], set()

    def visit(node):
        state[node] = 1
        stack.append(node)
        for target in graph.get(node, ()):
            if state.get(target, 0) == 0:
                visit(target)
            elif state.get(target) == 1:
                found.update(stack[stack.index(target):])
        stack.pop()
        state[node] = 2

    for node in ids:
        if state.get(node, 0) == 0:
            visit(node)
    return sorted(found)


def main():
    base = read(BASE)
    layers = [(name, read(path)) for name, path in LAYER_PATHS]
    base_nodes, base_rules, contexts = base["nodes"], base["rules"], base["context_links"]
    base_ids = [node["id"] for node in base_nodes]
    base_rule_ids = [rule["id"] for rule in base_rules]
    base_set = set(base_ids)

    context_missing = []
    for index, link in enumerate(contexts):
        for side in ("from", "to"):
            if link.get(side) not in base_set:
                context_missing.append([index, side, link.get(side)])

    known_ids, known_rules = set(base_ids), set(base_rule_ids)
    layer_audit = {}
    for name, layer in layers:
        ids = [node["id"] for node in layer["nodes"]]
        rules = layer["rules"]
        rule_ids = [rule["id"] for rule in rules]
        layer_audit[name] = {
            "nodes_traversed": len(ids),
            "rules_traversed": len(rules),
            "duplicate_ids_against_prior": sorted(set(ids) & known_ids),
            "duplicate_rule_ids_against_prior": sorted(set(rule_ids) & known_rules),
            "unresolved_rule_references": unresolved(rules, known_ids | set(ids)),
            "rules_with_empty_all_of": sorted(rule["id"] for rule in rules if not rule.get("all_of")),
            "nodes_missing_scope": sorted(node["id"] for node in layer["nodes"] if "scope" not in node),
            "rules_missing_statement": sorted(rule["id"] for rule in rules if "statement" not in rule),
            "enabled_as_established_premises": layer.get("enabled_as_established_premises"),
        }
        known_ids.update(ids)
        known_rules.update(rule_ids)

    all_rules = base_rules + sum((layer[1]["rules"] for layer in layers), [])
    targeted_nodes = [
        "A:ACTUAL_TOKEN", "A:C1", "A:U1", "A:P3", "A:P6",
        "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL",
        "R172:INTERFACE_COMPOSITION_THEOREM", "R172:EXPERIENCE_INTERNAL_ACTION_COORDINATE",
    ]
    targeted_rules = ["a01", "a03", "b03", "r157_coordinate_transport", "r157_semantic_residual", "r172_interface_composition", "r172_experience_internal_action_coordinate"]
    assert all(item in base_set for item in targeted_nodes)
    assert all(item in set(base_rule_ids) for item in targeted_rules)

    missing_node_fields = {
        field: sorted(node.get("id", "<missing>") for node in base_nodes if field not in node)
        for field in ("id", "kind", "statement", "scope", "status")
    }
    missing_rule_fields = {
        field: sorted(rule.get("id", "<missing>") for rule in base_rules if field not in rule)
        for field in ("id", "all_of", "conclusion", "statement")
    }

    result = {
        "schema": "uct-r185-map-audit-v1",
        "status": "AUDIT_INCOMPLETE",
        "base": {
            "path": "UCT_FORMAL_GRAPH.json",
            "revision": base["revision"],
            "sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
            "nodes_traversed": len(base_nodes),
            "rules_traversed": len(base_rules),
            "context_links_traversed": len(contexts),
            "node_id_order_sha256": digest_ids(base_ids),
            "rule_id_order_sha256": digest_ids(base_rule_ids),
            "duplicate_node_ids": duplicates(base_ids),
            "duplicate_rule_ids": duplicates(base_rule_ids),
            "unresolved_rule_references": unresolved(base_rules, base_set),
            "unresolved_context_references": context_missing,
            "deductive_cycle_nodes_with_all_visible_layers": cycles(list(known_ids), all_rules),
            "missing_node_fields": missing_node_fields,
            "missing_rule_fields": missing_rule_fields,
        },
        "layers": layer_audit,
        "targeted_semantic_scope": {
            "base_nodes_read": targeted_nodes,
            "base_rules_read": targeted_rules,
            "fixed_sources_read": [
                "UCT I v1.2 §§2.1-2.5,3.1-3.5,C1/U1,6.1-6.4,7",
                "TA25 §§3-4,6",
                "CG20261008 full checkpoint",
                "SB20261008 gluing/target-binding note",
                "R157, R172, R183 and R184 relevant contracts",
            ],
            "pending_layers_read": ["CORE20261008", "EI20261008 nonpremise witness", "R183", "OO20261008 preserved but unused", "RU20261008 preserved but unused", "R184", "R185"],
            "review_items_preserved_open": ["QC-20261008-10", "IA-QC11", "QC-20261008-12", "QC-20261008-13"],
        },
        "semantic_coverage": {
            "full_structural_traversal_completed": True,
            "full_per_item_semantic_reproof_completed": False,
            "exact_unreviewed_base_node_count": len(base_nodes) - len(targeted_nodes),
            "exact_unreviewed_base_rule_count": len(base_rules) - len(targeted_rules),
            "exact_unreviewed_base_context_count": len(contexts),
            "reason": "All visible IDs and references were structurally checked. Only the named affected base slice and visible pending layers were semantically reread; structural success is not theoretical truth.",
        },
        "direction_audit": {
            "concepts": "Episode occurrence, carried value, token membership, scientific view, complete token organization, C1 counterpart, named feeling and subjecthood remain distinct.",
            "quantifiers": "R185-C1 ranges over an explicitly fixed actual token family; finite checks range over two targets and crossed inert labels only.",
            "all_of": "Every positive application keeps one episode, occurrence, time, actual token family, complete signatures, faithful inclusions, overlap maps and C1 package simultaneous.",
            "joint_satisfiability": "Shared and copied toy packages have explicit witnesses; actual biological/AI membership and named experience are not asserted by toy satisfiability.",
            "object_time_signature_actuality_evidence": "Occurrence identity includes endpoints, type, mechanism/ports and time; equal values are not identity; perturbations are evidence rather than constitutive membership.",
            "inference_direction": "Actual faithful membership implies incidence; matched outputs do not imply occurrence identity; tokenwise C1 does not imply cross-token numerical phenomenal identity.",
            "unlinked_consistency": "P3/U1 preserve persisting local tokens, P6 separates token/type/lineage, §6 product limits remain, and CG gluing is credited rather than duplicated.",
            "purpose": "The result addresses how one action relation can inhabit overlapping actual processes without an exclusive owner; it does not add a basal gate or feeling label.",
        },
    }

    assert result["base"]["sha256"] == "40d17cd5f61ebcc1bfcea65eb59c3c730208bcfcf69ba92e2f615a993584e3ce"
    assert not result["base"]["duplicate_node_ids"]
    assert not result["base"]["duplicate_rule_ids"]
    assert not result["base"]["unresolved_rule_references"]
    assert not result["base"]["unresolved_context_references"]
    assert not result["base"]["deductive_cycle_nodes_with_all_visible_layers"]
    for audit in layer_audit.values():
        assert not audit["duplicate_ids_against_prior"]
        assert not audit["duplicate_rule_ids_against_prior"]
        assert not audit["unresolved_rule_references"]
        assert not audit["rules_with_empty_all_of"]

    output = Path(__file__).with_name("MAP_AUDIT.json")
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output), "counts": [len(base_nodes), len(base_rules), len(contexts)]}, indent=2))


if __name__ == "__main__":
    main()

