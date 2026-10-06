# R122 primary-source methods audit and T2 inference boundary

Author: UCT research audit, 2026-10-06. Baseline project HEAD supplied by the parent task: `ab02cb6ea51442aa434bdfbe3ef69d52d2877996`. This audit continues R117–R121; it does not alter published A/B/C or TA-TR-2026-24.

## Primary evidence actually inspected

1. Gupta et al., *Neuron* 114(3), 521–535.e5 (2026), DOI [10.1016/j.neuron.2025.12.029](https://doi.org/10.1016/j.neuron.2025.12.029). The corresponding author's [complete publication PDF](https://dikshagup.github.io/publication/multiregion-accumulation/multiregion-accumulation.pdf) was downloaded successfully: 11,663,991 bytes; SHA-256 `8daabdb02884a87b51c0c618f64c7f14a53e92b20eda7eaf70132ff640f24789`; 38 PDF pages including supplement. Inspected task/results PDF pp. 3–7, discussion/limitations pp. 11–12, the complete STAR Methods pp. 17–21, and Figure S3 caption on PDF p. 26. Page locations refer to the PDF file, not printed journal pagination.
2. [Figshare dataset](https://figshare.com/articles/dataset/Data_from_A_multi-region_recurrent_circuit_for_evidence_accumulation_in_rats/30369064), version DOI [10.6084/m9.figshare.30369064.v1](https://doi.org/10.6084/m9.figshare.30369064.v1), public description and field definitions. The actual files supersede advertised field availability when these differ; notably `recorded` is absent from some real files.
3. [Author source at pinned commit](https://github.com/Brody-Lab/fof_ads_interactions/tree/39d056fb12f688034b543d9ac8b7406a58ad0f77): complete `figure2/fig2_helpers/evidencedecoding.py`, `figure2/figure2_decodingfigs.py`, `helpers/physdata_preprocessing.py`, `helpers/phys_helpers.py`, and the neural-activity/raster/filter path in `helpers/rasters_and_psths.py`.
4. Kopec et al., primary preprint [10.1101/2024.08.21.609064](https://doi.org/10.1101/2024.08.21.609064), dated 2024-08-22 in the inspected [author-hosted PDF](https://dikshagup.github.io/publication/degenerate-strategies/degenerate-strategies.pdf). Targeted reading: psychophysical-kernel interpretation pp. 7–9, snapshot-conflict analysis pp. 14–18, and kernel definition pp. 37–38. This is separate prior evidence about identifiability, not additional data analyzed in R122. No 2024 preprint result is substituted for the final 2026 Neuron methods.

## What the final paper's B2 analysis measures

The target for Figure 2C is the cumulative **physical click-count difference**. It differs from the fitted, choice-conditioned accumulator posterior used for individual-neuron tuning curves. The latter incorporates the animal's eventual choice through backward conditioning; it is unsuitable as an independent experiential or internal-state ground truth.

The final methods specify all population neurons above 1 Hz, matched region counts, 50 ms bins, a 100 ms neural lag, Gaussian smoothing with sigma 75 ms, a single L1 regression across all trial time points, and nested 10-fold validation. Reported discrimination of the regions is an analysis-dependent comparison, not a formal equivalence test. The biological sample is five rats and 12 sessions; cells and time bins are repeated measurements, not independent animals.

## Executable source differs from a strict prospective decoder

The following are direct source observations at the pinned commit, not speculative explanations of the published results:

| Finding | Exact source location | Consequence for R122 |
|---|---|---|
| Target matrix is flattened; `KFold(..., shuffle=True)` is passed to `cross_val_predict` on time-bin rows | `figure2/fig2_helpers/evidencedecoding.py`, lines 55–75 | Neighboring rows from the same trial may be in training and validation. R122 instead holds out whole contiguous blocks of trials in both validation layers. |
| Neural feature means and standard deviations use the entire concatenated session before validation | `helpers/rasters_and_psths.py`, lines 859–870 | R122 fits every scaler on that training split only. |
| `Tshift=100` and delayed onset/offset columns are created, but the executed alignment remains `clicks_on`; `get_neural_activity` does not apply `Tshift` | `evidencedecoding.py`, parameter block and lines 168–169; `rasters_and_psths.py`, lines 837–857 | R122 explicitly pairs a target bin with a neural bin 100 ms later. The inspected path visibly uses the delayed offset mask; it does not implement the declared onset shift. |
| The final figure assembly constructs plotted time from bin size and start time without adding `Tshift` | `figure2/figure2_decodingfigs.py`, `compute_t` and evidence assembly | Time labels are audited separately from what array alignment actually executes. |
| Side-selectivity-derived neuron sampling and choice balancing occur before decoder fitting | `evidencedecoding.py`, lines 171–182; `phys_helpers.py`, `equalize_neurons_across_regions` | R122 uses training-only rate qualification and seeded outcome-blind count matching. It keeps the eligible choice distribution rather than balancing with held-out choices. |
| Gaussian filters use positive and negative temporal offsets | `phys_helpers.py`, `gaussian`; `rasters_and_psths.py`, convolution path | An acausal smoothed representation cannot independently establish when information first became available. R122 uses causal smoothing and excludes observations after stimulus offset. |

The R122 protocol is therefore a **different, conservative estimand**. Lower R122 performance does not by itself refute the published Figure 2C. Diagnosing which protocol change explains a difference would require a separately declared comparison; it is not performed opportunistically to improve R122's results.

## Statistical and mechanistic checks

Whole-trial validation removes an important form of within-trial leakage. Blocking trials also probes session drift more strictly than random trial folds. A decoder fitted separately to each session makes no claim that the same cell-weight map transfers to another session or rat. Equal-rat aggregation prevents animals with more sessions from dominating the summary. With only five rats, uncertainty about population generality remains substantial.

Pooled bin metrics weight long trials more heavily; elapsed-time metrics and session/rat summaries expose this. Eventual-choice/time/duration controls use an observed final choice and are descriptive references, not deployable online predictors. Within-choice/time centered metrics are post-prediction diagnostic correlations. They do not establish a causally used memory state, and their residual R-squared must not be called an out-of-sample nuisance-adjusted model R-squared.

B1 is an independent psychophysical-kernel analysis, not replication of a kernel estimator in the Gupta repository. Broad weights can reject an exclusively last-bin predictor within the specified model class. A broad or flat aggregate kernel alone does not establish that every individual trial integrates every click. Sampling probability and per-click weighting can yield similar average kernels; some snapshot or burst strategies require additional conflict-trial or model-discrimination evidence. This limitation was already investigated by the same laboratory and is not a new UCT discovery.

## Why B1/B2 cannot complete the R119 certificate alone

| R119 component | What B1/B2 contribute | What remains necessary |
|---|---|---|
| C0 grounding consistency | Audited left/right counts, clocks, source rows and choice semantics provide a concrete task coordinate. | State explicitly how different AI and rat stimulus distributions/time supports are transported. |
| C1 baseline correspondence | Actual rat behavior can be compared with the existing artificial accumulator's behavior. | Rat and R117 AI accuracy from different trial distributions/noise models are not a pointwise matched baseline law. A tolerance and common comparison domain must be declared. |
| C2 transition commutation | A decoder provides one candidate projection of neural observations onto a task statistic. | No biological transition law or causal sufficiency of that projected state is identified. A correlated observer can decode cumulative evidence without implementing its update. |
| C3 intervention transport | The paper provides source-level pathway and regional perturbation evidence; B1/B2 do not independently reproduce it. | Actual matched ports and quantitative perturbation responses. FOF→ADS gain reduction, whole-region suppression, external evidence addition and accumulator reset are different interventions. |
| C4 temporal correspondence | Fixed bins, explicit lag and stimulus-relative epochs make timing assumptions inspectable. | A 500 ms inhibition is not an instantaneous midpoint reset, and a 10-bin AI trial does not establish physical time or recurrence correspondence. |
| C5 nuisance stability | Separate sessions, rats, region counts, trial blocks and within-choice/time diagnostics test restricted stability. | Laterality, intervention conditions, model seeds and intended generalization domains remain only partially covered. |
| C6 anti-triviality / mapping discipline | The map is grounded in an external target and low-complexity cross-validated decoding with predeclared controls. | Unique causal role and intervention-preserving mapping are not established merely because the decoder works. The same-state/other-port or correlate-only alternatives remain relevant. |

The appropriate overall status remains **T2 incomplete** after B1/B2 alone, whether the decoding results are strong or weak. This is a substantive result boundary, not a reason to add further toy theorems.

## Perturbation and prior-art distinctions

The final paper already combines a constrained multi-region RNN with biological recordings and pathway perturbations. Some perturbation effects were training targets; the paper's bilateral FOF test was held out. Reproducing an effect that was used to construct training targets is not an independent intervention prediction. The novel value of this UCT round is the executable audit and explicit inference boundary, not claiming invention of biological–artificial accumulation comparisons.

The authors also state that temporally specific optogenetic samples are insufficient for reliable full behavioral-parameter recovery. A net ipsilateral choice bias need not isolate one accumulator parameter: evidence encoding, integration noise, prior bias, output selection and motor effects can all contribute. The paper reports altered movement times while gross trial-completion ability was preserved. These observations motivate a port-specific next step, not a direct identification of neural suppression with removal of accumulated evidence.

Throughout this round E remains latent. No C1-generated experiential labels are used as data. No claim is made about T3, ordinary phenomenal qualities, fear, valence or the unified subject boundary.
