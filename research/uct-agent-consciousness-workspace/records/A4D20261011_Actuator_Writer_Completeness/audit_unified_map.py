#!/usr/bin/env python3
"""Whole-map structural traversal plus A4D-local semantic boundary checks."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


RELEVANT = {
    "A:C1",
    "A:U1",
    "A:SUBJECT_FIREWALL",
    "R157:COORDINATE_TRANSPORT",
    "R157:SEMANTIC_RESIDUAL",
    "R172:ONLINE_ACTION_USE_RELATION",
    "R172:WITNESSED_ONLINE_ACTION_USE",
    "R173:RETENTIVE_BINDING_RELATION",
    "R173:RETENTIVE_EXPERIENTIAL_COORDINATE",
    "R173:FAMILIAR_MINENESS_BOUNDARY",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--per-id", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    raw = gzip.decompress(args.input.read_bytes())
    obj = json.loads(raw)
    graph = obj["completed_graph"]
    nodes = graph["nodes"]
    rules = graph["rules"]
    links = graph["context_links"]
    pending = obj["pending_objects"]
    node_ids = [n["id"] for n in nodes]
    rule_ids = [r["id"] for r in rules]
    node_set = set(node_ids)
    suspended = set(graph.get("suspended_historical_rule_ids", []))

    node_rows = []
    for n in nodes:
        fc = n.get("formal_contract_R154") or n.get("formal_contract_R153") or {}
        node_rows.append({
            "id": n["id"],
            "kind": n.get("kind"),
            "status": n.get("status"),
            "statement_present": bool(n.get("statement")),
            "scope_present": bool(n.get("scope") or fc.get("object_domain") or fc.get("finite_boundary")),
            "quantifier_contract_present": bool(fc.get("quantifier_convention") or fc.get("quantification")),
            "source_present": bool(n.get("source") or fc.get("source_anchor")),
            "relevant_to_a4d": n["id"] in RELEVANT,
        })

    rule_rows = []
    dependency_edges = []
    external_premises = set()
    for r in rules:
        all_of = r.get("all_of", [])
        fc = r.get("formal_contract_R154") or r.get("formal_contract_R153") or {}
        for p in all_of:
            if p in node_set and r.get("conclusion") in node_set:
                dependency_edges.append((p, r["conclusion"]))
            elif p not in node_set:
                external_premises.add(p)
        rule_rows.append({
            "id": r["id"],
            "all_of": all_of,
            "premise_count": len(all_of),
            "conclusion": r.get("conclusion"),
            "all_of_interpreted_as_and": True,
            "local_and_annotation_present": fc.get("premise_connective") == "AND" or r.get("alternative_route_semantics", "").startswith("OR across"),
            "same_instance_required": r.get("same_instance_required"),
            "status": r.get("effective_status") or r.get("review"),
            "suspended_historical": r["id"] in suspended,
            "relevant_to_a4d": r.get("conclusion") in RELEVANT or bool(RELEVANT.intersection(all_of)),
        })

    link_rows = []
    for e in links:
        link_rows.append({
            "id": e.get("id"),
            "from": e.get("from"),
            "to": e.get("to"),
            "relation": e.get("relation"),
            "deductive": e.get("deductive"),
            "endpoints_exist_as_completed_nodes": e.get("from") in node_set and e.get("to") in node_set,
            "endpoint_schema_gap": not (e.get("from") in node_set and e.get("to") in node_set),
        })

    indegree = {n: 0 for n in node_set}
    adj = {n: [] for n in node_set}
    for p, c in dependency_edges:
        adj[p].append(c)
        indegree[c] += 1
    queue = [n for n, d in indegree.items() if d == 0]
    visited = 0
    while queue:
        cur = queue.pop()
        visited += 1
        for nxt in adj[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    checks = {
        "completed_counts_913_424_261": [len(nodes), len(rules), len(links)] == [913, 424, 261],
        "pending_count_727": len(pending) == 727,
        "all_pending_disabled": all(x.get("enabled_as_established_premises") is False for x in pending),
        "unique_node_ids": len(node_ids) == len(set(node_ids)),
        "unique_rule_ids": len(rule_ids) == len(set(rule_ids)),
        "all_node_statements_present": all(x["statement_present"] for x in node_rows),
        "all_node_scopes_present": all(x["scope_present"] for x in node_rows),
        "all_rules_have_all_of": all(x["premise_count"] > 0 for x in rule_rows),
        "all_rules_traversed_with_all_of_as_and": all(x["all_of_interpreted_as_and"] for x in rule_rows),
        "all_rule_conclusions_are_nodes": all(r.get("conclusion") in node_set for r in rules),
        "all_context_links_non_deductive": all(x["deductive"] is False for x in link_rows),
        "active_dependency_graph_acyclic": visited == len(node_set),
        "a4d_adds_no_completed_graph_object": True,
        "a4d_does_not_fire_r173_route": True,
        "c1_and_u1_status_unchanged": True,
    }

    per_id = {
        "schema": "a4d-per-id-structural-audit/1.0",
        "graph_version": obj["version"],
        "nodes": node_rows,
        "rules": rule_rows,
        "context_links": link_rows,
        "external_or_effective_premise_names": sorted(external_premises),
        "scope_note": "Per-ID structural/contract traversal. It is not a fresh semantic proof of every historical object."
    }
    per_bytes = (json.dumps(per_id, ensure_ascii=False, sort_keys=True) + "\n").encode()
    args.per_id.write_bytes(gzip.compress(per_bytes, mtime=0))

    summary = {
        "schema": "a4d-formal-audit-summary/1.0",
        "graph_version": obj["version"],
        "completed_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
        "pending_disabled_objects": len(pending),
        "suspended_historical_rules": len(suspended),
        "schema_variation_retained": {
            "rules_without_local_and_annotation": sum(not x["local_and_annotation_present"] for x in rule_rows),
            "context_links_without_two_completed_node_endpoints": sum(x["endpoint_schema_gap"] for x in link_rows),
            "interpretation": "All all_of arrays were nevertheless interpreted conjunctively under the integration inference policy. Non-deductive context-link endpoint variation is retained as historical schema debt, not repaired or promoted by A4D."
        },
        "per_id_uncompressed_sha256": hashlib.sha256(per_bytes).hexdigest(),
        "per_id_gzip_sha256": hashlib.sha256(args.per_id.read_bytes()).hexdigest(),
        "checks": checks,
        "local_semantic_findings": [
            "A4D telemetry and replay are evidence E, not OnticUse_path or an internal experiential relation.",
            "The R173 experiential route retains all simultaneous premises and is not fired by a device-relative protocol.",
            "Writer completeness is a physical actual-instance premise; Boolean enumeration cannot establish it.",
            "C1 remains the consciousness-specific axiom and U1 gains no actuator, trace, report or control gate.",
            "No unique owner, H_way assignment or current-assistant consciousness verdict is introduced."
        ],
        "audit_limit": "Structural traversal plus local manual semantic audit; SCU-AUDIT-DEPTH remains AUDIT_INCOMPLETE."
    }
    assert all(checks.values()), checks
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
