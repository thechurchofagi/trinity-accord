#!/usr/bin/env python3
"""Exact rational checks for A4K common-scale interval prediction regions."""

from fractions import Fraction as F
import hashlib
import json


def q(x):
    return F(x)


def prod_interval(a, b):
    vals = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return min(vals), max(vals)


def ratio_positive(num, den):
    assert 0 < num[0] <= num[1] and 0 < den[0] <= den[1]
    return num[0] / den[1], num[1] / den[0]


def constrain_le(bounds, a, b):
    """Intersect bounds with a*x <= b, returning None when infeasible."""
    lo, hi = bounds
    if a > 0:
        hi = min(hi, b / a)
    elif a < 0:
        lo = max(lo, b / a)
    elif b < 0:
        return None
    return None if lo > hi else (lo, hi)


def constrain_ge(bounds, a, b):
    return constrain_le(bounds, -a, -b)


def scale_feasible(scale, source_intervals, target_intervals):
    """Existence of s in scale with target_i intersecting s*source_i."""
    bounds = scale
    for (dl, du), (ol, ou) in zip(source_intervals, target_intervals):
        # ol <= s*du and s*dl <= ou
        bounds = constrain_ge(bounds, du, ol)
        if bounds is None:
            return None
        bounds = constrain_le(bounds, dl, ou)
        if bounds is None:
            return None
    return bounds


def candidate_intersection(m_a, d_a, m_b, d_b):
    """Exact intersection test for {m*d}: common positive m per candidate."""
    lam = ratio_positive(m_b, m_a)  # d_a = lambda*d_b
    return scale_feasible(lam, d_b, d_a)


def hull(m, d):
    return [prod_interval(m, x) for x in d]


def rectangles_disjoint(a, b):
    return any(x[1] < y[0] or y[1] < x[0] for x, y in zip(a, b))


def enc_fraction(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def enc(x):
    if isinstance(x, F):
        return enc_fraction(x)
    if isinstance(x, tuple):
        return [enc(v) for v in x]
    if isinstance(x, list):
        return [enc(v) for v in x]
    if isinstance(x, dict):
        return {k: enc(v) for k, v in x.items()}
    return x


alpha = (q(4) / 5, q(6) / 5)
gain_relation = (q(9) / 10, q(11) / 10)
gain_fit = (q(1), q(5) / 4)
m_relation = prod_interval(alpha, gain_relation)
m_fit = prod_interval(alpha, gain_fit)

separating_relation = [(q(-6) / 5, q(-4) / 5), (q(-1) / 10, q(1) / 10)]
separating_fit = [(q(-1) / 10, q(1) / 10), (q(-11) / 10, q(-7) / 10)]

overlap_relation = [(q(-6) / 5, q(-4) / 5), (q(-11) / 10, q(-7) / 10)]
overlap_fit = [(q(-1), q(-3) / 4), (q(-1), q(-3) / 4)]

obs_relation = [(q(-1), q(-4) / 5), (q(-1) / 20, q(1) / 20)]
obs_fit = [(q(-1) / 20, q(1) / 20), (q(-1), q(-4) / 5)]

sep_hull_r = hull(m_relation, separating_relation)
sep_hull_f = hull(m_fit, separating_fit)
ov_hull_r = hull(m_relation, overlap_relation)
ov_hull_f = hull(m_fit, overlap_fit)

results = {
    "schema": "a4k-common-scale-interval-regions/1",
    "scope": "Exact rational interval propagation for two disabled pure bridge candidates; no participant or phenomenal assignment.",
    "orientation_interval": alpha,
    "candidate_gain_intervals": {"relation": gain_relation, "fit": gain_fit},
    "common_scale_intervals": {"relation": m_relation, "fit": m_fit},
    "separating_example": {
        "relation_input_effects": separating_relation,
        "fit_input_effects": separating_fit,
        "relation_outer_hull": sep_hull_r,
        "fit_outer_hull": sep_hull_f,
        "outer_hulls_disjoint": rectangles_disjoint(sep_hull_r, sep_hull_f),
        "exact_common_scale_intersection_feasible_lambda": candidate_intersection(
            m_relation, separating_relation, m_fit, separating_fit
        ),
        "relation_observation_compatible_scale": scale_feasible(m_relation, separating_relation, obs_relation),
        "relation_observation_fit_compatible_scale": scale_feasible(m_fit, separating_fit, obs_relation),
        "fit_observation_relation_compatible_scale": scale_feasible(m_relation, separating_relation, obs_fit),
        "fit_observation_compatible_scale": scale_feasible(m_fit, separating_fit, obs_fit),
    },
    "overlap_example": {
        "relation_input_effects": overlap_relation,
        "fit_input_effects": overlap_fit,
        "relation_outer_hull": ov_hull_r,
        "fit_outer_hull": ov_hull_f,
        "outer_hulls_disjoint": rectangles_disjoint(ov_hull_r, ov_hull_f),
        "exact_common_scale_intersection_feasible_lambda": candidate_intersection(
            m_relation, overlap_relation, m_fit, overlap_fit
        ),
    },
    "orientation_failure": {
        "zero_in_orientation_interval": True,
        "consequence": "Both candidate regions contain the zero vector when the orientation interval contains zero; global separation is impossible and strict sign transfer is not warranted.",
    },
    "phenomenal_assignments": 0,
}

assert results["separating_example"]["outer_hulls_disjoint"] is True
assert results["separating_example"]["exact_common_scale_intersection_feasible_lambda"] is None
assert results["separating_example"]["relation_observation_compatible_scale"] is not None
assert results["separating_example"]["relation_observation_fit_compatible_scale"] is None
assert results["separating_example"]["fit_observation_relation_compatible_scale"] is None
assert results["separating_example"]["fit_observation_compatible_scale"] is not None
assert results["overlap_example"]["outer_hulls_disjoint"] is False
assert results["overlap_example"]["exact_common_scale_intersection_feasible_lambda"] is not None

payload = json.dumps(enc(results), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
results["canonical_payload_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
print(json.dumps(enc(results), ensure_ascii=False, indent=2, sort_keys=True))
