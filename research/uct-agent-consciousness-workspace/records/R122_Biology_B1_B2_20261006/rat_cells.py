"""Independent, audited loader for Gupta et al. 2026 Cells MATLAB sessions.

Source contract: Brody-Lab/fof_ads_interactions commit
39d056fb12f688034b543d9ac8b7406a58ad0f77, helpers/physdata_preprocessing.py.
No author code is imported or executed. No experiential labels are constructed.
All source rows survive in Session.trials; `eligible` records analysis exclusions.
Raw click vectors use the author's explicit transformation x[1:] - x[0].
The omitted first click is the common stereo onset; its equality is audited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.io import loadmat, whosmat

AUTHOR_COMMIT = "39d056fb12f688034b543d9ac8b7406a58ad0f77"
SCHEMA_VERSION = "r122-gupta-cells-v1"


class SchemaError(ValueError):
    """Source schema or units were inconsistent; no silent reconstruction."""


@dataclass
class Unit:
    unit_id: str
    source_unit_row1: int
    region: str
    spikes_s: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    path: Path
    source_sha256: str
    rat: str
    session_id: str
    trials: pd.DataFrame
    audit: dict[str, Any]
    units: list[Unit] = field(default_factory=list)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (np.ndarray, list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def _text(x: Any) -> str:
    if isinstance(x, bytes):
        return x.decode("utf-8")
    a = np.asarray(x)
    if a.size == 1:
        x = a.reshape(-1)[0]
        if isinstance(x, bytes):
            return x.decode("utf-8")
        if isinstance(x, (float, np.floating)) and np.isfinite(x) and x == int(x):
            return str(int(x))
        return str(x)
    if a.dtype.kind in "US" and all(len(str(v)) == 1 for v in a.reshape(-1)):
        return "".join(str(v) for v in a.reshape(-1))
    raise SchemaError(f"Expected a scalar string, got shape {a.shape}")


def _scalar(x: Any, default: float = np.nan) -> float:
    try:
        a = np.asarray(x)
        return float(a.reshape(-1)[0]) if a.size == 1 else default
    except (TypeError, ValueError):
        return default


def _path(d: dict, dotted: str) -> Any:
    x = d
    for key in dotted.split("."):
        if not isinstance(x, dict) or key not in x:
            return None
        x = x[key]
    return x


def _column(x: Any, n: int, name: str, optional: bool = False) -> list:
    if x is None:
        if optional:
            return [None] * n
        raise SchemaError(f"Required field absent: {name}")
    if n == 1:
        # Click vectors and scalar fields are both single source trial objects.
        return [x]
    if isinstance(x, (list, tuple)) and len(x) == n:
        return list(x)
    a = np.asarray(x)
    if a.ndim == 0 or a.shape[0] != n:
        raise SchemaError(f"{name}: expected {n} source rows, got {a.shape}")
    return list(a)


def _metadata_text(d: dict, paths: list[str], name: str, fallback: str | None = None) -> tuple[str, dict]:
    values = {}
    skipped = {}
    for key in paths:
        x = _path(d, key)
        if x is not None:
            if type(x).__name__ == "MatlabOpaque":
                skipped[key] = "MATLAB opaque field not decoded; use explicit plain source metadata"
                continue
            a = np.asarray(x)
            if a.size > 1 and a.dtype.kind in "biufUS" and len(np.unique(a)) == 1:
                x = a.reshape(-1)[0]
            values[key] = _text(x)
    # Author files sometimes retain both sessiondate with dashes and sess_date without.
    canon = {v.replace("-", "") if name == "session_date" else v for v in values.values()}
    if len(canon) > 1:
        raise SchemaError(f"Conflicting {name} source metadata: {values}")
    if values:
        return next(iter(values.values())), {"parsed": values, "skipped": skipped}
    if fallback is None:
        raise SchemaError(f"No {name} metadata in {paths}")
    return fallback, {"explicit_fallback": fallback, "skipped": skipped}


def _click_vector(x: Any) -> tuple[np.ndarray, float, str | None]:
    try:
        a = np.asarray(x, dtype=float).reshape(-1)
    except (ValueError, TypeError):
        return np.empty(0), np.nan, "nonnumeric_clicks"
    if a.size == 0:
        return a, np.nan, "empty_click_field"
    if not np.all(np.isfinite(a)):
        return np.empty(0), np.nan, "nonfinite_clicks"
    if np.any(np.diff(a) < -1e-9):
        return np.empty(0), float(a[0]), "unsorted_clicks"
    return a[1:] - a[0], float(a[0]), None


def _trial_scalar_extras(trials: dict, n: int) -> dict[str, list]:
    """Preserve scalar nuisance fields without inferring any semantic labels."""
    out = {}
    for prefix in ("laser", "pharma"):
        sub = trials.get(prefix, {})
        if not isinstance(sub, dict):
            continue
        for key, val in sub.items():
            try:
                values = _column(val, n, f"Trials.{prefix}.{key}")
            except SchemaError:
                continue
            if all(np.asarray(v).size <= 1 for v in values):
                out[f"source_{prefix}_{key}"] = values
    for key in ("click_diff", "click_diff_hz", "stim_dur_s_theoretical", "is_frozen", "is_probe_trial", "gamma", "first_bup_stereo", "trial_id", "trialnum", "trial_num", "trial_idx"):
        if key in trials:
            out[f"source_{key}"] = _column(trials[key], n, f"Trials.{key}")
    return out


def _recorded_vectors(raw: Any, n_units: int, n_trials: int, audit: dict) -> list[np.ndarray | None]:
    if raw is None:
        audit["recorded_availability"] = "absent; no unrecorded intervals inferred"
        return [None] * n_units
    a = np.asarray(raw)
    audit["recorded_raw_shape"] = list(a.shape)
    # simplify_cells squeezes singleton axes; object arrays may wrap vectors.
    if a.dtype == object and a.size == n_units:
        rows = [np.asarray(v).reshape(-1) for v in a.reshape(-1)]
    elif a.ndim == 2 and a.shape == (n_units, n_trials):
        rows = list(a)
    elif a.ndim == 2 and a.shape == (n_trials, n_units) and n_units != n_trials:
        rows = list(a.T)
        audit["recorded_transposed"] = True
    elif n_units == 1 and a.size == n_trials:
        rows = [a.reshape(-1)]
    elif n_trials == 1 and a.size == n_units:
        rows = [np.asarray([v]) for v in a.reshape(-1)]
    else:
        raise SchemaError(f"recorded has unsupported shape {a.shape}; expected units×trials {(n_units,n_trials)}")
    out = []
    for row in rows:
        row = np.asarray(row, dtype=float).reshape(-1)
        if row.size != n_trials or not np.all(np.isin(row, [0, 1])):
            raise SchemaError("recorded must contain exactly 0/1 for each source unit/trial")
        out.append(row.astype(bool))
    audit["recorded_availability"] = "present; explicit source unit/trial flags"
    return out


def _load_units(d: dict, n_trials: int, source_name: str, audit: dict) -> list[Unit]:
    if "raw_spike_time_s" not in d or "regions" not in d or "penetration" not in d:
        raise SchemaError("Neural loading requires raw_spike_time_s, regions, penetration")
    ids = np.asarray(d["regions"]).reshape(-1)
    n_units = len(ids)
    spikes = _column(d["raw_spike_time_s"], n_units, "raw_spike_time_s")
    reg_struct = _path(d, "penetration.regions")
    if isinstance(reg_struct, dict):
        reg_struct = [reg_struct]
    elif reg_struct is None:
        raise SchemaError("penetration.regions missing")
    names = []
    for r in reg_struct:
        if not isinstance(r, dict) or "name" not in r:
            raise SchemaError("Each penetration.regions entry must have a name")
        name = np.asarray(r["name"])
        if name.size > 1:
            tokens = tuple(str(v) for v in name.reshape(-1))
            names.append("FOF" if tokens == ("M2", "FOF") else "|".join(tokens))
        else:
            names.append(_text(r["name"]))
    audit["source_region_names"] = names
    rec = _recorded_vectors(d.get("recorded"), n_units, n_trials, audit)
    units = []
    hemi = _path(d, "penetration.hemisphere")
    for i, (region_idx, st) in enumerate(zip(ids, spikes)):
        idx = _scalar(region_idx)
        if not np.isfinite(idx) or idx != int(idx) or not 1 <= idx <= len(names):
            raise SchemaError(f"Invalid MATLAB one-based region id for unit {i+1}: {region_idx}")
        original_region = names[int(idx)-1]
        region = {"DMS": "ADS", "M2": "FOF", "['M2' 'FOF']": "FOF"}.get(original_region, original_region)
        st = np.asarray(st, dtype=float).reshape(-1)
        nonfinite = np.flatnonzero(~np.isfinite(st))
        intervals = []
        if len(nonfinite):
            starts = nonfinite[np.r_[True, np.diff(nonfinite) > 1]]
            ends = nonfinite[np.r_[np.diff(nonfinite) > 1, True]]
            for begin, end in zip(starts, ends):
                intervals.append([float(st[begin-1]) if begin else -np.inf,
                                  float(st[end+1]) if end+1 < len(st) else np.inf])
        st = st[np.isfinite(st)]
        sorted_already = bool(np.all(np.diff(st) >= 0))
        if intervals and not sorted_already:
            # A time bracket is defensible only with monotonic finite timestamps.
            intervals = [[-np.inf, np.inf]]
        if not sorted_already:
            st = np.sort(st)
        metadata = {"original_region": original_region, "matlab_region_index": int(idx), "recorded_by_trial": rec[i], "spikes_sorted_in_source": sorted_already, "hemisphere": jsonable(hemi), "nonfinite_spike_count": len(nonfinite), "nonfinite_spike_intervals_s": intervals, "nonfinite_interval_semantics": "conservative bracketing interval between neighboring finite timestamps; not an observed recording mask"}
        for key in ("AP", "ML", "DV", "firing_rate", "ks_good", "frac_isi_violation", "unitCount"):
            if key in d:
                vals = _column(d[key], n_units, key)
                metadata[key] = jsonable(vals[i])
        units.append(Unit(f"{source_name}:unit_{i+1:05d}", i+1, region, st, metadata))
    audit["neural_unit_count"] = len(units)
    audit["neural_region_counts"] = pd.Series([u.region for u in units]).value_counts().to_dict()
    audit["nonfinite_spike_count"] = sum(u.metadata["nonfinite_spike_count"] for u in units)
    audit["units_with_nonfinite_spikes"] = sum(u.metadata["nonfinite_spike_count"] > 0 for u in units)
    return units


def load_session(path: str | Path, load_neural: bool = False) -> Session:
    path = Path(path)
    variables = ["Trials", "nTrials", "rat", "sessid", "sess_date", "rec"]
    if load_neural:
        variables += ["raw_spike_time_s", "regions", "penetration", "recorded", "hemisphere", "AP", "ML", "DV", "firing_rate", "ks_good", "frac_isi_violation", "unitCount"]
    try:
        d = loadmat(path, simplify_cells=True, variable_names=variables)
    except NotImplementedError as exc:
        raise SchemaError("MAT v7.3/HDF5 encountered; this source-audited scipy MAT loader does not silently reinterpret it") from exc
    if not isinstance(d.get("Trials"), dict):
        raise SchemaError("Expected top-level Trials scalar MATLAB structure")
    tr = d["Trials"]
    choice_source = tr.get("pokedR")
    if choice_source is None:
        raise SchemaError("Trials.pokedR absent")
    n = np.asarray(choice_source).size
    if "nTrials" in d and _scalar(d["nTrials"]) != n:
        raise SchemaError(f"nTrials metadata {_scalar(d['nTrials'])} differs from {n} choice rows")
    rat, rat_sources = _metadata_text(d, ["rec.rat", "rat", "Trials.rat"], "rat")
    date, date_sources = _metadata_text(d, ["rec.sessiondate", "sess_date", "Trials.sess_date"], "session_date", fallback="unknown")
    sessid, sess_sources = _metadata_text(d, ["sessid", "rec.sessid", "Trials.sessid"], "session_id", fallback=f"{rat}:{date}:{path.name}")
    sha = file_sha256(path)
    audit = {"schema_version": SCHEMA_VERSION, "author_commit": AUTHOR_COMMIT, "source_file": str(path), "source_sha256": sha, "source_bytes": path.stat().st_size, "source_trials_fields": sorted(tr), "source_stateTimes_fields": sorted(tr.get("stateTimes", {})), "rat_sources": rat_sources, "session_sources": sess_sources, "date_sources": date_sources, "n_source_trials": n, "click_transform": "onset-relative = raw[1:] - raw[0] separately per side; audit shared initial stereo click", "duration_definition": "Trials.stim_dur_s_actual; compare to stateTimes.clicks_off - clicks_on", "trial_identity_definition": "source filename plus source MATLAB row (1-based); never renumbered after exclusions", "ties": "retained in behavior fitting; only omitted from majority-target accuracy denominator", "warnings": []}
    columns = {name: _column(_path(tr, field), n, f"Trials.{field}") for name, field in {"choice": "pokedR", "violated": "violated", "trial_type": "trial_type", "duration_s": "stim_dur_s_actual", "clicks_on_s": "stateTimes.clicks_on", "clicks_off_s": "stateTimes.clicks_off", "left_raw": "leftBups", "right_raw": "rightBups"}.items()}
    columns["is_hit"] = _column(tr.get("is_hit"), n, "Trials.is_hit", optional=True)
    for output, source in (("cpoke_out_s", "stateTimes.cpoke_out"), ("laser_on_s", "stateTimes.laser_on"), ("laser_off_s", "stateTimes.laser_off")):
        columns[output] = _column(_path(tr, source), n, f"Trials.{source}", optional=True)
    extras = _trial_scalar_extras(tr, n)
    rows = []
    for i in range(n):
        row = {key: (_text(vals[i]).strip() if key == "trial_type" else _scalar(vals[i])) for key, vals in columns.items() if key not in ("left_raw", "right_raw")}
        row.update({"trial_id": f"{path.name}:row_{i+1:06d}", "source_row1": i+1, "rat": rat, "session_id": sessid})
        reasons = []
        row["author_eligible"] = row["trial_type"] == "a" and row["violated"] == 0
        if row["trial_type"] != "a":
            reasons.append("non_accumulation_trial")
        if row["violated"] != 0:
            reasons.append("violation_or_missing_flag")
        if row["choice"] not in (0, 1):
            reasons.append("nonbinary_or_missing_choice")
        duration = row["duration_s"]
        event_duration = row["clicks_off_s"] - row["clicks_on_s"]
        row["event_duration_s"] = event_duration
        if not np.isfinite(duration) or duration <= 0:
            reasons.append("nonpositive_or_missing_duration")
        if not np.isfinite(event_duration) or event_duration <= 0:
            reasons.append("nonpositive_or_missing_event_duration")
        row["duration_discrepancy_s"] = event_duration-duration
        left, first_left, left_err = _click_vector(columns["left_raw"][i])
        right, first_right, right_err = _click_vector(columns["right_raw"][i])
        for side, err in (("left", left_err), ("right", right_err)):
            if err:
                reasons.append(f"{side}_{err}")
        row["stereo_onset_difference_s"] = first_right-first_left
        if np.isfinite(first_left+first_right) and abs(first_left-first_right) > 1e-6:
            reasons.append("initial_stereo_time_mismatch")
        for side, clicks in (("left", left), ("right", right)):
            if len(clicks) and (np.min(clicks) < -1e-9 or np.max(clicks) > duration+1e-6):
                reasons.append(f"{side}_click_outside_stimulus")
            row[f"{side}_clicks_s"] = clicks
        row.update({"n_left": len(left), "n_right": len(right), "delta_clicks": len(right)-len(left), "tie": len(right)==len(left)})
        for key, vals in extras.items():
            row[key] = jsonable(vals[i])
        if "source_laser_isOn" in row:
            if _scalar(row["source_laser_isOn"]) != 0:
                reasons.append("laser_on_or_missing_flag")
        else:
            reasons.append("laser_status_unavailable")
        if "source_pharma_doseNG" in row and _scalar(row["source_pharma_doseNG"]) > 0:
            reasons.append("positive_pharmacological_dose")
        native_keys = [key for key in ("source_trial_id", "source_trialnum", "source_trial_num", "source_trial_idx") if key in row]
        row["native_trial_id"] = json.dumps({k: row[k] for k in native_keys}) if native_keys else None
        if "source_click_diff" in row:
            source_delta = _scalar(row["source_click_diff"])
            row["click_diff_discrepancy"] = row["delta_clicks"]-source_delta
            if np.isfinite(source_delta) and abs(row["click_diff_discrepancy"]) > 1e-8:
                reasons.append("computed_vs_source_click_diff_mismatch")
        row["eligible"] = not reasons
        row["exclusion_reason"] = "|".join(reasons)
        rows.append(row)
    df = pd.DataFrame(rows)
    # Previous means immediately previous SOURCE row, never previous retained trial.
    previous_valid = df.author_eligible.shift(1, fill_value=False) & df.choice.shift(1).isin([0,1]) & df.is_hit.shift(1).isin([0,1])
    previous_signed_choice = (2*df.choice.shift(1)-1).where(previous_valid, 0)
    df["previous_rewarded_choice"] = (previous_signed_choice*df.is_hit.shift(1).fillna(0)).where(previous_valid, 0)
    df["previous_error_choice"] = (previous_signed_choice*(1-df.is_hit.shift(1).fillna(0))).where(previous_valid, 0)
    df["previous_history_missing"] = (~previous_valid).astype(int)
    audit["n_author_eligible_trials"] = int(df.author_eligible.sum())
    audit["n_eligible_trials"] = int(df.eligible.sum())
    audit["n_source_ties"] = int(df.tie.sum())
    audit["n_eligible_ties"] = int(df.loc[df.eligible, "tie"].sum())
    audit["exclusion_counts_overlapping"] = {k: int(df.exclusion_reason.str.split("|").map(lambda xs: k in xs).sum()) for k in sorted({v for s in df.exclusion_reason for v in s.split("|") if v})}
    eligible = df.loc[df.eligible]
    audit["eligible_duration_range_s"] = [float(eligible.duration_s.min()), float(eligible.duration_s.max())] if len(eligible) else []
    audit["eligible_duration_discrepancy_max_abs_s"] = float(eligible.duration_discrepancy_s.abs().max()) if len(eligible) else None
    if len(eligible) and eligible.duration_discrepancy_s.abs().max() > 0.005:
        audit["warnings"].append("Actual duration differs from event duration by >5ms; preserve both and review before temporal interpretation")
    if not len(eligible):
        audit["warnings"].append("NO ELIGIBLE TRIALS: inspect source schema/exclusions before fitting")
    units = _load_units(d, n, path.name, audit) if load_neural else []
    return Session(path, sha, rat, sessid, df, audit, units)


def save_trial_table(df: pd.DataFrame, path: Path) -> None:
    """CSV JSON-encodes click vectors to preserve exact raw-derived trial rows."""
    out = df.copy()
    for key in ("left_clicks_s", "right_clicks_s"):
        out[key] = out[key].map(lambda x: json.dumps(jsonable(x), separators=(",", ":")))
    out.to_csv(path, index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("matfile", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--neural", action="store_true")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    session = load_session(args.matfile, load_neural=args.neural)
    save_trial_table(session.trials, args.out / "trials.csv")
    (args.out / "schema_audit.json").write_text(json.dumps(jsonable(session.audit), indent=2, allow_nan=False)+"\n")
    print(json.dumps(jsonable(session.audit), indent=2, allow_nan=False))
