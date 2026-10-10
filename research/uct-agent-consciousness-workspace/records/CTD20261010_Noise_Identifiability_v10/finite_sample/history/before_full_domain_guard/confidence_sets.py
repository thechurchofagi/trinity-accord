#!/usr/bin/env python3
"""Finite-sample confidence sets for the centered paired-interval model.

Statistical construction: an equal-tailed Clopper--Pearson binomial interval,
followed by the exact model-specific set projection proved in PROOF.md.
This is not a new general confidence-interval method.  It does not calibrate
the model's assumptions or infer an anatomical or experiential variable.

All supplied variances, halfwidths, lapses, and the criterion-correlation bound
are known parameters unless an explicitly named calibration-union function is
used. Trials must be independent, identically distributed paired observations
from one same internal Gaussian sensory draw. The two criterion noises are
jointly Gaussian and independent of that draw. Lapse indicators and fair
guesses are independent across reports and from the Gaussian variables.

The proofs concern exact real-valued probabilities. This module evaluates
special functions and monotone inverses in double precision; it is not an
interval-arithmetic certificate. No interpolation grid is used for inversion
or for the continuous nuisance covariance. In particular, a finite list of
calibrations is never represented as an envelope of a continuous domain.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from math import isfinite, sqrt
from numbers import Integral
from typing import Iterable

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import betaincinv, erf, ndtr, owens_t


VERSION = "1.0.0"
RHO_ROOT_XTOL = 5e-14
RHO_ROOT_RTOL = 1e-14


@dataclass(frozen=True)
class PairCalibration:
    v_o: float
    v_s: float
    k_o: float
    k_s: float
    lapse_o: float = 0.0
    lapse_s: float = 0.0
    kappa: float = 0.0

    def __post_init__(self):
        vals = asdict(self)
        if not all(isfinite(float(x)) for x in vals.values()):
            raise ValueError("All calibration parameters must be finite.")
        if min(self.v_o, self.v_s) <= 0:
            raise ValueError("Effective marginal variances must be positive.")
        if min(self.k_o, self.k_s) < 0:
            raise ValueError("Finite halfwidths must be nonnegative.")
        if not all(0 <= x <= 1 for x in
                   (self.lapse_o, self.lapse_s, self.kappa)):
            raise ValueError("Lapses and kappa must lie in [0,1].")

    @property
    def a_domain(self) -> tuple[float, float]:
        return 0.0, float(min(self.v_o, self.v_s))

    @property
    def degenerate_readout(self) -> bool:
        return (self.k_o == 0 or self.k_s == 0 or
                self.lapse_o == 1 or self.lapse_s == 1)

    @property
    def marginal_key(self) -> tuple[float, float, float, float]:
        # Kappa does not enter the probability-to-|rho| inverse.
        return (float(self.k_o / sqrt(self.v_o)),
                float(self.k_s / sqrt(self.v_s)),
                float(self.lapse_o), float(self.lapse_s))


@dataclass(frozen=True)
class ProjectionResult:
    a_interval: tuple[float, float] | None
    p_interval: tuple[float, float]
    model_p_range: tuple[float, float]
    rho_interval: tuple[float, float] | None
    status: str
    reason: str

    @property
    def empty(self) -> bool:
        return self.a_interval is None

    @property
    def width(self) -> float:
        return 0.0 if self.empty else self.a_interval[1] - self.a_interval[0]

    def contains(self, a: float, atol: float = 0.0) -> bool:
        if atol < 0:
            raise ValueError("Membership tolerance must be nonnegative.")
        return (not self.empty and self.a_interval[0] - atol <= a <=
                self.a_interval[1] + atol)

    def to_dict(self) -> dict:
        return {**asdict(self), "empty": self.empty, "width": self.width}


@dataclass(frozen=True)
class CalibrationUnionResult:
    intervals: tuple[tuple[float, float], ...]
    p_interval: tuple[float, float]
    alpha: float
    gamma: float
    coverage_lower_bound: float
    calibration_domain: str
    qualification: str

    @property
    def empty(self) -> bool:
        return not self.intervals

    def contains(self, a: float, atol: float = 0.0) -> bool:
        if atol < 0:
            raise ValueError("Membership tolerance must be nonnegative.")
        return any(lo - atol <= a <= hi + atol for lo, hi in self.intervals)

    def to_dict(self) -> dict:
        return {**asdict(self), "empty": self.empty}


def _check_probability_interval(lower: float, upper: float):
    if not (isfinite(lower) and isfinite(upper) and 0 <= lower <= upper <= 1):
        raise ValueError("Require 0 <= probability lower <= upper <= 1.")


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Equal-tailed closed CP interval; n=0 is defined to return [0,1]."""
    if (isinstance(k, bool) or isinstance(n, bool) or
            not isinstance(k, Integral) or not isinstance(n, Integral) or
            n < 0 or not 0 <= k <= n):
        raise ValueError("Require integer counts 0 <= k <= n.")
    if not 0 < alpha < 1:
        raise ValueError("Require 0 < alpha < 1.")
    if n == 0:
        return 0.0, 1.0
    lower = 0.0 if k == 0 else float(betaincinv(k, n-k+1, alpha/2))
    upper = 1.0 if k == n else float(betaincinv(k+1, n-k, 1-alpha/2))
    return lower, upper


