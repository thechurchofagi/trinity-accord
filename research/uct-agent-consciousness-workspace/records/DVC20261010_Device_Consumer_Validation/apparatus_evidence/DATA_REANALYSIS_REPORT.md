# Reanalysis of the published tactile-attention dataset

**Parent record:** DVC20261010_Device_Consumer_Validation  
**Result type:** retrospective reanalysis of already published human data; source and instrument audit. No new human observations or hardware measurements were collected.

## What was actually completed

The [author's public dataset, DOI 10.5281/zenodo.18877381](https://doi.org/10.5281/zenodo.18877381), was downloaded from the official Zenodo API. The 161,720-byte archive matches the registered MD5 `2618e6661e94135733595aa9bdc3d26d`; its SHA256 is `ed89e94719e87acc19cd905efd7ff44d09abce0e0291f2fd654b0453bfdfbd6a`. The source is CC BY 4.0. Original bytes are preserved, and all preparation occurs in separate outputs.

The archive contains 121 trial CSV files covering 21 participants. There are 10,875 nonempty trial records and five blank lines. The author's explicit exclusions are HN77, JD14 and JN98. The resulting 18 participants have 9,705 nonempty records covering all six movement-by-attention cells. One included record has command zero, outside the declared nine command levels. Excluding that record leaves **9,704 records and 108 participant-condition cells** for independent fits. There are 22 command-zero records in the entire archive, 21 in excluded participants. Their exact source locators remain in `results/EXACT_RESULTS.json`.

The independent analysis fits 108 cells twice: first with all declared-range endpoint records, then with an available-timing sensitivity filter applied to active movement. Thus **216 fits means 108 cells × two analyses; it is not a sample of 216 people or independent experiments**. All 216 fits converged without hitting the prespecified parameter bounds. Three starting values per fit agreed in objective value to within `5.6e-10`.

## Analysis contract

The first three fields in each nonempty source row identify trial number, response and vibration command without reconstructing any time column. We interpret `InputValue=1` as the comparison being judged stronger from the ascending command–response functions. The paper describes physical keys 1/2, whereas the CSV uses 0/1; no explicit key-to-`InputValue` conversion was found in the inspected material. This coding interpretation remains an assumption. PSE is the fitted Pr(InputValue=1)=0.5 location. For the same response curve, relabeling p as 1-p leaves its 0.5 crossing unchanged; the physical stronger/weaker naming still requires the unresolved coding bridge. Command is retained in the archive's numeric 1–9 scale. Converting it to calibrated tactile amplitude would require the unprovided actuator transfer function.

We fit `Pr(response=1 | x) = Phi((x-mu)/sigma)` by Bernoulli maximum likelihood, with positive `sigma`, no lapse parameter, fixed bounds and three starts. `mu` is PSE; `sigma` is the fitted normal standard deviation. We also output `Phi^-1(.75)*sigma`, the 75%-minus-50% threshold. These are kept distinct from the source's column named `JND`.

The [cited MATLAB repository](https://github.com/pierodonpac/Sensory-Gating-Analysis/tree/e3305c3097a3827fa0ec8f660d587215ad4c7b3e) contains a generic fitting script and README. Its required `anamax.m` is absent, and the script does not implement the released attention-folder layout directly. We read it; we did not execute an intact author pipeline. The Python implementation is an independent fit to the stated model, not an exact reproduction of the missing dependency.

The second analysis removes 341 active records using the available latency/duration fields and a ±2 SD rule within participant and attention cell. It does not reconstruct absent path curvature, gaze or device-commit events. This is explicitly a sensitivity analysis, not a claim to reproduce the article's complete exclusion procedure. Passive and control timing filters are not silently invented.

Subject-level paired contrasts use two-sided t intervals and tests. Holm adjustment applies separately to each declared family of three within-movement contrasts, three interaction contrasts or three marginal movement contrasts. ANOVA uses orthonormal repeated-measures contrasts; both uncorrected and Greenhouse–Geisser values are retained. We do not equate nonsignificance with equivalence.

## Main results and their proper scope

| Quantity | Reanalysis result | Meaning |
| --- | --- | --- |
| Archived `JND`, passive Start minus End | 0.49820; 95% CI [0.22387, 0.77253]; n=18; unadjusted p=0.001336; Holm p=0.004008 | The archived precision parameter changes with attention in passive movement. |
| Independently fitted `sigma`, passive Start minus End | 0.68300; 95% CI [0.30407, 1.06192]; n=18; unadjusted p=0.001422; Holm p=0.004266 | The same directional effect appears in the explicit normal-SD fit. |
| Independent `sigma`, passive attention effect minus active attention effect | 0.75857; 95% CI [0.28798, 1.22916]; Holm p=0.010203 | The attention difference depends on movement condition in this model. |
| Same interaction, available-timing sensitivity analysis | 0.75318; 95% CI [0.27285, 1.23352]; Holm p=0.012466 | This limited active-data filter preserves the direction. |
| Independent PSE, Active minus Control, averaged over attention | −0.40793; 95% CI [−0.70979, −0.10607] | Movement-related comparative bias is recovered separately from precision. |
| Independent PSE, Passive minus Control, averaged over attention | −0.75050; 95% CI [−0.95761, −0.54339] | The passive bias comparison also remains negative. |

These results support the bounded endpoint distinction already used in MPC. They do not establish motor-input sufficiency, proprioceptive-input sufficiency, a biological OR gate, actual intake by a specific consumer, agency, ownership, familiar mineness, or experience existence. The paper's qualitative “recovery” language is not promoted to an equivalence result.

## Reproduction successes and unresolved differences

From the archived parameters, the PSE ANOVA gives movement F=18.30096, attention F=0.76540 and interaction F=1.59424, reproducing the corresponding reported rounded values. The archived `JND` attention-difference analysis gives interaction F(2,34)=6.64762, reproducing the reported difference-score value of 6.65.

The same complete 18-person archive instead gives `JND` attention F(1,17)=19.82485. Another article paragraph reports F(1,15)=17.48 and interaction F(2,30)=6.53. The released summary does not identify a distinct 16-person analysis population that would justify those degrees of freedom. We retain this as an unresolved reporting/provenance difference; we do not select participants to force agreement.

The source's `JND` values also fail to equal the independently fitted normal `sigma`. Across the 108 unfiltered cells the ratio `archived JND / independent sigma` ranges from 0.68670 to 0.80233, with median 0.73256. This is neither a demonstrated unit conversion nor proof that the author's parameter is erroneous. Missing fitting details and unprovided preprocessing can matter. The largest PSE discrepancy is 0.52500 command units (ZO41, Passive/End), also retained. Both the archived and independent quantities are reported so this uncertainty cannot disappear through a relabeling.

Most complete source files contain 90 records, while the article's procedure paragraph uses different block/trial totals. The archive is not a complete hardware history. `TIMING_PARSE_REVIEW.md` documents its time-field and apparatus-identity questions in detail.

## Consequences for DVC/SCU/MPC

The mathematical source-routing results and MPC's missing-corner theorem are unchanged. An empirical application still needs the physical carrier, selected consumer, event readout, branch-selective intervention, shared trial/epoch, clock relation, consequence control and independent endpoint bridge to hold together. This release does not supply that conjunction. Its positive contribution is real behavior reanalysis plus an exact inventory of what an installed device test must additionally measure.

PSE is selected as the primary experience-related target in the **future apparatus contract** because it directly operationalizes a comparative intensity judgment. The current reanalysis remains retrospective and exploratory, and is not represented as preregistered. Intelligence, report, conceptual self and familiar mineness remain distinct; C1/U1 receive no new basal-experience gate.

## Reproduce

Run `code/fetch_public_dataset.py` to acquire the fixed archive and verify both hashes. Run `code/reanalyse_apparatus_data.py` and `code/build_timing_witnesses.py` with Python, NumPy and SciPy. The actual run used Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. `results/EXACT_RESULTS.json` records the executed code hash. No author MATLAB or hardware-control code is needed for this independent, bounded reanalysis.
