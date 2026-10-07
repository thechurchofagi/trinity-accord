#!/usr/bin/env python3
"""R163 deterministic checks for bounded simultaneous-coverage candidates.

The exact rare-spike calculation is the counterexample.  Monte Carlo blocks are
diagnostics only and are never treated as proofs of coverage.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta as beta_dist
from scipy.stats import binom, t


ALPHA = 0.05
M = 8
SEED = 16320261008
REPS = 20_000


def student_contains_zero_for_k(n: int, k: int, p: float) -> bool:
    """Whether the Bonferroni Student interval contains the true mean zero."""
    low_value = -p / (1.0 - p)
    high_value = 1.0
    mean = (k * high_value + (n - k) * low_value) / n
    if k == 0 or k == n:
        half_width = 0.0
    else:
        # Binary-sample sum of squares around the sample mean.
        ss = k * (high_value - mean) ** 2 + (n - k) * (low_value - mean) ** 2
        sample_sd = math.sqrt(ss / (n - 1))
        critical = float(t.ppf(1.0 - ALPHA / (2.0 * M), n - 1))
        half_width = critical * sample_sd / math.sqrt(n)
    return mean - half_width <= 0.0 <= mean + half_width


def exact_rare_spike(n: int, p: float = 0.05) -> dict:
    covered = [student_contains_zero_for_k(n, k, p) for k in range(n + 1)]
    marginal = sum(
        float(binom.pmf(k, n, p)) for k, does_cover in enumerate(covered) if does_cover
    )
    return {
        "n": n,
        "distribution": {"P(X=1)": p, "P(X=-1/19)": 1 - p, "E[X]": 0.0},
        "covered_success_counts": [k for k, does_cover in enumerate(covered) if does_cover],
        "marginal_coverage_exact": marginal,
        "simultaneous_coverage_exact_for_8_independent_components": marginal**M,
        "probability_no_spike": (1.0 - p) ** n,
    }


def hoeffding_half_width(n: int, m: int = M, alpha: float = ALPHA) -> float:
    # W_ij in [-1,1], hence range length 2.
    return math.sqrt(2.0 * math.log(2.0 * m / alpha) / n)


def simultaneous_student_coverage(x: np.ndarray, target: float) -> np.ndarray:
    n = x.shape[1]
    means = x.mean(axis=1)
    sds = x.std(axis=1, ddof=1)
    critical = float(t.ppf(1.0 - ALPHA / (2.0 * M), n - 1))
    half = critical * sds / math.sqrt(n)
    return np.all((means - half <= target) & (target <= means + half), axis=1)


def simultaneous_hoeffding_coverage(x: np.ndarray, target: float) -> np.ndarray:
    half = hoeffding_half_width(x.shape[1])
    means = x.mean(axis=1)
    return np.all((means - half <= target) & (target <= means + half), axis=1)


def beta_skew_diagnostic(rng: np.random.Generator, n: int = 36) -> dict:
    a, b = 0.35, 2.0
    target = 2.0 * a / (a + b) - 1.0
    student_hits = 0
    hoeffding_hits = 0
    batch = 500
    for _ in range(REPS // batch):
        x = 2.0 * rng.beta(a, b, size=(batch, n, M)) - 1.0
        student_hits += int(simultaneous_student_coverage(x, target).sum())
        hoeffding_hits += int(simultaneous_hoeffding_coverage(x, target).sum())
    return {
        "status": "diagnostic_not_proof",
        "replications": REPS,
        "n": n,
        "m": M,
        "distribution": "2*Beta(0.35,2)-1",
        "true_component_mean": target,
        "student_bonferroni_simultaneous_coverage_mc": student_hits / REPS,
        "hoeffding_bonferroni_simultaneous_coverage_mc": hoeffding_hits / REPS,
        "hoeffding_half_width": hoeffding_half_width(n),
    }


def mnar_diagnostic(rng: np.random.Generator, n: int = 36) -> dict:
    """Compare complete-case inference with a worst-case bounded band.

    Y is always mathematically defined here.  R=1[Y<=-0.2], so response is
    deliberately outcome-dependent.  The worst-case band is not available if
    the outcome itself is undefined after a safety abort.
    """
    a, b = 0.5, 2.0
    target = 2.0 * a / (a + b) - 1.0
    complete_case_hits = 0
    worst_case_hits = 0
    invalid_complete_case = 0
    batch = 500
    critical_cache: dict[int, float] = {}
    h = hoeffding_half_width(n)
    for _ in range(REPS // batch):
        y = 2.0 * rng.beta(a, b, size=(batch, n, M)) - 1.0
        r = y <= -0.2

        # Complete-case intervals, evaluated against the all-enrollee full-data mean.
        batch_cc = np.ones(batch, dtype=bool)
        for rep in range(batch):
            for j in range(M):
                obs = y[rep, r[rep, :, j], j]
                if obs.size < 2:
                    batch_cc[rep] = False
                    invalid_complete_case += 1
                    continue
                df = obs.size - 1
                critical = critical_cache.setdefault(
                    df, float(t.ppf(1.0 - ALPHA / (2.0 * M), df))
                )
                mean = float(obs.mean())
                half = critical * float(obs.std(ddof=1)) / math.sqrt(obs.size)
                batch_cc[rep] &= mean - half <= target <= mean + half
        complete_case_hits += int(batch_cc.sum())

        lower = np.where(r, y, -1.0).mean(axis=1) - h
        upper = np.where(r, y, 1.0).mean(axis=1) + h
        batch_wc = np.all((lower <= target) & (target <= upper), axis=1)
        worst_case_hits += int(batch_wc.sum())

    response_probability = float(beta_dist.cdf(0.4, a, b))  # Y<=-0.2 iff Beta<=0.4
    return {
        "status": "diagnostic_not_proof",
        "replications": REPS,
        "n": n,
        "m": M,
        "distribution": "Y=2*Beta(0.5,2)-1; R=1[Y<=-0.2]",
        "true_full_data_component_mean": target,
        "response_probability_exact": response_probability,
        "complete_case_student_simultaneous_coverage_for_full_target_mc": complete_case_hits
        / REPS,
        "worst_case_bounded_band_simultaneous_coverage_mc": worst_case_hits / REPS,
        "component_failures_due_to_fewer_than_2_observations": invalid_complete_case,
        "worst_case_hoeffding_half_width": h,
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    target_half_width = 0.05
    n_for_target_width = math.ceil(
        2.0 * math.log(2.0 * M / ALPHA) / (target_half_width**2)
    )
    result = {
        "round": "R163",
        "seed": SEED,
        "alpha": ALPHA,
        "components": M,
        "claims": {
            "exact_counterexample": "Analytic binomial enumeration; no Monte Carlo error.",
            "hoeffding_guarantee": (
                "For independent participant vectors with each component in [-1,1], "
                "the displayed intervals cover all component means simultaneously with "
                "probability at least 1-alpha. Component independence is not required."
            ),
            "monte_carlo": "Diagnostics only; not coverage proofs.",
        },
        "rare_spike_exact": [exact_rare_spike(n) for n in (24, 36, 60, 120)],
        "hoeffding_widths": {
            str(n): hoeffding_half_width(n) for n in (24, 36, 60, 120, n_for_target_width)
        },
        "n_for_half_width_at_most_005": n_for_target_width,
        "beta_skew": beta_skew_diagnostic(rng),
        "arbitrary_missingness": mnar_diagnostic(rng),
        "clipping_nonidentification": {
            "observed_clipped_distribution_A": "P(W=1)=1 from latent Z=2",
            "observed_clipped_distribution_B": "P(W=1)=1 from latent Z=100",
            "observed_laws_equal": True,
            "latent_means": [2.0, 100.0],
            "conclusion": "No estimator of clipped W can identify the latent mean without added assumptions.",
        },
        "order_target_boundary": {
            "model": "W=0.4*O+epsilon, O in {-1,+1}, E[epsilon|O]=0",
            "balanced_randomized_order_mean": 0.0,
            "canonical_O_plus_1_mean": 0.4,
            "conclusion": "Coverage for the randomized-order mixture mean does not cover an order-invariant or canonical-order target by implication.",
        },
    }
    output = Path(__file__).with_name("STRESS_TEST_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
