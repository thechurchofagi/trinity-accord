# R124-J executed artifacts
Start with [report](R124_Joint_Model_Report.md), [frozen protocol](PROTOCOL_FROZEN.md), [aggregate](aggregate.json), [independent checks](independent_result_checks.json), and [software checks](software_checks.json).

joint_decode.py is the actual executed decoder implementation; requirements.txt and environment.json pin the runtime. recover_cells.py documents source recovery. All twelve per-session feature NPZ files, model JSON.gz files, prediction CSV.gz files and summaries are retained. These are derived real-data artifacts, not sample or synthetic input. Original full MAT bytes are retrieved through the public archive and its pinned R122 identities.

From this directory, python3 joint_decode.py --data /absolute/path/to/Cells runs the full source-based fit on the verified archive members. Set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1 to reproduce the constrained runtime. The retained matrices and models allow R125 to run without another download or decoder fit.

The recovery and reconstruction scripts are preserved as history. They use the original scratch data location and require adapting that location on a new machine. First_Pass_11_Sessions_Aggregate.json and the failure logs remain historical; aggregate.json is the final twelve-session result. See SHA256SUMS for accepted artifact hashes.