def centered_rectangle_probability(h_o: float, h_s: float, rho: float) -> float:
    """P(|U_o|<=h_o, |U_s|<=h_s); handles the two singular correlations.

    The positive-radius Owen-T identity is used away from tiny rectangles.
    A direct deterministic 1D integral avoids subtracting numbers near one
    for tiny radii. rho may be signed: the centered rectangle is even.
    """
    if (not all(isfinite(x) for x in (h_o, h_s, rho)) or
            min(h_o, h_s) < 0 or not -1 <= rho <= 1):
        raise ValueError("Finite nonnegative radii and rho in [-1,1] required.")
    h1, h2 = sorted((float(h_o), float(h_s)))
    if h1 == 0:
        return 0.0
    r = abs(float(rho))
    q1, q2 = float(erf(h1 / sqrt(2))), float(erf(h2 / sqrt(2)))
    if r == 0:
        return q1*q2
    if r == 1:
        return q1
    sd = sqrt((1-r)*(1+r))
    if h1 >= 0.05:
        terms = (owens_t(h1, (h2/h1-r)/sd) +
                 owens_t(h2, (h1/h2-r)/sd) +
                 owens_t(h1, (h2/h1+r)/sd) +
                 owens_t(h2, (h1/h2+r)/sd))
        value = float(1 - 2*terms)
    else:
        def integrand(z):
            inside = ndtr((h2-r*z)/sd) - ndtr((-h2-r*z)/sd)
            return np.exp(-z*z/2) / sqrt(2*np.pi) * inside
        value, _ = quad(integrand, -h1, h1, epsabs=2e-14,
                        epsrel=2e-12, limit=200)
    # The analytic endpoints are also exact probabilistic bounds; this only
    # removes floating-point excursions of the special-function evaluation.
    return float(np.clip(value, q1*q2, q1))


def _p11_at_rho(r: float, h1: float, h2: float, l1: float, l2: float) -> float:
    q1, q2 = float(erf(h1 / sqrt(2))), float(erf(h2 / sqrt(2)))
    joint = centered_rectangle_probability(h1, h2, r)
    return float((1-l1)*(1-l2)*joint + l1*(1-l2)*q2/2 +
                 l2*(1-l1)*q1/2 + l1*l2/4)


def p11_from_abs_rho(r: float, calibration: PairCalibration) -> float:
    """Observed joint probability, including independent fair-guess lapses."""
    if not isfinite(r) or not 0 <= r <= 1:
        raise ValueError("Absolute total Gaussian correlation must be in [0,1].")
    return _p11_at_rho(float(r), *calibration.marginal_key)


