"""Exact scoped countermodel checks and map integrity, not general proof certification."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, combinations
import hashlib,json

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
g=json.loads((ROOT/'UCT_FORMAL_GRAPH.json').read_text())
base=json.loads((HERE/'baseline-graph.json').read_text())
N={n['id']:n for n in g['nodes']};R={r['id']:r for r in g['rules']}
assert len(N)==len(g['nodes'])==391 and len(R)==len(g['rules'])==188
assert set(N)=={n['id'] for n in base['nodes']}
assert set(R)=={r['id'] for r in base['rules']}
for r in R.values():
    assert r['all_of'] and set(r['all_of'])<=N.keys() and r['conclusion'] in N
    assert r['statement']==N[r['conclusion']]['statement']
    assert r['all_of']==next(x for x in base['rules'] if x['id']==r['id'])['all_of']
    assert r['conclusion']!='A:C1'
    assert r['formal_contract_R153']['machine_proof'] is False
for n in N.values():
    assert n['statement'] and n['scope']
    c=n['formal_contract_R153'];assert c['machine_formalized'] is False
    p=ROOT/c['source_anchor']['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==c['source_anchor']['sha256']
    assert all(set(t)<=N.keys() for t in c['root_premise_routes'])
seen=set();active=set();incoming={id:[] for id in N}
for r in R.values():incoming[r['conclusion']].extend(r['all_of'])
def visit(id):
    assert id not in active,('cycle',id)
    if id in seen:return
    active.add(id)
    for p in incoming[id]:visit(p)
    active.remove(id);seen.add(id)
for id in N:visit(id)
assert len(seen)==391
for s in g['source_versions']:
    assert hashlib.sha256((ROOT/s['snapshot_workspace_path']).read_bytes()).hexdigest()==s['sha256']
# A prior atom's status is never silently promoted to machine-verified.
for n in base['nodes']:assert N[n['id']]['status']==n['status']
for key in ['context_links','prohibited_inferences_D']:
    assert g[key]==base[key]

results=[]
def record(id,claim,details):results.append({'id':id,'status':'PASS','claim':claim,'details':details})

# Source correction: retained present p cannot be thrown away merely because r is constant.
states=(0,1);p=lambda s:s;r=lambda s:0;next_s=lambda s:s
joint_equiv=lambda s,t:(p(s),r(s))==(p(t),r(t))
output_equiv=lambda s,t:r(s)==r(t)
assert not joint_equiv(0,1) and output_equiv(0,1)
assert all(joint_equiv(s,t)==(s==t) for s,t in product(states,repeat=2))
record('T01','R126/R127 source correction is material',{'states':2,'p':'identity','r':'constant 0','update':'identity','joint_initial_blocks':2,'r_only_blocks':1,'effect':'The r-only quotient loses required p even at the empty word.'})

# Noninjectivity is existential rather than a universal strict-fiber claim.
j=(0,0,1);sizes=[sum(j[t]==j[s] for t in range(3)) for s in range(3)]
assert sizes==[2,2,1]
record('T02','Strict-fiber quantifier counterexample',{'J':list(j),'fiber_sizes':sizes})

# Probe dual: exact candidates avoid undefined 0/0 and agree with independent grid minima.
def probe_min(a,b):
    candidates={F(0),F(1)}|{y/(x+y) for x,y in zip(a,b) if x+y>0}
    fun=lambda q:sum(max(q*x,(1-q)*y) for x,y in zip(a,b))
    value=min(map(fun,candidates))
    assert all(fun(F(k,60))>=value for k in range(61))
    return value,len(candidates)
cases=[([F(0)],[F(0)],F(0)),([F(1),F(0),F(0)],[F(1,2),F(1,2),F(0)],F(2,3)),
       ([F(3,4),F(1,4),F(0)],[F(1,4),F(3,4),F(0)],F(3,4))]
for a,b,want in cases:assert probe_min(a,b)[0]==want
record('T03','Zero-mass breakpoint guard',{'cases':3,'exact_values':['0','2/3','3/4'],'note':'Grid is a regression check; general piecewise-affine proof is in the rule.'})

# Three-register image-size invariant.
images=[]
for alpha,beta in product((0,1),repeat=2):
    sizes=[]
    for u in (0,1):
        image={(s^u,s^(alpha*b),s^(beta*a)) for s,a,b in product((0,1),repeat=3)}
        sizes.append(len(image))
    assert sizes[0]==sizes[1];images.append(sizes[0])
assert images==[2,4,4,8]
record('T04','Image sizes distinguish three regimes, not four by themselves',{'image_sizes':images})

# Price with an actual nonzero descendant change, not simultaneous copying.
ps=(F(1,3),F(2,3));ws=(F(1),F(2));cs=(F(0),F(1));cp=(F(1),F(0))
mean=lambda vals:sum(p*v for p,v in zip(ps,vals))
bar=mean(ws);current=mean(cs);after=mean([w*c for w,c in zip(ws,cp)])/bar
cov=mean([w*c for w,c in zip(ws,cs)])-bar*current
trans=mean([w*(d-c) for w,d,c in zip(ws,cp,cs)])/bar
assert after-current==cov/bar+trans and trans!=0
record('T05','Selection/transmission decomposition',{'delta':str(after-current),'selection_term':str(cov/bar),'transmission_term':str(trans)})

# A genuinely three-way inconsistency: every pair satisfiable, all three impossible.
witnesses={};triple=0;tested=0
maps=list(product((0,1),repeat=2))
for k,e,r in product(maps,repeat=3):
    tested+=1
    constraints=((k[0]==k[1])==(e[0]==e[1]),r[0]!=r[1] or e[0]==e[1],r[0]==r[1] and k[0]!=k[1])
    if all(constraints):triple+=1
    for pair in combinations(range(3),2):
        if all(constraints[i] for i in pair):witnesses.setdefault(str(pair),{'k':k,'e':e,'r':r})
assert triple==0 and len(witnesses)==3
record('T06','Pairwise consistency does not establish triple consistency',{'assignments':tested,'all_pairs_witnessed':witnesses,'triple_models':triple,'general_argument':'C1 gives e(x)!=e(y); r equality plus e=h r gives e(x)=e(y).'})

# Fiber factorization on all maps with 3-element domain / 2-element output.
checked=0
for rep,target in product(product((0,1),repeat=3),repeat=2):
    fibers=all(rep[x]!=rep[y] or target[x]==target[y] for x,y in product(range(3),repeat=2))
    exists=any(all(h[rep[x]]==target[x] for x in range(3)) for h in product((0,1),repeat=2))
    assert fibers==exists;checked+=1
record('T07','Factorization and quantifiers in a complete bounded model class',{'map_pairs':checked,'domain_size':3,'output_size':2,'limitation':'General set theorem uses P04, not this enumeration.'})

# Joint law counterexample with unchanged individual marginals.
laws=[]
for z in (0,1):
    law={(a,b):F(sum((u,u^z)==(a,b) for u in (0,1)),2) for a,b in product((0,1),repeat=2)}
    for i in (0,1):assert sum(v for pair,v in law.items() if pair[i]==0)==F(1,2)
    laws.append(law)
tv=sum(abs(laws[0][x]-laws[1][x]) for x in laws[0])/2
assert tv==1
record('T08','Marginal closure does not entail joint closure',{'joint_TV':str(tv),'both_coordinate_marginals':'fair'})

# Simultaneous premises and policy quantifier order.
good=[{0},{1}]
assert all(good) and not set.intersection(*good)
sets=[{0,1},{1,2},{0,2}]
assert all(a&b for a,b in combinations(sets,2)) and not set.intersection(*sets)
record('T09','Common-policy and joint-intersection obstructions',{'individual_actions_exist':True,'common_action_exists':False,'three_pairwise_intersecting_sets_have_common_element':False})

# Countermodel to the overstrong half-diameter equality claim.
simplex=[(F(a,12),F(b,12),F(12-a-b,12)) for a in range(13) for b in range(13-a)]
radius=min(max(1-p[i] for i in range(3)) for p in simplex)
assert radius==F(2,3)
record('T10','Three point masses have radius 2/3, diameter one',{'attained_at':['1/3']*3,'radius':str(radius),'general_lower_bound':'At least one p_i<=1/3, hence max_i(1-p_i)>=2/3.'})

report={'structural_checks':{'nodes':len(N),'rules':len(R),'DAG':True,'all_source_hashes':True,
 'prior_ids_and_all_of_preserved':True,'all_rule_conclusions_synchronized':True,
 'context_links_not_promoted':True,'no_derivation_of_C1':True},
 'exact_checks':results,'all_checks_pass':True,
 'not_established':['truth of C1','actual physical completeness','specific self-experience bridge','all-source semantic consistency','proof-assistant verification','numerical-record reproduction']}
(HERE/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'structure':report['structural_checks'],'exact_checks':len(results),'pass':True,'limitations':report['not_established']},indent=2))
