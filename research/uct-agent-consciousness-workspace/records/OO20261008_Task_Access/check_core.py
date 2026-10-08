#!/usr/bin/env python3
"""Standard-library exact checks. Run: python check_core.py. Not an experience assay."""
from fractions import Fraction as F
from itertools import product
import json


def parity(x):
    return x.bit_count() & 1


def span(rows):
    out = {0}
    for row in rows:
        out |= {x ^ row for x in tuple(out)}
    return out


def encode(x, rows):
    return sum(parity(x & row) << j for j, row in enumerate(rows))


def optimal_profile(values, n):
    profile = []
    for a in range(1, 1 << n):
        counts = {}
        for x, message in enumerate(values):
            counts.setdefault(message, [0, 0])[parity(x & a)] += 1
        profile.append(F(sum(max(c) for c in counts.values()), 1 << n))
    return profile


def walsh(signs):
    out = list(signs)
    step = 1
    while step < len(out):
        for i in range(0, len(out), 2 * step):
            for j in range(i, i + step):
                x, y = out[j], out[j + step]
                out[j], out[j + step] = x + y, x - y
        step *= 2
    return out


def quadratic(x, m):
    return sum(((x >> (2*j)) & 1) * ((x >> (2*j+1)) & 1)
               for j in range(m)) & 1


matrix_cases = 0
for n in range(1, 5):
    for k in range(4):
        for rows in product(range(1 << n), repeat=k):
            U = span(rows)
            p = optimal_profile([encode(x, rows) for x in range(1 << n)], n)
            assert p == [F(1) if a in U else F(1, 2) for a in range(1, 1 << n)]
            matrix_cases += 1

profiles = {}
for name, rows in [('item', (1, 2)), ('relation', (5, 10))]:
    p = optimal_profile([encode(x, rows) for x in range(16)], 4)
    profiles[name] = [sum(p[a-1] for a in (1,2,4,8))/4,
                      sum(p[a-1] for a in (5,10))/2, sum(p)/15]
assert profiles == {'item': [F(3,4), F(1,2), F(3,5)],
                    'relation': [F(1,2), F(1), F(3,5)]}

best = -1
maximizers = 0
for code in range(65536):
    W = walsh([1 - 2*((code >> x) & 1) for x in range(16)])
    value = sum(abs(t) for t in W[1:])
    if value > best:
        best, maximizers = value, 1
    elif value == best:
        maximizers += 1
assert best == 60 and maximizers == 896
assert optimal_profile([quadratic(x, 2) for x in range(16)], 4) == [F(5,8)]*15

family = []
for m in range(1, 7):
    N = 1 << (2*m)
    W = walsh([1 - 2*quadratic(x, m) for x in range(N)])
    assert all(W[a] == (1 << m)*(1 - 2*quadratic(a,m)) for a in range(N))
    nonlinear = F(1,2) + F(1, 2*(1 << m))
    linear = F(1,2) + F(1, 2*((1 << m)+1))
    assert nonlinear > linear
    family.append([2*m, str(nonlinear), str(linear)])

noise = []
for rows in ((1,2), (3,2)):
    masses = {}
    eps = F(1,10)
    for x in range(4):
        for err in range(4):
            p = eps**err.bit_count() * (1-eps)**(2-err.bit_count()) / 4
            masses.setdefault(encode(x,rows)^err, [F(0),F(0)])[x & 1] += p
    noise.append(sum(max(v) for v in masses.values()))
assert noise == [F(9,10),F(41,50)]

subspaces = {frozenset(span(rows)) for k in range(4)
             for rows in product(range(16), repeat=k)} | {frozenset(range(16))}
assert len(subspaces) == 67
for U in subspaces:
    for V in subspaces:
        assert all(int(a in U) >= int(a in V) for a in range(1,16)) == (V <= U)
assert all(encode(x,(a,)) == parity(x&a) for x in range(16) for a in range(1,16))

print(json.dumps({'status':'PASS', 'matrix_cases':matrix_cases,
    'profiles':{k:[str(x) for x in v] for k,v in profiles.items()},
    'one_bit_four_variable_optimum':'5/8', 'maximizing_encoders':maximizers,
    'even_families':family, 'noise_accuracies':[str(x) for x in noise],
    'subspace_comparisons':4489, 'scope':'Exact finite mathematics; no phenomenal measurement'}, indent=2))