def paired_yes_probability(a: float, c: float,
                           calibration: PairCalibration) -> float:
    """P11 for a physical Gaussian decomposition with criterion covariance c.

    Validates a>=0 and criterion covariance PSD, but deliberately does not
    enforce calibration.kappa. This permits clearly labeled sensitivity
    checks with a wrong assumed kappa. Set c=0 for independent criteria.
    """
    m = min(calibration.v_o, calibration.v_s)
    if not (isfinite(a) and isfinite(c) and 0 <= a <= m):
        raise ValueError("Require finite a in [0,min(v_o,v_s)] and finite c.")
    criterion_limit = sqrt((calibration.v_o-a)*(calibration.v_s-a))
    if abs(c) > np.nextafter(criterion_limit, np.inf):
        raise ValueError("Criterion covariance matrix is not positive semidefinite.")
    rho = (a+c) / sqrt(calibration.v_o*calibration.v_s)
    return p11_from_abs_rho(float(np.clip(abs(rho), 0, 1)), calibration)


def attainable_abs_rho_max(calibration: PairCalibration) -> float:
    """Analytic global maximum of |a+c|/sqrt(v_o*v_s) under the kappa bound."""
    m = min(calibration.v_o, calibration.v_s) / max(calibration.v_o, calibration.v_s)
    kap = calibration.kappa
    if m == 1 or kap == 1:
        return 1.0
    root_m = sqrt(m)
    if kap == 0:
        return root_m
    threshold = 2*root_m/(1+m)
    if kap >= threshold:
        return float(kap)
    # This rationalized version avoids subtracting nearly equal numbers.
    s = sqrt((1-kap)*(1+kap))
    value = (2*m + (1-m)*kap*kap/(1+s))/(2*root_m)
    return float(min(1.0, value))


def attainable_probability_range(calibration: PairCalibration) -> tuple[float, float]:
    return (p11_from_abs_rho(0.0, calibration),
            p11_from_abs_rho(attainable_abs_rho_max(calibration), calibration))


@lru_cache(maxsize=100_000)
def _inverse_p11(p: float, h1: float, h2: float, l1: float, l2: float) -> float:
    # Cache excludes kappa and dimensional variance scale on purpose.
    p0, p1 = _p11_at_rho(0.0, h1, h2, l1, l2), _p11_at_rho(1.0, h1, h2, l1, l2)
    if p <= p0:
        return 0.0
    if p >= p1:
        return 1.0
    return float(brentq(lambda r: _p11_at_rho(r, h1, h2, l1, l2)-p,
                        0.0, 1.0, xtol=RHO_ROOT_XTOL, rtol=RHO_ROOT_RTOL))


def _sharp_point_interval(r: float, calibration: PairCalibration
                          ) -> tuple[float, float] | None:
    """Sharp a-set at one absolute correlation, including both covariance signs."""
    scale = max(calibration.v_o, calibration.v_s)
    m = min(calibration.v_o, calibration.v_s) / scale
    kap = calibration.kappa
    R = r*sqrt(m)
    if m == 1:
        if kap == 1:
            return 0.0, scale*(1+r)/2
        return (scale*max(0.0, (r-kap)/(1-kap)),
                scale*min(1.0, (r+kap)/(1+kap)))
    if kap == 0:
        if R > m + 8*np.finfo(float).eps:
            return None
        value = scale*min(R, m)
        return value, value
    if kap == 1:
        high = (m-R*R)/(1+m-2*R)
        return 0.0, scale*max(0.0, min(m, high))
    # Stable quadratic roots in normalized units, evaluated in extended
    # precision to reduce cancellation near singular correlation bounds.
    R, m_ld, kap = map(np.longdouble, (R, m, kap))
    A = (1-kap)*(1+kap)
    B = kap*kap*(1+m_ld)-2*R
    C = R*R-kap*kap*m_ld
    D = kap*kap*((1+m_ld-2*R)**2-A*(1-m_ld)**2)
    tolerance = np.longdouble(64*np.finfo(float).eps)
    if D < -tolerance:
        return None
    root = np.sqrt(max(np.longdouble(0), D))
    q = -(B + (root if B >= 0 else -root))/2
    if q == 0:
        roots = (-B/(2*A), -B/(2*A))
    else:
        roots = tuple(sorted((q/A, C/q)))
    lower, upper = max(np.longdouble(0), roots[0]), min(m_ld, roots[1])
    if lower > upper + tolerance:
        return None
    return float(min(lower, upper)*scale), float(upper*scale)


