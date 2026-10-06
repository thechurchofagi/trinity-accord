"""Independent small exact witnesses. No empirical simulation or general proof."""
from itertools import product,combinations
from fractions import Fraction as F
from pathlib import Path
import json

checks=[]
def check(name,ok):
    assert ok,name
    checks.append({'name':name,'pass':True})
def subsets(xs):
    return [tuple(c) for k in range(len(xs)+1) for c in combinations(xs,k)]

# Independent enumeration of legal assignments versus the Hall/deficit formulas.
hall_pass=deficit_pass=0
for mask in range(1<<9):
    N=[{r for r in range(3) if mask & (1<<(3*i+r))} for i in range(3)]
    deficit=max(len(J)-len(set().union(*(N[i] for i in J))) for J in subsets(list(range(3))))
    maximum=0
    for a in product([-1,0,1,2],repeat=3):
        used=[r for r in a if r>=0]
        if len(set(used))==len(used) and all(r<0 or r in N[i] for i,r in enumerate(a)):
            maximum=max(maximum,len(used))
    assert (maximum==3)==(deficit==0),(mask,N)
    assert maximum==3-deficit,(mask,N)
    hall_pass+=1;deficit_pass+=1
check('Hall equivalence on all 512 three-by-three bipartite graphs',hall_pass==512)
check('exact matching deficit on those 512 independent enumerations',deficit_pass==512)

for n in [3,4,100]:
    completions=[[int(i!=omitted) for i in range(n)] for omitted in range(n)]
    p=[sum(F(row[i],n) for row in completions) for i in range(n)]
    check(f'n={n}: exact marginal completion and zero joint completion',all(x==F(n-1,n) for x in p) and not any(all(row) for row in completions))
check('three tasks: every proper coalition fits two slots but full coalition does not',all(len(J)<=2 for J in subsets([0,1,2]) if len(J)<3) and 3>2)

# Generic partial stochastic interface, kernels represented as {(next,output):mass}.
def signature(s,P,menus,kernels,outputs):
    ans=[tuple(sorted(menus[s]))]
    for a in sorted(menus[s]):
        for B in P:
            for o in outputs:
                ans.append(sum(kernels[(s,a)].get((t,o),F(0)) for t in B))
    return tuple(ans)
def refine(P,menus,kernels,outputs):
    history=[P]
    while True:
        Q=[]
        for B in P:
            groups={}
            for s in B:groups.setdefault(signature(s,P,menus,kernels,outputs),[]).append(s)
            Q.extend(tuple(v) for v in groups.values())
        if Q==P:return P,history
        P=Q;history.append(P)
def stable(P,menus,kernels,outputs):
    return all(len({signature(s,P,menus,kernels,outputs) for s in B})==1 for B in P)

# Same laws on the common menu, differing three-task availability.
U=subsets([0,1,2]);menus={0:set(a for a in U if len(a)<=2),1:set(U)}
K={(s,a):{(s,0):F(1)} for s in menus for a in menus[s]}
Q,history=refine([(0,1)],menus,K,[0])
check('availability witness differs only on the full three-task request',menus[1]-menus[0]=={(0,1,2)})
check('availability witness cannot remain in a single quotient block',len(Q)==2)

# Same menu and both separate marginals, different joint(next summary,output).
states=list(product([0,1],repeat=2));menus={s:{0} for s in states};K={}
for x,b in states:K[((x,b),0)]={((u,b),u^b):F(1,2) for u in [0,1]}
P=[((0,0),(0,1)),((1,0),(1,1))]
def marg(s,target):
    return [sum(v for (t,o),v in K[(s,0)].items() if (t[0] if target=='state' else o)==j) for j in [0,1]]
check('joint witness preserves both separate marginals',all(marg(s,k)==[F(1,2),F(1,2)] for s in states for k in ['state','output']))
joint0=[sum(K[((0,0),0)].get((s,o),0) for s in B) for B in P for o in [0,1]]
joint1=[sum(K[((0,1),0)].get((s,o),0) for s in B) for B in P for o in [0,1]]
check('joint witness has exact TV one',sum(abs(a-b) for a,b in zip(joint0,joint1))/2==1)
Q,history=refine(P,menus,K,[0,1])
check('joint-law refinement retains the hidden parity distinction',len(Q)==4)

# A delayed obstruction requires two refinement rounds, not just a current menu check.
states=list(range(5));menus={0:set(),1:{0},2:{0},3:{0},4:{0}}
K={(1,0):{(0,0):F(1)},(2,0):{(1,0):F(1)},(3,0):{(2,0):F(1)},(4,0):{(2,0):F(1)}}
P0=[(0,1,2,3,4)];Q,h=refine(P0,menus,K,[0])
check('delayed resource/menu distinctions propagate across multiple rounds',len(h)-1==3 and sorted(map(len,Q))==[1,1,1,2])
check('nontrivial stable compression keeps equivalent states three and four',any(set(B)=={3,4} for B in Q) and stable(Q,menus,K,[0]))

# Exhaust all 52 partitions of five states to check the coarsest conclusion for this witness.
def partitions(xs):
    if not xs:yield [];return
    x,*rest=xs
    for P in partitions(rest):
        yield [(x,)]+P
        for i in range(len(P)):yield P[:i]+[(x,)+P[i]]+P[i+1:]
allp=list(partitions(states));good=[P for P in allp if stable(P,menus,K,[0])]
check('all 52 candidate partitions covered',len(allp)==52)
check('every stable partition refines the computed quotient',all(all(any(set(B)<=set(C) for C in Q) for B in P) for P in good))
result={'all_pass':True,'named_checks':checks,'count':len(checks),'matching_graphs':512,'candidate_partitions':len(allp),'stable_partitions_in_witness':len(good),'refinement_history':h,'scope':'Exact finite boundary checks, not general proof, empirical data or subjective-experience measurement.'}
Path(__file__).with_name('EXACT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='named_checks'}))
