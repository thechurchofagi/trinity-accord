"""Check graph bookkeeping, forbidden dependency paths and exact pinned sources.
This is NOT a proof assistant or a physical validation of premises.
"""
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parent.parent
graph = json.loads((ROOT / "UCT_FORMAL_GRAPH.json").read_text())
nodes = {n["id"]: n for n in graph["nodes"]}
rules = graph["rules"]
checks = []
def check(name, condition):
    checks.append({"check": name, "pass": bool(condition)})
    if not condition:
        raise AssertionError(name)

check("unique node IDs", len(nodes) == len(graph["nodes"]))
check("unique rule IDs", len({r["id"] for r in rules}) == len(rules))
check("no unresolved review markers", all(n["status"] != "REVIEW_PENDING" for n in nodes.values()))
check("rule endpoints exist", all(r["conclusion"] in nodes and all(p in nodes for p in r["all_of"]) for r in rules))
check("conjunctive rules have premises, claim, source and proof", all(r["all_of"] and r["statement"] and r["source"] and r["proof_sketch"] for r in rules))
check("no direct self-dependency", all(r["conclusion"] not in r["all_of"] for r in rules))
check("context endpoints exist", all(e["from"] in nodes and e["to"] in nodes for e in graph["context_links"]))
parents, children = defaultdict(set), defaultdict(set)
for r in rules:
    for p in r["all_of"]:
        parents[r["conclusion"]].add(p)
        children[p].add(r["conclusion"])
degree = {n: len(parents[n]) for n in nodes}
queue = deque(n for n in nodes if degree[n] == 0)
order = []
while queue:
    n = queue.popleft()
    order.append(n)
    for c in sorted(children[n]):
        degree[c] -= 1
        if degree[c] == 0:
            queue.append(c)
check("acyclic union of proof-rule dependencies", len(order) == len(nodes))
def ancestors(n):
    found = set()
    stack = list(parents[n])
    while stack:
        p = stack.pop()
        if p not in found:
            found.add(p)
            stack.extend(parents[p])
    return found
check("C1 remains an axiom without incoming inference", not parents["A:C1"] and nodes["A:C1"]["status"] == "FIXED_AXIOM")
check("U1 is not an input to U2", "A:U1" not in ancestors("A:U2"))
check("U2 is not an input to U1", "A:U2" not in ancestors("A:U1"))
check("E1 does not require continuity", "A:U2" not in ancestors("A:E1") and "A:EPS_CHAIN" not in ancestors("A:E1"))
check("E2 does not require U1", "A:U1" not in ancestors("A:E2"))
for n in ["A:E3","A:ORBIT_LEMMA","B:REP","A:UCTII_RECON","C:P2_COORD","C:P4","C:P5","C:P6","C:P7","R126:P2","R126:P3","R126:P4","R127:P1","R127:P2","R127:P3","N128:DET_JOIN","N128:MARKOV_JOIN","N128:JOINT_CRITERION"]:
    check(n+" mathematics independent of C1", "A:C1" not in ancestors(n))
check("full-type NESIG retains C1", "A:C1" in ancestors("C:P1"))
check("full identification retains C1", "A:C1" in ancestors("C:P2_FULL"))
check("screened-history experiential equality excludes P6", "A:P6" not in ancestors("A:GHOST_EQ"))
check("screened-history lineage addendum includes P6", "A:P6" in ancestors("A:GHOST_TOKEN_NOTE"))
synthesis = [set(r["all_of"]) for r in rules if r["conclusion"] == "A:EVOL_SYNTH"]
check("evolutionary synthesis has two alternative routes", len(synthesis)==2 and {"A:E1","A:E2"} in synthesis and {"A:E1","A:U2_APP"} in synthesis)
for n in ["A:C1","A:U1","A:U2"]:
    bad = {x for x in ancestors(n) if x.startswith(("B:","C:","R126:","R127:","N128:")) or x in {"A:TOY_MATH","A:BRIDGE_FWD","A:BRIDGE_REV","A:EPS_CHAIN","A:PHYS_CONT_PATH","A:MEAS"}}
    check(n+" has no downstream finite/empirical backflow", not bad)
check("selected experiential interpretation has actual-support premise", "R127:RELATIONAL_SUPPORT" in ancestors("A:UCTII_EXP"))

source_results = []
for v in graph["source_versions"]:
    raw = (RECORD/v["snapshot"]).read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    gitsha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    check(v["paper"]+" exact byte count", len(raw)==v["bytes"])
    check(v["paper"]+" publication SHA256", sha256==v["sha256"])
    check(v["paper"]+" Git blob identity", gitsha==v["blob_sha"])
    source_results.append({"paper":v["paper"],"bytes":len(raw),"sha256":sha256,"git_blob":gitsha})
legacy = json.loads((RECORD/"sources/A_original_formal_graph_v1_2.json").read_text())
check("original A graph inventory retained", len(legacy["nodes"])==78 and len(legacy["edges"])==105)
check("original A node IDs preserved in namespace", all("A:"+n["id"] in nodes for n in legacy["nodes"]))

result = {
    "revision":graph["revision"],
    "nodes":len(nodes), "rules":len(rules),
    "dependency_arcs":sum(len(x) for x in children.values()),
    "checks":checks, "all_pass":True,
    "source_snapshots":source_results,
    "scope":"Bookkeeping, stated dependency constraints and source identity only. Not machine proof of the theorem statements, physical premises, target-theory fidelity or exhaustive completeness.",
    "topological_order":order,
}
(RECORD/"MAP_CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"nodes":len(nodes),"rules":len(rules),"checks_passed":len(checks),"all_pass":True,"source_snapshots":source_results},indent=2))
