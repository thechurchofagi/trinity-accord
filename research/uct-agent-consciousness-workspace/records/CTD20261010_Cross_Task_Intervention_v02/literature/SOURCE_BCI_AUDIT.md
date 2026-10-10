# Source BCI likelihood and information-criterion audit

**Status:** completed numerical reconciliation of the released fitted parameters, raw counts, and the publisher's Figure S2 source data. This is an audit of saved fits; it does not certify the original optimizer's global optima or reconstruct an unrecorded execution history. Date: 2026-10-10.

## Main finding

The released model-prediction and negative-log-likelihood functions reproduce all 30 participants' saved objective values to numerical precision. A double sign change in the comparison portion of the public MATLAB script subsequently treats positive negative log likelihoods as log likelihoods. The resulting, incorrect-sign information-criterion differences reproduce the publisher's complete 30-row Figure S2 source-data vectors to numerical precision. Correcting this arithmetic changes the reported numbers and some participant-level preferences, **but retains the aggregate preference for the BCI-Sigma model**.

Thus the evidence supports a specific, traceable arithmetic discrepancy. It does not support saying that the paper's aggregate model preference was reversed, that the stimulus effect disappeared, or that the fitted sensory parameter has thereby been identified as a physiological sensory-noise component.

## 1. Source and data provenance

The audited primary study is D'Angelo, M., Lanfranco, R. C., Chancel, M., & Ehrsson, H. H. (2026). *Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals*. Nature Communications, 17, 53. https://doi.org/10.1038/s41467-025-67657-w .

Primary public code was downloaded without modification; the archived copies are in `code_archive/` and download receipts are in `code_archive/retrieval.json`. Stable OSF URLs, rather than expiring redirected object-store URLs, should be used in a publication.

| File | Stable original URL | SHA-256 |
|---|---|---|
| Master_BCI.m | https://osf.io/download/pnmsx/ | `06e5122cbe1ed7852eb3b3a429ab984125244f76edc503ed32ac33dc3195bb9d` |
| modelprediction_log_BCI.m | https://osf.io/download/uk2en/ | `fd06e42e6e61882475d6d6b4ff10321bd812d7e6c4038b7467dff89f6e8ff814` |
| NLL_BCI_tACS_Psame.m | https://osf.io/download/bgxn6/ | `21d8f3880d97e1b1e5b60d67d4f2febb2f7fe05cb681e6a24f5e952bf4a0fa9b` |
| NLL_BCI_tACS_Sigma.m | https://osf.io/download/vnfbx/ | `76f00bd51c4f880a03ae024597cafa9bcff4c5b64a9086bde4d0510a7435edc9` |
| NLL_BCI_EEG.m | https://osf.io/download/32k54/ | `43bd2c6df3c7c860496efeb35cd4666178b06ee9eb251ccaee13110bce8532fa` |
| ReadMe_BCI.txt | https://osf.io/download/u5anz/ | `442b5cf7e81545edab00e7680af8a2a23ca3a28fa2b4a2881d16c77f8a3a921e` |
| Experiment_3_Computational_modelling.xlsx | https://osf.io/download/yc4k2/ | `32e58a814b7d33f52f3dc994a753715d4ddfa21c8ec7424b80ebef43c6d560e4` |

The portable raw count workbook is `../empirical/inputs/Experiment_3.xlsx`, SHA-256 `d3b2fef22f077788e5299dedb68737d453c09b005d9360bab8dfbe6c35852bc9`. The publisher source-data workbook is `../empirical/inputs/NatComm2026_SourceData.xlsx`, SHA-256 `3202d68439ad502ff95e7a4d59535a4e8ff9072d5c6a76b5aebf7dde90228a82`. The parameter workbook is retained alongside them in `../empirical/inputs/Experiment_3_Computational_modelling.xlsx`.

The publisher supplement is available at https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM1_ESM.pdf . **PDF page 4** contains Figure S2 and Table S1. Its extracted text is `NatComm2026_supplement.txt`.

## 2. Exact observer family being audited

Let sigma be the positive internal-noise scale, S the stimulus-prior scale, pi the common-cause prior, lambda the total unbiased lapse probability, and s the signed stimulus onset asynchrony. The released predictor computes

\[
K=\frac{2\sigma^2(\sigma^2+S^2)}{S^2}
\left[\log\frac{\pi}{1-\pi}+\frac12\log\frac{\sigma^2+S^2}{\sigma^2}\right].
\]

For K below zero it sets the non-lapse common-cause response probability to zero. Otherwise it evaluates

