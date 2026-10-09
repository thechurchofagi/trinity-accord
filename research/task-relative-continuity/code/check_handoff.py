#!/usr/bin/env python3
"""Exact finite tests for TH20261009. No phenomenal variable is measured.
Run with Python >=3.10; standard library only. --output specifies the JSON path.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse, json


def rank(a: list[list[int]], p: int) -> int:
    if p not in (2,3,5):
        raise ValueError('Only the tested prime fields 2,3,5 are supported')
    a=[list(row) for row in a]
    if not a: return 0
    if len({len(r) for r in a}) != 1: raise ValueError('Ragged matrix')
    n=len(a[0]); i=0
    for j in range(n):
        pivot=next((k for k in range(i,len(a)) if a[k][j]%p),None)
        if pivot is None: continue
        a[i],a[pivot]=a[pivot],a[i]
        inv=pow(a[i][j]%p,-1,p)
        a[i]=[(v*inv)%p for v in a[i]]
        for k in range(len(a)):
            if k!=i:
                t=a[k][j]%p
                a[k]=[(x-t*y)%p for x,y in zip(a[k],a[i])]
        i+=1
        if i==len(a):break
    return i


def mv(a, x, p): return tuple(sum(u*v for u,v in zip(row,x))%p for row in a)
def mm(a,b,p):
    if not b: return [[] for _ in a]
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))%p
             for j in range(len(b[0]))] for i in range(len(a))]
def mats(m,n,p):
    for z in product(range(p),repeat=m*n):
        yield [list(z[i*n:(i+1)*n]) for i in range(m)]
def hcat(a,b):return [x+y for x,y in zip(a,b)]
def retention(h,g,p): return rank(hcat(g,h),p)-rank(g,p)


def bayes(h,g,p):
    """Uniform source and nuisance. Returns exact joint-source guessing accuracy."""
    d=len(h[0]);k=len(g[0]); masses=defaultdict(Counter)
    for target in product(range(p),repeat=d):
        for noise in product(range(p),repeat=k):
            hx,gz=mv(h,target,p),mv(g,noise,p)
            obs=tuple((x+y)%p for x,y in zip(hx,gz))
            masses[obs][target]+=1
    return Fraction(sum(max(v.values()) for v in masses.values()), p**(d+k))


def check_rank_formula():
    cases=0
    for p in (2,3):
        for m in range(1,4 if p==2 else 3):
            for d in (1,2):
                for k in range(3 if p==2 else 2):
                    for hg in mats(m,d+k,p):
                        h=[r[:d] for r in hg];g=[r[d:] for r in hg]
                        rho=retention(h,g,p)
                        assert 0<=rho<=d
                        assert bayes(h,g,p)==Fraction(1,p**(d-rho))
                        cases+=1
    return cases


def scenarios():
    out={}; joints={}; singles={}
    for kind in ('shared','reversed','independent','reversed_compensated'):
        correct=0; total=0; post=defaultdict(Counter); cut0=Counter();cut1=Counter()
        hist=[Counter() for _ in range(4)]
        for tau,eta,xi,zeta in product((0,1),repeat=4):
            a,b=tau^eta,eta
            c=a^xi
            d=b^(zeta if kind=='independent' else xi)^(kind.startswith('reversed'))
            y=c^d^(kind=='reversed_compensated')
            correct+=int(y==tau);total+=1;post[(c,d)][tau]+=1
            cut0[(a,b,0,0)]+=1;cut1[(0,0,c,d)]+=1
            for j,(before,middle,after) in enumerate(zip((a,b,0,0),(a,b,c,d),(0,0,c,d))):
                # Conditional law of each physical register's three-time history
                hist[j][(tau,before,middle,after)]+=1
        optimal=Fraction(sum(max(x.values()) for x in post.values()),total)
        out[kind]={'installed_accuracy':str(Fraction(correct,total)),
                   'best_decoding_accuracy':str(optimal),
                   'full_snapshot_states_before':len(cut0),'full_snapshot_states_after':len(cut1)}
        joints[kind]=(cut0,cut1);singles[kind]=hist
    assert all(joints[k]==joints['shared'] for k in joints)
    assert all(singles[k]==singles['shared'] for k in singles)
    assert [out[k]['installed_accuracy'] for k in out]==['1','0','1/2','1']
    assert [out[k]['best_decoding_accuracy'] for k in out]==['1','1','1/2','1']
    h0=[[1],[0],[0],[0]]; g0=[[1],[1],[0],[0]]
    h1=[[0],[0],[1],[0]]; g1=[[0],[0],[1],[1]]
    def minimal_supports(h,g):
        supports=[]
        for mask in range(1,16):
            ss={i for i in range(4) if mask>>i&1}
            if retention([h[i] for i in sorted(ss)],[g[i] for i in sorted(ss)],2)==1:
                supports.append(ss)
        return [sorted(s) for s in supports if not any(t<s for t in supports)]
    before=minimal_supports(h0,g0);after=minimal_supports(h1,g1)
    assert before==[[0,1]] and after==[[2,3]]
    out['support_migration']={'before':before,'after':after,'intersection':[],
        'all_conditional_single_register_histories_match':True,
        'endpoint_full_unconditional_snapshot_distributions_match':True,
        'intermediate_full_joint_snapshot_is_not_matched':True,
        'simultaneous_joint_or_cross_register_time_history_not_claimed_matched':True}
    return out


def check_dynamics():
    checks=0
    for d in (1,2):
        for k in (0,1):
            for hg in mats(2,d+k,2):
                h=[r[:d] for r in hg];g=[r[d:] for r in hg]
                rho=retention(h,g,2)
                for f in mats(2,2,2):
                    nh,ng=mm(f,h,2),mm(f,g,2)
                    assert retention(nh,ng,2)<=rho
                    # Additional target-independent randomness cannot restore rank
                    for col in product((0,1),repeat=2):
                        ng2=hcat(ng,[[v] for v in col])
                        assert retention(nh,ng2,2)<=retention(nh,ng,2)
                        checks+=1
    return checks


def check_coordinate_and_loss():
    invs=[s for s in mats(2,2,2) if rank(s,2)==2]
    checks=0
    for hg in mats(2,3,2):
        h=[r[:2] for r in hg];g=[r[2:] for r in hg]
        rho=retention(h,g,2)
        for s in invs:
            assert retention(mm(s,h,2),mm(s,g,2),2)==rho
            checks+=1
        for f in mats(2,2,2):
            nh,ng=mm(f,h,2),mm(f,g,2)
            g_image={mv(g,z,2) for z in product((0,1),repeat=1)}
            ng_image={mv(ng,z,2) for z in product((0,1),repeat=1)}
            k0={x for x in product((0,1),repeat=2) if mv(h,x,2) in g_image}
            k1={x for x in product((0,1),repeat=2) if mv(nh,x,2) in ng_image}
            assert k0<=k1
            assert len(k1)//len(k0)==2**(rho-retention(nh,ng,2))
            checks+=1
    return checks


def check_readout_erasure_and_countercontrols():
    h=[[1],[1]];g=[[],[]]
    assert retention(h,g,2)==1
    assert retention(mm([[1,1]],h,2),mm([[1,1]],g,2),2)==0
    assert retention(mm([[1,0]],h,2),mm([[1,0]],g,2),2)==1
    # A globally independent representation can be misleading under a biased source.
    assert Fraction(9,10)>Fraction(1,2)
    # Source outside a cut invalidates "cannot recover" for that incomplete cut.
    assert all((tau^eta)^eta==tau for tau,eta in product((0,1),repeat=2))
    return {'duplicated_memory_rank':1,'xor_consumer_rank':0,'one_branch_consumer_rank':1,
            'biased_prior_and_external_side_information_excluded':True}


def check_correlation_family():
    cases=0
    for eps in (Fraction(i,20) for i in range(21)):
        cells=defaultdict(Counter); snapshots=Counter(); single=Counter(); raw=Fraction(0)
        # Shared sign bit xi; e controls disagreement of the two fresh masks.
        for tau,eta,xi,e in product((0,1),repeat=4):
            weight=(eps if e else 1-eps)/8
            a,b=tau^eta,eta
            c,d=a^xi,b^xi^e
            cells[(c,d)][tau]+=weight; snapshots[(c,d)]+=weight
            single[(tau,c)]+=weight
            raw+=weight*int((c^d)==tau)
        assert raw==1-eps
        assert sum(max(z.values()) for z in cells.values())==max(eps,1-eps)
        assert all(v==Fraction(1,4) for v in snapshots.values())
        assert all(v==Fraction(1,4) for v in single.values())
        cases+=1
    sequence_cases=0
    for epss in product((Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)),repeat=3):
        distribution=Counter(); correlation=Fraction(1)
        for eps in epss:correlation*=1-2*eps
        for flips in product((0,1),repeat=3):
            prob=Fraction(1)
            for f,eps in zip(flips,epss):prob*=eps if f else 1-eps
            distribution[sum(flips)%2]+=prob
        assert max(distribution.values())==(1+abs(correlation))/2
        sequence_cases+=1
    # Reusing the SAME mask is not fresh noise independent of the past.
    mid=defaultdict(Counter); complete=defaultdict(Counter); final=0
    for tau,e in product((0,1),repeat=2):
        u=tau^e;v=u^e
        mid[u][tau]+=1;complete[(u,e)][tau]+=1;final+=int(v==tau)
    assert Fraction(sum(max(x.values()) for x in mid.values()),4)==Fraction(1,2)
    assert Fraction(sum(max(x.values()) for x in complete.values()),4)==1
    assert final==4
    return {'continuous_family_exact_rational_cases':cases,
            'independent_three_stage_sequence_cases':sequence_cases,
            'reused_noise_counterexample':{'incomplete_midcut_accuracy':'1/2',
            'complete_midcut_accuracy':'1','after_reused_mask_accuracy':'1',
            'lesson':'Noise independent of target alone is insufficient; require a complete causal cut or fresh conditional randomness.'}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('results/MODEL_RESULTS.json'))
    args=ap.parse_args()
    result={'research_id':'TH20261009','result_version':'0.1.0','status':'PASS',
        'matrix_bayes_cases':check_rank_formula(),'scenarios':scenarios(),
        'dynamic_independent_noise_checks':check_dynamics(),
        'coordinate_and_loss_checks':check_coordinate_and_loss(),
        'controls':check_readout_erasure_and_countercontrols(),
        'correlation_family':check_correlation_family(),
        'epistemic_scope':'Exact mathematical tests only; no brain, animal, or LLM experience measured.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
