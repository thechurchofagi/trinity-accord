#!/usr/bin/env python3
"""Finite-model calculations for the CTD response-level identifiability note.

No optimizer, experimental-fit routine, or claim of a validated human protocol.
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr, ndtri, expit, logit

SQRT2PI = np.sqrt(2 * np.pi)

def normal_pdf(x):
    return np.exp(-.5 * np.asarray(x)**2) / SQRT2PI

def interval_response(s, sigma, halfwidth, lapse=0., center=0.):
    """p(yes) for a symmetric interval with Gaussian effective noise."""
    x = (np.asarray(s) - center) / sigma
    r = halfwidth / sigma
    p = ndtr(r - x) - ndtr(-r - x)
    return lapse / 2 + (1 - lapse) * p

def source_halfwidth(prior, sigma, stimulus_sd, posterior_criterion=.5):
    """The source BCI decision interval, with an explicit posterior criterion."""
    rhs = (logit(prior) - logit(posterior_criterion) +
           .5 * np.log1p((stimulus_sd / sigma)**2))
    squared = 2 * sigma**2 * (1 + (sigma / stimulus_sd)**2) * rhs
    return np.sqrt(np.maximum(0., squared))

def prior_for_halfwidth(halfwidth, sigma, stimulus_sd, posterior_criterion=.5):
    effective_log_odds = (halfwidth**2 / (2 * sigma**2 * (1 + (sigma / stimulus_sd)**2)) -
                          .5 * np.log1p((stimulus_sd / sigma)**2))
    return expit(effective_log_odds + logit(posterior_criterion))

def identify_two_points(p_zero, p_offset, offset, lapse=0.):
    """Unique nondegenerate (sigma, k) from calibrated center, lapse and two p's.

    These are population response probabilities, not noisy proportions to which
    exact inversion can automatically be applied.
    """
    if not (0 <= lapse < 1 and offset > 0):
        raise ValueError('Require 0 <= lapse < 1 and positive calibrated offset.')
    q0 = (p_zero - lapse / 2) / (1 - lapse)
    qs = (p_offset - lapse / 2) / (1 - lapse)
    if not (0 < qs < q0 < 1):
        raise ValueError('No nondegenerate finite symmetric Gaussian interval.')
    r = ndtri((1 + q0) / 2)
    def objective(u):
        return ndtr(r - u) - ndtr(-r - u) - qs
    high = max(1., r)
    while objective(high) > 0:
        high *= 2
    u = brentq(objective, 0, high, xtol=1e-13, rtol=1e-13)
    sigma = offset / u
    return sigma, r * sigma

def gaussian_rectangle(lo1, hi1, lo2, hi2, rho):
    """Deterministic 1D quadrature, avoiding stochastic MVN-CDF integration."""
    if not -1 <= rho <= 1:
        raise ValueError('Correlation must lie in [-1,1].')
    if rho == 0:
        return float((ndtr(hi1) - ndtr(lo1)) * (ndtr(hi2) - ndtr(lo2)))
    if rho == 1:
        return float(max(0., ndtr(min(hi1, hi2)) - ndtr(max(lo1, lo2))))
    if rho == -1:
        return gaussian_rectangle(lo1, hi1, -hi2, -lo2, 1.)
    sd = np.sqrt(1 - rho**2)
    def integrand(z):
        return normal_pdf(z) * (ndtr((hi2 - rho * z) / sd) - ndtr((lo2 - rho * z) / sd))
    value, _ = quad(integrand, lo1, hi1, epsabs=2e-13, epsrel=2e-12, limit=150)
    return float(value)

def joint_interval_response(s, variance1, variance2, halfwidth1, halfwidth2,
                            covariance, lapse1=0., lapse2=0.):
    """Joint yes probability for one shared internal draw, independent lapses.

    covariance equals sensory variance only under independent criterion noises.
    Passing general covariance also exposes the correlated-criterion alias.
    """
    sd1, sd2 = np.sqrt(variance1), np.sqrt(variance2)
    rho = covariance / (sd1 * sd2)
    joint = gaussian_rectangle((-halfwidth1 - s) / sd1, (halfwidth1 - s) / sd1,
                               (-halfwidth2 - s) / sd2, (halfwidth2 - s) / sd2, rho)
    q1 = float(interval_response(s, sd1, halfwidth1))
    q2 = float(interval_response(s, sd2, halfwidth2))
    return ((1 - lapse1) * (1 - lapse2) * joint +
            lapse1 * (1 - lapse2) * q2 / 2 +
            lapse2 * (1 - lapse1) * q1 / 2 + lapse1 * lapse2 / 4)

def bivariate_pdf(x, y, rho):
    return np.exp(-(x*x - 2*rho*x*y + y*y) / (2*(1-rho*rho))) / (2*np.pi*np.sqrt(1-rho*rho))

def centered_joint_derivative_rho(r1, r2, rho):
    return 2 * (bivariate_pdf(r1, r2, rho) - bivariate_pdf(r1, -r2, rho))

def identify_shared_variance(joint_probability, variance1, variance2,
                              halfwidth1, halfwidth2, lapse1=0., lapse2=0.):
    """Sharp one-joint-probability inverse under the stated paired assumptions."""
    if min(variance1, variance2, halfwidth1, halfwidth2) <= 0:
        raise ValueError('Use nondegenerate positive marginal parameters.')
    if max(lapse1, lapse2) >= 1 or min(lapse1, lapse2) < 0:
        raise ValueError('Lapses must be known and below one.')
    def probability(a):
        return joint_interval_response(0., variance1, variance2, halfwidth1, halfwidth2,
                                       a, lapse1, lapse2)
    upper = min(variance1, variance2)
    lowp, upp = probability(0.), probability(upper)
    if joint_probability < lowp - 1e-12 or joint_probability > upp + 1e-12:
        raise ValueError('Joint probability is outside this independent-criterion family.')
    if abs(joint_probability - lowp) < 1e-14:
        return 0.
    if abs(joint_probability - upp) < 1e-14:
        return upper
    return brentq(lambda a: probability(a) - joint_probability, 0., upper,
                  xtol=1e-12, rtol=1e-12)

def independent_jitter_bounds(effective_variances, lower_jitter, upper_jitter):
    """Sharp common sensory-variance interval for calibrated jitter bounds."""
    v = np.asarray(effective_variances)
    low = max(0., float(np.max(v - np.asarray(upper_jitter))))
    high = float(np.min(v - np.asarray(lower_jitter)))
    return low, high

def bounded_criterion_correlation_interval(variance1, variance2, absolute_rho, kappa):
    """Sharp sensory-variance interval from a central joint readout and |corr C|<=kappa.

    Returns None for incompatibility. The covariance inequality, rather than
    correlation itself, defines the limiting cases with zero criterion variance.
    """
    if min(variance1, variance2) <= 0 or not (0 <= absolute_rho <= 1 and 0 <= kappa <= 1):
        raise ValueError('Positive variances and r,kappa in [0,1] required.')
    # Normalize units to avoid unnecessary cancellation with millisecond-squared inputs.
    scale = max(variance1, variance2)
    v1, v2 = variance1 / scale, variance2 / scale
    R = absolute_rho * np.sqrt(v1 * v2)
    maximum = min(v1, v2)
    if kappa == 1:
        denominator = v1 + v2 - 2*R
        if abs(denominator) < 1e-14:
            return 0., maximum * scale
        high = min(maximum, (v1*v2-R*R)/denominator)
        return (0., max(0., high)*scale)
    A = 1-kappa*kappa
    B = kappa*kappa*(v1+v2)-2*R
    C = R*R-kappa*kappa*v1*v2
    discriminant = B*B-4*A*C
    if discriminant < -1e-13:
        return None
    root = np.sqrt(max(0., discriminant))
    low = max(0., (-B-root)/(2*A))
    high = min(maximum, (-B+root)/(2*A))
    if low > high + 1e-13:
        return None
    return min(low, high)*scale, high*scale
