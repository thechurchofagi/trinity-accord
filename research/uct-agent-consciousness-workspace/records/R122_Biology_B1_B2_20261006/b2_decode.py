#!/usr/bin/env python3
"""R122: conservative raw-session cumulative-evidence decoding.

This is an independent reanalysis, not an exact author-figure reproduction.
See B2_PROTOCOL_FROZEN.md. It does not estimate experience, valence, or causal
necessity, and a positive decoding result does not complete a T2 certificate.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import warnings

# Keep BLAS concurrency bounded when 12 sessions are analyzed sequentially.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import Lasso
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class Config:
    seed: int = 122
    bin_s: float = 0.05
    lag_s: float = 0.1
    smooth_sigma_s: float = 0.075
    smooth_truncate: float = 4.0
    outer_folds: int = 5
    inner_folds: int = 3
    min_trials: int = 50
    min_metric_trials: int = 20
    fr_threshold_hz: float = 1.0
    alphas: tuple = (0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
    max_iter: int = 20000
    tol: float = 1e-4


def clean_json(v):
    if isinstance(v, dict):
        return {str(k): clean_json(x) for k, x in v.items()}
    if isinstance(v, (tuple, list, np.ndarray)):
        return [clean_json(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return float(v) if np.isfinite(v) else None
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, Path):
        return str(v)
    return v


def write_json(path, data):
    Path(path).write_text(json.dumps(clean_json(data), ensure_ascii=False,
                                    indent=2, allow_nan=False) + "\n")


def current_code_hashes():
    here = Path(__file__).resolve().parent
    return {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
            for name in ("b2_decode.py", "rat_cells.py")}


def reusable_summary(old, session, cfg, outdir):
    if (old.get("status") != "computed" or old.get("source_sha256") != session.source_sha256
            or old.get("config") != clean_json(asdict(cfg))
            or old.get("code_sha256") != current_code_hashes()):
        return False
    for key in ("predictions", "fold_audit"):
        artifact = old.get("artifacts", {}).get(key)
        expected = old.get("artifacts", {}).get(key + "_sha256")
        if artifact is None or expected is None:
            return False
        path = outdir / artifact
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            return False
    return True


def metric(y, prediction):
    y, prediction = np.asarray(y), np.asarray(prediction)
    m = np.isfinite(y) & np.isfinite(prediction)
    y, prediction = y[m], prediction[m]
    if len(y) < 2:
        return {"n_rows": int(len(y)), "pearson_r": None, "r2": None,
                "rmse": None}
    error = np.mean((y - prediction) ** 2)
    variance = np.var(y)
    r = (np.corrcoef(y, prediction)[0, 1]
         if variance > 0 and np.var(prediction) > 0 else np.nan)
    return {"n_rows": int(len(y)), "pearson_r": r,
            "r2": 1 - error / variance if variance > 0 else None,
            "rmse": np.sqrt(error)}


def trial_folds(trial_ids, n_splits):
    """Contiguous whole-trial folds; never split rows from one trial."""
    unique = np.unique(np.asarray(trial_ids, dtype=int))
    if len(unique) < n_splits:
        raise ValueError("Too few complete trials for requested folds")
    for tr, va in KFold(n_splits=n_splits, shuffle=False).split(unique):
        train, valid = unique[tr], unique[va]
        assert not set(train).intersection(valid)
        yield train, valid


def smoothing_weights(cfg):
    if cfg.smooth_sigma_s <= 0:
        return np.ones(1)
    pad = int(np.ceil(cfg.smooth_truncate * cfg.smooth_sigma_s / cfg.bin_s))
    w = np.exp(-0.5 * (np.arange(pad + 1) * cfg.bin_s /
                      cfg.smooth_sigma_s) ** 2)
    return w / w.sum()


def valid_laser_value(v):
    """A finite positive pulse onset is evidence of delivered laser light."""
    try:
        a = np.asarray(v, dtype=float).ravel()
    except (TypeError, ValueError):
        return False
    return bool(np.any(np.isfinite(a) & (a > 0)))


def build_arrays(session, cfg):
    """Construct predictors using fixed bins and no fitted preprocessing.

    Common loader returns original raw row IDs. Spikes and stateTimes use the
    clock used by the author's loader; click arrays are onset-relative.
    """
    frame = session.trials.loc[session.trials["eligible"].astype(bool)].copy()
    audit = {"n_behavior_eligible": len(frame), "excluded_trials": [],
             "unit_availability_policy": "retain only units observed on every analyzed trial",
             "no_laser_flag_metadata": True,
             "missing_center_poke_exit_trials": 0}
    good = []
    bins = []
    for _, row in frame.iterrows():
        reason = None
        duration, onset = float(row["duration_s"]), float(row["clicks_on_s"])
        if not (np.isfinite(duration) and duration > 0 and np.isfinite(onset)):
            reason = "invalid_stimulus_clock"
        else:
            cutoff = duration
            offset = row.get("clicks_off_s", np.nan)
            if pd.notna(offset) and np.isfinite(float(offset)) and float(offset) > onset:
                cutoff = min(cutoff, float(offset) - onset)
            has_exit = False
            for key in ("cpoke_out_s", "cpoke_out"):
                value = row.get(key, np.nan)
                if pd.notna(value) and np.isfinite(float(value)) and float(value) > onset:
                    cutoff = min(cutoff, float(value) - onset)
                    has_exit = True
            if not has_exit:
                audit["missing_center_poke_exit_trials"] += 1
            if "source_laser_isOn" in row.index:
                audit["no_laser_flag_metadata"] = False
                if pd.notna(row["source_laser_isOn"]) and float(row["source_laser_isOn"]) != 0:
                    reason = "laser_isOn_not_zero"
            for key in ("laser_on_s", "laser_on", "laser_pulses"):
                if key in row.index:
                    audit["no_laser_flag_metadata"] = False
                    if valid_laser_value(row[key]):
                        reason = "laser_stimulus_present"
            n = int(np.floor((cutoff - cfg.lag_s + 1e-9) / cfg.bin_s))
            if n < 1:
                reason = "no_complete_withinstimulus_lagged_bin"
        if reason:
            audit["excluded_trials"].append({"trial_id": str(row["trial_id"]),
                                             "reason": reason})
        else:
            good.append(row)
            bins.append(n)
    if len(good) < cfg.min_trials:
        raise ValueError(f"Only {len(good)} eligible trials; minimum {cfg.min_trials}")
    frame = pd.DataFrame(good).reset_index(drop=True)
    source_rows = frame["source_row1"].astype(int).to_numpy() - 1
    units = []
    omitted_units = []
    missing_availability = []
    for unit in session.units:
        if unit.region not in ("FOF", "ADS"):
            continue
        recorded = unit.metadata.get("recorded_by_trial")
        if recorded is None:
            # Schema metadata is reported explicitly; not an assertion of availability.
            missing_availability.append(unit.unit_id)
        else:
            recorded = np.asarray(recorded).ravel()
            if len(recorded) <= source_rows.max():
                omitted_units.append({"unit_id": unit.unit_id,
                                      "reason": "recorded_flag_length_mismatch"})
                continue
            values = recorded[source_rows]
            if not np.all(np.isfinite(values.astype(float)) &
                          (values.astype(float) > 0)):
                omitted_units.append({"unit_id": unit.unit_id,
                                      "reason": "not_recorded_on_all_selected_trials"})
                continue
        spikes = np.asarray(unit.spikes_s, dtype=float).ravel()
        if not np.all(np.isfinite(spikes)):
            omitted_units.append({"unit_id": unit.unit_id,
                                  "reason": "nonfinite_spike_times"})
            continue
        units.append(unit)
    if not units:
        raise ValueError("No FOF/ADS units with valid recording availability")
    unit_regions = np.array([u.region for u in units])
    if not all(np.any(unit_regions == r) for r in ("FOF", "ADS")):
        raise ValueError("Both simultaneous FOF and ADS populations are required")
    # The source has NaN runs in raw spike vectors even where `recorded` is absent.
    # A bracket between neighboring finite times is an inferred conservative gap,
    # not an independently observed record of why these events were unavailable.
    weights = smoothing_weights(cfg)
    pad = len(weights) - 1
    keep = []
    gap_exclusions = []
    gap_unit_count = 0
    gaps = []
    for unit in units:
        intervals = unit.metadata.get("nonfinite_spike_intervals_s", [])
        if intervals:
            gap_unit_count += 1
        for lo, hi in intervals:
            # None is accepted only as an explicitly unbounded endpoint.
            lo = -np.inf if lo is None else float(lo)
            hi = np.inf if hi is None else float(hi)
            if hi < lo:
                raise ValueError(f"Unordered NaN interval for {unit.unit_id}")
            gaps.append((lo, hi, unit.unit_id))
    for trial, row in frame.iterrows():
        onset = float(row["clicks_on_s"])
        neural_start = onset + cfg.lag_s - pad * cfg.bin_s
        neural_end = onset + cfg.lag_s + bins[trial] * cfg.bin_s
        # Union of readout/filter support and firing-rate QC support.
        start = min(onset, neural_start)
        end = max(onset + float(row["duration_s"]), neural_end)
        hit = [unit_id for lo, hi, unit_id in gaps if start <= hi and end >= lo]
        if hit:
            gap_exclusions.append({"trial_id": row["trial_id"],
                                   "reason": "analysis_or_qc_window_overlaps_inferred_NaN_bracket",
                                   "window_start_s": start, "window_end_s": end,
                                   "unit_ids": sorted(set(hit))})
        else:
            keep.append(trial)
    if len(keep) < cfg.min_trials:
        raise ValueError(f"Only {len(keep)} trials after inferred-NaN-window exclusion; minimum {cfg.min_trials}")
    frame = frame.iloc[keep].reset_index(drop=True)
    bins = [bins[i] for i in keep]
    audit["inferred_nan_gap_unit_count"] = gap_unit_count
    audit["inferred_nan_gap_trial_exclusions"] = gap_exclusions
    audit["nan_gap_assumption"] = (
        "Conservatively exclude any trial whose readout/filter or stimulus firing-rate "
        "window overlaps a finite-neighbor bracket of any FOF/ADS unit's raw NaN run. "
        "Bracket is not an observed artifact time or causal diagnosis.")
    audit.update({"availability_excluded_units": omitted_units,
                  "units_without_recorded_metadata": missing_availability,
                  "n_units_after_availability": len(units),
                  "n_trials": len(frame),
                  "clock_assumption": "raw_spike_time_s aligned as in author stateTimes loader",
                  "target": "cumulative (#R-#L) in stimulus bins, not subjective accumulator"})
    nrows = int(np.sum(bins))
    X = np.empty((nrows, len(units)), dtype=float)
    qc_counts = np.empty((len(frame), len(units)), dtype=float)
    groups = np.repeat(np.arange(len(frame)), bins)
    bin_ids = np.concatenate([np.arange(n) for n in bins])
    evidence = np.empty(nrows)
    recent_evidence = np.empty(nrows)
    times = (bin_ids + 1) * cfg.bin_s
    offsets = np.r_[0, np.cumsum(bins)]
    for trial, row in frame.iterrows():
        n = bins[trial]
        ends = (np.arange(n) + 1) * cfg.bin_s
        left = np.sort(np.asarray(row["left_clicks_s"], dtype=float))
        right = np.sort(np.asarray(row["right_clicks_s"], dtype=float))
        cumulative = np.searchsorted(right, ends, side="left") - np.searchsorted(left, ends, side="left")
        sl = slice(offsets[trial], offsets[trial + 1])
        evidence[sl] = cumulative
        recent_evidence[sl] = np.diff(np.r_[0, cumulative])
    for j, unit in enumerate(units):
        spikes = np.sort(np.asarray(unit.spikes_s, dtype=float).ravel())
        for trial, row in frame.iterrows():
            onset = float(row["clicks_on_s"])
            duration = float(row["duration_s"])
            n = bins[trial]
            neural_edges = onset + cfg.lag_s + np.arange(-pad, n + 1) * cfg.bin_s
            counts = np.diff(np.searchsorted(spikes, neural_edges, side="left"))
            # w[0] is the current bin; positive indices are earlier bins.
            rates = np.convolve(counts, weights, mode="full")[:len(counts)] / cfg.bin_s
            X[offsets[trial]:offsets[trial + 1], j] = rates[pad:pad + n]
            a, b = np.searchsorted(spikes, [onset, onset + duration], side="left")
            qc_counts[trial, j] = b - a
    assert np.all(np.isfinite(X)) and np.all(np.isfinite(evidence))
    row_choice = frame["choice"].astype(int).to_numpy()[groups]
    row_duration = frame["duration_s"].astype(float).to_numpy()[groups]
    # Descriptive nuisance controls use eventual choice only to audit decodability.
    nuisance = np.column_stack([np.ones(nrows), row_choice, times, times**2,
                                row_choice * times, row_choice * times**2,
                                row_duration])
    return {"X": X, "y": evidence, "groups": groups, "bin_id": bin_ids,
            "time_s": times, "choice": row_choice, "duration": row_duration,
            "frame": frame, "qc_counts": qc_counts, "units": units,
            "unit_regions": unit_regions, "nuisance": nuisance,
            "recent_evidence": recent_evidence, "audit": audit}


def choose_units(arr, train_trials, cfg, seed):
    # Every firing-rate criterion uses this training split only.
    exposure = arr["frame"].iloc[train_trials]["duration_s"].sum()
    fr = arr["qc_counts"][train_trials].sum(axis=0) / exposure
    candidates = {r: np.flatnonzero((arr["unit_regions"] == r) &
                                    (fr > cfg.fr_threshold_hz))
                  for r in ("FOF", "ADS")}
    n = min(len(v) for v in candidates.values())
    if n < 1:
        raise ValueError("No train-qualified matched FOF/ADS unit pair")
    rng = np.random.default_rng(seed)
    selected = {r: np.sort(rng.choice(ix, n, replace=False))
                for r, ix in candidates.items()}
    return selected, fr


def fit_lasso(X, y, alpha, cfg):
    model = Lasso(alpha=alpha, max_iter=cfg.max_iter, tol=cfg.tol,
                  selection="cyclic")
    with warnings.catch_warnings(record=True) as logged:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(X, y)
    warning_text = [str(w.message) for w in logged]
    return model, warning_text


def evaluate_predictions(arr, predictions, cfg):
    y = arr["y"]
    result = {"pooled": metric(y, predictions), "time_bins": [],
              "within_choice_by_time": []}
    residual_y, residual_pred = [], []
    for b in np.unique(arr["bin_id"]):
        m = arr["bin_id"] == b
        if m.sum() >= cfg.min_metric_trials:
            item = metric(y[m], predictions[m])
            item.update({"bin_index0": int(b), "target_time_s": (b + 1) * cfg.bin_s,
                         "neural_window_end_s": (b + 1) * cfg.bin_s + cfg.lag_s})
            result["time_bins"].append(item)
        for choice in (0, 1):
            mc = m & (arr["choice"] == choice)
            if mc.sum() >= cfg.min_metric_trials:
                item = metric(y[mc], predictions[mc])
                item.update({"bin_index0": int(b), "choice": choice,
                             "target_time_s": (b + 1) * cfg.bin_s})
                result["within_choice_by_time"].append(item)
                residual_y.extend(y[mc] - np.mean(y[mc]))
                residual_pred.extend(predictions[mc] - np.mean(predictions[mc]))
    result["same_time_within_choice_centered"] = metric(residual_y, residual_pred)
    result["same_time_within_choice_centered"]["interpretation"] = (
        "Descriptive correlation after centering held-out predictions and targets within "
        "choice x elapsed-time strata; not a causal estimate and not a refitted decoder.")
    return result


def decode_session(session, outdir, cfg):
    start = time.time()
    arr = build_arrays(session, cfg)
    X, y, groups = arr["X"], arr["y"], arr["groups"]
    all_trials = np.arange(len(arr["frame"]))
    predictions = {r: np.full(len(y), np.nan) for r in ("FOF", "ADS")}
    nuisance_pred = np.full(len(y), np.nan)
    recent_pred = np.full(len(y), np.nan)
    fold_id = np.full(len(y), -1, dtype=int)
    fold_audit = []
    warning_audit = []
    for outer, (train_trials, test_trials) in enumerate(trial_folds(all_trials, cfg.outer_folds)):
        print(json.dumps({"session": session.session_id, "outer_fold": outer,
                          "n_train_trials": len(train_trials), "n_test_trials": len(test_trials)}), flush=True)
        tr = np.flatnonzero(np.isin(groups, train_trials))
        te = np.flatnonzero(np.isin(groups, test_trials))
        assert not set(groups[tr]).intersection(groups[te])
        fold_id[te] = outer
        inner_mse = {r: [] for r in ("FOF", "ADS")}
        inner_audit = []
        for inner, (it, iv) in enumerate(trial_folds(train_trials, cfg.inner_folds)):
            itr = np.flatnonzero(np.isin(groups, it))
            iva = np.flatnonzero(np.isin(groups, iv))
            assert not set(groups[itr]).intersection(groups[iva])
            selected, fr = choose_units(arr, it, cfg, cfg.seed + outer * 100 + inner)
            record = {"inner_fold": inner,
                      "train_trial_ids": arr["frame"].iloc[it]["trial_id"].tolist(),
                      "validation_trial_ids": arr["frame"].iloc[iv]["trial_id"].tolist(),
                      "units": {r: [arr["units"][j].unit_id for j in selected[r]]
                                for r in ("FOF", "ADS")}}
            inner_audit.append(record)
            for region in ("FOF", "ADS"):
                ix = selected[region]
                scaler = StandardScaler().fit(X[np.ix_(itr, ix)])
                a = scaler.transform(X[np.ix_(itr, ix)])
                b = scaler.transform(X[np.ix_(iva, ix)])
                losses = []
                for alpha in cfg.alphas:
                    model, ww = fit_lasso(a, y[itr], alpha, cfg)
                    if ww:
                        warning_audit.append({"outer": outer, "inner": inner,
                                              "region": region, "alpha": alpha,
                                              "warnings": ww})
                    losses.append(float(np.mean((model.predict(b) - y[iva]) ** 2)))
                inner_mse[region].append(losses)
        selected, fr = choose_units(arr, train_trials, cfg, cfg.seed + outer * 100 + 99)
        outer_record = {"fold": outer,
                        "train_trial_ids": arr["frame"].iloc[train_trials]["trial_id"].tolist(),
                        "test_trial_ids": arr["frame"].iloc[test_trials]["trial_id"].tolist(),
                        "inner_folds": inner_audit, "regions": {}}
        # Nuisance baselines have no tuning and are trained only on outer training rows.
        for design, destination in ((arr["nuisance"], nuisance_pred),
                                     (np.column_stack([arr["nuisance"], arr["recent_evidence"]]), recent_pred)):
            coeff = np.linalg.lstsq(design[tr], y[tr], rcond=None)[0]
            destination[te] = design[te] @ coeff
        for region in ("FOF", "ADS"):
            # Equal fold weighting; at most one contiguous validation block is short.
            losses = np.mean(inner_mse[region], axis=0)
            best = np.flatnonzero(np.isclose(losses, losses.min(), rtol=1e-12, atol=1e-12))[-1]
            alpha = cfg.alphas[best]
            ix = selected[region]
            scaler = StandardScaler().fit(X[np.ix_(tr, ix)])
            model, ww = fit_lasso(scaler.transform(X[np.ix_(tr, ix)]), y[tr], alpha, cfg)
            predictions[region][te] = model.predict(scaler.transform(X[np.ix_(te, ix)]))
            if ww:
                warning_audit.append({"outer": outer, "region": region,
                                      "alpha": alpha, "warnings": ww})
            outer_record["regions"][region] = {
                "alpha": alpha, "candidate_alpha_inner_mean_mse": losses,
                "n_neurons": len(ix), "unit_ids": [arr["units"][j].unit_id for j in ix],
                "train_fr_hz": fr[ix], "train_scaler_mean": scaler.mean_,
                "train_scaler_scale": scaler.scale_, "coefs": model.coef_,
                "intercept": model.intercept_, "n_iter": model.n_iter_,
                "held_out_metrics": metric(y[te], predictions[region][te])}
        fold_audit.append(outer_record)
    assert np.all(fold_id >= 0) and all(np.all(np.isfinite(v)) for v in predictions.values())
    stem = Path(session.path).stem
    predframe = pd.DataFrame({"trial_id": arr["frame"].iloc[groups]["trial_id"].to_numpy(),
                              "source_row1": arr["frame"].iloc[groups]["source_row1"].to_numpy(),
                              "rat": session.rat, "session_id": session.session_id,
                              "outer_fold": fold_id, "bin_index0": arr["bin_id"],
                              "evidence_time_s": arr["time_s"],
                              "neural_window_start_s": arr["time_s"] - cfg.bin_s + cfg.lag_s,
                              "neural_window_end_s": arr["time_s"] + cfg.lag_s,
                              "duration_s": arr["duration"], "choice": arr["choice"],
                              "cumulative_click_difference": y,
                              "prediction_FOF": predictions["FOF"],
                              "prediction_ADS": predictions["ADS"],
                              "prediction_choice_time_nuisance": nuisance_pred,
                              "prediction_choice_time_recent_evidence": recent_pred})
    predpath = outdir / (stem + "_B2_predictions.csv.gz")
    predframe.to_csv(predpath, index=False, compression={"method": "gzip", "mtime": 0})
    foldpath = outdir / (stem + "_B2_folds.json")
    write_json(foldpath, fold_audit)
    summary = {"status": "computed", "analysis": "independent conservative B2 reanalysis",
               "rat": session.rat, "session_id": session.session_id,
               "source_path": str(session.path), "source_sha256": session.source_sha256,
               "config": asdict(cfg), "code_sha256": current_code_hashes(),
               "source_schema_audit": session.audit, "data_audit": arr["audit"],
               "regions": {r: evaluate_predictions(arr, predictions[r], cfg) for r in ("FOF", "ADS")},
               "controls": {"choice_time_nuisance": evaluate_predictions(arr, nuisance_pred, cfg),
                            "choice_time_recent_evidence": evaluate_predictions(arr, recent_pred, cfg)},
               "convergence_warnings": warning_audit,
               "artifacts": {"predictions": predpath.name,
                             "predictions_sha256": hashlib.sha256(predpath.read_bytes()).hexdigest(),
                             "fold_audit": foldpath.name,
                             "fold_audit_sha256": hashlib.sha256(foldpath.read_bytes()).hexdigest()},
               "elapsed_seconds": time.time() - start,
               "inference_ceiling": "stimulus decodability; no causal-use, T2 closure, T3, experience or valence claim"}
    write_json(outdir / (stem + "_B2_summary.json"), summary)
    return clean_json(summary)


def summarize_sessions(summaries, cfg):
    rows = []
    for s in summaries:
        if s.get("status") != "computed":
            continue
        for region in ("FOF", "ADS"):
            m = s["regions"][region]
            rows.append({"rat": s["rat"], "session_id": s["session_id"],
                         "region": region, **m["pooled"],
                         "within_choice_time_r": m["same_time_within_choice_centered"]["pearson_r"]})
    result = {"n_sessions_computed": sum(s.get("status") == "computed" for s in summaries),
              "n_sessions_failed": sum(s.get("status") != "computed" for s in summaries),
              "session_metrics": rows,
              "aggregation_rule": "equal-session mean within each rat, equal-rat mean across rats; no neuron/bin pseudoreplication"}
    if not rows:
        return result
    frame = pd.DataFrame(rows)
    measures = ["pearson_r", "r2", "rmse", "within_choice_time_r"]
    rats = frame.groupby(["rat", "region"], sort=True)[measures].mean().reset_index()
    result["rat_means"] = rats.to_dict("records")
    result["n_rats"] = rats["rat"].nunique()
    result["equal_rat_means"] = rats.groupby("region")[measures].mean().reset_index().to_dict("records")
    # Paired biological units are rats. Report intervals as descriptive with 5 rats.
    contrast = rats.pivot(index="rat", columns="region", values=measures)
    rng = np.random.default_rng(cfg.seed)
    comparisons = []
    for measure in measures:
        d = (contrast[measure]["FOF"] - contrast[measure]["ADS"]).dropna().to_numpy()
        if len(d):
            boot = np.mean(rng.choice(d, (2000, len(d)), replace=True), axis=1)
            comparisons.append({"metric": measure, "contrast": "FOF minus ADS",
                                "n_rats": len(d), "rat_contrasts": d,
                                "mean": d.mean(), "descriptive_cluster_bootstrap_95": np.quantile(boot, [.025, .975])})
    result["paired_rat_contrasts"] = comparisons
    result["uncertainty_limit"] = "Only five biological subjects expected; percentile intervals are descriptive and do not prove equivalence."
    return clean_json(result)


def self_check():
    cfg = Config()
    g = np.repeat(np.arange(30), 6)
    for tr, va in trial_folds(g, 5):
        assert not set(g[np.isin(g, tr)]).intersection(g[np.isin(g, va)])
    w = smoothing_weights(cfg)
    x = np.zeros(20)
    x[10] = 1
    smoothed = np.convolve(x, w, "full")[:len(x)]
    assert np.all(smoothed[:10] == 0)
    assert abs(w.sum() - 1) < 1e-12
    assert np.isclose(cfg.bin_s + cfg.lag_s, 0.15)
    assert metric([1, 2, 3], [1, 2, 3])["r2"] == 1
    print(json.dumps({"status": "software_checks_passed",
                      "checks": ["whole_trial_fold_disjointness", "causal_filter_no_future_smearing",
                                 "explicit_bin_plus_lag_endpoint", "metric_identity"],
                      "biological_data_executed": False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--session", type=Path, action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Reuse only computed files with identical source SHA256 and fixed config")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    if args.output is None or (not args.session and args.data is None):
        parser.error("Provide --output and either --data or --session")
    from rat_cells import load_session
    cfg = Config()
    args.output.mkdir(parents=True, exist_ok=True)
    paths = sorted(args.session or args.data.rglob("*.mat"))
    if not paths:
        write_json(args.output / "B2_status.json", {"status": "blocked_no_mat_files", "config": asdict(cfg)})
        raise SystemExit(2)
    summaries = []
    for path in paths:
        try:
            print(json.dumps({"event": "loading_session", "path": str(path)}), flush=True)
            session = load_session(path, load_neural=True)
            previous = args.output / (path.stem + "_B2_summary.json")
            if args.resume and previous.exists():
                old = json.loads(previous.read_text())
                if reusable_summary(old, session, cfg, args.output):
                    summaries.append(old)
                    print(json.dumps({"event": "reuse_verified_completed_session", "path": str(path)}), flush=True)
                    continue
            summary = decode_session(session, args.output, cfg)
            summaries.append(summary)
            print(json.dumps({"event": "session_complete", "rat": session.rat,
                              "session_id": session.session_id,
                              "metrics": {r: summary["regions"][r]["pooled"] for r in ("FOF", "ADS")}}), flush=True)
        except Exception as exc:
            import traceback
            failure = {"status": "failed", "path": str(path), "error_type": type(exc).__name__,
                       "error": str(exc), "traceback": traceback.format_exc(), "config": asdict(cfg)}
            summaries.append(failure)
            write_json(args.output / (path.stem + "_B2_failure.json"), failure)
            print(json.dumps({"event": "session_failed", "path": str(path), "error": str(exc)}), flush=True)
        write_json(args.output / "B2_run_checkpoint.json", summarize_sessions(summaries, cfg))
    aggregate = summarize_sessions(summaries, cfg)
    aggregate["config"] = asdict(cfg)
    aggregate["source_sessions"] = [{"path": s.get("source_path", s.get("path")),
                                     "sha256": s.get("source_sha256"), "status": s["status"]}
                                    for s in summaries]
    write_json(args.output / "B2_aggregate.json", aggregate)
    print(json.dumps({"event": "run_finished", "n_sessions": len(paths),
                      "n_computed": aggregate["n_sessions_computed"],
                      "n_failed": aggregate["n_sessions_failed"]}), flush=True)


if __name__ == "__main__":
    main()
