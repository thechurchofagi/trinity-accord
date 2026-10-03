#!/usr/bin/env python3
"""Adversarial witness proposals; exact ranks/scans validate every result.

MILP is a proposal mechanism. No exact optimality or chamber-coverage
claim is inferred from its floating solver status or objective bound.
"""
import json
import random
import time
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix
from verify_gray_reflection_graph import order_and_scores, counts, gray
from verify_paired_sibling_ranks import rank


def propose(weights):
    n, N = len(weights), 1 << len(weights)
    p = order_and_scores(weights)[0]
    offsets, offset = [], 0
    for h in range(n-1):
        offsets.append(offset)
        offset += 1 << (n-h-2)
    root, variables = offset, offset+1
    labels, signs = [], []
    for x,y in zip(p,p[1:]):
        h = (x ^ y).bit_length()-1
        labels.append(root if h == n-1 else offsets[h]+(x >> (h+2)))
        signs.append(1 if gray(y) > gray(x) else -1)
    J = defaultdict(int)
    D = 0
    for i in range(N-2):
        a,b = labels[i],labels[i+1]
        if a == b:
            D += 1
            assert signs[i] == -signs[i+1]
        else:
            J[tuple(sorted((a,b)))] += signs[i]*signs[i+1]
    edges = [(a,b,v) for (a,b),v in sorted(J.items()) if v]
    objective = np.zeros(variables+len(edges))
    A = lil_matrix((4*len(edges),len(objective)))
    upper = []
    for i,(a,b,v) in enumerate(edges):
        y = variables+i
        objective[y] = v
        # y is the XOR of the two binary orientation variables.
        for row,values,bound in ((4*i,{a:1,b:-1,y:-1},0),
                                 (4*i+1,{a:-1,b:1,y:-1},0),
                                 (4*i+2,{a:-1,b:-1,y:1},0),
                                 (4*i+3,{a:1,b:1,y:1},2)):
            for j,value in values.items():
                A[row,j] = value
            upper.append(bound)
    hi = np.ones(len(objective));hi[root] = 0
    result = milp(objective,integrality=np.ones(len(objective)),
                  bounds=Bounds(np.zeros(len(objective)),hi),
                  constraints=LinearConstraint(A.tocsr(),-np.inf,np.array(upper)),
                  options={'time_limit':0.75,'mip_rel_gap':0})
    if result.x is None:
        return {'n':n,'weights':weights,'solver_status':int(result.status),'witness':None}
    mask = sum(int(result.x[j] >= 0.5) << j for j in range(root))
    r = tuple(rank(x,n,mask) for x in range(N))
    assert len(set(r)) == N
    R,C,_ = counts(tuple(r[x] for x in p))
    value = sum(v*(-1 if ((mask >> a) ^ (mask >> b)) & 1 else 1) for a,b,v in edges)
    assert 2*(R-1) == N-2+D-value
    return {'n':n,'weights':weights,'solver_status':int(result.status),'mask':mask,
            'R':R,'C':C,'linear_forced_D':D,'linear_graph_energy':value,
            'violates_N_over_4':R < N/4,
            'violates_N_over_4_plus_1':R < N/4+1}


def main():
    rng = random.Random(202610030939)
    start = time.monotonic()
    rows = []
    for n in range(6,11):
        # One exact three-bit fast-top row sweep plus seven independent draws.
        seeds = [tuple(8*(1 << h) for h in range(n-3))+(1,2,4)]
        while len(seeds) < 8:
            w = tuple(rng.sample(range(1,10001),n))
            if order_and_scores(w) is not None:
                seeds.append(w)
        for w in seeds:
            row = propose(w)
            rows.append(row)
            print(json.dumps(row),flush=True)
    receipt = {'seed':202610030939,'rows':rows,'elapsed_seconds':time.monotonic()-start,
               'scope':'Genuine witnesses only; no coverage, solver-optimality, or lower-bound claim.'}
    Path(__file__).with_name('paired_sibling_general_weights_pressure.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'elapsed_seconds':receipt['elapsed_seconds'],'rows':len(rows),
                      'counterexamples_to_N_over_4':sum(r.get('violates_N_over_4',False) for r in rows)}))


if __name__ == '__main__':
    main()
