#!/usr/bin/env python3
"""Validate A4A artifacts and traverse the authoritative effective map."""

import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAP = ROOT / "integration" / "UCT-INTEGRATION-v1.0.0" / "UNIFIED_MAP.json.gz"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


with gzip.open(MAP, "rt", encoding="utf-8") as stream:
    unified = json.load(stream)
graph = unified["completed_graph"]
nodes, rules, links = graph["nodes"], graph["rules"], graph["context_links"]
node_ids = [n["id"] for n in nodes]
node_set = set(node_ids)
assert (len(nodes), len(rules), len(links)) == (913, 424, 261)
assert len(node_ids) == len(node_set)
assert len({r["id"] for r in rules}) == len(rules)
assert len({c["id"] for c in links}) == len(links)

required = {
    "A:C1", "A:U1", "R157:COORDINATE_TRANSPORT", "R157:SEMANTIC_RESIDUAL",
    "R173:RETENTIVE_BINDING_RELATION", "R173:RETENTIVE_EXPERIENTIAL_COORDINATE",
    "R173:FAMILIAR_MINENESS_BOUNDARY",
}
assert required <= node_set

per_id = [{"kind": "node", "id": n["id"], "status": "present"} for n in nodes]
relevant_rules = {}
for rule in rules:
    all_of = rule.get("all_of", [])
    conclusion = rule.get("conclusion")
    missing = [ref for ref in all_of + ([conclusion] if conclusion else []) if ref not in node_set]
    assert not missing, (rule["id"], missing)
    assert isinstance(all_of, list)
    per_id.append({
        "kind": "rule", "id": rule["id"], "premise_count": len(all_of),
        "connective": "AND", "conclusion": conclusion, "reference_status": "ok",
    })
    if rule["id"] in {"r173_retentive_coordinate_transport", "r175_r173_target_boundary_effective"}:
        relevant_rules[rule["id"]] = {"all_of": all_of, "conclusion": conclusion}
per_id.extend({"kind": "context_link", "id": c["id"], "status": "present"} for c in links)

assert relevant_rules["r173_retentive_coordinate_transport"]["all_of"] == [
    "R173:EFFECTIVE_R172_PATH_INSTANCE", "R173:RETENTIVE_BINDING_RELATION", "R157:COORDINATE_TRANSPORT"
]
assert relevant_rules["r175_r173_target_boundary_effective"]["conclusion"] == "R173:FAMILIAR_MINENESS_BOUNDARY"

subprocess.check_call([sys.executable, str(HERE / "check_exact_models.py")])
exact = json.loads((HERE / "EXACT_RESULTS.json").read_text(encoding="utf-8"))
assert exact["all_checks_pass"] and exact["model_count"] == 4
claims = json.loads((HERE / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))["claims"]
assert [claim["id"] for claim in claims] == ["A4A-C1", "A4A-C2", "A4A-C3", "A4A-C4"]
extension = json.loads((HERE / "MAP_EXTENSION.json").read_text(encoding="utf-8"))
assert extension["prospective_total_effect_all_of_gate"]["connective"] == "AND"
assert extension["prospective_controlled_direct_all_of_gate"]["connective"] == "AND"
assert (extension["added_completed_nodes"], extension["added_completed_rules"], extension["added_completed_context_links"]) == (0, 0, 0)

audit = {
    "schema": "uct-a4a-effective-map-per-id-audit-v1",
    "audit_scope": "Every effective node, rule and context link structurally traversed; not a global semantic proof.",
    "map_version": unified["version"],
    "counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "relevant_rules": relevant_rules,
    "records": per_id,
}
raw = json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
(HERE / "PER_ID_AUDIT.json.gz").write_bytes(gzip.compress(raw, mtime=0))

tracked = [
    "ROUND_RECORD.json", "RESEARCH_NOTE.md", "INTERVENTION_CONTRACT.md", "EXACT_RESULTS.json",
    "check_exact_models.py", "CLAIM_LEDGER.json", "GAP_LEDGER.md", "SOURCE_SCOPE.md",
    "MAP_EXTENSION.json", "MAP_AUDIT.md", "REVIEW_RESPONSE.md",
]
result = {
    "schema": "uct-a4a-validation-v1",
    "status": "PASS_STRUCTURAL_WITH_NONINSTALLABILITY_RESULT",
    "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "all_rule_references_resolve": True,
    "all_rules_treated_as_all_of": True,
    "exact_models": exact["model_count"],
    "exact_checks_pass": exact["all_checks_pass"],
    "controlled_five_way_route_jointly_discharged": False,
    "completed_graph_additions": {"nodes": 0, "rules": 0, "context_links": 0},
    "semantic_ceiling": "PASS does not establish an actual intervention, RetBind, H_way identity, C1, or global theory truth.",
    "files": {name: sha256(HERE / name) for name in tracked},
}
(HERE / "RUN_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