\[
q(s)=\Phi\!\left(\frac{\sqrt K-s}{\sigma}\right)
-\Phi\!\left(\frac{-\sqrt K-s}{\sigma}\right),\qquad
p(s)=\lambda/2+(1-\lambda)q(s).
\]

Both tACS likelihood helpers return

\[
\mathrm{NLL}=-\sum_j\{y_j\log p_j+(10-y_j)\log(1-p_j)\}.
\]

These are positive negative log likelihoods. The binomial combinatorial terms are omitted consistently; this omission cancels in comparisons on the same response cells.

### Parameter bookkeeping

| Model | Released parameter vector | Nominally free |
|---|---|---:|
| BCI-Sigma | pi_O, pi_S, log sigma_low, log sigma_sham, log sigma_high, log S, lambda | 6 |
| BCI-Psame | pi_O_low, pi_O_sham, pi_O_high, pi_S_low, pi_S_sham, pi_S_high, log sigma, log S, lambda | 8 |

The released bounds fix log S to `log(std([-400,-200,-100,100,200,400]))`, using MATLAB's sample-SD convention. This is approximately 5.6692860389, corresponding to S approximately 289.827534924 ms. The script counts the fixed entry in each vector as a parameter and therefore uses 7 versus 9 rather than 6 versus 8. **The difference remains minus 2, so this shared extra parameter does not explain any discrepancy in Delta AIC or Delta BIC.** Absolute IC values would receive a common offset.

### Workbook mapping checked against the likelihood

In `Experiment_3.xlsx`, worksheet `Foglio1`, rows 4–33 and columns B–AQ provide 30 rows of 42 yes counts. Each row is reshaped into six curves in this order: ownership-low, ownership-sham, ownership-high, simultaneity-low, simultaneity-sham, simultaneity-high. Within a curve, SOAs are minus 400, minus 200, minus 100, zero, plus 100, plus 200, plus 400 ms. Each count has denominator 10, giving 420 trials per participant.

In `Experiment_3_Computational_modelling.xlsx`, the left-side blocks of `Foglio1` contain the fitted log-scale parameters and NLL: Psame rows 2–31, parameters B:J and NLL K; Sigma rows 36–65, parameters B:H and NLL I. Right-side blocks duplicate quantities with exponentiated scales and were not substituted for the log-scale inputs. A header in the first block appears to label the first parameter as simultaneity, whereas the helper maps it to ownership. We retained the released numerical order, and the objective-value reconstruction confirms the helper's ordering. No participant permutation or fit matching was used.

## 3. Error chain in the released script

Line references here refer to the archived `Master_BCI.m` hash above.

1. Lines 218–219 negate the positive saved NLL values, correctly obtaining log likelihoods.
2. Line 221 combines those values into a variable named `NLL_allmodels`.
3. Line 222 negates them again, leaving **positive NLLs** in a variable named `LL_allmodels`.
4. Lines 238–239 evaluate `2*k - 2*LL_allmodels` and `log(n)*k - 2*LL_allmodels`. Given step 3, these subtract twice the positive NLL, whereas standard AIC and BIC add it.

For the convention Delta = Sigma minus Psame, and d = NLL_Sigma minus NLL_Psame, the resulting equations are

\[
\begin{array}{lll}
\Delta\mathrm{AIC}_{\rm released}=-4-2d,&\quad&
\Delta\mathrm{AIC}_{\rm corrected}=-4+2d,\\
\Delta\mathrm{BIC}_{\rm released}=-2\log(420)-2d,&&
\Delta\mathrm{BIC}_{\rm corrected}=-2\log(420)+2d.
\end{array}
\]

Negative differences favor Sigma throughout this audit.

## 4. Numerical reconciliation

`reconcile_source_bci.py` independently implements the released probability function in Python, evaluates the original saved parameters on the public counts, and compares both IC formulas with the publisher's `Fig S2` worksheet. It performs no optimization.

| Check | Maximum absolute discrepancy |
|---|---:|
| Recomputed versus saved Sigma NLL, 30 participants | 6.537e-13 |
| Recomputed versus saved Psame NLL, 30 participants | 1.994e-9 |
| Published Figure S2 Delta AIC versus released wrong-sign formula | 2.487e-14 |
| Published Figure S2 Delta BIC versus released wrong-sign formula | 4.796e-14 |
| Published Figure S2 Delta AIC versus corrected formula | 29.8210491064 |
| Published Figure S2 Delta BIC versus corrected formula | 29.8210491064 |

The slightly larger Psame discrepancy is still at numerical precision for the saved values; some fitted priors are close to one. The agreement of the entire publisher vector with the script is much stronger evidence than a static code inspection alone.

