"""Enumerate the finite binomial law for a fixed paired-readout confidence set.

No human observations, fitted source parameters, random draws, or prior model
fits are used. ANALYSIS_PLAN.json fixes all 480 cases before this computation.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import platform
import time

import numpy as np
import pandas as pd
import scipy
from scipy.stats import binom

import confidence_sets as cs


HERE = Path(__file__).resolve().parent
PLAN_PATH = HERE / "ANALYSIS_PLAN.json"
PLAN = json.loads(PLAN_PATH.read_text())
ALPHA = PLAN["alpha"]
P_TOL = PLAN["numerical_rules"]["probability_boundary_tolerance"]
A_TOL = PLAN["numerical_rules"]["variance_endpoint_tolerance"]
CANDIDATES = np.asarray(PLAN["candidate_variances_for_exclusion"], float)


def native(value):
    if isinstance(value, dict):
        return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    if isinstance(value, np.ndarray):
        return native(value.tolist())
    if isinstance(value, np.generic):
        return native(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calibration(profile, kappa, lapse=None):
    rate = profile["lapse"] if lapse is None else lapse
    return cs.PairCalibration(
        v_o=1., v_s=1.,
        k_o=profile["k_ownership"], k_s=profile["k_simultaneity"],
        lapse_o=rate, lapse_s=rate, kappa=kappa,
    )


def compatible_probability_range(a, cal):
    """Exact attainable P11 range at a, for equal marginal variances one."""
    b = 1. - a
    low_covariance = a - cal.kappa*b
    # If zero covariance is attainable it minimizes the centered rectangle.
    low_c = -a if low_covariance <= 0 else -cal.kappa*b
    high_c = cal.kappa*b
    return (
        cs.paired_yes_probability(a, low_c, cal),
        cs.paired_yes_probability(a, high_c, cal),
    )


def precompute_tables():
    """Enumerate interval endpoints once per profile, N, and supplied bound."""
    tables = {}
    packed = {}
    diagnostics = []
    start = time.monotonic()
    for n in PLAN["sample_sizes_paired_trials"]:
        cp = np.asarray([cs.clopper_pearson(k, n, ALPHA) for k in range(n+1)], float)
        assert cp.shape == (n+1, 2)
        assert np.all(cp[:, 0] <= cp[:, 1])
        packed[f"N{n}_binomial_CI"] = cp
        for profile in PLAN["profiles"]:
            for kappa in [0., .2]:
                cal = calibration(profile, kappa)
                lower = np.full(n+1, np.nan)
                upper = np.full(n+1, np.nan)
                rho_lower = np.full(n+1, np.nan)
                rho_upper = np.full(n+1, np.nan)
                empty = np.ones(n+1, dtype=bool)
                statuses = []
                for k, (p_lo, p_hi) in enumerate(cp):
                    projected = cs.project_probability_interval(float(p_lo), float(p_hi), cal)
                    statuses.append(projected.status)
                    if projected.a_interval is not None:
                        lower[k], upper[k] = projected.a_interval
                        empty[k] = False
                        if projected.rho_interval is not None:
                            rho_lower[k], rho_upper[k] = projected.rho_interval
                assert np.all(lower[~empty] >= -A_TOL)
                assert np.all(upper[~empty] <= 1.+A_TOL)
                assert np.all(lower[~empty] <= upper[~empty]+A_TOL)
                membership = (
                    (~empty[:, None])
                    & (lower[:, None] <= CANDIDATES[None, :]+A_TOL)
                    & (upper[:, None] >= CANDIDATES[None, :]-A_TOL)
                )
                # A direct probability-range intersection independently checks
                # inclusion of each fixed candidate for every possible K.
                for j, a in enumerate(CANDIDATES):
                    pmin, pmax = compatible_probability_range(float(a), cal)
                    direct = (cp[:, 0] <= pmax+P_TOL) & (cp[:, 1] >= pmin-P_TOL)
                    mismatch = np.flatnonzero(direct != membership[:, j])
                    if len(mismatch):
                        raise AssertionError({
                            "type": "candidate projection disagreement",
                            "profile": profile["profile_id"], "N": n,
                            "kappa": kappa, "candidate": float(a),
                            "counts": mismatch.tolist(),
                        })
                key = (profile["profile_id"], n, kappa)
                tables[key] = {
                    "cp": cp, "lower": lower, "upper": upper,
                    "empty": empty, "membership": membership,
                }
                prefix = f'{profile["profile_id"]}_N{n}_kappa{str(kappa).replace(".", "p")}'
                packed[prefix+"_lower"] = lower
                packed[prefix+"_upper"] = upper
                packed[prefix+"_empty"] = empty
                packed[prefix+"_rho_lower"] = rho_lower
                packed[prefix+"_rho_upper"] = rho_upper
                diagnostics.append({
                    "profile": profile["profile_id"], "N": n, "kappa": kappa,
                    "outcomes_enumerated": n+1,
                    "statuses": dict(Counter(statuses)),
                    "candidate_membership_checks": (n+1)*len(CANDIDATES),
                    "direct_candidate_intersection_checks_passed": True,
                })
                print(
                    "confidence_table", profile["profile_id"], n, kappa,
                    "elapsed_seconds", round(time.monotonic()-start, 2),
                    flush=True,
                )
    return tables, packed, diagnostics


def scenario_definitions():
    # Every combination is specified by the frozen plan; no result selects one.
    return [
        ("valid", "independent_criteria", 0., 0.),
        ("valid", "negative_boundary", .2, -.2),
        ("valid", "uncorrelated_criteria", .2, 0.),
        ("valid", "positive_boundary", .2, .2),
        ("wrong_independence_bound", "negative_actual_correlation", 0., -.2),
        ("wrong_independence_bound", "positive_actual_correlation", 0., .2),
        ("independent_sensory_resampling", "independent_draws", 0., 0.),
        ("shared_lapse_and_guess", "shared_lapse", 0., 0.),
    ]


def generating_probability(profile, a, family, actual_corr, assumed_kappa):
    c = actual_corr*(1.-a)
    if family == "independent_sensory_resampling":
        # Marginal variances remain one, but there is no common sensory draw.
        p = cs.paired_yes_probability(0., 0., calibration(profile, 0.))
        shared_a = 0.
        role = "per_task_sensory_variance_with_independent_samples"
    elif family == "shared_lapse_and_guess":
        nonlapse = cs.paired_yes_probability(a, 0., calibration(profile, 0., lapse=0.))
        p = (1.-profile["lapse"])*nonlapse + profile["lapse"]/2.
        shared_a = a
        role = "actual_shared_sensory_variance"
    else:
        actual_cal = calibration(profile, max(assumed_kappa, abs(actual_corr)))
        p = cs.paired_yes_probability(a, c, actual_cal)
        shared_a = a
        role = "actual_shared_sensory_variance"
    assert 0 <= p <= 1
    return float(p), float(c), float(shared_a), role


def evaluate_case(profile, n, a, family, condition, kappa, actual_corr, table):
    p_true, c_true, shared_a, target_role = generating_probability(
        profile, a, family, actual_corr, kappa
    )
    counts = np.arange(n+1)
    raw_weights = binom.pmf(counts, n, p_true)
    mass_sum = float(raw_weights.sum())
    assert abs(mass_sum-1.) < 1e-10
    weights = raw_weights/mass_sum
    cp = table["cp"]
    lower, upper, empty = (table[k] for k in ["lower", "upper", "empty"])
    nonempty = ~empty
    target_in = nonempty & (lower <= a+A_TOL) & (upper >= a-A_TOL)
    p_nonempty = float(weights @ nonempty)
    p_empty = float(weights @ empty)
    cp_contains = (cp[:, 0] <= p_true+P_TOL) & (cp[:, 1] >= p_true-P_TOL)
    cp_coverage = float(weights @ cp_contains)
    width = np.where(nonempty, upper-lower, 0.)
    expected_width = float(weights @ width)
    if p_nonempty > 0:
        conditional_weights = weights[nonempty]/p_nonempty
        conditional_width = float(conditional_weights @ width[nonempty])
        conditional_lower = float(conditional_weights @ lower[nonempty])
        conditional_upper = float(conditional_weights @ upper[nonempty])
    else:
        conditional_width = conditional_lower = conditional_upper = None
    cal = calibration(profile, kappa)
    identified = cs.population_identified_set(p_true, cal).a_interval
    id_coverage = None
    target_coverage = float(weights @ target_in)
    if family == "valid":
        assert identified is not None
        all_identified_in = nonempty & (lower <= identified[0]+A_TOL) & (upper >= identified[1]-A_TOL)
        id_coverage = float(weights @ all_identified_in)
        assert cp_coverage >= 1.-ALPHA-1e-10
        assert target_coverage >= cp_coverage-1e-10
        assert id_coverage >= cp_coverage-1e-10
    assert cp_coverage >= 1.-ALPHA-1e-10
    row = {
        "scenario_id": f'{profile["profile_id"]}__N{n}__a{a}__{family}__{condition}',
        "family": family, "condition": condition,
        "profile": profile["profile_id"], "N_pairs": n,
        "k_ownership": profile["k_ownership"], "k_simultaneity": profile["k_simultaneity"],
        "known_marginal_lapse": profile["lapse"],
        "assumed_kappa": kappa,
        "generating_sensory_variance_per_task": a,
        "actual_shared_sensory_variance": shared_a,
        "actual_criterion_covariance": c_true,
        "evaluated_target": a, "evaluated_target_role": target_role,
        "nominal_target_coverage_applies": family == "valid",
        "true_paired_yes_probability": p_true,
        "CP_probability_coverage": cp_coverage,
        "target_inclusion_probability": target_coverage,
        "valid_shared_variance_coverage": target_coverage if family == "valid" else None,
        "complete_population_identified_set_coverage": id_coverage,
        "empty_set_probability": p_empty,
        "nonempty_set_probability": p_nonempty,
        "expected_width_empty_as_zero": expected_width,
        "expected_width_conditional_nonempty": conditional_width,
        "expected_lower_conditional_nonempty": conditional_lower,
        "expected_upper_conditional_nonempty": conditional_upper,
        "population_set_lower_under_assumed_model": identified[0] if identified else None,
        "population_set_upper_under_assumed_model": identified[1] if identified else None,
        "population_set_width_under_assumed_model": identified[1]-identified[0] if identified else None,
        "binomial_mass_sum_before_normalization": mass_sum,
        "binomial_mass_sum_error": mass_sum-1.,
        "positive_probability_count_outcomes_in_float": int(np.count_nonzero(weights)),
    }
    for j, candidate in enumerate(CANDIDATES):
        suffix = str(float(candidate)).replace(".", "p")
        row["exclusion_probability_a_"+suffix] = float(weights @ (~table["membership"][:, j]))
    return row


def summary_for(frame, table_diagnostics, elapsed):
    valid = frame[frame.family == "valid"]
    grouped = []
    for (n, kappa), part in valid.groupby(["N_pairs", "assumed_kappa"], sort=True):
        grouped.append({
            "N_pairs": int(n), "kappa": float(kappa), "fixed_grid_cases": len(part),
            "minimum_shared_variance_coverage": float(part.valid_shared_variance_coverage.min()),
            "maximum_shared_variance_coverage": float(part.valid_shared_variance_coverage.max()),
            "minimum_complete_identified_set_coverage": float(part.complete_population_identified_set_coverage.min()),
            "minimum_expected_width": float(part.expected_width_empty_as_zero.min()),
            "maximum_expected_width": float(part.expected_width_empty_as_zero.max()),
            "fixed_grid_mean_expected_width": float(part.expected_width_empty_as_zero.mean()),
            "maximum_empty_set_probability": float(part.empty_set_probability.max()),
        })
    negatives = []
    for family, part in frame[frame.family != "valid"].groupby("family", sort=True):
        negatives.append({
            "family": family, "fixed_grid_cases": len(part),
            "target_role": part.evaluated_target_role.unique().tolist(),
            "minimum_target_inclusion_probability": float(part.target_inclusion_probability.min()),
            "maximum_target_inclusion_probability": float(part.target_inclusion_probability.max()),
            "maximum_empty_set_probability": float(part.empty_set_probability.max()),
            "minimum_CP_probability_coverage": float(part.CP_probability_coverage.min()),
            "nominal_target_coverage_claimed": False,
        })
    reference = frame[
        (frame.profile == PLAN["profiles"][0]["profile_id"])
        & frame.condition.isin(["independent_criteria", "uncorrelated_criteria"])
        & frame.generating_sensory_variance_per_task.isin([0., .3, .9])
    ]
    return {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "analysis_plan_sha256": sha256(PLAN_PATH),
        "cases": len(frame), "case_counts": dict(Counter(frame.family)),
        "method": "Finite sum over every possible binomial count; deterministic numerical probability integration/inversion; no Monte Carlo sampling.",
        "maximum_absolute_binomial_mass_sum_error": float(frame.binomial_mass_sum_error.abs().max()),
        "minimum_CP_probability_coverage_all_cases": float(frame.CP_probability_coverage.min()),
        "minimum_valid_shared_variance_coverage": float(valid.valid_shared_variance_coverage.min()),
        "minimum_valid_complete_identified_set_coverage": float(valid.complete_population_identified_set_coverage.min()),
        "all_fixed_valid_cases_meet_nominal_coverage": bool((valid.valid_shared_variance_coverage >= 1.-ALPHA-1e-10).all()),
        "valid_grid_summaries": grouped,
        "negative_control_summaries": negatives,
        "fixed_reference_rows": reference.to_dict(orient="records"),
        "confidence_table_diagnostics": table_diagnostics,
        "total_candidate_intersection_checks": sum(d["candidate_membership_checks"] for d in table_diagnostics),
        "uncertainty_scope": PLAN["reporting_rules"]["uncertainty_scope"],
        "negative_control_scope": "Target inclusion under a deliberately false contract is not valid confidence coverage. The resampling target is per-task variance rather than a shared component.",
        "no_power_claim": PLAN["reporting_rules"]["no_power_claim"],
    }


def main():
    start = time.monotonic()
    initial_plan_hash = sha256(PLAN_PATH)
    module_path = Path(cs.__file__).resolve()
    module_hash = sha256(module_path)
    runner_hash = sha256(__file__)
    tables, packed, diagnostics = precompute_tables()
    rows = []
    for profile in PLAN["profiles"]:
        for n in PLAN["sample_sizes_paired_trials"]:
            for a in PLAN["generating_sensory_variances"]:
                for family, condition, kappa, actual_corr in scenario_definitions():
                    rows.append(evaluate_case(
                        profile, n, a, family, condition, kappa, actual_corr,
                        tables[(profile["profile_id"], n, kappa)],
                    ))
    frame = pd.DataFrame(rows)
    expected = {k: v for k, v in PLAN["scenario_counts"].items() if k != "total"}
    assert dict(Counter(frame.family)) == expected
    assert len(frame) == PLAN["scenario_counts"]["total"]
    assert not frame.scenario_id.duplicated().any()
    assert sha256(PLAN_PATH) == initial_plan_hash
    assert sha256(module_path) == module_hash
    assert sha256(__file__) == runner_hash
    frame.to_csv(HERE / "operating_characteristics.csv", index=False)
    np.savez_compressed(HERE / "confidence_set_tables.npz", **packed)
    summary = summary_for(frame, diagnostics, time.monotonic()-start)
    (HERE / "operating_characteristics_summary.json").write_text(
        json.dumps(native(summary), indent=2, allow_nan=False)+"\n"
    )
    provenance = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_plan_sha256": initial_plan_hash,
        "runner": {"path": Path(__file__).name, "sha256": runner_hash},
        "confidence_module": {"path": module_path.name, "sha256": module_hash},
        "plan_and_code_unchanged_during_execution": True,
        "runtime": {
            "python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "pandas": pd.__version__,
        },
        "input_data_files": [],
        "source_parameter_examples": 0,
        "Monte_Carlo_draws": 0,
        "human_observations_added": 0,
        "prior_response_fits_rerun": 0,
        "prior_symmetry_simulations_rerun": 0,
        "outputs": [
            {"path": name, "sha256": sha256(HERE/name), "bytes": (HERE/name).stat().st_size}
            for name in ["operating_characteristics.csv", "operating_characteristics_summary.json", "confidence_set_tables.npz"]
        ],
    }
    (HERE / "EXECUTION_PROVENANCE.json").write_text(
        json.dumps(native(provenance), indent=2, allow_nan=False)+"\n"
    )
    print(json.dumps(native({
        key: summary[key] for key in [
            "elapsed_seconds", "cases", "case_counts",
            "minimum_CP_probability_coverage_all_cases",
            "minimum_valid_shared_variance_coverage",
            "minimum_valid_complete_identified_set_coverage",
            "valid_grid_summaries", "negative_control_summaries",
        ]
    }), indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
