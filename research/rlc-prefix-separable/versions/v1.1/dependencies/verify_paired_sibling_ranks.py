#!/usr/bin/env python3
"""Exact audits of a paired-sibling coordinate-tree family.

Finite sweeps are audits only. The general lexicographic range and
prefix separation have analytic proofs in PAIRED_SIBLING_RANKS.md.
"""
import hashlib
import json
import random
import time
from collections import Counter, defaultdict
from pathlib import Path
from verify_gray_reflection_graph import positive_chambers, order_and_scores, counts


def rank(x, n, mask, top=0):
    value, offset = 0, 0
    for h in range(n-1):
        index = offset+(x >> (h+2))
        value |= (((x >> h) ^ (x >> (h+1)) ^ (mask >> index)) & 1) << h
        offset += 1 << (n-h-2)
    value |= (((x >> (n-1)) & 1) ^ top) << (n-1)
    return value


def reflection_mask(n, mask, z, top=0):
    # rho(x xor z) remains in the same family.
    result, offset = 0, 0
    for h in range(n-1):
        for prefix in range(1 << (n-h-2)):
            old = offset+(prefix ^ (z >> (h+2)))
            bit = ((mask >> old) ^ (z >> h) ^ (z >> (h+1))) & 1
            result |= bit << (offset+prefix)
        offset += 1 << (n-h-2)
    return result, top ^ ((z >> (n-1)) & 1)


def separator_check(r, n, mask, top=0):
    N = 1 << n
    inverse = sorted(range(N), key=r.__getitem__)
    count = 0
    for excluded in range(1, N):
        z = inverse[excluded]
        coefficients, offset = [], 0
        for h in range(n-1):
            bit = ((z >> (h+1)) ^ (mask >> (offset+(z >> (h+2))))) & 1
            coefficients.append((3**h)*(-1 if bit else 1))
            offset += 1 << (n-h-2)
        coefficients.append((3**(n-1))*(-1 if top else 1))
        for x in range(N):
            score = sum(c*(((x >> h) & 1)-((z >> h) & 1)) for h,c in enumerate(coefficients))
            assert (score <= -1) == (r[x] < excluded)
            assert score == 0 if x == z else score != 0
            count += 1
    return count


def fast_runs(r, p):
    bits = 0
    for i in range(len(p)-1):
        bits |= int(r[p[i+1]] > r[p[i]]) << i
    return 1+((bits ^ (bits >> 1)) & ((1 << (len(p)-2))-1)).bit_count()


