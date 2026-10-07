#!/usr/bin/env python3
"""Structural, exact-result, scope, and direction validation for R170."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Open_World_Remainder_Certificates_v0_1.md"
RESULTS = HERE / "EXACT_CHECKS.json"
OUT = HERE / "MAP_AUDIT.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


g = json.loads(GRAPH.read_text())
ext = json.loads(EXT.read_text())
results = json.loads(RESULTS.read_text())
checks = []


def record(name, ok, detail):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


record("note_hash_frozen", digest(NOTE) == ext["note_sha256"], digest(NOTE))
record("graph_revision", g["revision"] == "R170-v1.0", g["revision"])
record(
    "graph_counts",
    (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (487, 234, 133),
    {"nodes": len(g["nodes"]), "rules": len(g["rules"]), "context_links": len(g["context_links"])},
)
node_ids = [n["id"] for n in g["nodes"]]
rule_ids = [r["id"] for r in g["rules"]]
nodes = set(node_ids)
record("unique_ids", len(node_ids) == len(nodes) and len(rule_ids) == len(set(rule_ids)), {"nodes": len(nodes), "rules": len(set(rule_ids))})
bad_rules = [r["id"] for r in g["rules"] if r["conclusion"] not in nodes or not set(r["all_of"]) <= nodes]
bad_links = [link for link in g["context_links"] if link["from"] not in nodes or link["to"] not in nodes]
record("all_endpoints_exist", not bad_rules and not bad_links, {"rules": bad_rules, "links": bad_links})
adj = {n: [] for n in nodes}
indeg = {n: 0 for n in nodes}
for rule in g["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"])
        indeg[rule["conclusion"]] += 1
queue = [n for n, degree in indeg.items() if degree == 0]
seen = 0
while queue:
    current = queue.pop()
    seen += 1
    for nxt in adj[current]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            queue.append(nxt)
record("dag", seen == len(nodes), {"visited": seen, "total": len(nodes)})
parent = deepcopy(g)
parent["nodes"] = parent["nodes"][:477]
parent["rules"] = parent["rules"][:227]
parent["context_links"] = parent["context_links"][:129]
parent["revision"] = "R169-v1.0"
parent.pop("research_R170")
parent_hash = sha256((json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode()).hexdigest()
record("exact_parent_reconstruction", parent_hash == ext["parent_sha256"], parent_hash)
rnodes = g["nodes"][477:]
rrules = g["rules"][227:]
fields = ("statement", "domain", "scope", "source", "source_lineage", "status", "proof", "counterexamples_and_limits", "formal_contract_R170")
record("new_node_contract_fields", all(all(n.get(field) for field in fields) for n in rnodes), [n["id"] for n in rnodes])
record("new_rules_explicit_all_of", all(r.get("all_of") and r["formal_contract_R170"]["premise_connective"] == "AND" for r in rrules), {r["id"]: r["all_of"] for r in rrules})
expected = {r["id"]: r["all_of"] for r in ext["rules"]}
actual = {r["id"]: r["all_of"] for r in rrules}
record("joint_premises_exact", actual == expected, actual)
record("partition_requires_target_and_cells", set(actual["r170_remainder_partition"]) == {"R170:TARGET_DOMAIN_ADMISSION_CONTRACT", "R170:CELL_ROUTE_COVER_CERTIFICATE"}, actual["r170_remainder_partition"])
record("pointwise_requires_effect_route_and_partition", set(actual["r170_pointwise_remainder_envelope"]) == {"R168:STOCHASTIC_CONTEXTUAL_EFFECT", "R169:DIRECT_ROUTE_ENVELOPE", "R170:OPEN_WORLD_REMAINDER_PARTITION"}, actual["r170_pointwise_remainder_envelope"])
record("amplitude_obstruction_keeps_remainder", set(actual["r170_global_supremum_obstruction"]) == {"R170:OPEN_WORLD_REMAINDER_PARTITION", "R170:SHARP_POINTWISE_REMAINDER_ENVELOPE"}, actual["r170_global_supremum_obstruction"])
measure_premises = {"R170:TARGET_DOMAIN_ADMISSION_CONTRACT", "R170:OPEN_WORLD_REMAINDER_PARTITION", "R170:SHARP_POINTWISE_REMAINDER_ENVELOPE"}
record("mean_and_exceedance_require_measure_contract", set(actual["r170_mean_remainder_bound"]) == measure_premises and set(actual["r170_exceedance_remainder_bound"]) == measure_premises, {"mean": actual["r170_mean_remainder_bound"], "exceedance": actual["r170_exceedance_remainder_bound"]})
record("application_keeps_R169_and_all_strength_distinctions", set(actual["r170_open_world_application_boundary"]) == {"R169:R168_ROUTE_APPLICATION_BOUNDARY", "R170:GLOBAL_SUPREMUM_OBSTRUCTION", "R170:MEAN_REMAINDER_BOUND", "R170:EXCEEDANCE_REMAINDER_BOUND", "R170:OPEN_WORLD_COVERAGE_TRIAGE"}, actual["r170_open_world_application_boundary"])
forbidden = {"A:C1", "A:U1", "F153-11", "F153-17", "R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_gate_or_familiar_mineness", not any(r["conclusion"] in forbidden for r in rrules), [r["conclusion"] for r in rrules])
markers = ("context only", "non-deductive", "obstruction retained", "no target coverage")
record("context_links_non_deductive", all(any(marker in link["relation"].lower() for marker in markers) for link in ext["context_links"]), ext["context_links"])
record(
    "exact_open_world_enumeration",
    results["domains"] == 62
    and results["covered_envelopes"] == 1364
    and results["compatible_effects"] == 66429
    and results["pointwise_checks"] == 323847
    and results["integral_checks"] == 66429
    and results["exceedance_checks"] == 132858
    and results["supremum_witnesses"] == 1001,
    {key: results[key] for key in ("domains", "covered_envelopes", "compatible_effects", "pointwise_checks", "integral_checks", "exceedance_checks", "supremum_witnesses")},
)
record("status_priority", results["status_assignments"] == 32 and sum(results["status_counts"].values()) == 32 and set(results["status_counts"]) == {"INVALID_OPEN_WORLD_PROTOCOL", "COVERAGE_CERTIFICATE_REFUTED", "CLOSED_DOMAIN_AMPLITUDE_CERTIFIED", "OPEN_WORLD_MASS_CERTIFIED", "UNRESOLVED"}, results["status_counts"])
record("claim_limits", all(value is False for value in results["claim_limits"].values()), results["claim_limits"])
required = ["ROUND_RECORD.md", "Open_World_Remainder_Certificates_v0_1.md", "PROOF_LEDGER.json", "GAP_LEDGER.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json", "verify_open_world.py", "EXACT_CHECKS.json", "build_map.py"]
record("required_core_artifacts_present", all((HERE / name).exists() for name in required), required)
payload = {
    "schema": "UCT_R170_MAP_AUDIT/v1",
    "round": "R170",
    "status": "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL",
    "checks": checks,
    "graph_sha256": digest(GRAPH),
    "exact_results_sha256": digest(RESULTS),
    "limitations": [
        "DAG and finite checks do not establish a physical target domain, continuum cell cover, target measure or theory truth.",
        "Sharpness is over the stated bounded-envelope information class unless a separate consumer-kernel realizability theorem is supplied.",
        "No neural completeness, C1 derivation, B_min validation, basal-experience gate or unique owner follows.",
    ],
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": payload["status"], "checks": len(checks), "graph_sha256": payload["graph_sha256"], "exact_results_sha256": payload["exact_results_sha256"]}, indent=2))
if payload["status"] != "PASS":
    raise SystemExit(1)
