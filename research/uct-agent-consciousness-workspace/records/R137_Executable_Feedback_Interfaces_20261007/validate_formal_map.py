"""Check graph bookkeeping, forbidden dependency paths and exact pinned sources.
This is NOT a proof assistant or a physical validation of premises.
"""
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parent.parent
DSOURCE = ROOT / "records/R129_Four_Paper_Integration_20261006"
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
    bad = {x for x in ancestors(n) if x.startswith(("B:","C:","R126:","R127:","N128:","D:")) or x in {"A:TOY_MATH","A:BRIDGE_FWD","A:BRIDGE_REV","A:EPS_CHAIN","A:PHYS_CONT_PATH","A:MEAS"}}
    check(n+" has no downstream finite/empirical backflow", not bad)
check("selected experiential interpretation has actual-support premise", "R127:RELATIONAL_SUPPORT" in ancestors("A:UCTII_EXP"))

source_results = []
for v in graph["source_versions"]:
    raw = (ROOT/v["snapshot_workspace_path"]).read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    gitsha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    check(v["paper"]+" exact byte count", len(raw)==v["bytes"])
    check(v["paper"]+" publication SHA256", sha256==v["sha256"])
    check(v["paper"]+" Git blob identity", gitsha==v["blob_sha"])
    source_results.append({"paper":v["paper"],"bytes":len(raw),"sha256":sha256,"git_blob":gitsha})
legacy = json.loads((ROOT/"records/R128_Unified_Formal_Map_Audit_20261006/sources/A_original_formal_graph_v1_2.json").read_text())
check("original A graph inventory retained", len(legacy["nodes"])==78 and len(legacy["edges"])==105)
check("original A node IDs preserved in namespace", all("A:"+n["id"] in nodes for n in legacy["nodes"]))

baseline=json.loads((RECORD/'baseline/UCT_FORMAL_GRAPH.json').read_text())
changed_nodes={n['id'] for n in baseline['nodes'] if nodes.get(n['id'])!=n}
check('all R136 nodes preserved field-for-field', not changed_nodes)
check('all R136 node IDs retained with 13 new nodes', {n['id'] for n in baseline['nodes']} <= set(nodes) and len(nodes)-len(baseline['nodes'])==13)
current_rules={r['id']:r for r in rules}
changed_rules={r['id'] for r in baseline['rules'] if current_rules.get(r['id'])!=r}
check('all R136 rules preserved field-for-field', not changed_rules)
check('all R136 rule IDs retained with 7 new rules', {r['id'] for r in baseline['rules']} <= set(current_rules) and len(rules)-len(baseline['rules'])==7)
check('all four source papers present', {v['paper'] for v in graph['source_versions']}=={'A','B','C','D'})
doriginal=json.loads((DSOURCE/'sources/D_original_FORMAL_MAP.json').read_text())
check('all original D definitions and claims retained', all('D:'+n['id'] in nodes for n in doriginal['definitions']+doriginal['claims']))
check('all original D allowed edges retained as context', all(any(e['from']=='D:'+a and e['to']=='D:'+b for e in graph['context_links']) for a,b in doriginal['allowed_edges']))
for n in ['D:E1','D:E2','D:E3','D:E4','D:A1','D:S1','D:D7']:
    check(n+' is not a derived proof conclusion', not parents[n])
for n in ['D:F1','D:F2','D:F3','D:PAYOFF','D:VALUE_GAP','D:FRECHET','D:GRID_BOUND','D:SEPARABLE']:
    check(n+' is mathematically independent of C1', 'A:C1' not in ancestors(n))
check('D experiential interpretation retains C1 and actual premise', {'A:C1','D:ACTUAL_CHANGE'}<=ancestors('D:UCT_INTERPRETATION'))
check('D full-rank identification does not pretend to follow from nonidentification alone', set(next(r['all_of'] for r in rules if r['conclusion']=='D:F2'))=={'D:PATH_MODEL','D:DIRECT_ROWS'})
check('D five original prohibited inferences retained', graph['prohibited_inferences_D']==doriginal['prohibited_inferences'])
check('D valence obligation remains OPEN', nodes['D:D7']['status']=='OPEN')
manifest=json.loads((DSOURCE/'SOURCE_MANIFEST.json').read_text())
for v in manifest['new_snapshots']:
    raw=(ROOT/v['snapshot_workspace_path']).read_bytes()
    check(v['name']+' exact source identity', len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==v['blob_sha'])
publication=json.loads((DSOURCE/'sources/D_publication_record.json').read_text())
for snap,remote in [('D_TA24_v1_0.md','from-shutdown-resistance-to-self-continuation-control-v1.0.md'),('D_published_FORMAL_MAP_AND_AUDIT.md','FORMAL-MAP-AND-AUDIT.md'),('D_claims_v1_0.json','claims-v1.0.json')]:
    raw=(DSOURCE/'sources'/snap).read_bytes()
    v=next(f for f in publication['files'] if f['name']==remote)
    check(snap+' matches publication manifest', len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'])
check('novelty correction retained', bool(graph['attribution_amendments']))

review=json.loads((RECORD/'REVIEW_MATRIX.json').read_text())
check('every rule has a second-review entry', {r['rule_id'] for r in review['rules']}=={r['id'] for r in rules} and len(review['rules'])==len(rules))
check('nine B theory bridges explicitly retain source-fidelity limits', sum(r['review']=='CONDITIONAL_BRIDGE_SCOPE_REVIEW' for r in review['rules'])==9)
check('F20 amendment matches exact changed IDs', graph['audit_amendments'][-1]['affected_nodes']==['R127:MEDIATION','R127:P2'] and graph['audit_amendments'][-1]['affected_rules']==['r127_2'])
check('R127 conditional cut law explicitly defined', 'P(C|x,b,q)' in nodes['R127:MEDIATION']['statement'] and 'joint cut (C,B)' in nodes['R127:MEDIATION']['statement'])
check('project memory exists and carries current baseline', 'R137-v1.0' in (ROOT/'MEMORY.md').read_text())
ledger=(RECORD/'PROOF_LEDGER.md').read_text()
check('all old and new node scope fields exported in readable ledger', sum('scope' in n for n in nodes.values())==105 and all(n['scope'] in ledger for n in nodes.values() if 'scope' in n))

for n in [n for n in nodes if n.startswith('R137:') and nodes[n]['kind']=='THEOREM']:
    check(n+' mathematics independent of C1', 'A:C1' not in ancestors(n))
check('R135 experiential application retains C1 and actual-support premise', {'A:C1','R135:ACTUAL_PROFILE'}<=ancestors('R135:UCT_INTERPRETATION'))
import csv
crosswalk=list(csv.DictReader((ROOT/'records/R131_Theorem_Synthesis_and_Archive_20261006/THOUGHT_EXPERIMENT_CROSSWALK.csv').open()))
check('38 consecutive case IDs without duplicates', len(crosswalk)==38 and {r['case_id'] for r in crosswalk}=={f'X{i:02d}' for i in range(1,39)})
check('all case graph references resolve', all(x in nodes for r in crosswalk for x in r['map_nodes'].split(';')))
check('47 historical family rows', len(list(csv.DictReader((ROOT/'records/R131_Theorem_Synthesis_and_Archive_20261006/HISTORICAL_FAMILIES.csv').open())))==47)
check('published four-source manifest unchanged', graph['source_versions']==baseline['source_versions'])
check('R137 counts correct', len(nodes)==328 and len(rules)==157)

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
