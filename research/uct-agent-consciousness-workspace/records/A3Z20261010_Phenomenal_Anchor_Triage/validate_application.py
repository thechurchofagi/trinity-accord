#!/usr/bin/env python3
"""Validate A3Z artifacts and traverse the full authoritative effective map."""

import gzip
import hashlib
import json
from pathlib import Path
import subprocess

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
assert len(node_set) == len(node_ids)
assert len({r["id"] for r in rules}) == len(rules)
assert len({c["id"] for c in links}) == len(links)

required = {"A:C1", "A:U1", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA", "R157:REPORT_COVERAGE_LIMIT", "R173:FIXED_FAMILIAR_TARGET_CONTRACT", "R173:RETENTIVE_EXPERIENTIAL_COORDINATE", "R173:THREE_TARGET_SEPARATION", "R173:FAMILIAR_MINENESS_BOUNDARY"}
assert required <= node_set

per_id = [{"kind": "node", "id": n["id"], "status": "present"} for n in nodes]
for rule in rules:
    all_of = rule.get("all_of", [])
    conclusion = rule.get("conclusion")
    missing = [x for x in all_of + ([conclusion] if conclusion else []) if x not in node_set]
    assert not missing, (rule["id"], missing)
    per_id.append({"kind": "rule", "id": rule["id"], "premise_count": len(all_of), "connective": "AND", "conclusion": conclusion, "reference_status": "ok"})
per_id.extend({"kind": "context_link", "id": c["id"], "status": "present"} for c in links)

subprocess.check_call([str(HERE / "check_anchor_triage.py")])
exact = json.loads((HERE / "EXACT_RESULTS.json").read_text(encoding="utf-8"))
assert exact["functions_enumerated"] == 256 and exact["survivor_count"] == 2
claims = json.loads((HERE / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))["claims"]
assert [c["id"] for c in claims] == ["A3Z-C1", "A3Z-C2", "A3Z-C3", "A3Z-C4"]
extension = json.loads((HERE / "MAP_EXTENSION.json").read_text(encoding="utf-8"))
assert extension["prospective_all_of_gate"]["connective"] == "AND"
assert (extension["added_completed_nodes"], extension["added_completed_rules"], extension["added_completed_context_links"]) == (0, 0, 0)

audit = {
    "schema": "uct-a3z-effective-map-per-id-audit-v1",
    "audit_scope": "Every effective node, rule, and context link structurally traversed; this is not a global semantic proof.",
    "map_version": unified["version"],
    "counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "records": per_id,
}
raw = json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
(HERE / "PER_ID_AUDIT.json.gz").write_bytes(gzip.compress(raw, mtime=0))

tracked = ["ROUND_RECORD.json", "RESEARCH_NOTE.md", "ANCHOR_CONTRACT.md", "EXACT_RESULTS.json", "check_anchor_triage.py", "CLAIM_LEDGER.json", "GAP_LEDGER.md", "SOURCE_SCOPE.json", "MAP_EXTENSION.json"]
result = {
    "schema": "uct-a3z-validation-v1",
    "status": "PASS_STRUCTURAL_WITH_DECLARED_SEMANTIC_CEILING",
    "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "all_rule_references_resolve": True,
    "all_rules_treated_as_all_of": True,
    "exact_functions_enumerated": exact["functions_enumerated"],
    "exact_survivors": exact["survivor_count"],
    "completed_graph_additions": {"nodes": 0, "rules": 0, "context_links": 0},
    "semantic_ceiling": "PASS does not establish bridge truth, H_way identity, manipulation fidelity, joint application satisfiability, or global theory truth.",
    "files": {name: sha256(HERE / name) for name in tracked},
}
(HERE / "RUN_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
