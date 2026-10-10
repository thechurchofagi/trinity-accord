#!/usr/bin/env python3
"""Validate the scoped A3X application and traverse the effective graph."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


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
nodes = graph["nodes"]
rules = graph["rules"]
links = graph["context_links"]
node_ids = [n["id"] for n in nodes]
rule_ids = [r["id"] for r in rules]
link_ids = [c["id"] for c in links]
node_set = set(node_ids)

assert (len(nodes), len(rules), len(links)) == (913, 424, 261)
assert len(node_set) == len(node_ids)
assert len(set(rule_ids)) == len(rule_ids)
assert len(set(link_ids)) == len(link_ids)

missing_refs = []
per_id = []
for node in nodes:
    per_id.append({"kind": "node", "id": node["id"], "status": "present"})
for rule in rules:
    all_of = rule.get("all_of", [])
    conclusion = rule.get("conclusion")
    missing = [ref for ref in all_of + ([conclusion] if conclusion else []) if ref not in node_set]
    if missing:
        missing_refs.append({"rule": rule["id"], "missing": missing})
    per_id.append(
        {
            "kind": "rule",
            "id": rule["id"],
            "premise_count": len(all_of),
            "connective": "AND",
            "conclusion": conclusion,
            "reference_status": "ok" if not missing else "missing",
        }
    )
for link in links:
    per_id.append({"kind": "context_link", "id": link["id"], "status": "present"})

assert not missing_refs

with (HERE / "SEMANTIC_PROBES.json").open(encoding="utf-8") as stream:
    probes = json.load(stream)
with (HERE / "CLAIM_LEDGER.json").open(encoding="utf-8") as stream:
    claims = json.load(stream)
with (HERE / "MAP_EXTENSION.json").open(encoding="utf-8") as stream:
    extension = json.load(stream)

probe_ids = [p["id"] for p in probes["probes"]]
claim_ids = [c["id"] for c in claims["claims"]]
assert len(probe_ids) == len(set(probe_ids)) == 9
assert len(claim_ids) == len(set(claim_ids)) == 4
assert all("H_way_truth" not in p for p in probes["probes"])
assert probes["ground_truth_policy"] == "No probe assigns a correct H_way rating."
assert extension["added_completed_nodes"] == 0
assert extension["added_completed_rules"] == 0
assert extension["added_completed_context_links"] == 0
assert extension["prospective_all_of_gate"]["connective"] == "AND"

per_id_document = {
    "schema": "uct-a3x-effective-map-per-id-audit-v1",
    "audit_scope": "Structural traversal of every effective node, rule, and context link; not full semantic proof.",
    "map_version": unified["version"],
    "completed_graph_sha256_declared": unified["completed_graph_sha256"],
    "counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "records": per_id,
}
per_id_bytes = json.dumps(
    per_id_document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
(HERE / "PER_ID_AUDIT.json.gz").write_bytes(gzip.compress(per_id_bytes, mtime=0))

results = {
    "schema": "uct-a3x-validation-v1",
    "status": "PASS_STRUCTURAL_WITH_DECLARED_SEMANTIC_CEILING",
    "effective_counts": {"nodes": len(nodes), "rules": len(rules), "context_links": len(links)},
    "all_rule_references_resolve": True,
    "all_rules_treated_as_all_of": True,
    "semantic_probe_count": len(probe_ids),
    "claim_count": len(claim_ids),
    "completed_graph_additions": {"nodes": 0, "rules": 0, "context_links": 0},
    "semantic_ceiling": "Structural PASS does not establish theory truth, C_H, O_H, or a full historical semantic audit.",
    "files": {
        name: sha256(HERE / name)
        for name in [
            "ROUND_RECORD.json",
            "RESEARCH_NOTE.md",
            "ENDPOINT_CONTENT_PROTOCOL.md",
            "SEMANTIC_PROBES.json",
            "CLAIM_LEDGER.json",
            "GAP_LEDGER.md",
            "SOURCE_SCOPE.json",
            "MAP_EXTENSION.json",
            "MAP_AUDIT.md",
            "REVIEW_RESPONSE.md",
            "PUBLICATION_COVERAGE_UPDATE.json",
            "WORK_LOG.md",
        ]
    },
}
with (HERE / "RUN_RESULTS.json").open("w", encoding="utf-8") as stream:
    json.dump(results, stream, ensure_ascii=False, indent=2, sort_keys=True)
    stream.write("\n")

print(json.dumps(results, ensure_ascii=False, sort_keys=True))
