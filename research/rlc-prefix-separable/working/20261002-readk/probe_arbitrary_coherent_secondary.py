#!/usr/bin/env python3
"""Exact exploratory pressure: low-range primary, arbitrary coherent secondary.

This does not certify all chambers. All sign optimizations are exhaustive
integer computations, with no optimizer heuristic.
"""
from pathlib import Path
import hashlib
import json
import random
import time
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import graph, optimize, energy, inverse_gray, counts, gray

SEED=202610030812
DIMENSIONS=(6,8,10,12,14,16,18)


def exact_gray_spin_optimizer(certificate,n):
    # Prior graph theorem: top coordinate is isolated; global spin inversion
    # lets us fix coordinate zero. Gray traversal flips one other spin at once.
    assert all(j<n-1 for i,j,v in certificate['edges'])
    neighbors=[[] for _ in range(n)]
    for i,j,v in certificate['edges']:
        neighbors[i].append((j,v));neighbors[j].append((i,v))
    spins=[1]*n;mask=0;value=sum(v for i,j,v in certificate['edges'])
    best=value;best_mask=0
    for step in range(1,1<<max(0,n-2)):
        j=(step & -step).bit_length()
        value-=2*spins[j]*sum(v*spins[i] for i,v in neighbors[j])
        spins[j]=-spins[j];mask^=1<<j
        if value>best:best=value;best_mask=mask
    assert energy(certificate['edges'],best_mask)==best
    return best,best_mask


def main():
    start=time.monotonic();rng=random.Random(SEED);rows=[];digest=hashlib.sha256()
    worst=None;graph_excesses=[];accepted=skipped=0
    for n in DIMENSIONS:
        for family in ('ones','k3'):
            primary=(1,)*n if family=='ones' else (1,2)+tuple(3*j-2 for j in range(2,n))
            primary_scores=subset_scores(primary);q=len(set(primary_scores));N=1<<n
            for mode in ('permuted_binary','signed_binary','random_integer'):
                for draw in range(4):
                    if mode=='random_integer':
                        secondary=tuple(rng.sample(range(-10**15,10**15),n))
                    else:
                        perm=list(range(n));rng.shuffle(perm)
                        secondary=tuple((rng.choice((-1,1)) if mode=='signed_binary' else 1)*(1<<j) for j in perm)
                    B=2*sum(map(abs,secondary))+1
                    weights=tuple(B*a+b for a,b in zip(primary,secondary))
                    score=subset_scores(weights)
                    if len(set(score))!=N:skipped+=1;continue
                    accepted+=1
                    p=tuple(sorted(range(N),key=score.__getitem__))
                    beta_score=subset_scores(secondary)
                    assert p==tuple(sorted(range(N),key=lambda x:(primary_scores[x],beta_score[x])))
                    g=graph(p,n);E,mask=exact_gray_spin_optimizer(g,n)
                    if n<=12:assert E==optimize(g,n)[0]
                    z=inverse_gray(mask)
                    signed=tuple(-a if z>>j&1 else a for j,a in enumerate(weights))
                    signed_score=subset_scores(signed)
                    actual=tuple(sorted(range(N),key=signed_score.__getitem__))
                    assert actual==tuple(x^z for x in p)
                    R,C,_=counts(tuple(map(gray,actual)))
                    assert C==(N+g['D']-E)//2
                    row={'n':n,'family':family,'mode':mode,'draw':draw,
                         'primary':primary,'secondary':secondary,'B':B,'q':q,
                         'D':g['D'],'W':g['W'],'E':E,'phi':(g['W']-E)//2,
                         'net_E_minus_D':E-g['D'],'minimum_C':C,
                         'attained_R':R,'reflection':z,
                         'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}
                    rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
                    if worst is None or (E-g['D'])* (1<<worst['n']) > worst['net_E_minus_D']*N:
                        worst={**row,'graph_edges':g['edges'],'signed_weights':signed}
                    if E>2*q:graph_excesses.append(row)
            selected=[r for r in rows if r['n']==n and r['family']==family]
            print(json.dumps({'n':n,'family':family,'accepted':len(selected),
                'maximum_net_energy':max(r['net_E_minus_D'] for r in selected),
                'minimum_C':min(r['minimum_C'] for r in selected),
                'elapsed':round(time.monotonic()-start,3)}),flush=True)
    out={'state':'EXACT_ARBITRARY_SECONDARY_PRESSURE_COMPLETE_NOT_GLOBAL_PROOF',
         'seed':SEED,'dimensions':DIMENSIONS,'draws_per_family_mode_dimension':4,
         'accepted':accepted,'skipped_ties':skipped,'cases':rows,
         'maximum_net_energy_density_case':worst,
         'cases_E_exceeds_numerical_bound_2q':len(graph_excesses),
         'verification_digest':digest.hexdigest(),'violations':0,
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Every individual sign minimum is exact; magnitude/secondary vectors are sampled. No all-dimensional theorem or chamber coverage follows.'}
    Path(__file__).with_name('arbitrary_coherent_secondary_pressure.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','accepted','skipped_ties',
          'cases_E_exceeds_numerical_bound_2q','verification_digest','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
