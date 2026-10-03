#!/usr/bin/env python3
"""Replay the completed compact witness discovery; not chamber coverage."""
import json,random
from pathlib import Path
from verify_prefix_transport_defect import check
rng=random.Random(202610030843)
for trial in range(3000):
    b=tuple(rng.sample(range(1,61),7))
    result=check((1,)*7,b)
    if result and result['W']>16:
        receipt={'rng_seed':202610030843,'domain':'Seven distinct integers sampled from 1..60; reject nongeneric joint scores.',
                 'max_draws':3000,'trial_index':trial,'secondary':b,'result':result,
                 'scope':'First retained witness only; no minimality or chamber coverage claim.'}
        Path(__file__).with_name('compact_cardinality_flux_discovery.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt,indent=2))
        break
else:
    raise RuntimeError('No witness in the specified replay domain')
