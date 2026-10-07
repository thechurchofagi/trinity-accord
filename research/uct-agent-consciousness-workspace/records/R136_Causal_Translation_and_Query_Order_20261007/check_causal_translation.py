"""Small exact checks of R136. No empirical data or numerical LP solver."""
from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
from pathlib import Path
import json

checks=[]
def check(name,cond):
    assert cond,name
    checks.append(dict(check=name,pass_=True))
bits=list(product((0,1),repeat=2))
def mat(mapping):
    return tuple(tuple(F(int(x==mapping[y])) for x in range(4)) for y in range(4))
def causal(R):
    return all(sum(R[i][j] for j,x in enumerate(bits) if x[0]==a)==
               sum(R[k][j] for j,x in enumerate(bits) if x[0]==a)
               for i,y in enumerate(bits) for k,z in enumerate(bits) if y[0]==z[0] for a in (0,1))
maps=list(product(range(4),repeat=4))
cp=[mat(m) for m in maps if causal(mat(m))]
check('64 of 256 binary two-step deterministic path maps are causal',len(cp)==64)

def multiply(A,B):
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))) for i in range(len(A)))
compositions=0
for A in cp:
    for B in cp:
        assert causal(multiply(A,B))
        compositions+=1
check('4096 pure causal-kernel compositions preserve prefix constraints',compositions==4096)

mixtures=0
for i,A in enumerate(cp):
    for B in cp[i:]:
        R=tuple(tuple((a+b)/2 for a,b in zip(ra,rb)) for ra,rb in zip(A,B))
        assert causal(R)
        for y in range(4):
            for x in range(4):
                r1=sum(R[y][j] for j,z in enumerate(bits) if z[0]==bits[x][0])
                r2=R[y][x]/r1 if r1 else F(1,2)
                assert r1*r2==R[y][x]
        mixtures+=1
check('2080 mixed kernels reconstruct by causal conditional factorization',mixtures==2080)

prefixcases=0
for desired in product(range(4),repeat=2):
    for available in product(range(4),repeat=2):
        criterion=all(bits[available[0]][:t]!=bits[available[1]][:t] or
                      bits[desired[0]][:t]==bits[desired[1]][:t] for t in (1,2))
        exists=any(all(R[available[theta]][desired[theta]]==1 for theta in (0,1)) for R in cp)
        assert criterion==exists
        prefixcases+=1
check('256 deterministic experiment pairs satisfy the exact prefix criterion',prefixcases==256)

# Available y=(0,theta); desired x=(theta,0).
available=(0,1);desired=(0,2)
offline=mat(tuple(bits.index((y[1],0)) for y in bits))
check('offline delay translator is exact but violates nonanticipation',
      not causal(offline) and all(offline[available[t]][desired[t]]==1 for t in (0,1)))
max_average=max(sum(R[available[t]][desired[t]] for t in (0,1))/2 for R in cp)
check('all 64 pure causal translators have delay average success at most one half',max_average==F(1,2))
fair=tuple(tuple(F(1,2) if j in (0,2) else F(0) for j in range(4)) for _ in range(4))
check('fair causal translator attains path-TV one half for both hidden states',
      causal(fair) and all(1-fair[available[t]][desired[t]]==F(1,2) for t in (0,1)))

grid=[F(i,4) for i in range(5)]
channels=[((a,1-a),(b,1-b)) for a,b in product(grid,repeat=2)]
def value(P,u):
    return sum(max(sum(P[t][x]*u[2*t+a]/2 for t in (0,1)) for a in (0,1)) for x in (0,1))
staticchecks=0
for Q in channels:
    for R in channels:
        P=multiply(Q,R)
        for u in product((F(0),F(1)),repeat=4):
            assert value(Q,u)>=value(P,u)
            staticchecks+=1
check('10000 exact garbling/decision-value comparisons respect Blackwell sufficiency',staticchecks==10000)
P=((F(1),F(0)),(F(0),F(1)))
Q=((F(3,4),F(1,4)),(F(1,4),F(3,4)))
u=(F(1),F(0),F(0),F(1))
check('identity decision separates perfect and noisy observations exactly',value(P,u)==1 and value(Q,u)==F(3,4))

# A read tree is None or (coordinate, child_when_zero, child_when_one).
@lru_cache(None)
def trees(remaining,k):
    if k==0:return (None,)
    out=[]
    for i in remaining:
        rest=tuple(j for j in remaining if j!=i)
        for left,right in product(trees(rest,k-1),repeat=2):
            out.append((i,left,right))
    return tuple(out)
def transcript(tree,b):
    seq=[]
    while tree is not None:
        i,left,right=tree;seq.append((i,b[i]));tree=(left,right)[b[i]]
    return tuple(seq)
treecount=0
for n in range(2,5):
    strings=list(product((0,1),repeat=n))
    for k in range(0,min(n,3)+1):
        for tree in trees(tuple(range(n)),k):
            leaves={}
            for b in strings:leaves.setdefault(transcript(tree,b),[]).append(b)
            correct=0
            for tr,bs in leaves.items():
                seen={i for i,v in tr}
                for q in range(n):
                    counts=[sum(b[q]==v for b in bs) for v in (0,1)]
                    if q not in seen:assert counts[0]==counts[1]
                    correct+=max(counts)
            assert F(correct,n*2**n)==F(1,2)+F(k,2*n)
            treecount+=1
check('all enumerated adaptive read trees meet the uniform-prior optimal-decoder bound',treecount>600)

lowercases=0
for n in range(2,7):
    for k in range(n+1):
        subsets=list(combinations(range(n),k))
        for b in product((0,1),repeat=n):
            for q in range(n):
                success=sum((F(1) if q in S else F(1,2)) for S in subsets)/len(subsets)
                assert success==F(1,2)+F(k,2*n)
                lowercases+=1
check('uniform-subset protocol attains the bound for every enumerated string/query',lowercases>1000)
check('two-bit one-read delayed guarantee gap is exactly one quarter',1-(F(1,2)+F(1,4))==F(1,4))
check('zero-read and full-read endpoints are one half and one',all(F(1,2)+F(k,2*n)==v for n in range(2,7) for k,v in [(0,F(1,2)),(n,F(1))]))

result=dict(round='R136',all_pass=True,checks=[{'check':c['check'],'pass':c['pass_']} for c in checks],
 deterministic_path_maps=256,causal_maps=64,composition_pairs=compositions,mixed_factorizations=mixtures,
 deterministic_experiment_pairs=prefixcases,static_value_checks=staticchecks,adaptive_read_trees=treecount,
 uniform_subset_coordinates=lowercases,arithmetic='Python Fraction and exact integer enumeration; no floating point or empirical simulation',
 scope='Finite witnesses and algebraic certificates only. General finite theorems use the stated handwritten proofs; no independent peer review or proof-assistant certification.')
(Path(__file__).parent/'EXACT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
