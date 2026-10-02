#!/usr/bin/env python3
"""Exact finite pressure tests for the 2026-10-02 RLC research note.

The proofs in NOTE.md are all-dimensional; these tests check implementations
and search for small counterexamples. NumPy is used only for integer arrays.
No numerical optimization or floating-point probability test is used.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import time
import numpy as np

SEED = 202610022315


def rank_from_code(n, code):
    # Independent leaf traversal, not the pairwise LCA comparison formula.
    stack = [(0, 0, 1 << n)]
    order = []
    while stack:
        u, lo, hi = stack.pop()
        if hi - lo == 1:
            order.append(lo)
            continue
        mid = (lo + hi) // 2
        left, right = (2*u+1, lo, mid), (2*u+2, mid, hi)
        first, last = (left, right) if (code >> u) & 1 else (right, left)
        stack.extend((last, first))
    rank = [0] * len(order)
    for i, x in enumerate(order):
        rank[x] = i
    return rank


def edge_label(a, b, n):
    u = 0
    for j in range(n-1, -1, -1):
        aa, bb = (a >> j) & 1, (b >> j) & 1
        if aa != bb:
            return u, bb-aa
        u = 2*u+1+aa
    raise AssertionError('distinct leaves required')


def run_count(values):
    signs = [1 if b > a else -1 for a, b in zip(values, values[1:])]
    return 1 + sum(a != b for a, b in zip(signs, signs[1:]))


def rational_tail_check(prob, length, threshold, read):
    # Exact exponentiated Chernoff bound, avoiding logarithms and roots:
    # prob**read <= ((1+a)/2)**length / a**threshold,
    # with a=threshold/(length-threshold), or the a -> 0 limit.
    assert 0 <= threshold < Fraction(length, 2) and read >= 1
    if threshold == 0:
        rhs = Fraction(1, 2) ** length
    else:
        a = Fraction(threshold, length-threshold)
        rhs = ((1+a)/2) ** length / a ** threshold
    assert prob ** read <= rhs


def check_readk():
    rng = random.Random(SEED)
    rows, digest = [], hashlib.sha256()
    for n in range(1, 5):
        N, nodes = 1 << n, (1 << n)-1
        codes = np.arange(1 << nodes, dtype=np.int64)
        ranks = np.array([rank_from_code(n, int(c)) for c in codes], dtype=np.int16)
        spins = np.array([[1 if (int(c)>>u)&1 else -1 for u in range(nodes)]
                          for c in codes], dtype=np.int8)
        if n <= 3:
            permutations = itertools.permutations(range(N))
        else:
            selected = {tuple(range(N)), tuple(reversed(range(N)))}
            for _ in range(15):
                v = list(range(N)); rng.shuffle(v); selected.add(tuple(v))
            for _ in range(15):
                w = [rng.randint(-20, 20) for _ in range(n)]
                scores = [sum(w[j]*((x>>j)&1) for j in range(n)) for x in range(N)]
                if len(set(scores)) == N:
                    selected.add(tuple(sorted(range(N), key=scores.__getitem__)))
            permutations = sorted(selected)
        count = uniform = refined = impossible = 0
        for pi in permutations:
            labels = [edge_label(a, b, n) for a, b in zip(pi, pi[1:])]
            indices = np.array([u for u, eta in labels], dtype=np.int16)
            eta = np.array([eta for u, eta in labels], dtype=np.int8)
            actual = np.sign(np.diff(ranks[:, pi], axis=1))
            assert np.array_equal(actual, spins[:, indices]*eta)
            runs = 1 + np.count_nonzero(actual[:, 1:] != actual[:, :-1], axis=1)
            J = int(sum(a == b for a, b in zip(indices, indices[1:])))
            L = N-2-J
            m = Counter(map(int, indices))
            degrees = Counter()
            for a, b in zip(indices, indices[1:]):
                if a != b:
                    degrees[int(a)] += 1; degrees[int(b)] += 1
            d = max(degrees.values(), default=0)
            assert all(degrees[u] <= 2*m[u] for u in m)
            assert int(runs.min()) >= max(m.values())
            hist = np.bincount(runs, minlength=N).tolist()
            digest.update(json.dumps([n, list(pi), hist, J, d], separators=(',', ':')).encode())
            for K in range(1, N//2):
                bad = sum(hist[:K+1])
                prob = Fraction(bad, len(codes))
                if max(m.values()) > K:
                    assert bad == 0; impossible += 1
                else:
                    rational_tail_check(prob, N-2, K-1, 2*K)
                    uniform += 1
                if J > K-1:
                    assert bad == 0
                elif L > 0 and K-1-J < Fraction(L, 2):
                    rational_tail_check(prob, L, K-1-J, d)
                    refined += 1
            count += 1
        rows.append(dict(n=n, permutations=count, sign_assignments=len(codes),
                         rank_sequences=count*len(codes), uniform_tail_checks=uniform,
                         refined_tail_checks=refined, deterministic_empty_checks=impossible,
                         coverage='all permutations and all signs' if n <= 3 else
                         'selected permutations, all signs'))
        print('read-k dimension', n, 'passed', flush=True)
    return dict(rows=rows, enumeration_sha256=digest.hexdigest())


def top_code(code, d):
    return code & ((1 << ((1 << d)-1))-1)


def interleaving_prediction(sigma, tau, L):
    vals = [sigma[z] for z in tau]
    a = [1 if y > x else -1 for x, y in zip(vals, vals[1:])]
    r = 1 + sum(x != y for x, y in zip(a, a[1:]))
    b = -1 if vals[-1] > vals[0] else 1
    return 1 + L*(r-1) + (L-1)*((a[-1] != b)+(b != a[0]))


def check_interleaving():
    rng = random.Random(SEED+1)
    checked = 0
    # All top orientations for d<=3; all permutations only for d<=2, with
    # 32 selected permutations at d=3. Lower orientations are sampled.
    for d in range(1, 4):
        k = 1 << d
        taus = list(itertools.permutations(range(k))) if d <= 2 else [
            tuple(range(k)), tuple(reversed(range(k)))]
        if d == 3:
            for _ in range(30):
                p = list(range(k)); rng.shuffle(p); taus.append(tuple(p))
        for n in (d, d+1, d+2):
            L, nodes = 1 << (n-d), (1 << n)-1
            for tc in range(1 << (k-1)):
                code = rng.getrandbits(nodes)
                mask = (1 << (k-1))-1
                code = (code & ~mask) | tc
                rank = rank_from_code(n, code)
                sigma = rank_from_code(d, tc)
                for tau in taus:
                    pi = [(z << (n-d)) | y for y in range(L) for z in tau]
                    actual = run_count([rank[x] for x in pi])
                    assert actual == interleaving_prediction(sigma, tau, L)
                    assert actual <= L*(run_count([sigma[z] for z in tau])+1)-1
                    checked += 1
    # Verify the score realization, including negative top weights, n<=10.
    realized = 0
    for n in range(2, 11):
        for d in range(1, min(n, 5)+1):
            k, L = 1 << d, 1 << (n-d)
            v = [(1 if rng.randrange(2) else -1)*3**h for h in range(d)]
            top_scores = [sum(v[h]*((z>>h)&1) for h in range(d)) for z in range(k)]
            tau = sorted(range(k), key=top_scores.__getitem__)
            A = 1+sum(map(abs, v))
            w = [A*2**j for j in range(n-d)] + v
            scores = [sum(w[j]*((x>>j)&1) for j in range(n)) for x in range(1<<n)]
            assert len(set(scores)) == 1 << n
            pi = sorted(range(1<<n), key=scores.__getitem__)
            assert pi == [(z << (n-d)) | y for y in range(L) for z in tau]
            code = rng.getrandbits((1<<n)-1)
            rank, sigma = rank_from_code(n, code), rank_from_code(d, top_code(code, d))
            assert run_count([rank[x] for x in pi]) == interleaving_prediction(sigma, tau, L)
            realized += 1
    return dict(identity_cases=checked, generic_integer_score_realizations=realized,
                coverage='all top orientations d<=3; all permutations d<=2; 32 selected permutations d=3; lower signs sampled; n<=10 integer sweeps')


def check_barrier():
    rng = random.Random(SEED+2)
    examples = []
    # Exact full event enumeration at n<=4; selected lower signs n=5..10.
    for n in range(2, 11):
        for d in range(1, min(n, 4)+1):
            k, L, nodes = 1 << d, 1 << (n-d), (1 << n)-1
            mask = (1 << (k-1))-1
            free = nodes-(k-1)
            lowers = range(1 << free) if n <= 4 else [rng.getrandbits(free) for _ in range(8)]
            pi = [(z << (n-d)) | y for y in range(L) for z in range(k)]
            count = 0
            for lower in lowers:
                for tc in (0, mask):
                    code = (lower << (k-1)) | tc
                    rank = rank_from_code(n, code)
                    assert run_count([rank[x] for x in pi]) == 2*L-1
                    count += 1
            examples.append(dict(n=n, d=d, k=k, runs=2*L-1,
                                 event_probability=f'1/{1<<(k-2)}', cases=count,
                                 coverage='entire event' if n <= 4 else 'selected lower signs'))
    return examples


def finite_certificate(n, K, a):
    # Rigorous sufficient existence certificate via rational read-k mgf bound.
    # Chamber upper bound S_n and both sides are integers; no floating point.
    N, H = 1 << n, ((3**n)-1)//2
    import math
    S = 2*sum(math.comb(H-1, j) for j in range(n))
    A, B = a.numerator, a.denominator
    # S**(2K)*((1+a)/2)**(N-2)/a**(K-1) < 1.
    left = S**(2*K)*(A+B)**(N-2)
    right = (2*B)**(N-2)*A**(K-1)
    left *= B**(K-1)
    passed = left < right
    assert passed
    return dict(n=n, K=K, M_n_at_least=K+1, a=str(a),
                chamber_bound=str(S), left_bits=left.bit_length(), right_bits=right.bit_length(),
                integer_inequality='S^(2K)*(A+B)^(N-2)*B^(K-1) < (2B)^(N-2)*A^(K-1)',
                left_sha256=hashlib.sha256(left.to_bytes((left.bit_length()+7)//8,'big')).hexdigest(),
                right_sha256=hashlib.sha256(right.to_bytes((right.bit_length()+7)//8,'big')).hexdigest())


def main():
    started = time.monotonic()
    result = dict(seed=SEED, readk=check_readk(), interleaving=check_interleaving(),
                  barrier=check_barrier())
    # A conservative finite instance. Asymptotic constant is proved in NOTE.md.
    result['finite_certificates'] = [finite_certificate(12, 11, Fraction(5, 2042)),
                                     finite_certificate(16, 98, Fraction(97, 65437))]
    result['elapsed_seconds'] = round(time.monotonic()-started, 3)
    result['violations'] = 0
    Path(__file__).with_name('verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
