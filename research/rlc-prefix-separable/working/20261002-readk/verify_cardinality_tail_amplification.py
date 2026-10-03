#!/usr/bin/env python3
"""Exact checks of arbitrary coherent seeds and dominant positive tails.

The all-dimensional statements are proved in CARDINALITY_TAIL_AMPLIFICATION.md;
the tested cases are an audit, not a claim of chamber completeness.
"""
import hashlib
import json
import random
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from verify_prefix_transport_defect import scores
from verify_gray_reflection_graph import graph, optimize, order_and_scores, counts, gray, energy, inverse_gray

COMPACT = (10, 11, 22, 4, 25)
POSITIVE_PAYMENT = (16, 59, 15, 4, 49, 11, 7)
EIGHT_CORE = (10, 11, 22, 4, 25, 73, 146, -148)
ELEVEN_CORE = (10, 11, 22, 4, 25, 3071, 146, -3170, 584, 1168, 2336)
PRIOR_NINE_CORE = (108, 106, 105, 102, 110, 126, 32, 170, 0)
NEGATIVE_CYCLE_PACKING = (((1, 2, 4, 6, 3), 12),
                          ((1, 2, 6, 3, 8, 9, 4), 2),
                          ((1, 2, 6, 8, 4, 9, 7, 3), 2),
                          ((1, 3, 9, 4), 2))


def interior_certificate(p, s, g):
    edges = defaultdict(int)
    D = 0
    for i in range(len(p)-2):
        if s[p[i]] == s[p[i+1]] == s[p[i+2]]:
            h, k = g['labels'][i], g['labels'][i+1]
            if h == k:
                D += 1
            else:
                edges[tuple(sorted((h, k)))] += g['signs'][i]*g['signs'][i+1]
    edges = tuple((h, k, v) for (h, k), v in sorted(edges.items()) if v)
    return {'D': D, 'edges': edges, 'W': sum(abs(v) for h, k, v in edges)}


def seed_certificate(b):
    d = len(b)
    s, u = scores((1,)*d), scores(b)
    assert len(set(zip(s, u))) == 1 << d
    p = tuple(sorted(range(1 << d), key=lambda x: (s[x], u[x])))
    g = graph(p, d)
    cert = interior_certificate(p, s, g)
    assert all(k < d-1 for h, k, v in cert['edges'])
    cert['E'], cert['phi'] = optimize(cert, d)
    return cert


def check(b, m, digest, signed_audit=False):
    d, n = len(b), len(b)+m
    N, copies, q = 1 << n, 1 << m, n+1
    seed = seed_certificate(b)
    M = 1 + sum(abs(v) for v in b)
    secondary = b + tuple(M*(1 << j) for j in range(m))
    L = M*copies
    assert sum(abs(v) for v in secondary) == L-1
    actual = tuple(L+v for v in secondary)
    result = order_and_scores(actual)
    assert result is not None and min(actual) > 0
    p = result[0]
    s, u = scores((1,)*n), scores(secondary)
    assert p == tuple(sorted(range(N), key=lambda x: (s[x], u[x])))
    g = graph(p, n)
    interior = interior_certificate(p, s, g)
    assert interior['D'] == copies*seed['D']
    assert interior['edges'] == tuple((h, k, copies*v) for h, k, v in seed['edges'])
    J = {(h, k): v for h, k, v in g['edges']}
    J0 = {(h, k): copies*v for h, k, v in seed['edges']}
    W_boundary = sum(abs(J.get(key, 0)-J0.get(key, 0)) for key in J.keys() | J0.keys())
    D_boundary = g['D']-interior['D']
    assert 0 <= D_boundary <= 2*q and W_boundary <= 2*q
    E, phi = optimize(g, n)
    assert abs(E-copies*seed['E']) <= W_boundary
    Cmin = (N+g['D']-E)//2
    assert 2*Cmin == N+g['D']-E
    Rmin = Cmin-int(min(range(n), key=actual.__getitem__) == n-1)
    alpha = Fraction(1, 2) + Fraction(seed['D']-seed['E'], 2*(1 << d))
    assert alpha*N-q <= Cmin <= alpha*N+2*q
    assert alpha*N-q-1 <= Rmin <= alpha*N+2*q
    signed_checked = 0
    if signed_audit:
        observed_R, observed_C = N, N
        for z in range(N):
            signed = tuple(-v if z >> j & 1 else v for j, v in enumerate(actual))
            pp = order_and_scores(signed)[0]
            assert pp == tuple(x ^ z for x in p)
            R, C, _ = counts(tuple(map(gray, pp)))
            observed_R, observed_C = min(observed_R, R), min(observed_C, C)
            signed_checked += 1
        assert (observed_R, observed_C) == (Rmin, Cmin)
    row = {'core': list(b), 'd': d, 'n': n, 'copies': copies,
           'D0': seed['D'], 'E0': seed['E'], 'phi0': seed['phi'],
           'interior_edges': [list(v) for v in interior['edges']],
           'D': g['D'], 'E': E, 'D_boundary': D_boundary, 'W_boundary': W_boundary,
           'minimum_C': Cmin, 'minimum_R': Rmin, 'alpha': str(alpha),
           'signed_orders_independently_sorted': signed_checked}
    digest.update(json.dumps(row, sort_keys=True).encode())
    return row


