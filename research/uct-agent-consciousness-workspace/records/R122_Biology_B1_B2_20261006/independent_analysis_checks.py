#!/usr/bin/env python3
"""Independent R122 B2 output/clock/fold audit, with no model refitting.

All saved prediction targets are checked directly against raw MAT click arrays.
Two sessions additionally check the exact neural rate and saved readout math.
This validates arithmetic/provenance, not consciousness or a biological mechanism.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_summary(path, data):
    s = json.loads(path.read_text())
    output = path.parent
    predpath, foldpath = [output / s["artifacts"][k] for k in ("predictions", "fold_audit")]
    assert sha(predpath) == s["artifacts"]["predictions_sha256"]
    assert sha(foldpath) == s["artifacts"]["fold_audit_sha256"]
    p = pd.read_csv(predpath)
    folds = json.loads(foldpath.read_text())
    rawpath = data / Path(s["source_path"]).name
    t = loadmat(rawpath, simplify_cells=True, variable_names=["Trials"])["Trials"]
    lag, dt = s["config"]["lag_s"], s["config"]["bin_s"]
    target_checks = 0
    for row1, g in p.groupby("source_row1", sort=False):
        i = int(row1)-1
        left = np.asarray(t["leftBups"][i], dtype=float).reshape(-1)
        right = np.asarray(t["rightBups"][i], dtype=float).reshape(-1)
        left, right = left[1:]-left[0], right[1:]-right[0]
        ends = (g.bin_index0.to_numpy()+1)*dt
        # Direct comparisons, no reused cumulative-target implementation.
        truth = np.array([np.count_nonzero(right < e)-np.count_nonzero(left < e) for e in ends])
        assert np.array_equal(truth, g.cumulative_click_difference.to_numpy())
        assert np.allclose(g.neural_window_end_s, ends+lag, atol=1e-12, rtol=0)
        assert np.allclose(g.neural_window_start_s, ends-dt+lag, atol=1e-12, rtol=0)
        assert np.all(g.neural_window_end_s <= float(t["stim_dur_s_actual"][i])+1e-8)
        assert g.outer_fold.nunique() == 1
        assert np.all(g.choice == int(t["pokedR"][i]))
        target_checks += len(g)
    all_test = []
    for fold in folds:
        train, test = set(fold["train_trial_ids"]), set(fold["test_trial_ids"])
        assert not train.intersection(test)
        observed = set(p.loc[p.outer_fold == fold["fold"], "trial_id"])
        assert observed == test
        for inner in fold["inner_folds"]:
            it, iv = set(inner["train_trial_ids"]), set(inner["validation_trial_ids"])
            assert it <= train and iv <= train and not it.intersection(iv)
            assert not (it | iv).intersection(test)
        assert fold["regions"]["FOF"]["n_neurons"] == fold["regions"]["ADS"]["n_neurons"]
        all_test.extend(test)
    assert len(all_test) == len(set(all_test)) == p.trial_id.nunique()
    max_metric_error = 0.0
    for region in ("FOF", "ADS"):
        y = p.cumulative_click_difference.to_numpy()
        pred = p[f"prediction_{region}"].to_numpy()
        expected = {"pearson_r": float(np.corrcoef(y, pred)[0, 1]),
                    "r2": float(1-np.sum((pred-y)**2)/np.sum((y-y.mean())**2)),
                    "rmse": float(np.sqrt(np.mean((pred-y)**2)))}
        for key, value in expected.items():
            delta = abs(value-s["regions"][region]["pooled"][key])
            assert delta < 1e-10
            max_metric_error = max(max_metric_error, delta)
    return {"session": rawpath.name, "n_trials": p.trial_id.nunique(),
            "n_target_rows_checked": target_checks, "outer_folds": len(folds),
            "nested_trial_disjointness": True, "matched_outer_unit_counts": True,
            "artifact_hashes_match": True, "max_saved_metric_error": max_metric_error,
            "source_of_target_check": "direct raw MAT click-array comparisons"}


def manual_neural_check(path, data):
    import b2_decode
    from rat_cells import load_session
    s = json.loads(path.read_text())
    rawpath = data / Path(s["source_path"]).name
    session = load_session(rawpath, load_neural=True)
    arr = b2_decode.build_arrays(session, b2_decode.Config())
    raw = loadmat(rawpath, simplify_cells=True,
                  variable_names=["Trials", "raw_spike_time_s"])
    p = pd.read_csv(path.parent / s["artifacts"]["predictions"])
    assert len(p) == len(arr["y"])
    fold = json.loads((path.parent / s["artifacts"]["fold_audit"]).read_text())[0]
    dt, lag, sigma = 0.05, 0.1, 0.075
    k = int(np.ceil(4*sigma/dt))
    weights = np.exp(-0.5*(np.arange(k+1)*dt/sigma)**2)
    weights /= weights.sum()
    rows = np.unique(np.linspace(0, len(p)-1, 21).astype(int))
    units = np.unique(np.linspace(0, len(arr["units"])-1, 9).astype(int))
    max_rate_error = 0.0
    for row in rows:
        src = int(p.iloc[row].source_row1)-1
        onset = float(raw["Trials"]["stateTimes"]["clicks_on"][src])
        b = int(p.iloc[row].bin_index0)
        for col in units:
            unit = arr["units"][col]
            spikes = np.asarray(raw["raw_spike_time_s"][unit.source_unit_row1-1], dtype=float).reshape(-1)
            spikes = spikes[np.isfinite(spikes)]
            expected = 0.0
            for j, w in enumerate(weights):
                # Independent direct interval count for each causal tap.
                a = onset+lag+(b-j)*dt
                z = onset+lag+(b-j+1)*dt
                expected += w*np.count_nonzero((spikes >= a)&(spikes < z))/dt
            err = abs(expected-arr["X"][row, col])
            assert err < 1e-10
            max_rate_error = max(max_rate_error, err)
    groups = arr["frame"].iloc[arr["groups"]].trial_id.to_numpy()
    train = np.isin(groups, fold["train_trial_ids"])
    test = np.isin(groups, fold["test_trial_ids"])
    idmap = {u.unit_id: j for j, u in enumerate(arr["units"])}
    max_scaler_error = 0.0
    max_readout_error = 0.0
    for region in ("FOF", "ADS"):
        r = fold["regions"][region]
        cols = [idmap[u] for u in r["unit_ids"]]
        tr = arr["X"][train][:, cols]
        mean, scale = np.mean(tr, axis=0), np.std(tr, axis=0)
        scale[scale == 0] = 1
        max_scaler_error = max(max_scaler_error, float(np.max(np.abs(mean-r["train_scaler_mean"]))),
                               float(np.max(np.abs(scale-r["train_scaler_scale"]))))
        assert max_scaler_error < 1e-10
        manual = ((arr["X"][test][:, cols]-mean)/scale) @ np.asarray(r["coefs"])+r["intercept"]
        stored = p.loc[test, f"prediction_{region}"].to_numpy()
        err = float(np.max(np.abs(manual-stored)))
        assert err < 1e-8
        max_readout_error = max(max_readout_error, err)
    return {"session": rawpath.name, "manual_neural_rate_checks": len(rows)*len(units),
            "max_rate_error": max_rate_error, "first_outer_fold_scaler_recomputed_from_training_only": True,
            "max_scaler_error": max_scaler_error, "max_saved_readout_error": max_readout_error,
            "n_first_fold_heldout_neural_rows": int(test.sum())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    summaries = sorted(args.results.glob("*_B2_summary.json"))
    results = [audit_summary(path, args.data) for path in summaries]
    # First two source sessions cover raw NaN handling and missing-exit metadata.
    neural = [manual_neural_check(path, args.data) for path in summaries[:2]]
    here = Path(__file__).resolve().parent
    report = {"status": "passed", "analysis_scope": "B2 arithmetic/clock/output provenance only; no refitting",
              "code_sha256": {n: sha(here/n) for n in
                  ["b2_decode.py", "rat_cells.py", "independent_analysis_checks.py"]},
              "all_session_checks": results, "manual_neural_checks": neural,
              "total_target_rows_checked": sum(x["n_target_rows_checked"] for x in results)}
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ["all_session_checks"]}, indent=2))


if __name__ == "__main__":
    main()
