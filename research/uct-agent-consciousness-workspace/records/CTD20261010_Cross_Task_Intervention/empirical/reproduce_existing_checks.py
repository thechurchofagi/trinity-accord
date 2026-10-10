"""Reproduce the recorded source mapping and fitted-boundary diagnostics.

These are the same integrity and numerical diagnostics used in the analysis;
they are not additional hypothesis tests. No source files are modified.
Run after fit_count_clock.py to refresh the saved boundary diagnostics.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "results"
OUT.mkdir(exist_ok=True)

osf = pd.read_excel(BASE / "Experiment_3.xlsx", header=None)
mapping = {
    "Fig 6a": (2, slice(63, 66)),
    "Fig 6c": (2, slice(66, 69)),
    "Fig 6b": (3, slice(1, 22)),
    "Fig 6d": (3, slice(22, 43)),
}
crosscheck = {}
for sheet, (first_row, osf_columns) in mapping.items():
    publisher = pd.read_excel(
        BASE / "NatComm2026_SourceData.xlsx", sheet_name=sheet, header=None
    ).iloc[first_row:].to_numpy(dtype=float)
    author = osf.iloc[3:33, osf_columns].to_numpy(dtype=float)
    equal = bool(np.array_equal(publisher, author))
    crosscheck[sheet] = {
        "shape": list(publisher.shape),
        "exact_values_equal_to_OSF": equal,
        "max_abs_difference": float(np.max(np.abs(publisher - author))),
    }
    assert equal, f"Source values or mapping differ: {sheet}"
(OUT / "source_data_crosscheck.json").write_text(
    json.dumps(crosscheck, indent=2) + "\n"
)

fits = np.load(OUT / "count_model_fits.npz")
diagnostics = {}
for label, key in [("null", "nulltheta"), ("alternative", "alttheta")]:
    theta = fits[key]
    amplitude_upper = np.isclose(theta[:, :6], 14.0, atol=1e-4, rtol=0)
    center_edge = np.isclose(np.abs(theta[:, 6:12]), .75, atol=1e-4, rtol=0)
    diagnostics[label] = {
        "participants_with_upper_amplitude_bound": int(amplitude_upper.any(axis=1).sum()),
        "curves_at_upper_amplitude_bound": int(amplitude_upper.sum()),
        "participants_with_mu_bound": int(center_edge.any(axis=1).sum()),
    }
(OUT / "count_model_boundary_diagnostics.json").write_text(
    json.dumps(diagnostics, indent=2) + "\n"
)
print(json.dumps({"source_mapping": crosscheck, "boundary_diagnostics": diagnostics}, indent=2))
