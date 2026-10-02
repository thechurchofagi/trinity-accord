#!/usr/bin/env python3
"""Exact arithmetic checks for the linear-size face obstruction extension.
The all-dimensional conclusion is proved in LINEAR_FACE_COHERENCE_OBSTRUCTION.md.
"""
import hashlib
import itertools
import json
import math
import time
from pathlib import Path


def forbidden(weights, support):
    sums = {0}
    for r in range(1, support + 1):
        for subset in itertools.combinations(weights, r):
            sums.update(sum(s * a for s, a in zip(signs, subset))
                        for signs in itertools.product((-1, 1), repeat=r))
    return sums


def weights(n, k):
    a = [1 << j for j in range(k)] + [(1 << k) - 1]
    for m in range(k + 1, n):
        F = forbidden(a, k - 1)
        candidate = a[-1] + 1
        while candidate in F:
            candidate += 1
        B = sum((1 << r) * math.comb(m, r) for r in range(k))
        assert candidate <= a[-1] + B + 1
        a.append(candidate)
    return a


def gray(x):
    return x ^ (x >> 1)


def check(n, k):
    a = weights(n, k)
    checked = 0
    for r in range(1, k + 1):
        for subset in itertools.combinations(a, r):
            # Global sign reversal gives the same zero test.
            for tail in itertools.product((-1, 1), repeat=r - 1):
                assert subset[0] + sum(s * v for s, v in zip(tail, subset[1:])) != 0
                checked += 1
    assert a == sorted(set(a)) and a[0] == 1
    assert sum(a[:k]) == a[k]
    T = sum(a)
    B = sum((1 << r) * math.comb(n - 1, r) for r in range(k))
    assert T <= n * (1 << k) + n * n * (B + 1)
    u, v, z = (1 << k) - 1, 1 << k, 1 << (k + 1)
    assert gray(u) < gray(v) and gray(v | z) < gray(u | z)
    assert 2 * (a[k] + a[k + 1]) < T
    return {'n': n, 'k': k, 'weights': a, 'T': T,
            'signed_relation_checks': checked,
            'contradictory_rows_support': k + 1}


def main():
    start = time.monotonic()
    # Exact rational certificate H_2(1/5)+1/5 < 1.
    assert 5 ** 5 < 2 ** 12
    cases = [check(n, k) for n, k in ((6, 2), (8, 3), (10, 4), (12, 5), (13, 6))]
    arithmetic = []
    for n in (10, 20, 50, 100, 200, 500, 1000, 2000):
        k = n // 5
        m = n - 1
        B = sum((1 << r) * math.comb(m, r) for r in range(k))
        # B <= 2^(m*(log2(5)-7/5)), verified without floating point.
        assert B ** 5 * 128 ** m <= 3125 ** m
        upper = 4 * (n * (1 << k) + n * n * (B + 1) + 1)
        if n >= 200:
            assert upper < (1 << n)
        arithmetic.append({'n': n, 'k': k, 'upper_bound_below_N': upper < (1 << n),
                           'approx_log2_run_upper_over_N': math.log2(upper) - n,
                           'run_upper_sha256': hashlib.sha256(str(upper).encode()).hexdigest()})
    data = {'status': 'PASS', 'seed': None, 'construction_checks': cases,
            'exact_entropy_checks': arithmetic, 'violations': 0,
            'scope': 'Finite arithmetic checks support the written all-dimensional proof; no additive RLC bound is claimed.',
            'seconds': round(time.monotonic() - start, 3)}
    payload = json.dumps({k: v for k, v in data.items() if k != 'seconds'}, sort_keys=True).encode()
    data['deterministic_sha256'] = hashlib.sha256(payload).hexdigest()
    output = Path(__file__).with_name('linear_face_obstruction_verification.json')
    output.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
