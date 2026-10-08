#!/usr/bin/env python3
"""Whole-base structural traversal and scoped semantic audit for R184."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "UCT_FORMAL_GRAPH.json"
CORE = ROOT / "records/CORE20261008_Target_Relative_Support/MAP_EXTENSION.json"
EI = ROOT / "records/EI20261008_Architecture_Dependence/MAP_EXTENSION.json"
R183 = ROOT / "records/R183_Target_Relative_Experiential_Relevance_20261008/MAP_EXTENSION.json"
OO = ROOT / "records/OO20261008_Task_Access/MAP_EXTENSION.json"
RU = ROOT / "records/RU20261008_Reliability_and_Use/MAP_EXTENSION.json"
R184 = Path(__file__).resolve().parent / "MAP_EXTENSION.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest_ids(ids):
    return hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()


def duplicates(values):
    return sorted(k for k, v in Counter(values).items() if v > 1)


def cycles(ids, rules):
    graph = defaultdict(set)
    for rule in rules:
        for p in rule.get("all_of", []):
            graph[p].add(rule["conclusion"])
    state, stack, found = {}, [], set()

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

    for n in ids:
        if state.get(n, 0) == 0:
            visit(n)
    return sorted(found)


def unresolved(rules, ids):
    out = []
    for rule in rules:
        for ref in rule.get("all_of", []) + [rule.get("conclusion")]:
            if ref not in ids:
                out.append([rule.get("id"), ref])
    return out


def main():
    base, core, ei, r183, oo, ru, r184 = map(read, (BASE, CORE, EI, R183, OO, RU, R184))
    base_nodes, base_rules, contexts = base["nodes"], base["rules"], base["context_links"]
    base_ids = [n["id"] for n in base_nodes]
    base_rule_ids = [r["id"] for r in base_rules]
    base_set = set(base_ids)
    context_missing = []
    for i, link in enumerate(contexts):
        for side in ("from", "to"):
            if link.get(side) not in base_set:
                context_missing.append([i, side, link.get(side)])

    layers = [("core", core), ("ei_pending", ei), ("r183_pending", r183), ("oo_pending", oo), ("ru_pending", ru), ("r184_pending", r184)]
    known_ids, known_rules = set(base_ids), set(base_rule_ids)
    layer_audit = {}
    for name, layer in layers:
        ids = [n["id"] for n in layer["nodes"]]
        rules = layer["rules"]
        rule_ids = [r["id"] for r in rules]
        layer_audit[name] = {
            "nodes_traversed": len(ids),
            "rules_traversed": len(rules),
            "duplicate_ids_against_prior": sorted(set(ids) & known_ids),
            "duplicate_rule_ids_against_prior": sorted(set(rule_ids) & known_rules),
            "unresolved_rule_references": unresolved(rules, known_ids | set(ids)),
            "rules_with_empty_all_of": sorted(r["id"] for r in rules if not r.get("all_of")),
            "nodes_missing_scope": sorted(n["id"] for n in layer["nodes"] if "scope" not in n),
            "rules_missing_statement": sorted(r["id"] for r in rules if "statement" not in r),
            "enabled_as_established_premises": layer.get("enabled_as_established_premises"),
        }
        known_ids.update(ids)
        known_rules.update(rule_ids)

    all_rules = base_rules + sum((layer[1]["rules"] for layer in layers), [])
    targeted_nodes = ["A:ACTUAL_TOKEN", "A:C1", "A:U1", "A:P3", "A:P6", "C:FIXED_J", "C:P1", "C:P2_FULL", "C:P7"]
    targeted_rules = ["a01", "a03", "c01", "c03", "c12"]
    assert all(x in base_set for x in targeted_nodes)
    assert all(x in set(base_rule_ids) for x in targeted_rules)

    missing_node_fields = {f: sorted(n.get("id", "<missing>") for n in base_nodes if f not in n) for f in ("id", "kind", "statement", "scope", "status")}
    missing_rule_fields = {f: sorted(r.get("id", "<missing>") for r in base_rules if f not in r) for f in ("id", "all_of", "conclusion", "statement")}
    result = {
        "schema": "uct-r184-map-audit-v1",
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
            "missing_rule_fields": missing_rule_fields
        },
        "layers": layer_audit,
        "targeted_semantic_scope": {
            "base_nodes_read": targeted_nodes,
            "base_rules_read": targeted_rules,
            "fixed_sources_read": ["UCT I v1.2 §§2.1-2.5,C1/U1,6.1", "UCT III v1.0 §§4-5", "TA25 §§3-8", "R179 prior-paper overlap audit", "R181-R183 main notes and ledgers"],
            "pending_layers_read": ["CORE20261008", "EI20261008 as nonpremise witness", "R183", "OO20261008 preserved but unused", "RU20261008 preserved but unused", "R184"],
            "review_items_preserved_open": ["QC-20261008-10", "IA-QC11", "QC-20261008-12", "QC-20261008-13"]
        },
        "semantic_coverage": {
            "full_structural_traversal_completed": True,
            "full_per_item_semantic_reproof_completed": False,
            "exact_unreviewed_base_node_count": len(base_nodes) - len(targeted_nodes),
            "exact_unreviewed_base_rule_count": len(base_rules) - len(targeted_rules),
            "exact_unreviewed_base_context_count": len(contexts),
            "reason": "All visible IDs and references were structurally checked; only the named affected slice was semantically reread. Acyclicity and schema presence are not theoretical truth."
        },
        "direction_audit": {
            "concepts": "Target, retained content, actual route use, evidence of use, selected capability, experience-internal counterpart and named feeling remain distinct.",
            "quantifiers": "Finite checks range only over four declared architectures and two targets; no universal human mechanism is inferred.",
            "all_of": "Every application keeps bearer, time, signature, TBI, no-reissue, boundary, protocol, actual membership and C1 together for one instance.",
            "joint_satisfiability": "Toy packages have explicit witnesses; actual application and named phenomenal target are deliberately not asserted satisfiable by the toy model.",
            "object_time_signature_actuality_evidence": "t1 obstruction and t2 release are distinct; copied values are not token identity; perturbation results are evidence, not constitutive membership.",
            "inference_direction": "Resumption supports a route claim only under the fixed model; route relevance does not imply felt trying, and no-report does not imply no experience.",
            "purpose": "The result strengthens a body/action organization account and returns to cross-scale overlap after the reflex counterexample; it does not expand generic certificates."
        }
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
    rendered = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    Path(__file__).with_name("MAP_AUDIT.json").write_text(rendered, encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(Path(__file__).with_name("MAP_AUDIT.json")), "counts": [len(base_nodes), len(base_rules), len(contexts)]}, indent=2))


if __name__ == "__main__":
    main()