| Quantity, summed over 30 participants | Released/publisher calculation | Corrected saved-fit calculation |
|---|---:|---:|
| NLL_Sigma | 5138.960411207294 | unchanged |
| NLL_Psame | 5142.889991070781 | unchanged |
| Delta AIC | -112.140840273026 | -127.859159726974 |
| Delta BIC | -354.556122949671 | -370.274442403619 |

Table S1's printed raw sums, minus 112 and minus 355, match the released wrong-sign quantities after rounding. The corrected aggregate preference remains Sigma.

At the individual level, lower raw NLL favors Sigma for 14 of 30 participants. With the parameter penalty included, the publisher's vector favors Sigma for 22 of 30 under AIC and 30 of 30 under BIC; the corrected saved-fit vectors favor Sigma for 29 of 30 under both. AIC signs change for participants 1, 5, 12, 14, 20, 22, 25, 27, and 29; the BIC sign changes for participant 27. These shifts illustrate why retaining the aggregate winner does not make the arithmetic discrepancy immaterial.

Per-participant evidence is in `source_bci_reconciliation.csv`; the machine-readable summary and data hashes are in `source_bci_reconciliation.json`.

## 5. Additional discrepancies and limits of the reconstruction

These are reported separately so they are not silently folded into the verified sign finding.

- **Source filename:** the script requests `DatatACS1905.xlsx` at line 10. A file with that name was not found in the inspected public experiment/code folders. The public `Experiment_3.xlsx` nevertheless reproduces the complete saved-fit objective vector with the helper functions, providing direct numerical evidence for its relevant contents.
- **Partial fit loop:** the Psame loop starts at participant 21 at line 179. The public fitted-parameter workbook contains all 30 participants. The script may reflect a resumed run; the inspected version is not a complete unattended reconstruction of all saved fits.
- **Bootstrap workflow:** the published Methods describes 15 participants per resample and 10,000 draws, while the released code uses all 30 participants per resample and 1,000,000 draws. The original seed and exact executed revision are not available in this audit. We do not claim to have exactly reproduced the published confidence intervals. The arithmetic relation between corrected and released summed differences for the same fixed-size resample is exact, but it does not resolve this provenance discrepancy.
- **BIC display:** the main article's rendered/MathML Equation 9 places the trial-count and parameter-count symbols in reversed roles relative to the standard k log n penalty. The public code uses `log(numObs)*numParam`, the standard penalty structure. This is a separate displayed-equation discrepancy; it did not generate the reconciled Figure S2 error.
- **VBA call:** line 225 also passes the doubly negated array to `VBA_groupBMC`. We did not execute or audit that toolbox's complete output and do not infer any published VBA result from the call alone.
- **Optimization:** saved-fit reconstruction validates the probability function, source data ordering, saved objective values, and IC arithmetic. It does not show that the saved values are global optima, establish parameter recovery, or replace an independent optimized fit with transparent numerical settings.
- **IC regularity:** the stated 6-versus-8 count is the nominal dimension after removing the fixed stimulus-prior scale. Boundary estimates or locally degenerate decision intervals can undermine standard large-sample IC interpretations. This audit corrects the conventional formulas used by the source; it does not establish all regularity conditions for using their differences as asymptotic evidence.
- **Mechanistic inference:** a relative preference between two restricted observer families is not an absolute-fit test and does not exclude response-equivalent sensory/decision mechanisms outside those families.

## 6. Reproduction

From the workspace root with the configured scientific Python runtime:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" ctd_v02/literature/reconcile_source_bci.py
```

The script locates the three workbooks relative to itself, in `../empirical/inputs/`, and writes its CSV and JSON only inside this literature-audit directory. The raw code and workbooks are retained unchanged. In a standalone package whose root is the current `ctd_v02/` directory, the corresponding command is `python literature/reconcile_source_bci.py` with NumPy, SciPy, and openpyxl installed.

## Suggested manuscript wording

“An independent evaluation of the released parameters reproduced their saved negative log likelihoods. The public comparison script then used the opposite likelihood sign in AIC and BIC; its resulting participant-level differences matched the publisher's Figure S2 source data to numerical precision. Correcting this arithmetic changed summed Delta AIC from -112.14 to -127.86 and Delta BIC from -354.56 to -370.27, while preserving the aggregate preference for the model allowing stimulus-condition differences in the fitted noise parameter. We therefore treat the comparison as a corrected relative result within the specified observer families, rather than as identification of a sensory implementation.”

This wording should be updated only if the new manuscript reports independent refits as a distinct analysis; saved-fit corrections and new-fit results must retain separate labels.
