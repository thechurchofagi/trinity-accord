#!/usr/bin/env python3
"""Exact four-setting checks, standard library only; not phenomenal measurements.

This is a new v1.1 checker, not the historical generation code. The original
rc4 verifier is preserved separately as check_rc4.py. Mathematical finite tests
cannot establish physical realization, A1, A5, or biological theory recovery.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
STATES = list(product((0, 1), repeat=3))
PAIRS = list(product((0, 1), repeat=2))
SETTINGS = PAIRS
CLAMPS = list(product((None, 0, 1), repeat=3))
checks: list[dict] = []

def check(name: str, condition: bool, **details) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'PASS', **details})

def step(x: tuple, u: int, alpha: int, beta: int) -> tuple:
    s, a, b = x
    return s ^ u, s ^ (alpha & b), s ^ (beta & a)

def clamp(x: tuple, act: tuple) -> tuple:
    return tuple(v if c is None else c for v, c in zip(x, act))

def pair_step(z: tuple, s: int, alpha: int, beta: int) -> tuple:
    return s ^ (alpha & z[1]), s ^ (beta & z[0])

def lin_step(z: tuple, alpha: int, beta: int) -> tuple:
    return alpha & z[1], beta & z[0]

def swap(x: tuple) -> tuple:
    return x[0], x[2], x[1]

rows = []
for (alpha, beta), u, x in product(SETTINGS, (0, 1), STATES):
    out = step(x, u, alpha, beta)
    rows.append(dict(alpha=alpha, beta=beta, u=u, s=x[0], a=x[1], b=x[2],
                     s_next=out[0], a_next=out[1], b_next=out[2]))
check('complete_four_setting_transition_table', len(rows) == 64, cases=len(rows))

closure = 0
for (alpha, beta), u, x, z in product(SETTINGS, (0, 1), STATES, STATES):
    if x[0] == z[0]:
        check_value = step(x, u, alpha, beta)[0] == step(z, u, alpha, beta)[0]
        if not check_value: raise AssertionError('closure')
        closure += 1
check('fixed_s_projection_closure', closure == 256, cases=closure)

commutation = 0
for (alpha, beta), u, x, act in product(SETTINGS, (0, 1), STATES, CLAMPS):
    s_reset = x[0] if act[0] is None else act[0]
    if step(clamp(x, act), u, alpha, beta)[0] != (s_reset ^ u):
        raise AssertionError('intervention commutation')
    commutation += 1
check('all_projected_reset_interventions', commutation == 1728, cases=commutation)

images = {}
for alpha, beta in SETTINGS:
    sizes = [len({step(x, u, alpha, beta) for x in STATES}) for u in (0, 1)]
    expected = 2 ** (1 + alpha + beta)
    check(f'whole_image_size_{alpha}{beta}', sizes == [expected, expected], sizes=sizes)
    images[f'{alpha}{beta}'] = expected

# Dependence witnesses use interventions at the fixed physical ports.
for alpha, beta in SETTINGS:
    for s in (0, 1):
        b_to_a = any(pair_step((a, 0), s, alpha, beta)[0] != pair_step((a, 1), s, alpha, beta)[0] for a in (0, 1))
        a_to_b = any(pair_step((0, b), s, alpha, beta)[1] != pair_step((1, b), s, alpha, beta)[1] for b in (0, 1))
        if (b_to_a, a_to_b) != (bool(alpha), bool(beta)):
            raise AssertionError('port dependence')
check('directed_dependencies_and_split_nonproduct', True,
      nonproduct_settings=['01', '10', '11'], cycle_settings=['11'])

retention_rows = []
trajectories_checked = 0
for alpha, beta in SETTINGS:
    for n in range(1, 9):
        expected = 4 if alpha == beta == 1 else (2 if alpha != beta and n == 1 else 1)
        linear = []
        for z in PAIRS:
            d = z
            for _ in range(n): d = lin_step(d, alpha, beta)
            linear.append(d)
        rank = {1: 0, 2: 1, 4: 2}[len(set(linear))]
        for boundary in product((0, 1), repeat=n):
            end = []
            for z in PAIRS:
                a = z
                for s in boundary: a = pair_step(a, s, alpha, beta)
                end.append(a)
            if len(set(end)) != expected or expected != 2 ** rank:
                raise AssertionError('retention class count')
            for z, w in product(range(4), repeat=2):
                delta = tuple(a ^ b for a, b in zip(PAIRS[z], PAIRS[w]))
                for _ in range(n): delta = lin_step(delta, alpha, beta)
                if delta != tuple(a ^ b for a, b in zip(end[z], end[w])):
                    raise AssertionError('difference propagation')
            trajectories_checked += 4
        retention_rows.append(dict(alpha=alpha, beta=beta, horizon=n, rank=rank,
                                   retained_classes=expected, boundary_strings=2**n))
check('all_boundary_strings_through_horizon_eight', True,
      initial_trajectories=trajectories_checked,
      scope='No resets after the initial perturbation; same conditioned boundary sequence.')
check('rank_nullity_retention_identity', all(r['retained_classes'] == 2**r['rank'] for r in retention_rows))
check('one_link_square_zero_two_link_square_identity',
      all(lin_step(lin_step(z, 1, 0), 1, 0) == (0, 0)
          and lin_step(lin_step(z, 0, 1), 0, 1) == (0, 0)
          and lin_step(lin_step(z, 1, 1), 1, 1) == z for z in PAIRS))

# The port-swapping isomorphism must also transport the marked current state.
check('one_link_settings_covary_under_declared_port_swap',
      all(swap(step(x, u, 1, 0)) == step(swap(x), u, 0, 1)
          for u, x in product((0, 1), STATES)),
      scope='Only when a/b swapping is admissible, with the pointed state transported.')
check('port_preserving_one_link_dependence_is_distinct',
      pair_step((0, 1), 0, 1, 0) != pair_step((0, 1), 0, 0, 1))

output_cases = 0
for n in range(1, 7):
    for us, x in product(product((0, 1), repeat=n), STATES):
        expected_s = x[0]
        for u in us: expected_s ^= u
        for alpha, beta in SETTINGS:
            state = x
            for u in us: state = step(state, u, alpha, beta)
            if state[0] != expected_s: raise AssertionError('output invariance')
            output_cases += 1
check('all_input_strings_through_horizon_six', True, cases=output_cases,
      scope='Analytic induction in manuscript proves all finite lengths.')

# Complete identity can coexist with a lossy physical view or a lossy target.
D = {0: 0, 1: 1}
Phi = {0: 0, 1: 1}
view_lossy = {0: 0, 1: 0}
target_faithful = {0: 0, 1: 1}
target_lossy = {0: 0, 1: 0}
check('failed_finite_sufficiency_does_not_isolate_A5',
      D == Phi and view_lossy[0] == view_lossy[1] and target_faithful[0] != target_faithful[1])
check('failed_finite_reflection_does_not_isolate_A5',
      D == Phi and D[0] != D[1] and target_lossy[0] == target_lossy[1])
check('finite_prediction_can_hold_without_using_A5',
      all(target_faithful[x] == D[x] for x in (0, 1)),
      scope='The numerical equality alone does not select an interpretation of D.')

for filename, table in [('four_setting_transitions.csv', rows), ('retention_partitions.csv', retention_rows)]:
    with (ROOT / filename).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(table[0])); w.writeheader(); w.writerows(table)
result = {'state': 'PASS', 'checks': checks, 'check_count': len(checks),
          'whole_image_sizes': images,
          'empirical_validation': False,
          'original_rc4_script': 'check_rc4.py',
          'scope': 'Exact finite models and countermodels only; no biological or phenomenal data.'}
(ROOT / 'transformation_results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'state': 'PASS', 'checks': len(checks), 'transitions': len(rows),
                  'closure': closure, 'clamps': commutation, 'retention_trajectories': trajectories_checked}))
