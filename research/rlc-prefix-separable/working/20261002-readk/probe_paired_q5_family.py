#!/usr/bin/env python3
"""All paired ranks at sampled Q5 scans; no chamber coverage claim."""
import json
import random
from pathlib import Path
import numpy as np
from verify_gray_reflection_graph import order_and_scores

n,N = 5,32
mm = np.arange(32768,dtype=np.uint16)
ranks = np.zeros((32768,N),dtype=np.uint8)
for x in range(N):
    offset = 0
    for h in range(n-1):
        index = offset+(x >> (h+2))
        bit = ((x >> h) ^ (x >> (h+1)) ^ (mm >> index)) & 1
        ranks[:,x] |= bit.astype(np.uint8) << h
        offset += 1 << (n-h-2)
    ranks[:,x] |= ((x >> (n-1)) & 1) << (n-1)
rng = random.Random(202610030929)
seeds = [(1,14,4,12,20)]+[tuple(rng.sample(range(1,101),n)) for _ in range(80)]
rows,best = [],None
for w in seeds:
    result = order_and_scores(w)
    if result is None:
        continue
    p = result[0]
    signs = ranks[:,p[1:]] > ranks[:,p[:-1]]
    R = 1+np.sum(signs[:,:-1] != signs[:,1:],axis=1)
    row = {'w':w,'minimum_over_all_paired_ranks':int(R.min()),'mask':int(R.argmin())}
    rows.append(row)
    if best is None or row['minimum_over_all_paired_ranks'] < best['minimum_over_all_paired_ranks']:
        best = row
        print(json.dumps(row),flush=True)
receipt = {'seed':202610030929,'rank_masks_exhausted_per_scan':32768,
           'weight_draws':81,'rows':rows,'best':best,
           'scope':'Complete paired family for sampled weights, not full weight chamber coverage.'}
Path(__file__).with_name('paired_q5_pressure.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'best':best,'generic_seeds':len(rows)}))
