# R122 reproducibility package — real rat B1/B2

This package contains the actual executed analyses, complete derived outputs, and independent checks for all 12 Gupta et al. recording sessions. Read the [main report](../R122_Real_Rat_B1_B2_and_Open_T2_Certificate_20261006.md) and [current handoff](../R122_Worklog_and_Handoff_20261006.md) first.

**Status:** B1/B2 executed and independently checked; primary B1 contrast inconclusive; modest/heterogeneous B2; T2 not closed. No B3 optogenetic trial replication and no experience labels.

## Input identity and retrieval

- Dataset: [Figshare version DOI 10.6084/m9.figshare.30369064.v1](https://doi.org/10.6084/m9.figshare.30369064.v1).
- File: `Cells.zip`, 1,929,137,550 bytes, stable endpoint `https://ndownloader.figshare.com/files/58773835`.
- MD5: `3b0ab5c964fb492ec36ee0f55a5d53de`.
- SHA-256: `e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494`.
- Author code: [Brody-Lab/fof_ads_interactions at 39d056fb12f688034b543d9ac8b7406a58ad0f77](https://github.com/Brody-Lab/fof_ads_interactions/tree/39d056fb12f688034b543d9ac8b7406a58ad0f77).

The source metadata snapshot, original successful transfer receipt, archive inventory and per-session hashes are preserved in `provenance/` and `R122_Input_Manifest.json`. The raw archive is public upstream; it is not duplicated in this Git directory. Allow approximately 7 GB for the archive plus its extracted MAT files, in addition to working memory and outputs.

From this directory, use a separate output location so the preserved primary results remain unchanged:

```bash
python download_cells.py --out /path/to/raw --extract-to /path/to/extracted
python b1_kernel.py --data /path/to/extracted/Cells_upload --out /path/to/rerun/b1_results
python b2_decode.py --data /path/to/extracted/Cells_upload --output /path/to/rerun/b2_results
```

`download_cells.py` verifies the fixed version's size, MD5 and SHA-256, supports a retained partial download, checks archive integrity and selects exactly the 12 safe session paths for extraction. For an existing archive, use `--out /path/to/raw --verify-only`; add `--extract-to` to extract it. The generalized downloader was verified against the completed archive. `provenance/download_cells_executed.py` preserves the original one-off retrieval script that actually acquired it.

## Environment and frozen analysis

Executed with Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, scikit-learn 1.8.0; plotting and numerical-library information is in `R122_Environment.json`. `requirements.txt` pins the main Python packages. Floating-point or BLAS differences may produce small numerical differences on other platforms; source identities and trial/fold definitions should remain exact.

Keep `rat_cells.py`, `b1_kernel.py`, and `R122_B1_Frozen_Protocol.md` adjacent. B1 hashes them into the output. B2 also saves loader/script hashes. The protocol files document local choices made before outcome fitting, including schema-only amendments. They are not externally preregistered. Do not modify an executed file and claim its historical output hash belongs to the changed code.

The independent verification scripts can be run against either preserved outputs or a new rerun:

```bash
python independent_raw_audit.py --data /path/to/extracted/Cells_upload --output /path/to/rerun/raw_audit.json
python independent_b1_checks.py --data /path/to/extracted/Cells_upload --results b1_results --output /path/to/rerun/b1_audit.json
python independent_analysis_checks.py --data /path/to/extracted/Cells_upload --results b2_results --output /path/to/rerun/b2_audit.json
```

These were already executed successfully for the checkpoint. Routine reading or saving does not require another analysis run.

## Artifact map

| Path | Purpose |
|---|---|
| `R122_B1_Report.md`, `R122_B2_Real_Data_Results.md` | Full methods, results, negative results and limits |
| `R122_B1_Frozen_Protocol.md`, `B2_PROTOCOL_FROZEN.md` | Local pre-fit method specifications |
| `rat_cells.py` | Source-aware MATLAB loader; preserves rows, raw clocks and missing-data flags |
| `b1_kernel.py`, `b2_decode.py` | Actual executed primary estimators |
| `b1_results/` | All original behavioral rows/exclusions, OOF predictions, kernels, full JSON, initial manifest and figures |
| `b2_results/` | All OOF time-bin predictions, nested trial memberships, selected units, scalers, coefficients, source audits and aggregate results |
| `schema_scan/`, `schema_a294/` | Preliminary schema-only inspections, retained as such |
| `independent_*.py`, `independent_*.json`, `independent_review.md` | Separate raw/arithmetic/method audit and its scope |
| `R122_*Ledger.json`, `R122_Primary_Methods_and_T2_Audit.md` | Exact sources, source hashes, actual reading scope and failed retrievals |
| `R122_T2_Certificate.csv`, `.json` | C0–C6 evidence vector with explicit remaining gaps |
| `R122_Research_Status.json`, `R122_Input_Manifest.json` | Machine-readable research status and input identity |
| `R122_B2_Execution_Manifest.json` | Primary B2 artifact hashes and coverage |
| `figures/`, `figures/plot_r122_summary.py` | Summary figure rendered only from saved results |
| `provenance/`, `b1_run.log`, `B2_run.log` | Original retrieval and execution records |
| `SHA256SUMS.txt` | Package file integrity manifest; excludes itself |

Original scratch paths inside execution JSON/logs are historical provenance, not required installation paths. Source basenames and explicit `--data`, `--results` arguments make reruns portable. Detailed original row identities are retained after exclusions. Large raw data and the copyrighted article PDF remain at their cited upstream sources; no generated experiential labels or synthetic replacements are included.

## Interpretation ceiling

B1 predicts the animal's observed choice; its accuracy is not animal task accuracy. B2 decodes a physical stimulus statistic; neither its predictive R² nor its within-choice/time residual correlation identifies a causally used accumulator state. R117's artificial state-noise R² has a different estimand and must not be compared as a relative intelligence or experience score.

The archive has no laser-on trials. B3 remains unreplicated. T2 requires transition and port-specific intervention correspondence; T3/G4, phenomenal labels, valence/fear, subject boundaries and external UCT C1/U1 validation remain unestablished.
