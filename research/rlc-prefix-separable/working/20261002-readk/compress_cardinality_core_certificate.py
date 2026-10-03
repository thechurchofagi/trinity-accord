#!/usr/bin/env python3
"""LP proposes compact weights; exact integer inequalities certify them."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import math
import time
from scipy.optimize import linprog
from probe_larger_cardinality_cores import analyze
from verify_cardinality_half_density import primary_order

def main():
    root=Path(__file__).parent;start=time.monotonic()
    source=json.loads((root/'larger_cardinality_core_pressure.json').read_text())
    rows=[]
    for record in source['records']:
        old=record['best'];n=old['n'];b=tuple(old['secondary']);p=primary_order(b)
        constraints=[]
        for x,y in zip(p,p[1:]):
            if x.bit_count()==y.bit_count():
                constraints.append(tuple(((y>>j)&1)-((x>>j)&1) for j in range(n)))
        zero=b.index(0)
        bounds=[(0,0) if j==zero else (0,None) for j in range(n)]
        proposal=linprog([1]*n,A_ub=[tuple(-v for v in d) for d in constraints],
                         b_ub=[-1]*len(constraints),bounds=bounds,method='highs')
        assert proposal.success
        candidate=None
        for maxden in (16,64,256,1024,4096,65536):
            rational=[Fraction(float(x)).limit_denominator(maxden) for x in proposal.x]
            den=math.lcm(*(x.denominator for x in rational))
            nums=tuple(int(x*den) for x in rational)
            if all(sum(a*v for a,v in zip(d,nums))>0 for d in constraints):
                candidate=nums;break
        assert candidate is not None
        divisor=math.gcd(*candidate);candidate=tuple(x//divisor for x in candidate)
        margins=[sum(a*v for a,v in zip(d,candidate)) for d in constraints]
        assert min(margins)>0 and min(candidate)==0
        compact=analyze(candidate)
        assert compact['secondary']==candidate and not compact['tie_refined']
        assert primary_order(candidate)==p
        for key in ('D_int','E_int','net','interior_edges','tail_limit_fraction','core_order_sha256'):
            assert json.dumps(compact[key])==json.dumps(old[key])
        row={'n':n,'original_secondary':b,'compact_secondary':candidate,
             'strict_adjacent_row_count':len(constraints),'minimum_integer_margin':min(margins),
             'strict_rows_sha256':hashlib.sha256(json.dumps(constraints).encode()).hexdigest(),
             'certificate':compact,
             'proof':'All within-cardinality adjacent difference rows have strictly positive INTEGER dot product; hence the full order and every graph value are preserved. No floating solver optimality is asserted.'}
        rows.append(row);print(json.dumps(row),flush=True)
    out={'state':'EXACT_INTEGER_ORDER_EQUIVALENCE_CERTIFICATES',
         'records':rows,'violations':0,
         'verification_digest':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3)}
    (root/'compact_larger_cardinality_cores.json').write_text(json.dumps(out,separators=(',',':'))+'\n')

if __name__=='__main__':main()
