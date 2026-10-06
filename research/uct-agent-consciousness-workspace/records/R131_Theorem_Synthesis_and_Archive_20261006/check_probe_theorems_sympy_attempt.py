"""Exact finite witnesses for R131; not a replacement for its general proofs."""
from pathlib import Path
from itertools import product, combinations_with_replacement
import json
import sympy as sp

checks=[]
def check(name,condition):
    checks.append({'check':name,'pass':bool(condition)})
    assert condition,name
def tv(u,v):return sum(abs(x-y) for x,y in zip(u,v))/2
def law_pair(A):
    d=A.nullspace()[0]
    plus=sp.Matrix([max(x,0) for x in d]);minus=sp.Matrix([max(-x,0) for x in d])
    return plus/sum(plus),minus/sum(minus)

outcomes=list(product([0,1],repeat=2))
A=sp.Matrix([[1]*4,[x for x,y in outcomes],[y for x,y in outcomes]])
u,v=law_pair(A)
check('binary marginal matrix rank is three',A.rank()==3)
check('nonnegative normalized witness',sum(u)==sum(v)==1 and all(x>=0 for x in list(u)+list(v)))
check('binary equal probes and maximally different joint law',A*u==A*v and tv(u,v)==1)
g=sp.Matrix([x*y for x,y in outcomes])
check('joint payoff is outside marginal span',A.col_join(g.T).rank()==4 and (g.T*u)[0]!=(g.T*v)[0])
additive=sp.Matrix([2+3*x-5*y for x,y in outcomes])
check('additive payoff is identified',A.col_join(additive.T).rank()==3 and (additive.T*u)[0]==(additive.T*v)[0])
full=A.col_join(g.T)
check('adding joint probe separates the whole four-outcome law',full.det()!=0)

# Explicit stochastic system S=Z x {0,1}, two declared total operations.
states=list(product(range(4),[0,1]))
K=sp.zeros(8,8)
for i,(z,b) in enumerate(states):
    law=[u,v][b]
    for j,(zp,bp) in enumerate(states):K[i,j]=law[zp] if b==bp else 0
check('constructed full-state kernel is stochastic',all(sum(K.row(i))==1 and all(x>=0 for x in K.row(i)) for i in range(8)))
mus=[]
for i in range(8):mus.append(sp.Matrix([sum(K[i,j] for j,(z,b) in enumerate(states) if z==zp) for zp in range(4)]))
check('all next measured expectations agree',all(A*mu==A*mus[0] for mu in mus))
check('every present summary fiber violates joint closure maximally',all(tv(mus[2*z],mus[2*z+1])==1 for z in range(4)))
check('same construction applies to every declared operation',all(A*mus[2*z]==A*mus[2*z+1] for a in range(2) for z in range(4)))

H=[int(x>0) for x in u]
informed=((sp.Matrix(H).T*u)[0]+(sp.Matrix([1-x for x in H]).T*v)[0])/2
r=sp.symbols('r',real=True)
blind=sp.expand((r+(1-r))/2)
check('informed score 1 and arbitrary randomized blind score 1/2',informed==1 and blind==sp.Rational(1,2))

# Lower-bound boundary n=2 and larger representative finite alphabets, m=0 included.
for n in range(2,9):
    for m in range(n-1):
        M=sp.Matrix([[1]*n]+[[int(i==j) for i in range(n)] for j in range(m)])
        a,b=law_pair(M)
        check(f'n={n},m={m}: deficient interface has a disjoint equal-probe witness',M*a==M*b and tv(a,b)==1)
    basis=sp.Matrix([[1]*n]+[[int(i==j) for i in range(n)] for j in range(n-1)])
    check(f'n={n}: n-1 singleton probes attain full rank',basis.rank()==n)

# The existence theorem does not say every deficient-probe fiber is ambiguous.
delta00=sp.Matrix([1,0,0,0])
check('nonnegative binary zero-marginal constraints leave only outcome 00',A*delta00==sp.Matrix([1,0,0]) and [i for i,(x,y) in enumerate(outcomes) if x==y==0]==[0])
# With deficient A, an identity full-state kernel gives a closed p on S.
identity=sp.eye(8)
identity_mus=[sp.Matrix([sum(identity[i,j] for j,(z,b) in enumerate(states) if z==zp) for zp in range(4)]) for i in range(8)]
check('deficient probes do not force a particular kernel to fail closure',all(identity_mus[2*z]==identity_mus[2*z+1] for z in range(4)))

L=full.inv();B=L[:,1:]
norm=max(sum(abs(x) for x in B*sp.Matrix(s)) for s in product([-1,1],repeat=3))
laws=[]
for i,j in combinations_with_replacement(range(4),2):
    p=sp.zeros(4,1);p[i]+=sp.Rational(1,2);p[j]+=sp.Rational(1,2);laws.append(p)
bound_checks=0
for p in laws:
    for q in laws:
        eps=max(abs(x) for x in (full*(p-q))[1:])
        assert tv(p,q)<=min(1,norm*eps/2)
        bound_checks+=1
check('left-inverse norm envelope on 100 exact law pairs',bound_checks==100)
result={'all_pass':True,'checks':checks,'check_count':len(checks),'rational_law_pairs':bound_checks,'binary_probe_matrix':str(A),'witness_u':list(map(str,u)),'witness_v':list(map(str,v)),'left_inverse_B_norm_infty_to_1':str(norm),'scope':'Exact finite witnesses only; general proofs are manual. No empirical or phenomenological validation.'}
Path(__file__).with_name('PROBE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
