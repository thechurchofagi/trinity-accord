#!/usr/bin/env python3
"""Exact counterexample to the minimum-highest Gray half-density conjecture."""
from pathlib import Path
import hashlib
import json
import time
from verify_gray_reflection_graph import order_and_scores, graph, optimize, counts, gray

SECONDARY = (4,6,3,0,8)


def main():
    start = time.monotonic(); digest = hashlib.sha256(); base = []; lifts = []
    reference = None
    for B in (20,25,100,10000,10**12):
        a = tuple(B+s for s in SECONDARY)+(12,)
        p, scores = order_and_scores(a)
        if reference is None: reference = p
        assert p == reference
        g = graph(p,6); E,phi = optimize(g,6)
        assert (g['D'],g['W'],E,phi)==(8,12,12,0)
        assert g['edges']==((1,2,-4),(1,3,-4),(2,3,4))
        orbit=[]
        for z in range(64):
            signed=tuple(-v if z>>j&1 else v for j,v in enumerate(a))
            actual=order_and_scores(signed)[0]
            assert actual==tuple(x^z for x in p)
            R,C,_=counts(tuple(map(gray,actual)))
            assert R==C-1
            orbit.append((R,C))
        assert min(r for r,c in orbit)==29 and min(c for r,c in orbit)==30
        w=(-a[0],-a[1])+a[2:]
        witness=order_and_scores(w)[0]
        assert counts(tuple(map(gray,witness)))[:2]==(29,30)
        row={'B':B,'positive_magnitudes':a,'signed_witness':w,
             'signed_order':witness,'D_W_E_phi':[8,12,12,0],
             'off_diagonal_couplings':g['edges'],
             'all_64_reflections_R_C':orbit,
             'minimum_nonhighest_to_highest_ratio':f'{B}/12'}
        base.append(row); digest.update(json.dumps(row,sort_keys=True).encode())
        for n in (range(6,19) if B==25 else range(6,11)):
            m=n-6;A=sum(a)+1;positive=tuple(A<<j for j in range(m))+a
            signed=tuple(A<<j for j in range(m))+w
            full=order_and_scores(positive)[0];q=order_and_scores(signed)[0]
            full_graph=graph(full,n);actual=counts(tuple(map(gray,q)))[:2]
            L=1<<m
            assert full_graph['D']==8*L and full_graph['W']==12*L
            assert full_graph['edges']==tuple((i+m,j+m,v*L)
                                              for i,j,v in g['edges'])
            assert actual==(30*L-1,30*L)
            assert min(positive)==positive[-1]==12
            row={'n':n,'B':B,'A':A,'weights':signed,'positive_magnitudes':positive,
                 'R_C':actual,'net_maximum_graph_energy':4*L,
                 'net_energy_fraction':'1/16',
                 'order_sha256':hashlib.sha256(json.dumps(q).encode()).hexdigest()}
            lifts.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
    # Independent cardinality bucket proof obligations, including all exact
    # secondary subset scores and worst gaps, rather than numerical limits.
    buckets=[]
    for k in range(6):
        vals=sorted(sum(SECONDARY[j] for j in range(5) if x>>j&1)
                    for x in range(32) if x.bit_count()==k)
        assert len(vals)==len(set(vals)) and vals[-1]-vals[0]<=11
        buckets.append(vals)
    assert max(buckets[k-1][-1]-buckets[k][0] for k in range(1,6))==7
    out={'state':'MINIMUM_HIGHEST_HALF_DENSITY_CONJECTURE_FALSE',
         'all_dimensional_result':'For every n>=6 and every K>0, some generic magnitudes have every nonhighest weight >K times the highest, yet min_sign C=(15/32)2^n and min_sign R=C-1. Net E_*-D=2^n/16.',
         'secondary':SECONDARY,'secondary_cardinality_scores':buckets,
         'base_sign_orbit_cases':base,'separated_row_lifts':lifts,
         'targeted_discovery':{'seed':202610030755,'parent_secondary_domain':'range(-100000,100001)',
             'attempts_n4_n5_n6':[400,400,140],'accepted':[400,400,140],
             'first_failure_n6_zero_based_attempt':139,
             'original_positive_magnitudes':[953242,983318,936098,862068,1052123,476207],
             'original_secondary':[828,30904,-16316,-90346,99709]},
         'supersedes':'The UNPROVED minimum-highest conjecture in minimum_top_bit_probe_receipt.json; 4772 unstructured random tests had missed the counterexample.',
         'violations':0,'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'No minimal-dimension claim. Does not improve the existing unrestricted Gray upper ceiling 5/16 or disprove the main M_n target. The weaker positive Gray density question remains OPEN.'}
    Path(__file__).with_name('minimum_highest_counterexample_verification.json').write_text(
        json.dumps(out,indent=2)+'\n')
    print(json.dumps({key:out[key] for key in ('state','verification_digest',
          'elapsed_seconds','violations')}))


if __name__=='__main__':main()
