#!/usr/bin/env python3
"""Replay local counterexample pressure; no absence-to-bound inference."""
import hashlib
import json
import random
import time
from pathlib import Path
from probe_paired_sibling_general_weights import propose
from verify_gray_reflection_graph import order_and_scores

rng = random.Random(202610030944)
start = time.monotonic()
rows,hist = [],[]
digest = hashlib.sha256()
reject = 0
for n,budget in ((6,2000),(7,1000),(8,500)):
    best_w = tuple(8*(1 << h) for h in range(n-3))+(1,2,4)
    best = propose(best_w)
    current_w,current = best_w,best
    for trial in range(budget):
        ww = list(current_w)
        h = rng.randrange(n)
        scale = max(2,int(max(ww)/(1+trial%5)))
        ww[h] = max(1,ww[h]+rng.randint(-scale,scale))
        ww = tuple(ww)
        if order_and_scores(ww) is None:
            reject += 1
            continue
        row = propose(ww)
        if 'R' not in row:
            continue
        digest.update(json.dumps(row,sort_keys=True).encode())
        if row['R'] < best['R']:
            best_w,best = ww,row
            item = {'trial':trial,**row}
            hist.append(item)
            print(json.dumps(item),flush=True)
        if row['R'] < current['R'] or (row['R'] == current['R'] and rng.random() < 0.2):
            current_w,current = ww,row
        if trial%100 == 99 and rng.random() < 0.3:
            current_w,current = best_w,best
    result = {'n':n,'budget':budget,'best':best}
    rows.append(result)
    print(json.dumps(result),flush=True)
receipt = {'seed':202610030944,
           'policy':'one-coordinate positive mutation at five scales; nonincreasing witness R with 20 percent plateau moves; occasional restart to best',
           'nongeneric_rejections':reject,'rows':rows,'improvements':hist,
           'evaluated_witness_digest':digest.hexdigest(),'elapsed_seconds':time.monotonic()-start,
           'scope':'Floating MILP proposals checked by exact integer ranks and additive orders; no bound inferred from lack of counterexamples.'}
Path(__file__).with_name('paired_sibling_local_pressure.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'elapsed':receipt['elapsed_seconds'],'improvements':len(hist),'digest':receipt['evaluated_witness_digest']}))