def rho_interval_to_a_interval(r_lower: float, r_upper: float,
                               calibration: PairCalibration
                               ) -> tuple[float, float] | None:
    """Exact analytic union of sharp a-sets over a closed |rho| interval.

    This also handles unequal marginal variances. It does not use a grid of
    nuisance covariances. See PROOF.md for the endpoint and convexity argument.
    """
    _check_probability_interval(r_lower, r_upper)
    r_upper = min(r_upper, attainable_abs_rho_max(calibration))
    if r_lower > r_upper:
        return None
    if calibration.v_o == calibration.v_s:
        v, kap = calibration.v_o, calibration.kappa
        lower = 0.0 if kap == 1 else v*max(0.0, (r_lower-kap)/(1-kap))
        return float(lower), float(v*min(1.0, (r_upper+kap)/(1+kap)))
    lower_set = _sharp_point_interval(r_lower, calibration)
    if lower_set is None:
        return None
    at_max_a = sqrt(min(calibration.v_o, calibration.v_s) /
                    max(calibration.v_o, calibration.v_s))
    maximizing_r = max(r_lower, min(at_max_a, r_upper))
    upper_set = _sharp_point_interval(maximizing_r, calibration)
    if upper_set is None:
        return None
    return lower_set[0], upper_set[1]


def project_probability_interval(lower: float, upper: float,
                                 calibration: PairCalibration) -> ProjectionResult:
    """Project a CLOSED probability interval; None is an empty confidence set.

    Crucially, an interval wholly outside the model range is not clipped to a
    single boundary parameter. Zero halfwidth or a unit lapse produces a
    constant readout: the result is then the full a-domain or the empty set.
    """
    _check_probability_interval(lower, upper)
    p_range = attainable_probability_range(calibration)
    if upper < p_range[0] or lower > p_range[1]:
        return ProjectionResult(None, (lower, upper), p_range, None, "empty",
                                "Probability interval and attainable model range are disjoint.")
    if calibration.degenerate_readout:
        return ProjectionResult(calibration.a_domain, (lower, upper), p_range,
                                (0.0, attainable_abs_rho_max(calibration)), "full_domain",
                                "The calibrated readout is constant in a and criterion covariance.")
    if p_range[0] == p_range[1]:
        return ProjectionResult(calibration.a_domain, (lower, upper), p_range,
                                (0.0, attainable_abs_rho_max(calibration)), "full_domain",
                                "Numerical probability range collapsed; conservative full domain, not an exact degeneracy assertion.")
    lo_p, hi_p = max(lower, p_range[0]), min(upper, p_range[1])
    r_max = attainable_abs_rho_max(calibration)
    r_lo = 0.0 if lo_p == p_range[0] else _inverse_p11(lo_p, *calibration.marginal_key)
    r_hi = r_max if hi_p == p_range[1] else _inverse_p11(hi_p, *calibration.marginal_key)
    r_lo, r_hi = max(0.0, min(r_max, r_lo)), max(0.0, min(r_max, r_hi))
    interval = rho_interval_to_a_interval(r_lo, r_hi, calibration)
    if interval is None:
        # Intersection with the global attainable range should make this
        # impossible in real arithmetic; do not silently report model rejection.
        raise ArithmeticError("Numerical projection failed inside the attainable range.")
    full = interval == calibration.a_domain
    return ProjectionResult(interval, (lower, upper), p_range, (r_lo, r_hi),
                            "full_domain" if full else "informative",
                            "Closed model projection with bounded criterion correlation and both covariance signs.")


