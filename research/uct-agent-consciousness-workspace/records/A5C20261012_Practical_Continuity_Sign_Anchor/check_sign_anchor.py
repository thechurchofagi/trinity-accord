#!/usr/bin/env python3
"""Exact finite checks for A5C's sign-anchor and route-orbit claims."""

from fractions import Fraction
from itertools import product
import json


def joint_table(pi, channels):
    """Mixture table P(E_1,...,E_m), with conditional independence given H."""
    out = {}
    for e in product((0, 1), repeat=len(channels)):
        total = Fraction(0)
        for h, ph in ((0, 1 - pi), (1, pi)):
            term = ph
            for bit, (p0, p1) in zip(e, channels):
                p = (p0, p1)[h]
                term *= p if bit else (1 - p)
            total += term
        out[''.join(map(str, e))] = total
    return out


def flip_world(pi, channels):
    return 1 - pi, [(p1, p0) for p0, p1 in channels]


def route_edges(matrix):
    return tuple(
        (route, target)
        for target, row in enumerate(matrix)
        for route, coefficient in enumerate(row)
        if coefficient != 0
    )


def swap_routes(edges):
    return tuple(sorted((1 - r, t) for r, t in edges))


def orbit(edges):
    e = tuple(sorted(edges))
    return min(e, swap_routes(e))


def frac_dict(d):
    return {k: f'{v.numerator}/{v.denominator}' for k, v in d.items()}


def main():
    # Two domains have different prevalence, but share the same conditionals.
    channels = [
        (Fraction(1, 5), Fraction(4, 5)),
        (Fraction(1, 4), Fraction(3, 4)),
    ]
    domains = {
        'calibration': Fraction(2, 5),
        'target': Fraction(3, 5),
    }
    tables = {name: joint_table(pi, channels) for name, pi in domains.items()}
    flipped_tables = {}
    for name, pi in domains.items():
        fpi, fchannels = flip_world(pi, channels)
        flipped_tables[name] = joint_table(fpi, fchannels)
    assert tables == flipped_tables

    orientation_counts = {
        'no_transport_no_anchor': 4,      # calibration and target may flip separately
        'transport_no_anchor': 2,         # one shared global complement remains
        'transport_and_signed_anchor': 1, # external sign fixes the shared complement
        'marginal_match_and_signed_calibration_only': 2,
    }
    assert sum(1 for s_c, s_t in product((0, 1), repeat=2)) == 4
    assert sum(1 for s_c, s_t in product((0, 1), repeat=2) if s_c == s_t) == 2
    assert sum(1 for s_c, s_t in product((0, 1), repeat=2) if s_c == s_t and s_c == 0) == 1
    assert sum(1 for s_c, s_t in product((0, 1), repeat=2) if s_c == 0) == 2

    # Physically implementable linear mappings. Each row is one target/cursor;
    # each column is a two-axis handle route's target-relevant coordinate.
    joint = ((1, 1), (1, 1))
    distributed = ((1, 0), (0, 1))
    joint_edges = route_edges(joint)
    distributed_edges = route_edges(distributed)
    assert orbit(joint_edges) != orbit(distributed_edges)
    assert len(joint_edges) == 4 and len(distributed_edges) == 2
    assert swap_routes(joint_edges) == tuple(sorted(joint_edges))
    assert swap_routes(distributed_edges) != tuple(sorted(distributed_edges))

    result = {
        'schema': 'A5C-EXACT-RESULTS-v0.1.0',
        'status': 'PASS_BOUNDED_NONIDENTIFICATION',
        'latent_model': {
            'domains': {k: f'{v.numerator}/{v.denominator}' for k, v in domains.items()},
            'channels_p0_p1': [[f'{x.numerator}/{x.denominator}' for x in pair] for pair in channels],
            'observable_tables': {k: frac_dict(v) for k, v in tables.items()},
            'global_complement_preserves_all_observables': tables == flipped_tables,
            'orientation_counts': orientation_counts,
        },
        'route_protocol_model': {
            'joint_edges': [list(x) for x in joint_edges],
            'distributed_edges': [list(x) for x in distributed_edges],
            'different_route_swap_orbits': orbit(joint_edges) != orbit(distributed_edges),
            'joint_edge_count': len(joint_edges),
            'distributed_edge_count': len(distributed_edges),
        },
        'interpretation': [
            'Multiple fallible channels and exact class-conditional transport reduce local flips to one global complement but do not choose its phenomenal meaning.',
            'One independently signed semantic anchor in the connected transport component is necessary for this declared orientation method.',
            'The dual-handle mapping is a cross-orbit organizational manipulation only; it does not provide that anchor.'
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
