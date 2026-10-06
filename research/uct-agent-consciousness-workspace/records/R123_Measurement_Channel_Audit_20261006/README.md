# R123 — Measurement-channel and retained-data audit

Date: 2026-10-06. Continuation of R122, not a new paper release.

Read `R123_Report.md` and `NEXT_EXPERIMENT.md`. The two programs were executed in the current session. The CSV was retrieved through the GitHub connector and reconstructed locally; its Git blob SHA-1 and SHA-256 exactly match the pinned R122 file. No raw rat sessions were rerun or redownloaded in this round.

Reproduce with Python, NumPy, SciPy and pandas:

```bash
python measurement_channel_check.py
python retained_data_audit.py
```

`measurement_channel_results.json` is a synthetic measurement-null calibration, NOT biological data. `retained_data_audit_results.json` is a new exploratory aggregation of already computed R122 biological results, NOT a new neural fit. The prospective joint-model experiment in `NEXT_EXPERIMENT.md` has NOT been executed.

The result is a concrete qualification of the next mechanism test. It is not a completed T2 certificate, a major empirical breakthrough, an experience score, or independent validation of UCT C1.
