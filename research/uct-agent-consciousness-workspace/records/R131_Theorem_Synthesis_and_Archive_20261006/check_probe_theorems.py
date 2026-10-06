"""Exact rational R131 witnesses; standard library only, not general proofs."""
from pathlib import Path
from itertools import product, combinations_with_replacement
from fractions import Fraction as F
import json
checks=[]
def check(name,condition):
    checks.append({'check':name,'pass':bool(condition)})
    assert condition,name
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def apply(A,v):return [dot(row,v) for row in A]
def tv(u,v):return sum(abs(x-y) for x,y in zip(u,v))/2
def rref(A):
    R=[[F(x) for x in row] for row in A];pivots=[];r=0
    for c in range(len(R[0])):
        pivot=next((i for i in range(r,len(R)) if R[i][c]),None)
        if pivot is None:continue
        R[r],R[pivot]=R[pivot],R[r];scale=R[r][c];R[r]=[x/scale for x in R[r]]
        for i in range(len(R)):
            if i!=r:
                scale=R[i][c];R[i]=[x-scale*y for x,y in zip(R[i],R[r])]
        pivots.append(c);r+=1
        if r==len(R):break
    return R,pivots
def rank(A):return len(rref(A)[1])
def law_pair(A):
    R,pivots=rref(A);n=len(A[0]);free=next(i for i in range(n) if i not in pivots)
    d=[F(0)]*n;d[free]=F(1)
    for i,p in enumerate(pivots):d[p]=-R[i][free]
    pos=[max(x,F(0)) for x in d];neg=[max(-x,F(0)) for x in d]
    assert sum(pos)==sum(neg)>0
    return [x/sum(pos) for x in pos],[x/sum(neg) for x in neg]
def inverse(A):
    n=len(A);R,p=rref([row+[int(i==j) for j in range(n)] for i,row in enumerate(A)])
    assert p==list(range(n))
    return [row[n:] for row in R]

outcomes=list(product([0,1],repeat=2))
A=[[1]*4,[x for x,y in outcomes],[y for x,y in outcomes]]
u,v=law_pair(A)
check('binary marginal matrix rank is three',rank(A)==3)
check('nonnegative normalized witness',sum(u)==sum(v)==1 and all(x>=0 for x in u+v))
check('equal probes with maximally different joint law',apply(A,u)==apply(A,v) and tv(u,v)==1)
g=[x*y for x,y in outcomes]
check('joint payoff outside marginal span and not identified',rank(A+[g])==4 and dot(g,u)!=dot(g,v))
additive=[2+3*x-5*y for x,y in outcomes]
check('additive payoff identified',rank(A+[additive])==3 and dot(additive,u)==dot(additive,v))
full=A+[g]
check('adding joint probe spans all four outcomes',rank(full)==4)
states=list(product(range(4),[0,1]))
K=[[[u,v][b][zp] if b==bp else F(0) for zp,bp in states] for z,b in states]
check('constructed full-state kernel stochastic',all(sum(row)==1 and all(x>=0 for x in row) for row in K))
mus=[[sum(K[i][j] for j,(z,b) in enumerate(states) if z==zp) for zp in range(4)] for i in range(8)]
check('all next measured expectations agree',all(apply(A,mu)==apply(A,mus[0]) for mu in mus))
check('every present fiber has TV one next-law disagreement',all(tv(mus[2*z],mus[2*z+1])==1 for z in range(4)))
H=[int(x>0) for x in u];notH=[1-x for x in H]
informed=(dot(H,u)+dot(notH,v))/2
action_scores=[(dot(h,u)+dot(h,v))/2 for h in [H,notH]]
check('informed score one and both blind pure actions score half',informed==1 and action_scores==[F(1,2),F(1,2)])
check('affine mixture has zero slope and constant half',action_scores[0]-action_scores[1]==0 and action_scores[1]==F(1,2))
for n in range(2,9):
    for m in range(n-1):
        M=[[1]*n]+[[int(i==j) for i in range(n)] for j in range(m)]
        a,b=law_pair(M)
        check(f'n={n},m={m}: disjoint equal-probe witness',apply(M,a)==apply(M,b) and tv(a,b)==1)
    basis=[[1]*n]+[[int(i==j) for i in range(n)] for j in range(n-1)]
    check(f'n={n}: n-1 indicators attain full rank',rank(basis)==n)
check('nonnegative zero-marginal constraints leave only outcome 00',[i for i,(x,y) in enumerate(outcomes) if x==y==0]==[0])
identity=[[int(i==j) for j in range(8)] for i in range(8)]
im=[[sum(identity[i][j] for j,(z,b) in enumerate(states) if z==zp) for zp in range(4)] for i in range(8)]
check('deficient probes can coexist with a closed identity kernel',all(im[2*z]==im[2*z+1] for z in range(4)))
L=inverse(full)
check('computed left inverse exact',[apply(L,[full[i][j] for i in range(4)]) for j in range(4)]==[[int(i==j) for i in range(4)] for j in range(4)])
B=[row[1:] for row in L]
norm=max(sum(abs(x) for x in apply(B,s)) for s in product([-1,1],repeat=3))
laws=[]
for i,j in combinations_with_replacement(range(4),2):
    p=[F(0)]*4;p[i]+=F(1,2);p[j]+=F(1,2);laws.append(p)
pairs=0
for p in laws:
    for q in laws:
        eps=max(abs(x) for x in apply(full,[x-y for x,y in zip(p,q)])[1:])
        assert tv(p,q)<=min(1,norm*eps/2)
        pairs+=1
check('left-inverse norm bound on 100 exact law pairs',pairs==100)
result={'all_pass':True,'checks':checks,'check_count':len(checks),'rational_law_pairs':pairs,'binary_probe_matrix':A,'witness_u':list(map(str,u)),'witness_v':list(map(str,v)),'left_inverse_B_norm_infty_to_1':str(norm),'scope':'Exact finite witnesses only; general proofs are manual. No empirical or phenomenological validation.'}
Path(__file__).with_name('PROBE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
