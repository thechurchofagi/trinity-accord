#!/usr/bin/env python3
"""Exact optimal limiting density among all coherent five-bit cores."""
from pathlib import Path
from collections import Counter
import itertools
import hashlib
import json
from probe_cardinality_interior_lift import interior
from verify_gray_reflection_graph import optimize

def main():
    root=Path(__file__).parent
    source=root/'cardinality_layer_chamber_certificate.json'
    cert=json.loads(source.read_text());hist=Counter();best=None;dig=hashlib.sha256();seen=set()
    assert len(cert['feasible_sign_patterns'])==12
    assert len(cert['infeasible_pattern_integer_certificates'])==20
    for r in cert['infeasible_pattern_integer_certificates']:
        ids=r['row_indices'];c=r['positive_multipliers'];rows=r['strict_rows']
        assert all(a>0 for a in c)
        assert all(sum(a*rows[j][i] for j,a in zip(ids,c))==0 for i in range(4))
    for seed in cert['feasible_sign_patterns']:
        gaps=seed['gaps'];s=(0,gaps[0],sum(gaps[:2]),sum(gaps[:3]),sum(gaps))
        for b in itertools.permutations(s):
            p,edges,D=interior(b)
            assert p not in seen;seen.add(p)
            E,phi=optimize({'edges':edges,'W':sum(abs(v) for h,k,v in edges)},5)
            hist[E-D]+=1;dig.update(json.dumps((b,D,edges,E)).encode())
            if best is None or E-D>best['net']:
                best={'secondary':b,'D_int':D,'E_int':E,'edges_int':edges,'net':E-D}
    assert len(seen)==1440 and best['net']==4 and hist[4]==8
    out={'scope':'Complete Q5 coherent secondary cardinality-interior class; coverage uses inherited 12 feasible and 20 infeasible integer certificates.',
         'source_certificate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'orders':len(seen),'net_histogram':dict(sorted(hist.items())),'maximum':best,
         'minimum_extended_limit_fraction':[32-best['net'],64],
         'verification_digest':dig.hexdigest(),'violations':0,
         'limitations':'Exact optimal 7/16 limit for five-dimensional cores with the prescribed numerical-tail extension; not all six-dimensional cores or general M_n.'}
    (root/'cardinality_q5_interior_complete.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps(out))

if __name__=='__main__':main()
