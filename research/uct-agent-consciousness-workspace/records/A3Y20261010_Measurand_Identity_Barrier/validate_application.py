#!/usr/bin/env python3
"""Validate A3Y artifacts and traverse the full effective UCT map."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAP = ROOT / "integration" / "UCT-INTEGRATION-v1.0.0" / "UNIFIED_MAP.json.gz"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


with gzip.open(MAP, "rt", encoding="utf-8") as stream:
    unified = json.load(stream)
graph = unified["completed_graph"]
nodes, rules, links = graph["nodes"], graph["rules"], graph["context_links"]
node_ids = [n["id"] for n in nodes]
rule_ids = [r["id"] for r in rules]
link_ids = [c["id"] for c in links]
node_set = set(node_ids)
assert (len(nodes), len(rules), len(links)) == (913, 424, 261)
assert len(node_set) == len(node_ids)
assert len(set(rule_ids)) == len(rule_ids)
assert len(set(link_ids)) == len(link_ids)

required_nodes = {
    "A:C1", "A:U1", "R157:SEMANTIC_RESIDUAL", "R157:MINENESS_BRIDGE_SCHEMA",
    "R173:RETENTIVE_EXPERIENTIAL_COORDINATE", "R173:FAMILIAR_MINENESS_BOUNDARY",
}
assert required_nodes <= node_set

per_id, missing_refs = [], []
for node in nodes:
    per_id.append({"kind": "node", "id": node["id"], "status": "present"})
for rule in rules:
    all_of = rule.get("all_of", [])
    conclusion = rule.get("conclusion")
    missing = [x for x in all_of + ([conclusion] if conclusion else []) if x not in node_set]
    if missing:
        missing_refs.append({"rule": rule["id"], "missing": missing})
    per_id.append({
        "kind": "rule", "id": rule["id"], "premise_count": len(all_of),
        "connective": "AND", "conclusion": conclusion,
        "reference_status": "ok" if not missing else "missing",
    })
for link in links:
    per_id.append({"kind": "context_link", "id": link["id"], "status": "present"})
assert not missing_refs

exact_actual = json.loads(subprocess.check_output([str(HERE / "check_measurand_identity.py")], text=True))
with (HERE / "EXACT_RESULTS.json").open(encoding="utf-8") as stream:
    exact_saved = json.load(stream)
assert exact_actual == exact_saved
with (HERE / "CLAIM_LEDGER.json").open(encoding="utf-8") as stream:
    claims = json.load(stream)["claims"]
with (HERE / "MAP_EXTENSION.json").open(encoding="utf-8") as stream:
    extension = json.load(stream)
assert [c["id"] for c in claims] == ["A3Y-C1", "A3Y-C2", "A3Y-C3", "A3Y-C4"]
assert extension["prospective_all_of_gate"]["connective"] == "AND"
assert (extension["added_completed_nodes"], extension["added_completed_rules"], extension["added_completed_context_links"]) == (0, 0, 0)

per_id_document = {
    "schema": "uct-a3y-effective-map-per-id-audit-v1",
    "audit_scope": "Structural traversal of every effective node, rule and context link; not full semantic proof.",
    "map_version": unified["version"],
    "completed_graph_sha256_declared": unified["completed_graph_sha256"],
    "counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "records": per_id,
}
raw = json.dumps(per_id_document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
(HERE / "PER_ID_AUDIT.json.gz").write_bytes(gzip.compress(raw, mtime=0))

tracked = [
    "ROUND_RECORD.json", "RESEARCH_NOTE.md", "MEASURAND_CONTRACT.md", "EXACT_RESULTS.json",
    "check_measurand_identity.py", "CLAIM_LEDGER.json", "GAP_LEDGER.md", "SOURCE_SCOPE.json",
    "MAP_EXTENSION.json", "MAP_AUDIT.md", "REVIEW_RESPONSE.md",
    "PUBLICATION_COVERAGE_UPDATE.json", "WORK_LOG.md", "HANDOFF_ZH.md",
]
results = {
    "schema": "uct-a3y-validation-v1",
    "status": "PASS_STRUCTURAL_WITH_DECLARED_SEMANTIC_CEILING",
    "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "all_rule_references_resolve": True,
    "all_rules_treated_as_all_of": True,
    "claim_count": len(claims),
    "exact_h_kernel_count": len(exact_actual["h_kernels_checked"]),
    "completed_graph_additions": {"nodes": 0, "rules": 0, "context_links": 0},
    "semantic_ceiling": "Structural and exact-witness PASS does not establish theory truth, Z=H_way, C_H, O_H, or a full historical semantic audit.",
    "files": {name: sha256(HERE / name) for name in tracked},
}
with (HERE / "RUN_RESULTS.json").open("w", encoding="utf-8") as stream:
    json.dump(results, stream, ensure_ascii=False, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(results, ensure_ascii=False, sort_keys=True))
