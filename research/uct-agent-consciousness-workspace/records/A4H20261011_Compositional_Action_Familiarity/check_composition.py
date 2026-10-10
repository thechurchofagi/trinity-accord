"""A4H: exact finite organizational witness; no phenomenal values are generated."""
from collections import Counter
from itertools import product
import json
from pathlib import Path

def counts(word, n):
    return Counter(''.join(word[(i+j) % len(word)] for j in range(n)) for i in range(len(word)))

def retained(word, target, width):
    return target[-width:] in counts(word, width)

def episode(word, context, target, mode):
    # Executed model consumer reads its learned triple carrier unless bypassed.
    carrier = counts(word, 3)
    query = context + target
    used = mode == 'use'
    support = bool(carrier.get(query, 0)) if used else False
    # A slow generic dispatcher remains available; the retained route reduces
    # the internal number of resolution stages, not a phenomenal variable.
    stages = ['read_context', 'read_retained_triple', 'dispatch'] if support else ['read_context', 'generic_resolve', 'generic_dispatch', 'dispatch']
    return dict(query=query, carrier_support=bool(carrier.get(query, 0)),
                carrier_read=used, effective_support=support, stages=stages,
                action=target, success=True)

A, B = '00110011', '00010111'
assert counts(A, 1) == counts(B, 1)
assert counts(A, 2) == counts(B, 2)
assert counts(A, 3) != counts(B, 3)
queries = [''.join(x) for x in product('01', repeat=3)]
rows = []
for q in queries:
    rows.append(dict(query=q, A=episode(A,q[:2],q[-1],'use'),
                     B=episode(B,q[:2],q[-1],'use'),
                     B_bypassed=episode(B,q[:2],q[-1],'bypass')))
different = [r['query'] for r in rows if r['A']['effective_support'] != r['B']['effective_support']]
assert different == ['000', '010', '101', '111']
assert all(r['A']['action']==r['B']['action']==r['B_bypassed']['action'] and r['A']['success'] and r['B']['success'] for r in rows)
assert all(not r['B_bypassed']['effective_support'] for r in rows)
# Bijective relabeling transports every organizational predicate.
flip = lambda s: ''.join('1' if c=='0' else '0' for c in s)
assert all(retained(w,q,3)==retained(flip(w),flip(q),3) for w in [A,B] for q in queries)
# A stronger scalar based on any function of the matched summaries cannot
# distinguish these histories, although the detailed carrier/consumer can.
out = dict(schema='a4h-exact/1', histories=dict(A=A,B=B),
    count_convention='cyclic words; wraparound events included',
    counts={k:{str(n):dict(sorted(counts(w,n).items())) for n in [1,2,3]} for k,w in [('A',A),('B',B)]},
    distinguishable_queries=different, rows=rows,
    relabeling_checks=16, query_checks=8, semantic_assignments=0,
    boundaries=['stipulated finite model, not a human or complete-K installation',
                'support is binary occurrence support, not probability, familiarity or performance',
                'bypass changes consumer use; same output does not imply same organization',
                'no claims about physical timing or H_way'])
Path(__file__).with_name('EXACT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(query_checks=8,distinguishable_queries=different,relabeling_checks=16,semantic_assignments=0)))
