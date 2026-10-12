#!/usr/bin/env python3
"""Finite checks for conditional exclusion witnesses; not a consciousness test.

Standard library only. All numerics are synthetic/exact. No IIT phi is computed.
Run: python check_exclusion.py --out exact_results.json
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


def stable(mask: int, edges: tuple[tuple[int, int], ...]) -> bool:
    return all(not ((mask >> i & 1) and (mask >> j & 1)) for i, j in edges)


def alpha(n: int, edges: tuple[tuple[int, int], ...], weights: tuple[int, ...]) -> int:
    if len(weights) != n or any(w < 0 for w in weights):
        raise ValueError('Need n nonnegative weights')
    if any(not (0 <= i < j < n) for i, j in edges):
        raise ValueError('Edges must satisfy 0 <= i < j < n')
    return max(sum(weights[i] for i in range(n) if mask >> i & 1)
               for mask in range(1 << n) if stable(mask, edges))


def violation_lower(lower: tuple[Fraction, ...], edges: tuple[tuple[int, int], ...],
                    weights: tuple[int, ...]) -> Fraction:
    if any(x < 0 or x > 1 for x in lower):
        raise ValueError('Occupancy lower bounds must lie in [0,1]')
    a = alpha(len(lower), edges, weights)
    total = sum(weights)
    if total == a:
        return Fraction(0)  # No positively weighted exclusion constraint.
    return max(Fraction(0), (sum(w*x for w, x in zip(weights, lower))-a)/(total-a))


def run() -> dict:
    pair_rows = 0
    for n in range(1, 9):
        for a in range(1 << n):
            for b in range(1 << n):
                k_a, k_b, common = a.bit_count(), b.bit_count(), (a & b).bit_count()
                assert max(0, k_a+k_b-n) <= common <= min(k_a, k_b)
                pair_rows += 1
    graph_rows = schedule_rows = nonexclusive_schedules = 0
    for n in range(2, 5):
        possible_edges = tuple(combinations(range(n), 2))
        for graph_mask in range(1 << len(possible_edges)):
            edges = tuple(e for j, e in enumerate(possible_edges) if graph_mask >> j & 1)
            graph_rows += 1
            for weights in ((1,)*n, tuple(range(1, n+1))):
                cap = alpha(n, edges, weights)
                total = sum(weights)
                scores = [sum(weights[i] for i in range(n) if mask >> i & 1)
                          for mask in range(1 << n)]
                bad = [int(not stable(mask, edges)) for mask in range(1 << n)]
                for a, b, c in product(range(1 << n), repeat=3):
                    score = scores[a]+scores[b]+scores[c]
                    violations = bad[a]+bad[b]+bad[c]
                    # Integrating the pointwise bound; cross-multiplied exactly.
                    assert score-3*cap <= (total-cap)*violations
                    if violations == 0:
                        assert score <= 3*cap
                    else:
                        nonexclusive_schedules += 1
                    schedule_rows += 1
    edge = ((0, 1),)
    pair = violation_lower((Fraction(4, 5), Fraction(7, 10)), edge, (1, 1))
    assert pair == Fraction(1, 2)
    c5 = ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))
    half = (Fraction(1, 2),)*5
    assert all(half[i]+half[j] <= 1 for i, j in c5)
    assert alpha(5, c5, (1,)*5) == 2
    c5_bound = violation_lower(half, c5, (1,)*5)
    assert c5_bound == Fraction(1, 6)
    # Sharp witness: five stable pairs plus the all-on state, one slot each.
    pairs = [mask for mask in range(32) if mask.bit_count()==2 and stable(mask, c5)]
    schedule = pairs + [31]
    assert len(schedule) == 6
    assert all(sum(mask >> i & 1 for mask in schedule)==3 for i in range(5))
    assert sum(not stable(mask, c5) for mask in schedule)==1
    # Synthetic calibration allowance: 0.02 measurement + 0.03 overcount.
    lower = (Fraction(1, 2)-Fraction(2, 100)-Fraction(3, 100),)*5
    robust = violation_lower(lower, c5, (1,)*5)
    assert robust == Fraction(1, 12)
    # Unknown overlap can destroy the inference; the empty graph is admissible here.
    uncertain_support = violation_lower(lower, (), (1,)*5)
    assert uncertain_support == 0
    # Same means, different overlap: alternation and all-on/all-off.
    alt_a, alt_b = 0b11110000, 0b00001111
    con_a, con_b = 0b11110000, 0b11110000
    assert (alt_a.bit_count(), alt_b.bit_count()) == (con_a.bit_count(), con_b.bit_count())
    assert (alt_a & alt_b).bit_count()==0 and (con_a & con_b).bit_count()==4
    # Different sample windows make each channel look continuously present.
    assert (alt_a & alt_a).bit_count()/alt_a.bit_count() == 1
    assert (alt_b & alt_b).bit_count()/alt_b.bit_count() == 1
    # Persistent reports m_A=m_B=1 can coexist despite exclusive targets.
    # Correct overcount allowance (1/2 each) prevents the invalid target verdict.
    wrong = violation_lower((Fraction(1), Fraction(1)), edge, (1, 1))
    corrected = violation_lower((Fraction(1, 2), Fraction(1, 2)), edge, (1, 1))
    assert wrong == 1 and corrected == 0
    return {
        'study': 'XRT20261012', 'version': '0.1.0',
        'evidence_type': 'synthetic_exact_finite_checks_not_empirical',
        'iit_phi_computed': False,
        'basal_experience_or_subject_count_identified': False,
        'pair_trace_checks': pair_rows, 'simple_graphs_n2_through_n4': graph_rows,
        'three_slot_graph_weight_schedule_checks': schedule_rows,
        'checked_schedules_with_at_least_one_conflict': nonexclusive_schedules,
        'assertion_failures': 0,
        'fixtures': {
            'two_channels_0.8_0.7_minimum_overlap': str(pair),
            'same_marginals_half_alternating_overlap': '0',
            'same_marginals_half_concurrent_overlap': '1/2',
            'c5_half_occupancy_all_edge_tests_pass': True,
            'c5_independence_number': 2,
            'c5_minimum_violation_fraction_sharp': str(c5_bound),
            'c5_sharp_six_slot_schedule_bitmasks': schedule,
            'c5_measurement_error_0.02_overcount_0.03_lower_fraction': str(robust),
            'c5_overlap_unverified_empty_graph_allowed_lower_fraction': str(uncertain_support),
            'different_windows_false_joint_inference': True,
            'persistent_report_invalid_target_bound': str(wrong),
            'persistent_report_with_valid_overcount_target_bound': str(corrected)
        },
        'conditions': ['common normalized time measure', 'same event and actual candidates',
                       'independently grounded overlap/grain', 'calibrated target-specific lower bounds',
                       'nonnegative weights', 'no inference from report alone'],
        'map_status': 'PENDING_MAP_AUDIT_INCOMPLETE_DISABLED',
        'publication_decision': 'HOLD_NO_DOI'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('exact_results.json'))
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
