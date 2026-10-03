#!/usr/bin/env python3
"""Replay a completed local pressure run; failure to improve is not a bound."""
import json
import random
from pathlib import Path
from verify_cardinality_tail_amplification import seed_certificate, EIGHT_CORE

rng = random.Random(202610030926)
best_b = EIGHT_CORE
best = seed_certificate(best_b)
rows = []
for trial in range(8000):
    b = list(best_b)
    j = rng.randrange(8)
    scale = max(4, max(abs(v) for v in b)//(1+(trial % 7)))
    b[j] += rng.randint(-scale, scale)
    b = tuple(b)
    try:
        c = seed_certificate(b)
    except AssertionError:
        continue
    if c['E']-c['D'] > best['E']-best['D']:
        best_b, best = b, c
        rows.append({'trial': trial, 'b': b, 'certificate': c})
        print(json.dumps(rows[-1]), flush=True)
receipt = {'seed': 202610030926, 'trials': 8000,
           'policy': 'one-coordinate mutation with seven alternating scales; strict improvements only',
           'best_b': best_b, 'certificate': best, 'improvements': rows,
           'scope': 'Sampling and local pressure only.'}
Path(__file__).with_name('cardinality_eight_core_refinement.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
