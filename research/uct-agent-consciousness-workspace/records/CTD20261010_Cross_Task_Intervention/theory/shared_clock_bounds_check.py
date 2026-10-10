#!/usr/bin/env python3
"""Finite checks for proportional and monotone shared-clock distances.

No neural or participant data are used here.  For 729 integer log-width
matrices, proportional distance is checked by an independent nuisance-parameter
feasibility search; monotone distance is checked against an exhaustive finite
set of all common-order half-grid corrected matrices.  The half-grid contains
an optimum for integer data by the constructive proof in the research note.
"""

from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
from pathlib import Path
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parent
PERMUTATIONS = tuple(permutations(range(3)))


def proportional_distance(log_width):
    differences = [a-b for a,b in zip(*log_width)]
    return (max(differences)-min(differences))/4


def proportional_witness(log_width):
    row0, row1 = log_width
    differences = [a-b for a,b in zip(row0,row1)]
    offset = (max(differences)+min(differences))/2
    column_means = [(a+b)/2 for a,b in zip(row0,row1)]
    fitted = [[column + offset/2 for column in column_means],
              [column - offset/2 for column in column_means]]
    error = max(abs(a-b) for row,fitrow in zip(log_width,fitted)
                for a,b in zip(row,fitrow))
    return fitted, error


def proportional_grid_feasibility(log_width):
    # Gauge-fix a_0=0. Search a_1 independently of the closed-form d_f range.
    for epsilon in [k/4 for k in range(9)]:
        for second_task_offset in [k/4 for k in range(-16,17)]:
            feasible = True
            for first, second in zip(*log_width):
                first_interval = (first-epsilon, first+epsilon)
                second_interval = (second-second_task_offset-epsilon,
                                   second-second_task_offset+epsilon)
                if max(first_interval[0], second_interval[0]) > min(first_interval[1], second_interval[1]):
                    feasible = False
                    break
            if feasible:
                return epsilon
    raise AssertionError("Search range should include all [-1,1] log matrices")


def order_distance(log_width, order):
    worst = max([0] + [row[order[j]] - row[order[k]]
                      for row in log_width
                      for j in range(len(order))
                      for k in range(j+1,len(order))])
    return worst/2


def monotone_distance(log_width):
    values = [(order_distance(log_width, order), order) for order in PERMUTATIONS]
    return min(values)


def monotone_witness(log_width, order, epsilon):
    fitted = []
    for row in log_width:
        result = [None]*len(row)
        running = -math.inf
        for position in order:
            running = max(running, row[position]-epsilon)
            result[position] = running
            assert running <= row[position]+epsilon+1e-12
        fitted.append(result)
    return fitted


def pairwise_opposition_distance(log_width):
    # An optional two-task closed form, verified against full order enumeration.
    a,b = log_width
    bottleneck = max([0] + [min(abs(a[j]-a[k]), abs(b[j]-b[k]))
                            for j in range(len(a))
                            for k in range(j+1,len(a))
                            if (a[j]-a[k])*(b[j]-b[k]) < 0])
    return bottleneck/2


def exact_strict_common_order(log_width):
    a,b = log_width
    sign = lambda value: int(value > 0) - int(value < 0)
    return all(sign(a[j]-a[k]) == sign(b[j]-b[k])
               for j in range(len(a)) for k in range(len(a)))


def all_monotone_half_grid_targets():
    target_set = set()
    half_grid = [-1, -.5, 0, .5, 1]
    ordered_rows = tuple(combinations_with_replacement(half_grid,3))
    for order in PERMUTATIONS:
        for left,right in product(ordered_rows, repeat=2):
            rows = [[None]*3 for _ in range(2)]
            for rank,column in enumerate(order):
                rows[0][column] = left[rank]
                rows[1][column] = right[rank]
            target_set.add(tuple(rows[0]+rows[1]))
    return np.array(sorted(target_set), dtype=float)


