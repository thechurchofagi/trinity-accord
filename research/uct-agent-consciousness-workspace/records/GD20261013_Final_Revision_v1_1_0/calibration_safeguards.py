"""Validated measurement-boundary helpers for the GD v1.1 revision.

This module does not certify Gaussianity, correct wiring, or physical safety.
Original numerical scripts are preserved separately for reproducibility.
No unresolved or invalid score is converted to zero cost.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import numpy as np
from scipy.stats import beta
from calibration_core import recover, score_interval

@dataclass(frozen=True)
class ScoreResult:
    status: Literal['ENCLOSURE', 'NOT_IDENTIFIED', 'INCONSISTENT_BOX']
    lower: float | None = None
    upper: float | None = None


def _positive_scalar(x: float, name: str) -> float:
    x = float(x)
    if not np.isfinite(x) or x <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return x


def validated_probability_box(bounds, columns: int = 4) -> np.ndarray:
    a = np.asarray(bounds, dtype=float)
    if a.shape != (columns, 2) or not np.isfinite(a).all():
        raise ValueError(f'Expected a finite ({columns}, 2) probability box')
    if np.any(a < 0) or np.any(a > 1) or np.any(a[:, 0] > a[:, 1]):
        raise ValueError('Probability endpoints must be ordered and in [0,1]')
    return a


def trace_enclosure(bounds, c: float = 1.) -> ScoreResult:
    """Conservative range, conditional on simultaneous probability coverage.

    Passing this check does NOT establish the centered/isotropic Gaussian model.
    In particular it does not rule out the exact misspecification twins.
    """
    c = _positive_scalar(c, 'reference energy')
    a = validated_probability_box(bounds)
    lo, hi = a.T
    # Any valid model obeys q0 >= qc, q0 >= q1 >= q2.
    # Strict contradictions can be rejected; overlapping boxes are not proofs.
    if lo[1] > hi[0] or lo[2] > hi[0] or lo[3] > hi[2]:
        return ScoreResult('INCONSISTENT_BOX')
    if np.min(lo) <= 0 or lo[0] <= hi[1]:
        return ScoreResult('NOT_IDENTIFIED')
    lower, upper = score_interval(a, c)
    if not np.isfinite(lower + upper):
        return ScoreResult('INCONSISTENT_BOX')
    return ScoreResult('ENCLOSURE', float(lower), float(upper))


def clopper_pearson_box(counts, n: int, alpha: float = .05,
                        family_columns: int = 4) -> np.ndarray:
    """Bonferroni allocation; requires independent Bernoulli trials per column.

    Dependence BETWEEN columns is allowed. The error allocation must include all
    candidates inspected in one decision family, not just the chosen candidate.
    """
    x = np.asarray(counts)
    if x.ndim != 1 or not np.isfinite(x).all() or np.any(x != np.rint(x)):
        raise ValueError('Counts must be a finite one-dimensional integer array')
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n <= 0:
        raise ValueError('n must be a positive integer')
    if not 0 < alpha < 1 or family_columns < len(x):
        raise ValueError('Invalid confidence allocation')
    k = x.astype(np.int64)
    if np.any(k < 0) or np.any(k > n):
        raise ValueError('Counts must lie between 0 and n')
    tail = alpha / (2 * family_columns)
    low = np.zeros(len(k)); high = np.ones(len(k))
    j = k > 0; low[j] = beta.ppf(tail, k[j], n-k[j]+1)
    j = k < n; high[j] = beta.ppf(1-tail, k[j]+1, n-k[j])
    return np.column_stack((low, high))


def validate_spd(matrix, name: str = 'metric') -> np.ndarray:
    a = np.asarray(matrix, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not np.isfinite(a).all():
        raise ValueError(f'{name}: finite square matrix required')
    if not np.allclose(a, a.T, atol=1e-12, rtol=1e-12):
        raise ValueError(f'{name}: symmetric matrix required')
    if np.linalg.eigvalsh(a).min() <= 0:
        raise ValueError(f'{name}: positive definite matrix required')
    return a


def standard_reference_vectors(n: int) -> list[np.ndarray]:
    """n diagonal and n(n-1)/2 polarization vectors in fixed physical units."""
    if not isinstance(n, int) or n < 1:
        raise ValueError('n must be a positive integer')
    e = np.eye(n)
    return [e[i].copy() for i in range(n)] + [e[i]+e[j] for i in range(n) for j in range(i+1,n)]


def reconstruct_metric(q0: float, qrefs, n: int) -> np.ndarray:
    """Exact-population polarization reconstruction; no noise guarantee claimed."""
    if not np.isfinite(q0) or not 0 < q0 <= 1:
        raise ValueError('q0 must be in (0,1]')
    q = np.asarray(qrefs, dtype=float)
    if q.shape != (n*(n+1)//2,) or not np.isfinite(q).all() or np.any(q<=0) or np.any(q>=q0):
        raise ValueError('Invalid reference probabilities')
    ell = np.log(q0/q); g = np.diag(ell[:n]); index = n
    for i in range(n):
        for j in range(i+1,n):
            g[i,j] = g[j,i] = .5*(ell[index]-ell[i]-ell[j]); index += 1
    return validate_spd(g)


def metric_equalizer(metric) -> np.ndarray:
    """Returns proposed H=G^-1/2. H must be implemented/verified physically."""
    g = validate_spd(metric)
    vals, vec = np.linalg.eigh(g)
    return (vec * (1/np.sqrt(vals))) @ vec.T


def metric_bound(weighted_trace: float, effective_metric) -> tuple[float,float]:
    """For J=tr(K Sigma), Sigma PSD, eigenvalue bounds yield trace enclosure."""
    k = validate_spd(effective_metric, 'effective metric')
    if not np.isfinite(weighted_trace) or weighted_trace < 0:
        raise ValueError('weighted trace must be nonnegative')
    eig = np.linalg.eigvalsh(k)
    return float(weighted_trace/eig[-1]), float(weighted_trace/eig[0])
