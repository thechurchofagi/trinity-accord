#!/usr/bin/env python3
"""Exact coordinate-adaptive tree tail obstruction; no general lower proof."""
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json
import random
import time
from verify_face_local_obstruction import direct_counts, subset_scores

SEED = 202610030740


def denominator(n, d):
    out = 1
    for level in range(d): out *= (2 * (n-level)) ** (1 << level)
    return out


def full_orders(free, base, target):
    """Uniform configurations, not an empirical distribution of permutations."""
    if not free:
        yield (base,), True
        return
    for j in free:
        rest = tuple(k for k in free if k != j)
        next_target = target[1:] if target else ()
        lo = list(full_orders(rest, base, next_target))
        hi = list(full_orders(rest, base | (1 << j), next_target))
        for (a, gooda), (b, goodb) in product(lo, hi):
            for sign in (1, -1):
                good = not target or (j == target[0] and sign == 1
                                        and gooda and goodb)
                yield (a+b if sign == 1 else b+a), good


def sampled_tree(n, d, rng):
    paths = {}
    def visit(free, base, level, path):
        if not free:
            paths[base] = path
            return (base,)
        j = n-1-level if level < d else rng.choice(free)
        sign = 1 if level < d else rng.choice((1, -1))
        assert j in free
        rest = tuple(k for k in free if k != j)
        lo = visit(rest, base, level+1, path+((j, sign, 0),))
        hi = visit(rest, base | (1 << j), level+1, path+((j, sign, 1),))
        return lo+hi if sign == 1 else hi+lo
    traversal = visit(tuple(range(n)), 0, 0, ())
    rank = [0] * (1 << n)
    for i, x in enumerate(traversal): rank[x] = i
    return rank, paths


def row_order(n, d):
    k = 1 << d; m = n-d
    a = tuple(k << j for j in range(m)) + tuple(1 << h for h in range(d))
    scores = subset_scores(a)
    p = tuple(sorted(range(1 << n), key=scores.__getitem__))
    assert tuple(scores[x] for x in p) == tuple(range(1 << n))
    assert p == tuple((z << m) | y for y in range(1 << m)
                      for z in range(k))
    return a, p


def audit_prefixes(rank, paths, n, rng):
    size = 1 << n
    excluded = range(1, size) if n <= 8 else sorted({
        1, 2, size-2, size-1, *(rng.randrange(1, size) for _ in range(16))})
    inv = sorted(range(size), key=rank.__getitem__); checks = 0
    for r in excluded:
        z = inv[r]
        coefficients = [0] * n
        for level, (j, sign, bit) in enumerate(paths[z]):
            assert bit == ((z >> j) & 1)
            coefficients[j] = sign * 3 ** (n-1-level)
        for x in range(size):
            value = sum(coefficients[j] * (((x >> j) & 1)-((z >> j) & 1))
                        for j in range(n))
            assert (value < 0) == (rank[x] < r)
            assert (value == 0) == (x == z)
            checks += 1
    return checks


def main():
    start = time.monotonic(); rng = random.Random(SEED)
    digest = hashlib.sha256(); exhaustive = []; rows = []; prefix_checks = 0
    for n in (2, 3):
        for d in range(1, n+1):
            total = selected = 0; _, scan = row_order(n, d)
            for traversal, event in full_orders(tuple(range(n)), 0,
                                                 tuple(range(n-1, n-d-1, -1))):
                total += 1
                if not event: continue
                selected += 1; pos = [0] * (1 << n)
                for i, x in enumerate(traversal): pos[x] = i
                R, C = direct_counts(tuple(pos[x] for x in scan))
                assert R == (1 << (n-d+1)) - 1
                digest.update(json.dumps((n, d, traversal, R, C)).encode())
            assert total == {2: 16, 3: 1536}[n]
            assert Fraction(selected, total) == Fraction(1, denominator(n, d))
            exhaustive.append({'n': n, 'd': d, 'configurations': total,
                               'selected': selected, 'event_probability': str(Fraction(selected,total))})
    for n in range(4, 13):
        for d in (1, min(3, n), min(5, n)):
            a, scan = row_order(n, d)
            rank, paths = sampled_tree(n, d, rng)
            R, C = direct_counts(tuple(rank[x] for x in scan))
            assert R == (1 << (n-d+1)) - 1
            prefix_checks += audit_prefixes(rank, paths, n, rng)
            prob = Fraction(1, denominator(n, d))
            assert prob >= Fraction(1, (2*n)**((1 << d)-1))
            row = {'n': n, 'd': d, 'generic_weights': a, 'R_C': [R,C],
                   'exact_event_probability': str(prob),
                   'unrestricted_subtree_seed': SEED,
                   'rank_sha256': hashlib.sha256(json.dumps(rank).encode()).hexdigest()}
            rows.append(row); digest.update(json.dumps(row, sort_keys=True).encode())
    result = {'state': 'ADAPTIVE_COORDINATE_TREE_TAIL_OBSTRUCTION_PASS',
              'seed': SEED, 'exhaustive_event_counts': exhaustive,
              'conditional_completion_cases': rows, 'prefix_vertex_checks': prefix_checks,
              'all_dimensional_theorem': 'For the specified independent random coordinate/sign model, a fixed genuine row sweep has R=2^(n-d+1)-1 with probability at least product_l [2(n-l)]^(-2^l) >= (2n)^(-(2^d-1)).',
              'violations': 0, 'verification_digest': digest.hexdigest(),
              'elapsed_seconds': round(time.monotonic()-start, 3),
              'limitations': 'This excludes a strong uniform fixed-sweep lower tail for the UNCONDITIONED adaptive model. It does not exclude existence of good trees, a conditioned model, or the primary constant-density target.'}
    Path(__file__).with_name('adaptive_tree_tail_verification.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('state','prefix_vertex_checks',
          'verification_digest','elapsed_seconds','violations')}))


if __name__ == '__main__': main()
