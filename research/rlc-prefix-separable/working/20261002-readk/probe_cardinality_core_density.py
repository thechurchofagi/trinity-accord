#!/usr/bin/env python3
"""Reproducible genuine-score pressure; not chamber enumeration."""
import argparse
import hashlib
import json
import random
import time
from pathlib import Path
from verify_cardinality_tail_amplification import seed_certificate, COMPACT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-d', type=int, default=12)
    parser.add_argument('--trials', type=int, default=300)
    args = parser.parse_args()
    rng = random.Random(202610030845)
    start = time.monotonic()
    rows, history = [], []
    rejections = 0
    for d in range(6, args.max_d+1):
        baseline = COMPACT + tuple(73*(1 << j) for j in range(d-5))
        best_b, best = baseline, seed_certificate(baseline)
        for trial in range(args.trials):
            if trial % 3 == 0:
                b = tuple(rng.sample(range(-100000, 100001), d))
                kind = 'independent'
            else:
                bb = list(best_b)
                for j in rng.sample(range(d), 1 if trial % 3 == 1 else min(3,d)):
                    bb[j] += rng.randint(-max(8, max(abs(v) for v in bb)), max(8, max(abs(v) for v in bb)))
                b, kind = tuple(bb), 'mutation'
            try:
                c = seed_certificate(b)
            except AssertionError:
                rejections += 1
                continue
            if c['E']-c['D'] > best['E']-best['D']:
                best_b, best = b, c
                h = {'d':d,'trial':trial,'kind':kind,'b':b,'D0':c['D'],'E0':c['E'],
                     'phi0':c['phi'],'edges':c['edges'],'net':c['E']-c['D']}
                history.append(h)
                print(json.dumps(h),flush=True)
        row={'d':d,'trials':args.trials,'best_b':best_b,'D0':best['D'],'E0':best['E'],
             'W0':best['W'],'phi0':best['phi'],'edges':best['edges'],
             'net':best['E']-best['D'],
             'limiting_density':0.5+(best['D']-best['E'])/(2*(1 << d))}
        rows.append(row)
        print(json.dumps(row),flush=True)
    receipt={'random_seed':202610030845,'proposal_policy':'one independent proposal followed by one-coordinate and three-coordinate mutations of retained best',
             'max_d':args.max_d,'trials_per_d':args.trials,'nongeneric_rejections':rejections,
             'rows':rows,'improvement_history':history,'elapsed_seconds':time.monotonic()-start,
             'scope':'Only retained genuine coherent score orders; no completeness or lower-bound claim.'}
    receipt['deterministic_sha256']=hashlib.sha256(json.dumps({k:v for k,v in receipt.items() if k!='elapsed_seconds'},sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('cardinality_core_density_pressure.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'elapsed_seconds':receipt['elapsed_seconds'],'digest':receipt['deterministic_sha256']}))


if __name__=='__main__':
    main()
