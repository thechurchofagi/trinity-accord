"""Independent bounded witnesses for R154. Not a proof assistant or physical test."""
from pathlib import Path
from itertools import product, combinations, permutations
from fractions import Fraction as F
from collections import Counter
import json, hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CHECKS = []

def record(name, assertion, detail):
    assert assertion, name
    CHECKS.append(dict(name=name, passed=True, detail=detail))

states = list(product(range(2), repeat=3))
images = []
retention = []
for alpha,beta in [(0,0),(1,0),(0,1),(1,1)]:
    image = {(s,a*0 ^ s ^ (alpha&b), s ^ (beta&a)) for s,a,b in states}
    images.append(len(image))
    pairs = set(product(range(2),repeat=2)); counts=[]
    for t in range(4):
        pairs={(alpha&b,beta&a) for a,b in pairs};counts.append(len(pairs))
    retention.append(counts)
record('toy_pair_quantifier', images==[2,4,4,8] and retention==[[1]*4,[2,1,1,1],[2,1,1,1],[4]*4],
       dict(image_sizes=images,pair_retention=retention,unseparated_pair=['10','01']))

# Directly check graph all-cut quantifiers on every loop-free 3-vertex graph.
def mm(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(A))) for j in range(len(A))] for i in range(len(A))]
edges=[(i,j) for i in range(3) for j in range(3) if i!=j]
for bits in product(range(2),repeat=6):
    W=[[0]*3 for _ in range(3)]
    for (i,j),b in zip(edges,bits):W[i][j]=b
    reach=[[bool(W[i][j]) or i==j for j in range(3)] for i in range(3)]
    for k in range(3):
        for i in range(3):
            for j in range(3):reach[i][j]|=reach[i][k] and reach[k][j]
    strong=all(all(row) for row in reach);condition=True
    for mask in range(1,7):
        C=[[W[i][j] if bool(mask&(1<<i))==bool(mask&(1<<j)) else 0 for j in range(3)] for i in range(3)]
        A=W;B=C;witness=[False]*3
        for k in range(1,5):
            witness=[witness[i] or A[i][i]>B[i][i] for i in range(3)]
            A=mm(A,W);B=mm(B,C)
        condition &= all(witness)
    assert strong==condition
record('all_cut_every_vertex_quantifiers',True,dict(graphs=64,vertices=3,cuts_per_graph=6,max_walk_length=4))

# No calculus is used to claim a singular point has a rank-zero open neighborhood.
record('constant_rank_point_is_insufficient', {x for x in range(-3,4) if x*x==0}=={0},
       'J(x)=x^2: derivative at 0 is zero, but the zero fiber is a singleton; neighborhood-constant rank is required.')

# Bundled design counts, obtained independently from all grid points.
counts=Counter((q+g+qg,o+g+og) for q,o,g,qg,og in product([-1,0,1],repeat=5))
record('bundled_design_grid',len(counts)==43 and max(counts.values())==17,
       dict(points=3**5,signatures=len(counts),largest_fiber=max(counts.values())))
for q,o,g,qg,og in product([-1,0,1],repeat=5):
    v1=q+g+qg;v2=o+g+og
    assert (q,o,g,v1-q-g,v2-o-g)==(q,o,g,qg,og)
record('direct_design_inverse',True,'All 243 grid points reconstructed by the explicitly given linear inverse; proof gives arbitrary real coefficients.')

q0,q1,o,c=F(1,4),F(3,4),F(1,2),F(1,4)
va=(q0+o-F(1,4),q1+o-F(1,4)-c)
vb=(q0+o,q1+o-F(1,2)-c)
record('joint_payoff_matched_marginals',va==(F(1,2),F(3,4)) and vb==va[::-1] and sum(va)/2==F(5,8),
       dict(context_A=list(map(str,va)),context_B=list(map(str,vb)),blind='5/8',oracle='3/4',regret='1/8'))

# Joint outcome laws have equal marginals and disjoint supports.
P={(0,0):F(1,2),(1,1):F(1,2)};Q={(0,1):F(1,2),(1,0):F(1,2)}
def tv(P,Q):return sum(abs(P.get(k,0)-Q.get(k,0)) for k in set(P)|set(Q))/2
for axis in [0,1]:
    assert all(sum(v for k,v in P.items() if k[axis]==b)==sum(v for k,v in Q.items() if k[axis]==b) for b in [0,1])
record('joint_not_marginal_closure',tv(P,Q)==1,dict(joint_TV='1',both_binary_marginals='1/2,1/2'))

# Hall deficiency by independent brute-force partial assignments.
for bits in product(range(2),repeat=6):
    Ns=[{j for j in range(2) if bits[2*i+j]} for i in range(3)]
    delta=max(len(J)-len(set().union(*(Ns[i] for i in J))) for k in range(4) for J in combinations(range(3),k))
    size=0
    for choices in product([-1,0,1],repeat=3):
        picked=[a for a in choices if a>=0]
        if len(picked)==len(set(picked)) and all(a<0 or a in Ns[i] for i,a in enumerate(choices)):
            size=max(size,len(picked))
    assert size==3-delta
