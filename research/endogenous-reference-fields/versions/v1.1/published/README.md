# TA-TR-2026-10 v1.1

Endogenous Reference Fields and Experiential Attribution: A Slow Shared-Modulation Hypothesis and Its Discriminating Tests

Hongju Liu · 2026-09-20 · DOI 10.5281/zenodo.22854705.
Revised version of v1.0 DOI 10.5281/zenodo.22852885; concept DOI 10.5281/zenodo.22852884. One paper, not an eleventh research paper. Not peer reviewed.

The PDF is generated from the accompanying Chinese Markdown, with an English title and abstract. CC BY 4.0 within author rights. Substantial AI assistance is disclosed; Hongju Liu assumes publication responsibility.

## Reproduce

Use Python 3.12 and NumPy 2.3.5 (the reviewed run used these versions). In a directory containing all deposited source files:

```bash
OPENBLAS_NUM_THREADS=1 python3 reproduce.py --output-dir rerun
```

This retrains all nine models (tasks T1/T2/T3, seeds 0/1/2), tests on seed 999, measures with seed 123, executes Appendix A, and compares all 171 numeric fields with original results.json. Expect about five minutes on the reviewed single-thread CPU; hardware varies. The output directory contains weights, results-rerun.json, reproduction.json, diagnostics.json and verification.log. Original results.json is never overwritten.

For a measurement-only check, extract computational-evidence.zip and use:

```bash
python3 reproduce.py --reuse-weights weights --output-dir measurement-check
```

The reviewed full retraining matched all 171 fields exactly and all nine test accuracies were 1.0. Numerical portability tolerances (rtol 1e-7, atol 1e-10) are comparison tolerances, not consciousness thresholds. The deposited reproduction.json records the full retraining; measurement-only verification is supplementary.

train.py is unchanged. measure.py changes only its executable entry point, default output filename, scientific-notation console display and clarifying comments. It preserves numerical computation. Historical rounded A coefficients remain in results for exact comparison; full coefficients are in diagnostics.json inside the evidence ZIP.

## Files

The package contains 18 explicitly manifested assets: PDF, Markdown, four Python scripts, original and rerun results, reproduction record, computational evidence ZIP, this README, method/source review, license, three citation formats, checksums, and manifest. manifest.json inventories content assets except itself and SHA256SUMS.txt to avoid circular hashes. SHA256SUMS.txt covers every other deposited file, including manifest.json. The repository EXPECTED-PUBLICATION.json separately covers every public file including SHA256SUMS.txt.

Do not infer machine consciousness, an exact zero, a complete ERF, or population-wide statistics from these small computational probes. Appendix A and Appendix C are different evidence types. See METHOD-AND-SOURCES.md and manuscript limitations.
