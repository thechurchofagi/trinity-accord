# R125 executed frozen-map correspondence test
Read [report](R125_Report.md), [protocol](PROTOCOL_FROZEN.md), [certificate](T2_Certificate.csv), [status](STATUS.json), [aggregate](aggregate.json), and [source/concurrency ledger](source_and_concurrency_ledger.json).

state_correspondence.py is the executed primary and declared sensitivity implementation. increment_compatibility.py is the separately labeled post-concurrency compatibility calculation. All twelve transition CSV.gz files, endpoint output CSV.gz files, per-fold calibration JSON.gz files and session summaries are retained. R124-J supplies the preserved real feature matrices and frozen models.

Replay from this directory: python3 state_correspondence.py, then python3 increment_compatibility.py. Use the R124-J requirements.txt runtime and OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1. This replay does not need the original MAT archive or fit new decoders. Run generate_reports.py to regenerate the reports and exact summary figures from saved results. See SHA256SUMS for artifact integrity.

The selected observable candidate fails; latent biological kernels and C3 interventions remain unidentified. No experience label is present in this analysis.