def main():
    digest = hashlib.sha256()
    rows = [check(COMPACT, m, digest, signed_audit=(m <= 3)) for m in range(12)]
    c = seed_certificate(COMPACT)
    compact_certificate = c
    assert (c['D'], c['E'], c['W'], c['phi']) == (4, 8, 8, 0)
    assert c['edges'] == ((1, 2, 4), (1, 3, -4))
    for row in rows:
        assert row['alpha'] == '7/16'
        assert row['E']-row['D'] >= (1 << row['n'])//8-4*(row['n']+1)
    payment = [check(POSITIVE_PAYMENT, m, digest, signed_audit=(m <= 1)) for m in range(7)]
    assert all(row['alpha'] == '67/128' for row in payment)
    improvements = [check(b, m, digest, signed_audit=(m == 0))
                    for b in (EIGHT_CORE, ELEVEN_CORE) for m in range(7)]
    assert all(r['alpha'] == ('55/128' if r['d'] == 8 else '879/2048') for r in improvements)
    prior_nine = [check(PRIOR_NINE_CORE,m,digest,signed_audit=(m == 0)) for m in range(7)]
    assert all(r['alpha'] == '109/256' for r in prior_nine)
    exact_spin_certificates = []
    for b in (EIGHT_CORE, ELEVEN_CORE):
        c = seed_certificate(b)
        d = len(b)
        # Independently evaluate all 2^d spins, including redundant choices.
        values = [energy(c['edges'], mask) for mask in range(1 << d)]
        assert max(values) == c['E']
        witness = values.index(max(values))
        histogram = {v:values.count(v) for v in sorted(set(values))}
        exact_spin_certificates.append({'core':b,'D0':c['D'],'E0':c['E'],'W0':c['W'],
                                        'phi0':c['phi'],'edges':c['edges'],
                                        'optimizing_spin_mask':witness,'reflection':inverse_gray(witness),
                                        'all_spin_choices_evaluated':len(values),'energy_histogram':histogram})
    # Integer cycle packing gives a short analytic upper certificate for E0.
    eleven = seed_certificate(ELEVEN_CORE)
    J = {(h,k):v for h,k,v in eleven['edges']}
    loads = defaultdict(int)
    for cycle, amount in NEGATIVE_CYCLE_PACKING:
        sign = 1
        for h,k in zip(cycle, cycle[1:]+cycle[:1]):
            key = tuple(sorted((h,k)))
            sign *= 1 if J[key] > 0 else -1
            loads[key] += amount
        assert sign == -1 and amount > 0
    assert all(load <= abs(J[key]) for key,load in loads.items())
    packing_weight = sum(amount for cycle,amount in NEGATIVE_CYCLE_PACKING)
    assert packing_weight == eleven['phi'] == 18
    assert energy(eleven['edges'],70) == eleven['W']-2*packing_weight == eleven['E'] == 554
    rng = random.Random(202610030915)
    random_seeds = []
    for d in range(2, 9):
        for _ in range(6):
            while True:
                b = tuple(rng.sample(range(-2000, 2001), d))
                s, u = scores((1,)*d), scores(b)
                if len(set(zip(s, u))) == 1 << d:
                    break
            random_seeds.append(b)
    random_rows = [check(b, m, digest, signed_audit=(len(b)+m <= 7))
                   for b in random_seeds for m in range(4)]
    all_rows = rows+payment+improvements+prior_nine+random_rows
    receipt = {'status': 'PASS', 'violations': 0,
               'compact_seed': list(COMPACT), 'compact_interior_certificate': compact_certificate,
               'compact_lifts': rows, 'positive_payment_lifts': payment,
               'improved_core_lifts':improvements,'exact_spin_certificates':exact_spin_certificates,
               'prior_nine_core_lifts':prior_nine,
               'eleven_core_negative_cycle_packing':NEGATIVE_CYCLE_PACKING,
               'eleven_core_cycle_loads':[[h,k,load,abs(J[h,k])] for (h,k),load in sorted(loads.items())],
               'random_seed': 202610030915, 'random_core_vectors': random_seeds,
               'random_audit_rows': random_rows, 'total_coherent_orders': len(all_rows),
               'vertices_in_positive_orders': sum(1 << r['n'] for r in all_rows),
               'actual_signed_orders_sorted': sum(r['signed_orders_independently_sorted'] for r in all_rows),
               'deterministic_sha256': digest.hexdigest(),
               'scope': 'Specified dominant-tail theorem audit; no coverage of all additive sweeps.'}
    Path(__file__).with_name('cardinality_tail_amplification_verification.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('random_audit_rows','random_core_vectors','compact_lifts','positive_payment_lifts','improved_core_lifts','prior_nine_core_lifts','exact_spin_certificates','eleven_core_negative_cycle_packing','eleven_core_cycle_loads')}, indent=2))


if __name__ == '__main__':
    main()
