#!/usr/bin/env python3
"""Replay of completed exploratory probes. No theorem from random samples.

Modes use the exact seeds and parameter domains of the 2026-10-03 run.
Do not repeat completed modes as a substitute for the next proof gap.
"""
import argparse
import random
from verify_gray_reflection_graph import order_and_scores, graph, optimize, gray
from verify_gray_face_merge_dp import signed_chambers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('sorted', 'longest', 'crossings'))
    mode = parser.parse_args().mode
    seed = {'sorted': 202610030736, 'longest': 202610030740,
            'crossings': 202610030745}[mode]
    rng = random.Random(seed)
    if mode == 'crossings':
        for n in range(2, 5):
            _, orders = signed_chambers(n); best = 1 << n
            for p, w in orders.items():
                m = [sum(((x ^ y) >> j) & 1 for x, y in zip(p, p[1:]))
                     for j in range(n)]
                if max(m) < best: best = max(m); witness = (w, m)
            print(n, best, witness, flush=True)
    for n in range(3 if mode != 'crossings' else 5, 13):
        best = 0 if mode == 'longest' else 1 << n
        accepted = positives = 0
        trials = {'sorted': 300, 'longest': 200, 'crossings': 1000}[mode]
        for _ in range(trials):
            a = rng.sample(range(1, 1000000), n)
            w = tuple(sorted(a)) if mode == 'sorted' else (
                tuple(rng.choice((-1, 1)) * v for v in a)
                if mode == 'longest' else tuple(a))
            result = order_and_scores(w)
            if result is None: continue
            accepted += 1; p = result[0]
            if mode == 'sorted':
                g = graph(p, n); E, _ = optimize(g, n)
                value = ((1 << n) + g['D'] - E) // 2
                positives += any(v > 0 for i, j, v in g['edges'])
            elif mode == 'crossings':
                m = [sum(((x ^ y) >> j) & 1 for x, y in zip(p, p[1:]))
                     for j in range(n)]
                value = max(m)
            else:
                last = length = value = 0
                for x, y in zip(p, p[1:]):
                    sign = 1 if gray(y) > gray(x) else -1
                    length = length+1 if sign == last else 1
                    last = sign; value = max(value, length)
            if (mode == 'longest' and value > best) or (
                    mode != 'longest' and value < best):
                best = value; witness = (w, m) if mode == 'crossings' else w
        print(mode, n, accepted, best, positives, witness, flush=True)


if __name__ == '__main__': main()
