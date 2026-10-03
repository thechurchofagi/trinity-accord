#!/usr/bin/env python3
"""Pressure the unrestricted coherent-secondary cancellation claim."""
import json,random
from pathlib import Path
from verify_prefix_transport_defect import check
rng=random.Random(202610030832)
rows=[]
for n in range(5,11):
    first_W=None;first_cost=None;minimum=1<<n
    for draw in range(300):
        b=tuple(v*(1<<(n+2))+(1<<j) for j,v in enumerate(rng.sample(range(-100,101),n)))
        r=check((1,)*n,b,False);assert r
        minimum=min(minimum,r['minimum_C'])
        if r['W']>2*r['q'] and first_W is None:
            first_W={'draw':draw,'secondary':b,'graph_and_defect':r}
        if r['minimum_C']<(1<<(n-1))-r['q']:
            first_cost={'draw':draw,'secondary':b,'graph_and_defect':r};break
    row={'n':n,'draws':draw+1,'min_C_seen':minimum,'first_W_gt_2q':first_W,
         'counterexample_to_unqualified_cost':first_cost}
    rows.append(row)
    print(json.dumps(row),flush=True)
    if first_cost:break
Path(__file__).with_name('cardinality_transport_boundary_receipt.json').write_text(json.dumps({'seed':202610030832,'rows':rows,'scope':'Exact counterexamples only; finite negative searches do not imply coverage.'},indent=2)+'\n')
