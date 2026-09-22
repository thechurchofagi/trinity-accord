# Reproducing the bounded study

Run `python3 audit.py --out audit-rerun` using Python 3.10 or later. No third-party Python packages are required. `checks.json` reports the actual run and `illustration.csv` contains stipulated, uncalibrated examples. Numeric checks are not empirical data or independent peer review.

The audit uses independently evaluated factor derivatives and numerical market roots in addition to algebraic checks. It does not formally verify the full manuscript.

Run `bash build.sh` with Pandoc, XeLaTeX, TeX Gyre Pagella and Noto Serif CJK SC available to rebuild a searchable PDF from the DOI-bearing Markdown. Binary identity across different toolchains is not promised. Review and cite the deposited exact PDF, not a locally rebuilt file.

Observed build tools:

{
  "pandoc": "pandoc 2.9.2.1",
  "xelatex": "XeTeX 3.141592653-2.6-0.999993 (TeX Live 2022/dev/Debian)"
}

The source Markdown carries the full mathematical equations. No revised file inherits the old v1.1 timestamp. Source and publication receipts remain in the repository version directory.
