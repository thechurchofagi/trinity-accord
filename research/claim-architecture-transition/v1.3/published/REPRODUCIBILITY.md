# Reproduce the bounded study

Run `python3 audit.py --out rerun` with Python 3.10 or later; only the standard library is needed. Run `python3 symbolic_check.py` with SymPy 1.14.0 for optional exact derivative checks. Both are internal checks, not independent replication. Synthetic regimes.csv is not empirical data.

Build the DOI-bearing Markdown with Pandoc and XeLaTeX using TeX Gyre Pagella and Noto Serif CJK SC. `build.sh` gives the command. Binary identity across toolchains is not promised; cite the deposited exact PDF.

The repository version directory contains the hash-bound review gate and public-readback receipt. No v1.1/v1.2 timestamp is reused to attest to v1.3.
