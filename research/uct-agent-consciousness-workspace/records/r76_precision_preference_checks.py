"""Analytical comparator checks, not a replication or consciousness experiment."""
from fractions import Fraction as F
from math import exp, log
import json


def channel(m, k):
    return [[k if o == s else (1-k)/(m-1) for s in range(m)] for o in range(m)]


def transform(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def expected(A, q, v):
    return sum(a*b for a,b in zip(transform(A,q),v))


def softmax(v):
    c=max(v); e=[exp(x-c) for x in v]; return [x/sum(e) for x in e]


def entropy(q):
    return -sum(float(x)*log(float(x)) for x in q if x)


def main():
    m=6; k0=F(13,20); A0=channel(m,k0)
    v=list(map(F,[-2,-1,0,1,2,3])); mean=sum(v)/m
    beliefs=[[F(i==j) for i in range(m)] for j in range(m)]
    beliefs += [[F(1,m)]*m, [F(1,2),F(1,3),F(1,6),F(0),F(0),F(0)]]
    lam0=(m*k0-1)/(m-1); rows=[]
    for k in [F(9,10),F(17,30),k0,F(1,m),F(1)]:
        A=channel(m,k); ratio=((m*k-1)/(m-1))/lam0
        vp=[ratio*x for x in v]
        expected_shift=(ratio-1)*mean
        original=[expected(A,q,v) for q in beliefs]
        comparator=[expected(A0,q,vp) for q in beliefs]
        assert all(b-a==expected_shift for a,b in zip(original,comparator))
        # Normalized positive preference distributions retain policy differences.
        C=softmax(list(map(float,v))); Cp=softmax(list(map(float,vp)))
        Go=[-float(expected(A,q,list(map(log,C)))) for q in beliefs]
        Gp=[-float(expected(A0,q,list(map(log,Cp)))) for q in beliefs]
        po=softmax([-x for x in Go]);pp=softmax([-x for x in Gp])
        err=max(abs(a-b) for a,b in zip(po,pp));assert err<1e-12
        rows.append(dict(kappa=k,ratio=ratio,constant_utility_shift=expected_shift,
                         policy_probability_max_error=err))
    # Replaying one common observation with a uniform prior exposes the difference.
    k=F(9,10); A=channel(m,k);q=[F(1,m)]*m;o=0
    post=lambda B: [B[o][s]*q[s]/sum(B[o][j]*q[j] for j in range(m)) for s in range(m)]
    pa,p0=post(A),post(A0)
    tv=sum(abs(x-y) for x,y in zip(pa,p0))/2
    assert pa[0]==k and p0[0]==k0 and tv==F(1,4)
    # At a chance baseline, no outcome-only preferences recover a nonconstant state score.
    Ac=channel(m,F(1,m))
    chance_scores=[expected(Ac,qb,v) for qb in beliefs[:m]]
    attentive_scores=[expected(A,qb,v) for qb in beliefs[:m]]
    assert len(set(chance_scores))==1 and len(set(attentive_scores))>1
    # Uniform preferences leave pragmatic scores equal. Adding information gain
    # changes the softmax contrast between delta-state and uniform-state policies.
    information_gain=lambda B,qb:entropy(transform(B,qb))-sum(float(qb[s])*entropy([B[i][s] for i in range(m)]) for s in range(m))
    delta=beliefs[0]
    iga=[information_gain(A,qb) for qb in [delta,q]]
    ig0=[information_gain(A0,qb) for qb in [delta,q]]
    iga_policy=softmax(iga);ig0_policy=softmax(ig0)
    assert abs(iga_policy[1]-ig0_policy[1])>1e-3
    print(json.dumps(dict(
        status="formal_source_motivated_comparator_not_source_code_replication",
        exact_identity_cases=len(rows)*len(beliefs),cases=rows,
        common_observation_posterior_attentive=pa,common_observation_posterior_comparator=p0,
        posterior_total_variation=tv,
        chance_baseline_failure=dict(baseline_scores=chance_scores,attentive_scores=attentive_scores),
        information_gain_failure=dict(attentive=iga,comparator=ig0,
            attentive_policy=iga_policy,comparator_policy=ig0_policy),
        full_agent_equivalence_claimed=False,phenomenal_bridge_established=False),
        indent=2,default=lambda x:{"exact":str(x),"decimal":float(x)}))


if __name__=="__main__":
    main()
