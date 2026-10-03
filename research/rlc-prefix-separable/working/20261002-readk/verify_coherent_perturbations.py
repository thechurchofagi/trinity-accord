#!/usr/bin/env python3
"""Exact genuine-sweep perturbation pressure; not a general density proof."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import time
from verify_face_local_obstruction import subset_scores, gray, direct_counts
from verify_gray_reflection_graph import graph, optimize, energy, inverse_gray


def sweep(weights):
    scores = subset_scores(weights)
    assert len(set(scores)) == len(scores)
    return tuple(sorted(range(len(scores)), key=scores.__getitem__))


def main():
    start = time.monotonic(); digest = hashlib.sha256(); rows = []
    for family in ('ones', 'arithmetic', 'k3'):
        for n in range(5, 19):
            primary = ((1,) * n if family == 'ones' else
                       tuple(range(1, n + 1)) if family == 'arithmetic' else
                       (1, 2) + tuple(3 * j - 2 for j in range(2, n)))
            B = 1 << n
            weights = tuple(B * a + (1 << j) for j, a in enumerate(primary))
            p = sweep(weights)
            scores = subset_scores(primary)
            assert p == tuple(sorted(range(B), key=lambda x: (scores[x], x)))
            assert all(p[-1-i] == (p[i] ^ (B-1)) for i in range(B))
            R, C = direct_counts(tuple(map(gray, p)))
            assert R == C
            best = None
            if n <= 12:
                g = graph(p, n); E, phi = optimize(g, n)
                best = (B + g['D'] - E) // 2
                mask = max((z << 1 for z in range(1 << (n-2))),
                           key=lambda z: energy(g['edges'], z))
                z = inverse_gray(mask)
                signed = tuple(-a if z >> j & 1 else a
                               for j, a in enumerate(weights))
                actual = sweep(signed)
                assert actual == tuple(x ^ z for x in p)
                assert direct_counts(tuple(map(gray, actual))) == (best, best)
                assert best >= B // 2  # Finite pressure, NOT an all-n theorem.
            row = {'family': family, 'n': n, 'primary': primary,
                   'generic_integer_weights': weights, 'R': R, 'C': C,
                   'sign_orbit_min_C': best,
                   'order_sha256': hashlib.sha256(
                       json.dumps(p, separators=(',', ':')).encode()).hexdigest()}
            rows.append(row); digest.update(json.dumps(row, sort_keys=True).encode())

    # Sorted-positive chamber coverage through n=4: quotient the established
    # signed chamber counts by n! 2^n. No coordinate permutations here.
    small = []
    for n, count in ((2, 1), (3, 2), (4, 14)):
        chambers = {}
        for a in combinations(range(1, 13), n):
            scores = subset_scores(a)
            if len(set(scores)) != len(scores): continue
            p = tuple(sorted(range(1 << n), key=scores.__getitem__))
            chambers.setdefault(p, a)
        assert len(chambers) == count
        minimum = 1 << n
        for p in chambers:
            g = graph(p, n); E, _ = optimize(g, n)
            minimum = min(minimum, ((1 << n) + g['D'] - E) // 2)
        assert minimum == (1 << (n-1))
        small.append({'n': n, 'sorted_positive_chambers': count,
                      'minimum_C_over_signs': minimum})

    lifts = []
    for n in range(5, 19):
        a = (1, 6, 8, 12, 16) + tuple(64 << j for j in range(n-5))
        assert all(x < y for x, y in zip(a, a[1:]))
        assert all(a[j] > sum(a[:j]) for j in range(5, n))
        p = sweep(a); actual = direct_counts(tuple(map(gray, p)))
        expected = 14 << (n-5)
        assert actual == (expected, expected)
        lifts.append({'n': n, 'weights': a, 'R_C': actual})
        digest.update(json.dumps((a, actual)).encode())

    long_faces = []
    for n in range(2, 19):
        free = tuple(range(0, n, 2)); controllers = tuple(range(1, n, 2))
        B = sum(1 << j for j in free) + 1
        w = tuple((1 << j) if j % 2 == 0 else B << controllers.index(j)
                  for j in range(n))
        p = sweep(w); length = 1 << len(free)
        face = tuple(sum(((y >> i) & 1) << j for i, j in enumerate(free))
                     for y in range(length))
        assert p[:length] == face
        assert all(gray(x) < gray(y) for x, y in zip(face, face[1:]))
        row = {'n': n, 'weights': w, 'initial_monotone_face_vertices': length,
               'same_sign_edges': length-1}
        long_faces.append(row); digest.update(json.dumps(row).encode())

    crossing_seed = (133155,187135,633646,896257,867970,597105)
    p = sweep(crossing_seed)
    crossings = tuple(sum(((x ^ y) >> j) & 1 for x, y in zip(p,p[1:]))
                      for j in range(6))
    assert crossings == (29,27,29,29,31,27) and max(crossings) < 32

    result = {'state': 'COHERENT_PERTURBATION_AND_SORTED_WEIGHT_AUDIT_PASS',
              'perturbation_cases': rows, 'sorted_chamber_audit': small,
              'minimal_dimension_for_sorted_half_density_counterexample': 5,
              'sorted_positive_all_dimensional_witness_lifts': lifts,
              'exponentially_long_monotone_faces': long_faces,
              'Q6_maximum_coordinate_crossing_counterexample':
                  {'weights': crossing_seed, 'crossing_counts': crossings},
              'coverage_source': 'Maclagan math/9809134 Section 4, region counts 8, 96, 5376; quotient by n! 2^n.',
              'violations': 0, 'verification_digest': digest.hexdigest(),
              'elapsed_seconds': round(time.monotonic()-start, 3),
              'limitations': 'Perturbation densities and sign minima are finite results. The sorted witness gives 7/16 density in every n>=5, which does not improve the existing unrestricted Gray ceiling 5/16. The primary lower bound is OPEN.'}
    Path(__file__).with_name('coherent_perturbation_verification.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps({'state': result['state'], 'cases': len(rows),
          'verification_digest': result['verification_digest'],
          'elapsed_seconds': result['elapsed_seconds'], 'violations': 0}))


if __name__ == '__main__': main()
