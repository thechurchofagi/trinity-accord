"""Read-only numerical audit of the fixed four-model response comparison.

Does not fit, refit, regenerate CV partitions, or edit empirical outputs.
Writes only its audit result next to this script.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from scipy.special import ndtr, xlogy
from scipy import stats

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / "root_analysis"))
from verify_execution_source import verify_source_provenance
MODEL_FILE = BASE / "root_analysis" / "fit_response_models.py"
spec = importlib.util.spec_from_file_location("audited_bci_response", MODEL_FILE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
OUT = BASE / "empirical" / "results" / "bci_response"


def independently_evaluated_probability(theta, name):
    """Direct signed-SOA expression, independently mapped from parameters."""
    theta = np.asarray(theta, float)
    if name.startswith("sigma"):
        prior_logits = np.repeat(theta[:2], 3)
        sd = np.tile(np.exp(theta[2:5]), 2)
        lapse = theta[5]
    else:
        prior_logits = theta[:6]
        sd = np.repeat(np.exp(theta[6]), 6)
        lapse = theta[7]
    center = np.repeat(theta[-2:] * 100., 3) if name.endswith("_shift") else np.zeros(6)
    variance = sd**2
    stimulus_variance = 84000.
    k_squared = 2 * variance * (variance + stimulus_variance) / stimulus_variance * (
        prior_logits + .5 * np.log1p(stimulus_variance / variance)
    )
    k = np.sqrt(np.maximum(k_squared, 0.))
    relative = np.array([-400., -200., -100., 0., 100., 200., 400.])[None, :] - center[:, None]
    q = ndtr((k[:, None] - relative) / sd[:, None]) - ndtr((-k[:, None] - relative) / sd[:, None])
    return lapse / 2 + (1 - lapse) * q


def binary_nll(y, n, p):
    return -float(np.sum(xlogy(y, p) + xlogy(n-y, 1-p)))


def main():
    summary = json.loads((OUT / "response_comparison_summary.json").read_text())
    full = json.loads((OUT / "full_fits.json").read_text())
    cv = json.loads((OUT / "cv_fits.json").read_text())
    partition = np.load(OUT / "cv_partition_counts.npz")
    y, test, train = (partition[k] for k in ("full_counts", "test_counts", "train_counts"))
    assert y.shape == (30, 6, 7) and test.shape == train.shape == (5, 30, 6, 7)
    assert np.array_equal(test.sum(axis=0), y)
    assert np.array_equal(train, y[None] - test)
    assert np.all((test >= 0) & (test <= 2)) and np.all((train >= 0) & (train <= 8))
    source_sheet = pd.read_excel(BASE / "empirical" / "inputs" / "Experiment_3.xlsx", header=None)
    for i in range(30):
        for t, task in enumerate(["ownership", "simultaneity"]):
            for f, condition in enumerate(["8Hz", "sham", "13Hz"]):
                first_column = 1 + 7*(t*3+f)
                expected = source_sheet.iloc[3+i, first_column:first_column+7].to_numpy(int)
                assert np.array_equal(y[i, t*3+f], expected)
    source_provenance = verify_source_provenance(BASE, summary["source_model_sha256"])
    max_probability_discrepancy = 0.
    max_nll_discrepancy = 0.
    max_projected_gradient_discrepancy = 0.
    accumulated_scores = {name: np.zeros(30) for name in model.MODELS}
    checks = []
    for i in range(30):
        for name in model.MODELS:
            for phase, fold, record in [("full", None, full[i][name])] + [
                ("cv", f, cv[i][f][name]) for f in range(5)
            ]:
                counts, trials = (y[i], 10) if phase == "full" else (train[fold, i], 8)
                assert np.array_equal(np.asarray(record["counts"]), counts)
                assert record["trials"] == trials
                p = independently_evaluated_probability(record["theta"], name)
                original_probability = model.probabilities_and_derivatives(record["theta"], name)[0]
                max_probability_discrepancy = max(max_probability_discrepancy,
                    float(np.max(np.abs(p-original_probability))))
                actual_nll = binary_nll(counts, trials, p)
                max_nll_discrepancy = max(max_nll_discrepancy, abs(actual_nll-record["nll"]))
                _, gradient = model.nll_and_gradient(record["theta"], counts, trials, name)
                pg = model.projected_gradient(record["theta"], gradient, model.bounds(name))
                max_projected_gradient_discrepancy = max(max_projected_gradient_discrepancy,
                    abs(pg-record["projected_gradient_max"]))
                assert record["success"] and not record["numerical_quality_flag"]
                assert pg <= 1e-3
                if phase == "cv":
                    assert not record["full_data_or_source_initialization_used"]
                    if name.endswith("_shift"):
                        base_name = name.removesuffix("_shift")
                        expected_start = np.r_[cv[i][fold][base_name]["theta"], 0., 0.]
                        assert np.array_equal(np.asarray(record["additional_start_parameters"]),
                            expected_start[None, :])
                        assert record["same_training_fold_unshifted_start_added"]
                        assert record["nll"] <= cv[i][fold][base_name]["nll"] + 1e-6
                    else:
                        assert record["additional_start_parameters"] == []
                    assert record["generic_starts_requested"] == 8
                    assert np.array_equal(record["heldout_counts"], test[fold, i])
                    score = binary_nll(test[fold, i], 2, p)
                    max_nll_discrepancy = max(max_nll_discrepancy, abs(score-record["heldout_nll"]))
                    accumulated_scores[name][i] += score
            if name.endswith("_shift"):
                base = name.removesuffix("_shift")
                nested = np.r_[full[i][base]["theta"], 0., 0.]
                nested_p = independently_evaluated_probability(nested, name)
                base_p = independently_evaluated_probability(full[i][base]["theta"], base)
                assert np.array_equal(nested_p, base_p)
                assert full[i][name]["nll"] <= full[i][base]["nll"] + 1e-6
    for j, name in enumerate(model.MODELS):
        points = list(model.generic_starts(name, 4, 2026101060+j))
        nu, ns, _, _, shifted = model.structure(name)
        for tail_sd, tail_logit in [(2., -5.), (6.5, 12.)]:
            x = np.r_[np.repeat(tail_logit, nu), np.repeat(tail_sd, ns), .15,
                ([-.2, .35] if shifted else [])]
            points.append(x)
        errors = []
        for x in points:
            analytical = model.nll_and_gradient(x, y[j], 10, name)[1]
            numeric = approx_derivative(lambda z: binary_nll(y[j], 10,
                independently_evaluated_probability(z, name)), x, method="3-point").ravel()
            error = float(np.max(np.abs(analytical-numeric)/(1+np.abs(numeric))))
            errors.append(error)
        assert max(errors) < 1e-4, (name, errors)
        checks.append({"model": name, "finite_difference_points": len(points),
            "maximum_scaled_derivative_error": max(errors)})
    saturated = binary_nll(y, 10, y/10)
    parameter_counts = {"sigma": 6, "prior": 8, "sigma_shift": 8, "prior_shift": 10}
    for name, k in parameter_counts.items():
        reported = summary["models"][name]
        nll = sum(full[i][name]["nll"] for i in range(30))
        assert reported["effective_parameters_per_participant"] == k
        assert reported["nominal_deviance_df"] == 1260-30*k
        assert abs(reported["full_deviance"]-2*(nll-saturated)) < 1e-8
        assert abs(reported["sum_AIC"]-(2*nll+60*k)) < 1e-8
        assert abs(reported["heldout_nll_sum"]-sum(accumulated_scores[name])) < 1e-8
    contrast = accumulated_scores["sigma_shift"]-accumulated_scores["prior_shift"]
    confidence = stats.t.interval(.95, 29, loc=contrast.mean(), scale=stats.sem(contrast))
    result = {
        "status": "Read-only independent audit passed; no refitting performed",
        "model_sha256": hashlib.sha256(MODEL_FILE.read_bytes()).hexdigest(),
        "execution_source_provenance": source_provenance,
        "runner_sha256": hashlib.sha256((BASE / "empirical" / "run_bci_response_comparison.py").read_bytes()).hexdigest(),
        "partition_count_mapping_matches_canonical": True,
        "partitions_exhaust_counts_once_and_have_two_trials_per_cell_per_fold": True,
        "train_counts_exclude_the_scored_fold": True,
        "source_or_full_initializations_in_cv": False,
        "independent_probability_and_nll_records_checked": 720,
        "maximum_probability_discrepancy": max_probability_discrepancy,
        "maximum_nll_discrepancy": max_nll_discrepancy,
        "maximum_projected_gradient_discrepancy": max_projected_gradient_discrepancy,
        "finite_difference_checks": checks,
        "zero_center_nesting_checks": 60,
        "full_nesting_violations": 0,
        "training_fold_nesting_checks": 300,
        "cv_nesting_violations": 0,
        "shifted_cv_starts": "Eight Sobol, canonical, and same-training-fold unshifted fit embedded with two zero centers",
        "repair_scope": "All 300 shifted training-fold fits were uniformly repaired after a nesting failure was detected; no heldout score selected individual repairs.",
        "effective_parameter_counts": parameter_counts,
        "shifted_sigma_minus_shifted_prior_cv": {
            "sum": float(contrast.sum()), "mean": float(contrast.mean()),
            "participant_mean_t95": list(map(float, confidence))},
        "limits": [
            "Artificial exchangeable binary partitions of aggregate counts do not reconstruct chronology or independent replication.",
            "A participant interval treats each participant's whole fivefold score as one paired unit; it does not treat overlapping folds as independent.",
            "Held-out scoring is conditionally honest for the selected fixed pipeline, not an external validation of an analysis family selected after inspecting this dataset.",
            "Zero projected-gradient flags certify this numerical stopping check, not global optimum or parameter identifiability.",
            "Several parameter estimates hit bounds; nominal chi-square deviance p values are reference diagnostics only.",
            "Shifted models add exactly two task centers per participant, stable across stimulation; they do not fit six condition-specific centers.",
            "No relative score identifies an anatomical noise source or resolves the exact decision-side counterpart."
        ]
    }
    (HERE / "RESPONSE_COMPARISON_AUDIT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
