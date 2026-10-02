#!/usr/bin/env python3
"""Retained first exploratory probe, not a theorem or complete chamber audit."""

import json
import random

from verify_gray_reflection_graph import graph, optimize, order_and_scores

SEED = 202610030659


def main():
    rng = random.Random(SEED)
    for n in range(2, 10):
        accepted = 0
        max_surplus = -10**8
        max_net = -10**8
        bad = None
        for draw in range(600):
            a = sorted(rng.sample(range(1, 100000), n))
            small = a.pop(0)
            rng.shuffle(a)
            a.append(small)
            result = order_and_scores(a)
            if result is None:
                continue
            g = graph(result[0], n)
            energy, _ = optimize(g, n)
            accepted += 1
            max_surplus = max(max_surplus, g["W"] - g["D"])
            max_net = max(max_net, energy - g["D"])
            if energy > g["D"]:
                bad = {"weights": a, "D": g["D"], "W": g["W"],
                       "E": energy, "C": ((1 << n) + g["D"] - energy) // 2,
                       "edges": g["edges"]}
                break
        print(json.dumps({"n": n, "accepted": accepted,
                          "max_W_minus_D": max_surplus,
                          "max_E_minus_D": max_net,
                          "counterexample": bad}), flush=True)
        if bad:
            break


if __name__ == "__main__":
    main()
