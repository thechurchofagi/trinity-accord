#!/usr/bin/env python3
"""Replay of completed targeted discovery; do not duplicate it."""
import random
from verify_gray_reflection_graph import order_and_scores, graph, optimize

rng=random.Random(202610030755)
for n in range(4,12):
    for attempt in range(400):
        secondary=rng.sample(range(-100000,100001),n-1)
        B=4*sum(map(abs,secondary))+2
        a=tuple(B+s for s in secondary)+(B//2,)
        result=order_and_scores(a)
        if result is None:continue
        g=graph(result[0],n);E,_=optimize(g,n)
        C=((1<<n)+g['D']-E)//2
        if C<(1<<(n-1)):
            print(n,attempt,a,secondary,C)
            raise SystemExit(0)