def linear_graph(p,n):
    offsets,offset = [],0
    for h in range(n-1):
        offsets.append(offset)
        offset += 1 << (n-h-2)
    variables,signs = [],[]
    for x,y in zip(p,p[1:]):
        h = (x ^ y).bit_length()-1
        variables.append(offset if h == n-1 else offsets[h]+(x >> (h+2)))
        gx,gy = x ^ (x >> 1), y ^ (y >> 1)
        signs.append(1 if gy > gx else -1)
    J = defaultdict(int)
    D = 0
    for i in range(len(signs)-1):
        a,b = variables[i:i+2]
        if a == b:
            D += 1
            assert signs[i] == -signs[i+1]
        else:
            J[tuple(sorted((a,b)))] += signs[i]*signs[i+1]
    edges = tuple((a,b,v) for (a,b),v in sorted(J.items()) if v)
    W = sum(abs(v) for a,b,v in edges)
    mixed = len(p)-2-D
    assert (mixed-W) % 2 == 0
    return {'D':D,'W':W,'K':(mixed-W)//2,'edges':edges,'variables':offset+1}


def cycle_certificate(digest):
    w = (1,6,8,4)
    p = order_and_scores(w)[0]
    g = linear_graph(p,4)
    assert (g['D'],g['W'],g['K']) == (0,10,2)
    J = {(a,b):v for a,b,v in g['edges']}
    cycles = ((0,7,1,6),(2,7,3,6))
    loads = defaultdict(int)
    for cycle in cycles:
        sign = 1
        for a,b in zip(cycle,cycle[1:]+cycle[:1]):
            key = tuple(sorted((a,b)))
            sign *= 1 if J[key] > 0 else -1
            loads[key] += 1
        assert sign == -1
    assert all(load <= abs(J[key]) for key,load in loads.items())
    mask = 8
    E = sum(v*(-1 if ((mask >> a) ^ (mask >> b)) & 1 else 1) for a,b,v in g['edges'])
    assert E == g['W']-2*len(cycles) == 6
    r = tuple(rank(x,4,mask) for x in p)
    R,C,_ = counts(r)
    assert R == 1+g['D']+g['K']+len(cycles) == 5
    cert = {'weights':w,'order':p,**g,'negative_cycles':cycles,'packing_value':2,
            'attaining_mask':mask,'E_max_certified':E,'phi_certified':2,'R_min_certified':R,'C_at_witness':C}
    digest.update(json.dumps(cert,sort_keys=True).encode())
    return cert


def numerical_audit(digest):
    rows = []
    separator_tests = 0
    reflection_tests = 0
    for n in range(1, 5):
        N = 1 << n
        variables = (1 << (n-1))-1
        histogram = Counter()
        cyclic_histogram = Counter()
        for mask in range(1 << variables):
            r = tuple(rank(x,n,mask) for x in range(N))
            assert sorted(r) == list(range(N))
            histogram[fast_runs(r,tuple(range(N)))] += 1
            cyclic_histogram[counts(r)[1]] += 1
            separator_tests += separator_check(r,n,mask)
            for z in range(N):
                mm, top = reflection_mask(n,mask,z)
                rr = tuple(rank(x,n,mm,top) for x in range(N))
                assert rr == tuple(r[x ^ z] for x in range(N))
                R = fast_runs(r,tuple(x ^ z for x in range(N)))
                assert (N+2)//3 <= R <= (2*N)//3
                reflection_tests += N
        assert sorted(histogram) == list(range((N+2)//3,(2*N)//3+1))
        row = {'n':n,'normalized_top_family_size':1 << variables,
               'lexical_run_histogram':dict(sorted(histogram.items())),
               'lexical_cyclic_histogram':dict(sorted(cyclic_histogram.items())),
               'minimum':min(histogram),'maximum':max(histogram)}
        rows.append(row)
        digest.update(json.dumps(row,sort_keys=True).encode())
    # Build attaining masks by exploiting the independent lowest signs;
    # every larger dimension is verified with actual rank permutations.
    def extremal(n, maximize):
        if n <= 2:
            return 0
        upper = extremal(n-2,True)
        T = 1 << (n-2)
        upper_values = [rank(t,n-2,upper) for t in range(T)]
        signs = [1 if upper_values[t+1] > upper_values[t] else -1 for t in range(T-1)]
        aa = [0]*T
        aa[0] = signs[0] if maximize else -signs[0]
        aa[-1] = -signs[-1] if maximize else signs[-1]
        for t in range(1,T-1):
            # At a straight upper vertex both choices cost one.
            aa[t] = -signs[t-1] if maximize else signs[t-1]
        lower = sum(int(a < 0) << t for t,a in enumerate(aa))
        offset = (1 << (n-2))+(1 << (n-3))
        return lower | (upper << offset)
    rng = random.Random(202610030911)
    attained = []
    for n in range(5,17):
        N = 1 << n
        masks = [extremal(n,False),extremal(n,True)]
        values = []
        for mask in masks:
            r = tuple(rank(x,n,mask) for x in range(N))
            assert len(set(r)) == N
            values.append(fast_runs(r,tuple(range(N))))
        assert values == [(N+2)//3,(2*N)//3]
        for _ in range(3):
            mask = rng.getrandbits((1 << (n-1))-1)
            z = rng.randrange(N)
            r = tuple(rank(x,n,mask) for x in range(N))
            R = fast_runs(r,tuple(x ^ z for x in range(N)))
            assert (N+2)//3 <= R <= (2*N)//3
        attained.append({'n':n,'minimum':values[0],'maximum':values[1]})
    return rows, attained, separator_tests, reflection_tests


def cyclic_extremal(n, maximize):
    if n <= 2:
        return 0
    upper = cyclic_extremal(n-2,True)
    T = 1 << (n-2)
    values = [rank(t,n-2,upper) for t in range(T)]
    signs = [1 if values[(t+1)%T] > values[t] else -1 for t in range(T)]
    aa = [(-signs[(t-1)%T] if maximize else signs[(t-1)%T]) for t in range(T)]
    lower = sum(int(a < 0) << t for t,a in enumerate(aa))
    return lower | (upper << ((1 << (n-2))+(1 << (n-3))))


def row_audit(digest):
    rng = random.Random(202610030934)
    extremal_rows = []
    actual_orders = 0
    for n in range(2,17):
        N = 1 << n
        observed = []
        for maximize in (False,True):
            mask = cyclic_extremal(n,maximize)
            r = tuple(rank(x,n,mask) for x in range(N))
            observed.append(counts(r)[1])
        assert observed == [(N+2*((-1)**n))//3,(2*N-2*((-1)**n))//3]
        extremal_rows.append({'n':n,'minimum_C':observed[0],'maximum_C':observed[1]})
    rows = []
    for n in range(3,13):
        N = 1 << n
        for d in range(2,min(n,6)+1):
            ell = n-d
            H, T = 1 << d, 1 << ell
            # Embed a cyclic-minimal top core, arbitrary lower orientations.
            top_mask = cyclic_extremal(d,False)
            offset = sum(1 << (n-h-2) for h in range(ell))
            mask = rng.getrandbits(offset) | (top_mask << offset)
            r = tuple(rank(x,n,mask) for x in range(N))
            weights = tuple(H*(1 << h) for h in range(ell))+tuple(1 << h for h in range(d))
            for z in (0,rng.randrange(N),rng.randrange(N)):
                signed = tuple(-v if z >> h & 1 else v for h,v in enumerate(weights))
                p = order_and_scores(signed)[0]
                top_z = z >> ell
                core = tuple(rank(x ^ top_z,d,top_mask) for x in range(H))
                R0,C0,_ = counts(core)
                R,C,_ = counts(tuple(r[x] for x in p))
                assert C == T*C0
                assert R == (T-1)*C0+R0
                assert R >= N//4+1
                actual_orders += 1
            # Exact row minimum is attained when z=0; same rank also minimizes
            # linear count in its cyclic-minimal core if d is even.
            if d % 2 == 0:
                # The first and last lower signs can be chosen to attain delta=0.
                # Exhausting only four endpoint choices suffices.
                first_index = offset
                last_index = offset+(1 << (d-2))-1
                for flips in (0,1 << first_index,1 << last_index,(1 << first_index)|(1 << last_index)):
                    candidate = mask ^ flips
                    cc = tuple(rank(x >> ell,d,(candidate >> offset)) for x in range(0,N,T))
                    rr,cy,_ = counts(cc)
                    if cy == (H+2)//3 and rr == cy:
                        mask = candidate
                        break
            r = tuple(rank(x,n,mask) for x in range(N))
            p = order_and_scores(weights)[0]
            R,C,_ = counts(tuple(r[x] for x in p))
            predicted = T*((H+2*((-1)**d))//3)+int(d%2)
            assert R == predicted
            row = {'n':n,'fast_top_dimension':d,'row_count':T,'minimum_R':R,'C':C}
            rows.append(row)
            digest.update(json.dumps(row,sort_keys=True).encode())
    return {'cyclic_extrema':extremal_rows,'genuine_signed_row_orders_sorted':actual_orders,
            'attained_row_minima':rows,'scope':'Only lexicographic fast-top-face row sweeps.'}


def q4_general_sweeps(digest):
    n, N = 4, 16
    orders = [tuple(x ^ z for x in order_and_scores(w)[0])
              for w in positive_chambers(n) for z in range(N)]
    assert len(orders) == len(set(orders)) == 5376
    distribution, rank_rows = Counter(), []
    worst = None
    for mask in range(128):
        r = tuple(rank(x,n,mask) for x in range(N))
        best, witness = N, None
        for i,p in enumerate(orders):
            R = fast_runs(r,p)
            if R < best:
                best, witness = R, i
        distribution[best] += 1
        rank_rows.append({'mask':mask,'RLC':best,'minimizing_order_index':witness})
        if worst is None or best < worst['R']:
            p = orders[witness]
            worst = {'R':best,'mask':mask,'order':p,'rank_values':r}
        digest.update(json.dumps(rank_rows[-1],sort_keys=True).encode())
    # Independently sort the exact signed integer witness.
    seed_index, z = divmod(rank_rows[worst['mask']]['minimizing_order_index'],N)
    weights = positive_chambers(n)[seed_index]
    signed = tuple(-v if z >> h & 1 else v for h,v in enumerate(weights))
    assert order_and_scores(signed)[0] == worst['order']
    R,C,_ = counts(tuple(worst['rank_values'][x] for x in worst['order']))
    assert R == worst['R']
    worst.update({'signed_weights':signed,'C':C})
    return {'all_signed_q4_chambers':5376,'all_normalized_ranks':128,
            'rank_sweep_pairs':5376*128,'RLC_histogram':dict(sorted(distribution.items())),
            'best_RLC_in_family':max(distribution),'worst_RLC_in_family':min(distribution),
            'rank_rows':rank_rows,'worst_witness':worst,
            'scope':'Finite Q4 coverage only, not a general-weight lower bound for all n.'}


def main():
    start = time.monotonic()
    digest = hashlib.sha256()
    numerical, attained, separators, reflections = numerical_audit(digest)
    rows = row_audit(digest)
    cycles = cycle_certificate(digest)
    q4 = q4_general_sweeps(digest)
    receipt = {'status':'PASS','violations':0,'lexical_exhaustion':numerical,
               'attaining_masks_verified':attained,'prefix_separator_vertex_tests':separators,
               'reflection_rank_vertex_tests':reflections,'q4_arbitrary_additive_sweeps':q4,
               'row_lift_audit':rows,
               'linear_graph_cycle_certificate':cycles,
               'random_seed':202610030911,'deterministic_sha256':digest.hexdigest(),
               'elapsed_seconds':time.monotonic()-start}
    Path(__file__).with_name('paired_sibling_ranks_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('q4_arbitrary_additive_sweeps','row_lift_audit')},indent=2))
    print(json.dumps({k:v for k,v in q4.items() if k not in ('rank_rows','worst_witness')}))


if __name__ == '__main__':
    main()