def counterexamples():
    # 1: nonlinear monotone bridge preserves common latent order but not ratios.
    nonlinear = [[0, math.log(2), math.log(4)],
                 [0, 2*math.log(2), 2*math.log(4)]]
    # 2: a directional reversal needs a nonzero correction even under monotonicity.
    reversal = [[0,1,2],[0,2,1]]
    # 3: mismatch of exact ties belongs to the closed model but not the strict one.
    ties = [[0,0,1],[0,1,2]]
    # 4: a group summary can conceal incompatible subject-specific effects.
    cancellation_subject1 = [[0,1,0],[0,0,0]]
    cancellation_subject2 = [[0,0,0],[0,1,0]]
    averaged_logs = [[(a+b)/2 for a,b in zip(rowa,rowb)]
                     for rowa,rowb in zip(cancellation_subject1,cancellation_subject2)]
    examples = []
    for name, matrix in [("nonlinear_bridge", nonlinear),
                         ("direction_reversal", reversal),
                         ("strict_tie_failure", ties),
                         ("cancellation_subject1",cancellation_subject1),
                         ("cancellation_subject2",cancellation_subject2),
                         ("averaged_logs",averaged_logs)]:
        epsilon_mon, order = monotone_distance(matrix)
        examples.append({"name":name,"log_widths":matrix,
                         "epsilon_proportional":proportional_distance(matrix),
                         "epsilon_monotone_closure":epsilon_mon,
                         "best_common_order":order,
                         "exact_strict_common_order":exact_strict_common_order(matrix)})
    assert proportional_distance(nonlinear) > 0
    assert monotone_distance(nonlinear)[0] == 0
    assert exact_strict_common_order(nonlinear)
    assert monotone_distance(reversal)[0] == .5
    assert monotone_distance(ties)[0] == 0 and not exact_strict_common_order(ties)
    assert proportional_distance(averaged_logs) == 0
    assert proportional_distance(cancellation_subject1) == .25
    assert proportional_distance(cancellation_subject2) == .25
    return examples


def main():
    targets = all_monotone_half_grid_targets()
    count = 0
    strict_fail_closed_pass = 0
    for entries in product((-1,0,1),repeat=6):
        matrix = [list(entries[:3]),list(entries[3:])]
        epsilon_prop = proportional_distance(matrix)
        assert epsilon_prop == proportional_grid_feasibility(matrix)
        prop_fit, prop_error = proportional_witness(matrix)
        assert prop_error == epsilon_prop
        assert proportional_distance(prop_fit) == 0
        epsilon_mon, order = monotone_distance(matrix)
        fit = monotone_witness(matrix, order, epsilon_mon)
        assert all(row[order[j]] <= row[order[j+1]] for row in fit for j in range(2))
        assert max(abs(a-b) for row,fitrow in zip(matrix,fit)
                   for a,b in zip(row,fitrow)) == epsilon_mon
        brute_distance = float(np.min(np.max(np.abs(targets - np.array(entries)),axis=1)))
        assert epsilon_mon == brute_distance
        assert epsilon_mon == pairwise_opposition_distance(matrix)
        assert epsilon_mon <= epsilon_prop
        if epsilon_mon == 0 and not exact_strict_common_order(matrix):
            strict_fail_closed_pass += 1
        count += 1
    result = {
        "kind":"finite mathematical enumeration; no new participant data",
        "all_checks_passed": True,
        "log_matrix_domain":[-1,0,1],
        "matrices_checked":count,
        "common_condition_orders":len(PERMUTATIONS),
        "all_common_order_half_grid_targets":len(targets),
        "independent_target_distance_comparisons":count*len(targets),
        "strict_tie_exceptions":strict_fail_closed_pass,
        "examples":counterexamples(),
    }
    (ROOT / "shared_clock_bounds_results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({key:value for key,value in result.items() if key != "examples"},indent=2))


if __name__ == "__main__":
    main()
