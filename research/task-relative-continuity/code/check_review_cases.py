#!/usr/bin/env python3
"""Independent release-review fixtures. Only exact finite mathematics is tested."""
from __future__ import annotations
import argparse, itertools, json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


def inverse(p):
    r=[0]*len(p)
    for i,j in enumerate(p):r[j]=i
    return tuple(r)


def compose(p,q):return tuple(p[q[i]] for i in range(len(p)))


def group(generators,n):
    out={tuple(range(n))}; queue=list(out)
    for p in queue:
        for q in generators:
            z=compose(q,p)
            if z not in out:out.add(z);queue.append(z)
    return out


def bayes(f,routes,source=None,route_weights=None):
    n=len(f)
    source=source or [Fraction(1,n)]*n
    route_weights=route_weights or [Fraction(1,len(routes))]*len(routes)
    weights=defaultdict(Counter)
    for p,w in zip(routes,route_weights):
        for x,pr in enumerate(source):weights[p[x]][f[x]]+=w*pr
    return sum(max(v.values()) for v in weights.values())


def run():
    count=0; nonidentity_reference=0
    for n in (1,2,3):
        ps=tuple(itertools.permutations(range(n)))
        for k in range(1,min(len(ps),3)+1):
            for routes in itertools.combinations(ps,k):
                i0=inverse(routes[0]); G=group([compose(i0,p) for p in routes],n)
                for f in itertools.product(range(3),repeat=n):
                    decoders=[d for d in itertools.product(range(3),repeat=n)
                              if all(d[p[x]]==f[x] for p in routes for x in range(n))]
                    invariant=all(f[g[x]]==f[x] for g in G for x in range(n))
                    assert bool(decoders)==invariant
                    if invariant:
                        assert len(decoders)==1
                        assert decoders[0]==tuple(f[i0[y]] for y in range(n))
                    count+=1
                    nonidentity_reference+=routes[0]!=tuple(range(n))
    # The sampled family is not necessarily uniform over its generated group.
    I=(0,1,2); C=(1,2,0); f=(0,1,2)
    actual=bayes(f,(I,C)); generated=bayes(f,tuple(group([C],3)))
    assert actual==Fraction(1,2) and generated==Fraction(1,3)
    # Uniform source is essential to the displayed average-accuracy formula.
    bias=bayes((0,1),((0,1),(1,0)),[Fraction(9,10),Fraction(1,10)])
    assert bias==Fraction(9,10)
    # A fixed clock/key is omitted side information, not information regeneration.
    assert all(((x^p)^p)==x for x,p in itertools.product((0,1),repeat=2))
    # Handoff endpoints can preserve a target via a complemented reader.
    for t,eta,xi in itertools.product((0,1),repeat=3):
        a,b=t^eta,eta;c,d=a^xi,b^xi^1
        assert c^d==t^1 and 1^c^d==t
    return {'status':'PASS','decoder_cases':count,
        'cases_without_identity_as_reference':nonidentity_reference,
        'target_alphabet':'three labels, including constants and non-surjective targets',
        'actual_two_route_accuracy':str(actual),'generated_group_accuracy':str(generated),
        'biased_prior_accuracy':str(bias),
        'scope':'New review fixtures only; no empirical or phenomenal validation.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('review_cases.json'));a=ap.parse_args()
    data=run();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
