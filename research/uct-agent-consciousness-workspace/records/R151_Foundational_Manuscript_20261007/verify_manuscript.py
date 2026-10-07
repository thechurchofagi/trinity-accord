"""Focused finite checks and graph bookkeeping; not semantic proof certification."""
from pathlib import Path
from itertools import product, permutations, combinations
from collections import defaultdict
import json, hashlib, math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
g=json.loads((ROOT/'UCT_FORMAL_GRAPH.json').read_text())
nodes={n['id']:n for n in g['nodes']}
assert len(nodes)==len(g['nodes'])==391
rule_ids={r['id'] for r in g['rules']}
assert len(rule_ids)==len(g['rules'])==188
adj=defaultdict(list)
for r in g['rules']:
    assert r['all_of'] and r['conclusion'] in nodes
    assert all(x in nodes for x in r['all_of'])
    for x in r['all_of']: adj[x].append(r['conclusion'])
active=set(); seen=set()
def visit(x):
    assert x not in active, ('cycle',x)
    if x in seen:return
    active.add(x)
    for y in adj[x]:visit(y)
    active.remove(x);seen.add(x)
for x in nodes:visit(x)
assert len(json.loads((HERE/'NODE_REVIEW_INDEX.json').read_text()))==391
assert len(json.loads((HERE/'RULE_REVIEW_INDEX.json').read_text()))==188
for c in json.loads((HERE/'MANUSCRIPT_CLAIMS.json').read_text()):
    assert all(x in nodes for x in c['map_nodes'])

# Exhaustive decoder existence rather than only re-evaluating a fiber formula.
def decoder_exists(rep,target):
    labels=tuple(sorted(set(rep))); values=tuple(sorted(set(target)))
    for output in product(values,repeat=len(labels)):
        table=dict(zip(labels,output))
        if all(table[r]==t for r,t in zip(rep,target)):return True
    return False
t2_cases=0
for k in product(range(2),repeat=3):
    for r in product(range(2),repeat=3):
        for flip in range(2):
            e=tuple(v^flip for v in k)
            reflect=all(r[i]!=r[j] or k[i]==k[j] for i in range(3) for j in range(3))
            assert decoder_exists(r,e)==reflect==decoder_exists(r,k)
            t2_cases+=1
assert decoder_exists((0,1,2),(0,0,1))  # external labels can refine a type
assert not decoder_exists((0,0),(0,1))
assert decoder_exists((0,0),(1,1))  # a selected target can still be exact

# Evaluate body-state dynamics, then compare complete labeled sensor laws.
rows=0; pairing_cases=0; classes={}
for n in (2,3):
    perms=list(permutations(range(n))); vectors=list(product(range(2),repeat=n))
    law_groups=defaultdict(list)
    for sigma in perms:
        for tau in perms:
            inv={j:i for i,j in enumerate(tau)}
            relative=tuple(inv[sigma[i]] for i in range(n))
            law=[]; exact=[True]*n
            for m in vectors:
                x=[0]*n
                for i in range(n):x[sigma[i]]=m[i]
                for u in vectors:
                    xp=tuple(x[j]^u[inv[j]] for j in range(n))
                    observed=tuple(xp[sigma[i]] for i in range(n))
                    expected=tuple(m[i]^u[relative[i]] for i in range(n))
                    assert observed==expected
                    for i in range(n):exact[i]&=observed[i]==(m[i]^u[i])
                    law.append(observed);rows+=1
            assert exact==[sigma[i]==tau[i] for i in range(n)]
            law_groups[tuple(law)].append(relative);pairing_cases+=1
    assert len(law_groups)==math.factorial(n)
    assert all(len(v)==math.factorial(n) and len(set(v))==1 for v in law_groups.values())
    assert len({v[0] for v in law_groups.values()})==math.factorial(n)
    classes[str(n)]={'laws':len(law_groups),'pairs_per_law':math.factorial(n)}

# A conjunction cannot be certified by checking only all pairs.
assignments=list(product(range(2),repeat=3))
constraints=(lambda t:t[0]==t[1],lambda t:t[1]==t[2],lambda t:t[0]!=t[2])
assert all(any(all(constraints[i](t) for i in pair) for t in assignments) for pair in combinations(range(3),2))
assert not any(all(c(t) for c in constraints) for t in assignments)
sources=0
for s in g['source_versions']:
    if 'snapshot_workspace_path' in s and 'sha256' in s:
        assert hashlib.sha256((ROOT/s['snapshot_workspace_path']).read_bytes()).hexdigest()==s['sha256']
        sources+=1
result={'status':'PASS','t2_finite_assignments':t2_cases,'rewiring_pairings':pairing_cases,
        'rewiring_state_command_rows':rows,'rewiring_law_classes':classes,
        'joint_inconsistency_control':'PASS','nodes':391,'rules':188,'source_hashes':sources,
        'limits':'Finite checks plus graph bookkeeping; general proofs are in the manuscript. No global semantic consistency, actual realization, phenomenology or independent review is certified.'}
(HERE/'EXACT_AND_STRUCTURAL_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