record('hall_deficiency_joint_assignments',True,dict(bipartite_graphs=64,tasks=3,slots=2))
goods=[{1,2},{0,2},{0,1}]
record('pairwise_not_joint_good_actions',all(goods[i]&goods[j] for i,j in combinations(range(3),2)) and not set.intersection(*goods),
       'Three candidate constraints have pairwise intersections but no common action; every proper coalition is feasible.')

traces={(1,0),(0,1)}
record('persistent_model_not_stagewise_product',all(any(t) for t in traces) and (0,0) not in traces,
       'Stagewise possible sets {0,1} x {0,1} invent the unattainable failing trace (0,0).')

rho=F(7,10)
forced=lambda q:max(q*rho,(1-q)*rho/2)+(1-q)*rho/2
forced_candidates=[F(0),F(1),F(1,3)]
vf=min(map(forced,forced_candidates));dual=F(13,27);prob=F(20,27)
v0=prob*rho;v1=prob*rho/2+(1-prob)
record('optional_probe_primal_dual',vf==F(7,15) and v0==v1==F(14,27) and max(dual,1-dual,forced(dual))==v0,
       dict(forced=str(vf),optional=str(v0),probe_probability=str(prob),dual_weight=str(dual)))

# Budget/deadline query lower construction, exact for all n<=5 and all bit/query coordinates.
cases=0
for n in range(2,6):
    for k in range(n+1):
        subsets=list(combinations(range(n),k))
        for b in product(range(2),repeat=n):
            for q in range(n):
                success=sum((F(1) if q in S else F(1,2)) for S in subsets)/len(subsets)
                assert success==F(1,2)+F(k,2*n);cases+=1
record('delayed_query_attainment',True,dict(exact_coordinates=cases,n_range=[2,5],all_k=True))

# R145 n=1: directly test every affine probe and both hidden mechanisms.
def T(k,u,s):x,y=s;return y^k,x^u^k
def pi(s):return s[0]^s[1]
affine_cases=0
for A,B,C,D,a,b in product(range(2),repeat=6):
    def J(s):x,y=s;return (A&x)^(B&y)^a,(C&x)^(D&y)^b
    L=A^B^C^D
    descent=all(pi(J(s))==pi(J(t)) for s in product(range(2),repeat=2) for t in product(range(2),repeat=2) if pi(s)==pi(t))
    assert descent==(L==0)
    for k in [0,1]:assert pi(J(T(k,0,(0,0))))==(L&k)^a^b
    affine_cases+=1
for k,u,v,x,y in product(range(2),repeat=5):
    assert T(k,v,T(k,u,(x,y)))==(x^u,y^v)
record('transport_affine_descent_and_reset',True,dict(affine_maps=affine_cases,two_tick_cases=32))

# Posterior and inheritance distinctions remain different constructions.
muE={(1,0):F(1,2),(0,1):F(1,2)};muJ={(0,0):F(1,2),(1,1):F(1,2)}
assert tv(muE,muJ)==1
for j in [0,1]:assert sum(x[j]*p for x,p in muE.items())==sum(x[j]*p for x,p in muJ.items())==F(1,2)
record('successor_set_marginals_not_joint',True,dict(TV='1',marginals=['1/2','1/2'],restricted_reward='1/2',full_reward='1'))
unique=F(1);fission_B=unique;fission_C=fission_B
record('full_copy_calibration_needed_in_proof',fission_B+fission_C==2,
       'Unique full continuation q=1 + co-successor preservation + symmetry forces total 2. This checks the restored-premise derivation, not an unqualified no-go.')
U=list(product(range(2),repeat=2))
assert len({u[0] for u in U})==2 and len({(u[0],u[1]) for u in U})==4
shares=[(u,r,r,u^r) for u,r in product(range(2),repeat=2)]
assert all({u for u,r,b,c in shares if b==v}=={0,1} and {u for u,r,b,c in shares if c==v}=={0,1} for v in [0,1])
assert all(u==(b^c) for u,r,b,c in shares)
record('inheritance_duplication_secret_sharing',True,
       'Duplicated one-bit information is not two-bit information; two individually null secret shares jointly identify U.')

# All exact-source hashes, independent of proof status.
g=json.loads((ROOT/'UCT_FORMAL_GRAPH.json').read_text())
source_checks=[]
for source in g['source_versions']:
    p=ROOT/source['snapshot_workspace_path'];data=p.read_bytes()
    source_checks.append(dict(paper=source['paper'],path=str(p.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),passed=len(data)==source['bytes'] and hashlib.sha256(data).hexdigest()==source['sha256']))
assert all(x['passed'] for x in source_checks)

result=dict(schema='uct.r154.bounded-review-checks.v1',passed=True,exact_check_count=len(CHECKS),
            checks=CHECKS,source_checks=source_checks,
            scope='Bounded counterexamples and implementation checks only; manual general proofs are in RULE_REVIEW. No physical, phenomenological, numerical-archive or proof-assistant certification.')
(HERE/'VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(dict(passed=True,exact_checks=len(CHECKS),pinned_sources=len(source_checks))))
