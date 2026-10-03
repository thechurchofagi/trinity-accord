#!/usr/bin/env python3
"""All Q5 cardinality-first coherent secondary orders via audited circuits."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import json
import time
from verify_gray_reflection_graph import graph, counts, gray, order_and_scores, optimize

def main():
    start=time.monotonic();root=Path(__file__).parent
    source=root/'cardinality_layer_chamber_certificate.json';cert=json.loads(source.read_text())
    seeds=cert['feasible_sign_patterns'];reject=cert['infeasible_pattern_integer_certificates']
    assert len(seeds)==12 and len(reject)==20
    assert len({tuple(s['signs']) for s in seeds}|{tuple(s['comparison_signs']) for s in reject})==32
    for r in reject:
        rows=r['strict_rows'];ids=r['row_indices'];c=r['positive_multipliers']
        assert all(x>0 for x in c)
        assert all(sum(v*rows[j][i] for j,v in zip(ids,c))==0 for i in range(4))
    seen=set();hist=Counter();whist=Counter();digest=hashlib.sha256();minR=minC=32;scans=0;worst=None
    for seed in seeds:
        gaps=seed['gaps'];sorted_b=(0,gaps[0],sum(gaps[:2]),sum(gaps[:3]),sum(gaps))
        assert all(g>0 for g in gaps)
        actual_signs=tuple(1 if sum(a*b for a,b in zip(row,gaps))>0 else -1 for row in cert['strict_normal_rows'])
        assert actual_signs==tuple(seed['signs'])
        for b in permutations(sorted_b):
            B=sum(b)+1;w=tuple(B+v for v in b);p=order_and_scores(w)[0]
            assert p is not None and p not in seen;seen.add(p)
            g=graph(p,5);E,phi=optimize(g,5);net=E-g['D']
            hist[net]+=1;whist[g['W']-g['D']]+=1
            orbitR=orbitC=32
            for z in range(32):
                signed=tuple(-v if z>>j&1 else v for j,v in enumerate(w))
                actual=order_and_scores(signed)[0]
                assert actual==tuple(x^z for x in p)
                R,C,_=counts(tuple(map(gray,actual)));scans+=1
                orbitR=min(orbitR,R);orbitC=min(orbitC,C)
                minR=min(minR,R);minC=min(minC,C)
            assert orbitC==(32-net)//2
            row={'secondary':b,'D':g['D'],'W':g['W'],'edges':g['edges'],'E':E,'net':net,'minimum_R_C':[orbitR,orbitC]}
            digest.update(json.dumps(row,sort_keys=True).encode())
            if worst is None or net>worst['net']:worst=row
    assert len(seen)==1440 and scans==46080
    out={'state':'COMPLETE_Q5_CARDINALITY_FIRST_COHERENT_SECONDARY_CLASS',
         'coverage_proof':'Inherited five strict pair normals, all 12 feasible patterns and 20 positive integer zero-row circuits; fixed-cardinality triple orders are complementary pair orders.',
         'source_certificate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'positive_orders':len(seen),'signed_integer_scans':scans,'minimum_R_C':[minR,minC],
         'net_energy_histogram':dict(sorted(hist.items())),
         'independent_edge_excess_histogram':dict(sorted(whist.items())),
         'worst_case':worst,'violations':0,'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Complete only for Q5 cardinality-first coherent secondary scans, not all Q5 magnitude chambers or all dimensions.'}
    (root/'cardinality_q5_secondary_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