def confidence_set(k: int, n: int, calibration: PairCalibration,
                   alpha: float = 0.05) -> ProjectionResult:
    """At least 1-alpha coverage under the complete known-calibration contract."""
    return project_probability_interval(*clopper_pearson(k, n, alpha), calibration)


def population_identified_set(p11: float,
                              calibration: PairCalibration) -> ProjectionResult:
    """The population sharp set, NOT a finite-sample confidence statement."""
    return project_probability_interval(p11, p11, calibration)


def _merge_intervals(intervals: Iterable[tuple[float, float]]
                     ) -> tuple[tuple[float, float], ...]:
    merged: list[list[float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    return tuple((lo, hi) for lo, hi in merged)


def _check_error_budget(alpha: float, gamma: float):
    if not (0 < alpha < 1 and 0 <= gamma < 1 and alpha+gamma < 1):
        raise ValueError("Require 0<alpha<1, 0<=gamma<1, and alpha+gamma<1.")


def finite_calibration_union(k: int, n: int,
                             calibrations: Iterable[PairCalibration],
                             alpha: float = 0.05, gamma: float = 0.05
                             ) -> CalibrationUnionResult:
    """Exact union over an EXPLICIT FINITE calibration set, not a box or grid.

    The 1-alpha-gamma statement requires an externally valid probability
    >=1-gamma that the TRUE full calibration belongs to this finite set.
    Supplying samples of a continuous calibration region does not satisfy that
    premise and must not be described as its confidence envelope.
    Independence between calibration and paired data is not required by the
    union-bound proof; each marginal coverage guarantee must still be valid.
    """
    _check_error_budget(alpha, gamma)
    p_interval = clopper_pearson(k, n, alpha)
    sets = [project_probability_interval(*p_interval, c) for c in calibrations]
    intervals = _merge_intervals(x.a_interval for x in sets if not x.empty)
    return CalibrationUnionResult(intervals, p_interval, alpha, gamma, 1-alpha-gamma,
                                  "explicit finite set only",
                                  "Coverage conditional on the full model and a valid 1-gamma calibration-set guarantee; no continuous-grid envelope is claimed.")


def kappa_calibration_interval(k: int, n: int, calibration: PairCalibration,
                               kappa_lower: float, kappa_upper: float,
                               alpha: float = 0.05, gamma: float = 0.05
                               ) -> CalibrationUnionResult:
    """Analytic continuous-calibration union when ONLY kappa is uncertain.

    With other parameters known, increasing kappa enlarges the feasible
    covariance set. Thus the union over [kappa_lower,kappa_upper] equals the
    projection at kappa_upper exactly. No nuisance-parameter grid is needed.
    """
    _check_error_budget(alpha, gamma)
    _check_probability_interval(kappa_lower, kappa_upper)
    result = confidence_set(k, n, replace(calibration, kappa=kappa_upper), alpha)
    intervals = () if result.empty else (result.a_interval,)
    return CalibrationUnionResult(intervals, result.p_interval, alpha, gamma,
                                  1-alpha-gamma, "continuous kappa interval, analytic upper endpoint",
                                  "Other calibration parameters must be known; interval must cover a valid criterion-correlation bound with probability at least 1-gamma.")


if __name__ == "__main__":
    import json
    calibration = PairCalibration(1.0, 1.0, 0.8, 1.3, 0.05, 0.05, 0.2)
    print(json.dumps(confidence_set(130, 256, calibration).to_dict(), indent=2))
