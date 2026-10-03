#!/usr/bin/env python3
"""Complete Q6 cardinality-layer SUBCLASS: rational circuits, exact scans.

This is not a classification of all Q6 additive chambers or a general bound.
No floating solver, numerical feasibility tolerance or sampled coverage.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json
import time
from verify_gray_reflection_graph import order_and_scores, graph, optimize, counts, gray

NORMALS = ((-1,0,1,0),(-1,0,1,1),(-1,0,0,1),(-1,-1,0,1),(0,-1,0,1))
POSITIVITY = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))


def positive_circuit(rows):
    """Find a positive zero-sum combination; every returned proof is checked."""
    for size in range(2,6):
        for ids in combinations(range(len(rows)),size):
            mat = [[Fraction(rows[j][i]) for j in ids] for i in range(4)]
            pivots=[];r=0
            for col in range(size):
                pivot=next((i for i in range(r,4) if mat[i][col]),None)
                if pivot is None:continue
                mat[r],mat[pivot]=mat[pivot],mat[r]
                scale=mat[r][col];mat[r]=[v/scale for v in mat[r]]
                for i in range(4):
                    if i!=r and mat[i][col]:
                        scale=mat[i][col];mat[i]=[a-scale*b for a,b in zip(mat[i],mat[r])]
                pivots.append(col);r+=1
                if r==4:break
            free=[i for i in range(size) if i not in pivots]
            if len(free)!=1:continue
            v=[Fraction(0)]*size;v[free[0]]=1
            for i,col in enumerate(pivots):v[col]=-mat[i][free[0]]
            if all(a<0 for a in v):v=[-a for a in v]
            if not all(a>0 for a in v):continue
            den=lcm(*(a.denominator for a in v));nums=[int(a*den) for a in v]
            common=gcd(*nums);nums=[a//common for a in nums]
            assert all(sum(c*rows[j][i] for j,c in zip(ids,nums))==0 for i in range(4))
            return {'row_indices':ids,'positive_multipliers':nums,'zero_sum':[0]*4}
    return None


def signs(gaps):
    h=tuple(sum(a*b for a,b in zip(row,gaps)) for row in NORMALS)
    return None if 0 in h else tuple(1 if x>0 else -1 for x in h)


def pack_records(records):
    return {'classified_positive_order_count':len(records),
            'record_order':'Feasible sign patterns lexicographically, then itertools.permutations of the increasing cumulative secondary seed.',
            'minimum_R_C':[r['min_R_C'] for r in records],
            'D_E_phi':[r['D_E_phi'] for r in records],
            'minimizing_reflections':[r['minimizing_reflection'] for r in records],
            'order_hash_chain_sha256':hashlib.sha256(
                ''.join(r['order_sha256'] for r in records).encode()).hexdigest()}


def main():
    start=time.monotonic();seeds={};rejected=[];digest=hashlib.sha256()
    # This finite grid is ONLY a source of integer feasible witnesses. It is
    # not used as a coverage argument for absent patterns.
    for g in product(range(1,9),repeat=4):
        key=signs(g)
        if key is not None:seeds.setdefault(key,g)
    assert len(seeds)==12
    for key in product((-1,1),repeat=5):
        rows=POSITIVITY+tuple(tuple(s*a for a in row) for s,row in zip(key,NORMALS))
        if key in seeds:
            assert all(sum(a*b for a,b in zip(row,seeds[key]))>0 for row in rows)
        else:
            cert=positive_circuit(rows)
            assert cert is not None
            assert all(c>0 for c in cert['positive_multipliers'])
            rejected.append({'comparison_signs':key,'strict_rows':rows,**cert})
    assert len(rejected)==20

    hist=Counter();records=[];order_set=set();signed_scans=0;best=64;witness=None
    for key,gaps in sorted(seeds.items()):
        a,b,c,d=gaps;sorted_s=(0,a,a+b,a+b+c,a+b+c+d)
        for secondary in permutations(sorted_s):
            t=2*sum(secondary)+1;B=4*t
            positive=tuple(B+s for s in secondary)+(t,)
            order=order_and_scores(positive)[0]
            model=tuple(x|(z<<5) for k in range(6) for z in (0,1)
                        for x in sorted((x for x in range(32) if x.bit_count()==k),
                                        key=lambda x:sum(secondary[j] for j in range(5) if x>>j&1)))
            assert order==model and order not in order_set;order_set.add(order)
            g=graph(order,6);E,phi=optimize(g,6);predicted=(64+g['D']-E)//2
            min_R=min_C=64;min_z=None
            for z in range(64):
                signed=tuple(-v if z>>j&1 else v for j,v in enumerate(positive))
                actual=order_and_scores(signed)[0]
                assert actual==tuple(x^z for x in order)
                R,C,_=counts(tuple(map(gray,actual)))
                assert R==C-1
                min_R=min(min_R,R)
                if C<min_C:min_C=C;min_z=z
                signed_scans+=1
            assert min_C==predicted and min_R==predicted-1
            hist[min_C]+=1
            if min_C<best:
                best=min_C;witness=tuple(-v if min_z>>j&1 else v for j,v in enumerate(positive))
            record={'comparison_signs':key,'secondary':secondary,
                    'min_R_C':[min_R,min_C],'D_E_phi':[g['D'],E,phi],
                    'minimizing_reflection':min_z,
                    'order_sha256':hashlib.sha256(bytes(order)).hexdigest()}
            records.append(record);digest.update(json.dumps(record,sort_keys=True).encode())
    assert len(order_set)==1440 and signed_scans==92160 and best==30
    expected={30:8,34:124,36:160,38:192,40:240,42:168,44:264,46:84,48:184,52:16}
    assert dict(hist)==expected
    cert={'scope':'Q6 cardinality-layer model only; not all magnitude chambers',
          'strict_normal_rows':NORMALS,'feasible_sign_patterns':[{'signs':k,'gaps':g} for k,g in sorted(seeds.items())],
          'infeasible_pattern_integer_certificates':rejected,**pack_records(records)}
    path=Path(__file__).with_name('cardinality_layer_chamber_certificate.json')
    path.write_text(json.dumps(cert,separators=(',',':'))+'\n')
    receipt={'state':'COMPLETE_Q6_CARDINALITY_LAYER_SUBCLASS_PASS',
             'feasible_comparison_patterns':12,'strict_infeasibility_certificates':20,
             'distinct_positive_model_orders':1440,'actual_signed_integer_scans':signed_scans,
             'minimum_R_C':[29,30],'cyclic_minimum_histogram':dict(sorted(hist.items())),
             'attaining_signed_weights':witness,'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'verification_digest':digest.hexdigest(),'violations':0,
             'elapsed_seconds':round(time.monotonic()-start,3),
             'limitations':'Exact finite subclass conclusion. No exact G6 or M6, and no proof of all-dimensional positive density.'}
    Path(__file__).with_name('cardinality_layer_chamber_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
