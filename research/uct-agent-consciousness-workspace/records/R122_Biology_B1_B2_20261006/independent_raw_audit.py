#!/usr/bin/env python3
"""Independent raw-schema/timestamp audit; does not import the analysis loader.

Only finite neighboring times are reported for nonfinite spike runs. Their
causal provenance is not inferred. Overlap counts use a deliberately broad
clicks_on-0.3 s through clicks_off window and do not label missing spikes zero.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def scalar(x):
    a = np.asarray(x)
    return float(a.reshape(-1)[0]) if a.size == 1 else float("nan")


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [clean(v) for v in x]
    if isinstance(x, np.generic):
        return clean(x.item())
    if isinstance(x, float) and not np.isfinite(x):
        return None
    return x


def audit_file(path):
    variables = ["Trials", "nTrials", "recorded", "penetration", "regions",
                 "hemisphere", "raw_spike_time_s", "rec"]
    d = loadmat(path, simplify_cells=True, variable_names=variables)
    tr, n = d["Trials"], int(d["nTrials"])
    state = tr["stateTimes"]
    basic = ((tr["trial_type"] == "a") & (tr["violated"] == 0)
             & np.isin(tr["pokedR"], [0, 1]))
    onset = np.asarray(state["clicks_on"], dtype=float)
    offset = np.asarray(state["clicks_off"], dtype=float)
    duration = np.asarray(tr["stim_dur_s_actual"], dtype=float)
    temporal = basic & np.isfinite(onset) & np.isfinite(offset) & (duration > 0)
    info = {"source_file": path.name, "n_trials": n,
            "basic_eligible": int(basic.sum()),
            "trial_fields_aligned": all(np.size(tr[k]) == n for k in
                ["pokedR", "violated", "trial_type", "stim_dur_s_actual", "click_diff"]),
            "laser_isOn_unique": np.unique(tr["laser"]["isOn"]),
            "cpoke_out_missing_basic_eligible": int((~np.isfinite(state["cpoke_out"][basic])).sum()),
            "hemisphere_agrees": str(d["hemisphere"]) == str(d["penetration"]["hemisphere"]),
            "event_duration_difference_max_abs_s": float(np.max(np.abs((offset-onset-duration)[temporal]))),
            "raw_clock_extent_s": [float(np.nanmin(onset)), float(np.nanmax(offset))],
            "click_checks": {}, "units": []}
    stereo_mismatch, delta_mismatch, missing_click, unsorted_click = [], [], [], []
    outside = []
    for i in np.flatnonzero(basic):
        left, right = [np.asarray(tr[k][i], dtype=float).reshape(-1)
                       for k in ("leftBups", "rightBups")]
        if not left.size or not right.size or not np.isfinite(left).all() or not np.isfinite(right).all():
            missing_click.append(int(i+1))
            continue
        if np.any(np.diff(left) < 0) or np.any(np.diff(right) < 0):
            unsorted_click.append(int(i+1))
        if abs(left[0]-right[0]) > 1e-6:
            stereo_mismatch.append(int(i+1))
        eleft, eright = left[1:]-left[0], right[1:]-right[0]
        if len(eright)-len(eleft) != scalar(tr["click_diff"][i]):
            delta_mismatch.append(int(i+1))
        if any(np.any((x < -1e-9) | (x > duration[i]+1e-6)) for x in [eleft, eright]):
            outside.append(int(i+1))
    info["click_checks"] = {"stereo_time_mismatch_rows1": stereo_mismatch,
        "delta_count_mismatch_rows1": delta_mismatch,
        "missing_nonfinite_rows1": missing_click, "unsorted_rows1": unsorted_click,
        "outside_actual_duration_rows1": outside}
    record = d.get("recorded")
    if record is not None:
        r = np.stack([np.asarray(x, dtype=np.int64).reshape(-1) for x in record])
        info["recorded"] = {"present": True, "shape": list(r.shape),
            "expected_shape": [len(d["regions"]), n],
            "all_binary": bool(np.isin(r, [0, 1]).all()),
            "false_count": int(np.count_nonzero(r == 0))}
    else:
        info["recorded"] = {"present": False}
    for j, spike in enumerate(d["raw_spike_time_s"]):
        x = np.asarray(spike, dtype=float).reshape(-1)
        finite = x[np.isfinite(x)]
        bad = np.flatnonzero(~np.isfinite(x))
        unit = {"unit_row1": j+1, "region_index1": int(d["regions"][j]),
                "n_raw_entries": len(x), "n_nonfinite": len(bad),
                "finite_monotone": bool(np.all(np.diff(finite) >= 0)),
                "finite_extent_s": [float(finite[0]), float(finite[-1])] if len(finite) else [],
                "nonfinite_runs": []}
        if len(bad):
            starts = np.r_[0, np.flatnonzero(np.diff(bad) > 1)+1]
            ends = np.r_[starts[1:], len(bad)]
            for a, b in zip(starts, ends):
                lo, hi = int(bad[a]), int(bad[b-1])
                before = x[lo-1] if lo > 0 else -np.inf
                after = x[hi+1] if hi+1 < len(x) else np.inf
                overlap = temporal & (offset >= before) & (onset-0.3 <= after)
                unit["nonfinite_runs"].append({"source_index0_start": lo,
                    "source_index0_end": hi, "count": hi-lo+1,
                    "finite_neighbor_bracket_s": [before, after],
                    "broad_window_overlap_rows1": np.flatnonzero(overlap)+1})
        info["units"].append(unit)
    sync = d.get("rec", {}).get("sync", {})
    info["sync_metadata"] = {"present": bool(sync), "fields": list(sync),
                             "params": clean(sync.get("params", {}))}
    for key in ("tnts_imec_s", "tnts_bcontrol_s"):
        if key in sync:
            x = np.asarray(sync[key], dtype=float).reshape(-1)
            info["sync_metadata"][key] = {"n": len(x),
                "nonfinite_count": int((~np.isfinite(x)).sum()),
                "nonincreasing_pairs": int((np.diff(x) <= 0).sum())}
    ia = sync.get("imec_tnt_timestamps", {}).get("timestamps")
    ba = sync.get("bcontrol_tnt_timestamps", {}).get("timestamps")
    if ia is not None and ba is not None:
        ia, ba = np.asarray(ia).reshape(-1), np.asarray(ba).reshape(-1)
        info["sync_metadata"]["trial_number_codes"] = {
            "imec_only": np.setdiff1d(ia, ba),
            "bcontrol_only": np.setdiff1d(ba, ia),
            "same_ordered_codes": np.array_equal(ia, ba),
            "pairing_warning": "Equal-length clock arrays need not have matching code identities; do not pair by array index."}
    info["summary"] = {"n_units": len(info["units"]),
        "n_units_with_nonfinite": sum(u["n_nonfinite"] > 0 for u in info["units"]),
        "n_nonfinite_entries": sum(u["n_nonfinite"] for u in info["units"]),
        "n_runs": sum(len(u["nonfinite_runs"]) for u in info["units"]),
        "n_runs_overlapping_broad_window": sum(bool(len(r["broad_window_overlap_rows1"]))
             for u in info["units"] for r in u["nonfinite_runs"]),
        "n_nonmonotone_finite_units": sum(not u["finite_monotone"] for u in info["units"])}
    return clean(info)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    results = []
    for path in sorted(args.data.glob("*.mat")):
        result = audit_file(path)
        results.append(result)
        print(json.dumps({"file": path.name, **result["summary"]}), flush=True)
    report = {"independent_of_analysis_loader": True,
              "nonfinite_provenance": "Unknown. Brackets report finite neighbors in original vector order; no causal cause assigned.",
              "preliminary_diagnostic_failures": [
                  "Initial exploratory code assumed recorded existed; KeyError on A294.",
                  "Initial exploratory object-array summation retained unitwise vector; uint8 subtraction overflow on >255 units. Corrected by explicit int64 stack.",
                  "scipy.io.whosmat fails TypeError on A294 opaque MATLAB variables; selected-variable loadmat works."],
              "sessions": results}
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
