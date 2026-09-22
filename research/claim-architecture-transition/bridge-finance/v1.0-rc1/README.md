# Public-upside bridge finance — working paper v1.0-rc1

**Title:** Financing the Automation Transition Without Pledging Subsistence: Public Upside Claims, Endogenous Prices, and Investment Limits

**Author:** Hongju Liu. **Date:** 22 September 2026.

Status: complete release candidate for working-paper criticism. Not externally peer reviewed, not a securities offering, not a journal acceptance, and not a certification of foundational priority. No new DOI or main-branch merge has been performed. This is a separate extension of the TA-TR-2026-14 research program; no published version is overwritten.

## Contents preserved in this branch

- `manuscript.md`: complete English manuscript, four propositions and nineteen numbered equations.
- `verify.py`: deterministic reproduction of analytical examples, clearing conditions, state-by-state resource accounts, convex payment design, and the investment-preserving issuance bound.
- `checks-summary.json`: executed results and digest of the complete generated results.
- `SOURCE-AUDIT.md`: primary-source reading scope and close predecessors.
- `RELEASE-CHECKPOINT.md`: final completed-work record and exact release artifact hashes.

## Reproduce the checks and English PDF

Use Python with NumPy and SciPy. The checked environment was Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0.

```sh
python -m pip install numpy==2.3.5 scipy==1.17.0
python verify.py
pandoc manuscript.md --from markdown+tex_math_dollars --pdf-engine=xelatex \
  -o Financing_the_Automation_Transition_v1.0-rc1.pdf
```

The PDF build additionally requires Pandoc, XeLaTeX, and the Liberation Serif font available locally. Fonts are not supplied with the release. The check script writes the complete `checks.json`. Numerical solver output or formatting can vary across versions; the mathematical tolerances, source, and tested environment are disclosed.

## Companion release archive

The author-facing archive contains fourteen files: the manuscript, 14-page English PDF, 3-page Chinese explanatory PDF and source, verification source and full output, build instructions, pinned Python requirements, source audit, release notes, PDF review record, and SHA-256 manifest.

The archive and PDFs were delivered as downloadable artifacts in the current research interaction. Binary PDFs and the complete archive are not uploaded into this source directory; this README does not claim otherwise. The complete English source and verification source were read back through GitHub, and their Git blob hashes matched the local release files exactly.

## Claim hierarchy

The exchange model proves a clearing-price frontier and a unique least-cost future-payment allocation under stated beneficiary preferences. A separate investment model establishes a trade-off between current transfers and private capital formation and derives an investment-floor limit. A conditional aggregate-demand diagnostic is not a full macroeconomic result or a measured multiplier.

Protecting the new instrument's payment cap does not by itself fund basic needs in every future state. A fixed debt and feasible insurance package with identical payments, access, enforcement and costs remains an equivalence benchmark. No claim is made that naming a new security creates new resources.

The original idea of drawing on a potentially abundant future to support present basic living was proposed by Hongju Liu. AI contributed substantially to literature review, formalization, derivation, checks, and writing. The release retains this distinction and the boundaries of the evidence.
