# R122 independent review of raw rat B1/B2 reanalysis

Date: 2026-10-06. Review baseline: research branch commit `ab02cb6ea51442aa434bdfbe3ef69d52d2877996`.

## Decision

**Accept the completed B1/B2 checkpoint for its explicitly limited observational claims. No blocking source-alignment, click-count, cross-validation or numerical-reconstruction error was found in the inspected final implementations. T2 mechanism closure remains incomplete.**

B1's prespecified flexible ten-bin versus last-bin predictive contrast is inconclusive across five rats. Its prespecified, simpler total-evidence control predicts choice better than the last-bin control in all twelve sessions and all five rats. B2 finds modest, heterogeneous cumulative-stimulus decodability under the frozen conservative pipeline. Several session-region results are negative. These findings must remain in the record without tuning settings to obtain a cleaner correspondence.

This review did not implement either primary analysis. It inspected author source and raw MATLAB data, independently recomputed raw-derived targets and output statistics, and checked the existing implementations. It did not measure experience, valence, subjective labels, a complete biological transition law, or transported neural interventions.

## Files and exact code reviewed

The author repository was inspected at commit `39d056fb12f688034b543d9ac8b7406a58ad0f77`. The specific relevant paths are:

- `helpers/physdata_preprocessing.py`: click transformation, behavioral exclusions, region mapping, recording metadata and firing-rate preprocessing.
- `helpers/rasters_and_psths.py`: raster/PSTH alignment and `get_neural_activity` normalization.
- `helpers/phys_helpers.py`: Gaussian and half-Gaussian definitions.
- `figure2/fig2_helpers/evidencedecoding.py`: source evidence target, flattening, cross-validation, neural alignment and delayed offset.
- `run_params.py`: source study configuration.

The R117, R118 and R119 reports and the research `AGENTS.md` files were read for the evidence and interpretation boundaries. The final paper was not independently reread in full by this reviewer; paper-method comparisons supplied by the methods agent must retain that agent's separate reading scope. Author source was read directly, not inferred from a paper description.

| Implementation | SHA-256 reviewed |
|---|---|
| `rat_cells.py` | `21a84a802ded32bb73d59316332c838ff84b4e5a14e6363d975b09db39009ca4` |
| `b1_kernel.py` | `776e7e92a130bc9b29235f8382541d5b65398779d85f1c01e109f87027fdafd7` |
| `b2_decode.py` | `7db8c365282f3560eee07c39d2cf460f854b5af4c70608b949d0e8dcf34b610a` |

The data source is [Figshare version 1](https://doi.org/10.6084/m9.figshare.30369064.v1). Source parsing was performed on all twelve extracted MAT sessions. The parent execution acquired and verified the archive; this independent review did not repeat the entire binary-download or archive-checksum process.

## 1. Raw schema and timing audit

`independent_raw_audit.py` does not import the shared loader. Its JSON output records all session counts, recording-flag shapes, click checks, unit finite-order checks and nonfinite spike runs.

The source contains **5,230 trial rows and 3,014 raw units** across twelve sessions. There are **3,344** accumulation trials with nonviolations and binary observed choices; the loader's further source checks do not remove any of these in this dataset. All twelve source `nTrials` values agree with their choice and relevant scalar-column lengths. Both errors and exact evidence ties are retained for the behavioral models.

### Clock coordinate

`Trials.stateTimes.clicks_on`, `clicks_off`, and `cpoke_in` are absolute times in the behavioral/session clock used for the supplied spike alignment. For example, A294 contains a valid onset at `752.909263` seconds. They are not durations measured from center-poke onset.

The author's comment describing click times as relative to `cpoke_in` is potentially misleading. The executed transformation is `raw[1:] - raw[0] + clicks_on`, and the raster implementation subtracts the selected absolute event. The independent loader correctly keeps onset-relative click vectors and the absolute `clicks_on` separately. Adding `cpoke_in` again would be an error; neither final analysis does so.

### Stereo click and evidence sign

For every basic eligible source trial:

- Each click vector is finite and ordered.
- The first left and right click times match under the specified tolerance.
- Removing that common stereo onset and subtracting its time is consistent with the author code.
- The resulting number of right clicks minus left clicks agrees exactly with source `click_diff`.
- The click times lie inside the source actual stimulus duration.

The independent checks preserve the right-minus-left sign. `pokedR=1` is the modeled right choice. No choice variable is constructed from UCT or treated as an experiential label.

### Region and hemisphere mapping

MATLAB region indices are one-based. The loader's `index-1` lookup is correct. The source mappings `DMS → ADS`, `M2 → FOF`, and the explicit `['M2', 'FOF']` name → FOF agree with the author preprocessing. Non-FOF/ADS units are excluded from B2 rather than relabeled.

The top-level and penetration hemisphere fields agree in all twelve sessions. The current analysis does not establish invariance under changes of recording hemisphere; matching metadata is a schema check, not a laterality experiment.

### Laser status and center-poke exit

All twelve sessions have `Trials.laser.isOn` identically zero. The final loader exposes the event scalars and preserves the source laser flag. The no-laser filter is therefore based on actual supplied trial metadata, not a session name or an optogenetic registry entry.

A297 has **40 of 176 basic eligible trials** with missing `cpoke_out`. Other sessions have no such missing exits among basic eligible trials. B2 still limits every observation to the valid stimulus interval, but the additional center-poke-exit clamp cannot be independently enforced for the missing A297 events. This limitation is reported and must not be rewritten as universal pre-movement coverage.

## 2. Recording availability and NaN spike entries

Seven sessions, the four X046 and three X062 recordings, supply `recorded` as per-unit trial vectors. Their correctly normalized shapes are units × trials, every value is binary, and every supplied flag is true. A294, A297 and the three X087 sessions omit this field. The absence is recorded explicitly; it is not converted into an observed all-true recording mask.

Only A294 contains nonfinite raw spike entries: **3,956 NaNs in 54 of 67 units**, each affected unit having one internal run. All finite subsequences remain monotonically ordered. The other eleven sessions have no nonfinite raw spike entries.

The retained interpretation is conservative uncertainty. A NaN run is bracketed by its neighboring finite timestamps in original vector order. A trial is excluded if any candidate FOF/ADS unit's bracket overlaps the entire neural observation/filter or firing-rate-QC interval. This removes A294 source rows **203, 204, 205, 208 and 210** from B2. It does not remove these behaviorally valid trials from B1.

Some brackets extend beyond the likely common technical interval because a low-rate unit has distant neighboring spikes. For example, unit 19 brackets `4351.0815–4433.71474` seconds. The conservative removal of five trials is therefore intentionally broader than a claim about five genuinely unrecorded trials. No neuron is called unavailable merely because it emits no spikes in a window.

The supplied `rec.sync` metadata contains an unmatched trial-number code 214 in the behavioral timestamps at about `4366.630124` seconds, between codes 213 and 215, near the concentrated NaN interval. This is compatible with a synchronization-related origin. **The generating conversion code was not obtained, so that origin remains an inference rather than an established causal diagnosis.** The upstream repository linked by the author loader, `Brody-Lab/npx-utils`, returned HTTP 404 through the GitHub connector. A web open also failed and searches did not produce a usable source.

An additional trap was documented: the A294 IMEC and BControl synchronization arrays each contain 290 entries, but their ordered code identities differ at 77 positions. They must not be paired by raw array index. Neither B1 nor B2 attempts a new clock synchronization from these arrays; both use the supplied aligned timestamps.

## 3. B1 correctness and findings

The final `b1_kernel.py` implements the frozen model family and source-order blocked folds. Training-only standardization is inside each held-out fit. A separate full-data fit supplies descriptive regularized coefficients; those coefficients are not used to generate the held-out probabilities.

The prior-history predictors refer to the immediately preceding source row, not the preceding retained row. Prior invalid/nonaccumulation history is marked missing. The current test choice is never used as its own predictor. Prior observed choices within a held-out block may be used as trial-history covariates, so this is prediction conditional on available behavioral history. It is not unconditional generation of a whole unseen choice sequence. The adjacent retained training row is purged at each block boundary, preventing a held-out response from becoming a training row's previous-choice predictor.

`independent_b1_checks.py` independently verified:

- All **33,440 temporal-bin evidence counts** for **3,344 eligible trials**, using direct inequalities against the raw MAT click vectors.
- All prior-source-row history predictors for the eligible trials.
- The sixty held-out session blocks and their one-trial boundary purges.
- Every saved OOF log loss, Brier score, accuracy and paired loss contrast.
- Equal-session-within-rat and equal-rat aggregate means and descriptive t intervals.
- The first A294 held-out fold for all four models, refitted independently from raw-derived predictors and a training-only scaler. The maximum difference from the saved probabilities was `1.12e-16`.

The numerical audit passed. The main results remain:

| Held-out B1 quantity | Equal-rat result |
|---|---:|
| Ten-bin model log loss | 0.587307 |
| Last-bin model log loss | 0.606539 |
| Total-evidence model log loss | 0.562148 |
| Nuisance-only model log loss | 0.691398 |
| Primary ten-bin gain over last-bin | 0.019232 |
| Primary gain descriptive 95% t interval | −0.031799 to 0.070263 |
| Prespecified total-evidence gain over last-bin | 0.044391 |
| Total-evidence gain descriptive 95% t interval | 0.005989 to 0.082794 |

The primary contrast's interval crosses zero and two rats have a worse flexible ten-bin result. The total-evidence control beats last-bin in all twelve sessions and all five rats. Flexible ten-bin prediction is worse than total evidence in eleven sessions. The observed advantage of the simpler total model is compatible with limited per-session sample size and regularized model variance; it is not proof that all true temporal weights are equal.

The prespecified absolute-time sensitivity includes 902 long trials across all five rats. Its first three 200 ms bin intervals remain broad and cross zero; the final 600–800 ms coefficient has a positive descriptive interval. That sensitivity cannot justify claiming uniformly strong early and late weights.

Accordingly, the defensible conclusion is that a prespecified summary using the wider click history improves choice prediction over a final-bin summary. This does not uniquely identify an ideal integrator or exclude every intermittent observation strategy. Normalized B1 time fractions and raw regression coefficients must not be directly equated to the R117 artificial physical-bin pulse magnitudes.

## 4. B2 correctness and findings

The B2 implementation uses whole-trial nested folds, training-only firing-rate qualification and feature scaling, training-only matched population selection, a fixed alpha grid and the declared 100 ms neural lag. The half-Gaussian uses the current and preceding bins only. Its support is confined to each trial's own clock window, and NaN uncertainty exclusions include the smoothing and firing-rate-QC support.

`independent_analysis_checks.py` independently verified:

- All **32,656** saved cumulative-evidence targets against direct raw click counts.
- Every target's reported 50 ms bin and 100 ms lagged neural window.
- All twelve sessions' outer and inner trial identities, with no trial straddling training and validation and no inner fit containing outer-test trials.
- Exactly one outer held-out assignment per trial and matched region unit counts.
- Prediction/fold artifact hashes and saved pooled metrics.
- **378** manually computed causal neural rates across A294 and A297. Maximum discrepancy was `2.14e-14` Hz.
- First-fold training means/scales for both regions in those two sessions; maximum discrepancy was below `1e-13`.
- The corresponding saved continuous evidence predictions; maximum readout discrepancy was below `2e-14` evidence-count units.

There were twelve completed sessions and zero fitting failures or convergence warnings. B2 retained **3,319 trials** after the declared short-window and NaN-bracket exclusions. This review accepts the completed computation, including its weak and negative results.

| B2 equal-rat summary | FOF | ADS |
|---|---:|---:|
| Pooled held-out Pearson r | 0.184790 | 0.136561 |
| Pooled held-out R² | 0.054277 | 0.036449 |
| Within-choice/time centered descriptive r | 0.049238 | 0.042104 |

Eight of the twenty-four session-region R² values are negative, including both A294 regions. The region-contrast intervals include zero. This neither proves region equivalence nor establishes a reliable region advantage.

Three interpretation limits are essential:

1. Pooled trial-bin metrics give longer trials more rows; per-time metrics involve the trials that survive to each time. The explicit equal-rat aggregation addresses biological pseudoreplication but does not make the temporal sample identical.
2. The within-choice/time statistic centers saved predictions and targets using all available OOF rows in each stratum. It is a descriptive residual statistic, not a separately cross-validated nuisance-adjusted model R². The model itself is still held out correctly.
3. Cumulative stimulus decodability can arise from correlated task side, recent sensory evidence, eventual choice or other task variables. Within-choice conditioning and a nuisance baseline do not by themselves establish stored history, causal use, or transition commutation. A fixed neural lag is an analysis alignment, not proof of a unique physiological latency.

The author code and this conservative pipeline differ in cross-validation unit, fold-specific preprocessing, smoothing, delay handling, behavior balancing and time domain. The result is a disclosed independent reanalysis. It is not an exact reproduction or a refutation of the paper's Figure 2 result.

## 5. T2 certificate and UCT inference boundary

B1/B2 materially improve the independently executed biological evidence level. Their narrow observation-level validity does not supply the unperformed mechanistic tests.

| R119 item | What this checkpoint supports | Remaining limit |
|---|---|---|
| C0 grounding | Actual click histories, choice and region metadata audited | Entire rat and AI input distributions are not identical |
| C1 baseline | Independent rat history-to-choice models now computed | No fully calibrated biology↔AI behavioral error bound |
| C2 transition | Some selected cumulative-stimulus information can be decoded | No identified biological update law or tested commutation map |
| C3 intervention transport | AI interventions and published biology remain separately sourced | No matched physical intervention family independently transported |
| C4 time | Actual biological clock and declared neural lag verified | Normalized kernels, physical neural time and abstract AI bins need an explicit correspondence |
| C5 nuisance stability | Sessions and five rats reported separately | Weak/negative sessions and untested laterality/resource conditions remain |
| C6 mapping discipline | Frozen low-complexity analyses and prespecified controls preserved | A good decoder is not yet a part/port-preserving mechanism map |

The proposed selected correspondence is therefore **partial**. No averaged decoder score can close the remaining certificate components. T3/G4 constitutive homology, ordinary phenomenal labeling, valence/fear, a unified bearer boundary and external confirmation of U1/C1 are not established here. The code creates no AI experiential labels and does not use C1 to manufacture its own empirical validation.

## 6. Reproducibility, failures and review completion

The following companion files preserve the independent checks:

- `independent_raw_audit.py` and `independent_raw_audit.json`.
- `independent_b1_checks.py` and `independent_b1_checks.json`.
- `independent_analysis_checks.py` and `independent_analysis_checks.json`.

The raw-audit JSON records preliminary inspection failures: an initial assumption that every session had `recorded`; object-array/uint8 aggregation unsuitable for this schema; and `scipy.io.whosmat` failing on opaque MATLAB variables. They were diagnostic failures, not primary model fits. The corrected audit uses explicit per-unit int64 vectors and selected-variable `loadmat`. No failed run was silently represented as a successful model result.

The review did not alter either analysis agent's files or retune an estimator after seeing the results. The required corrections discovered during collaboration were incorporated before the accepted primary run: explicit absolute-clock handling, scalar event availability, the no-laser flag, and conservative NaN-bracket handling. The final data and implementation hashes agree with the inspected outputs.

**Review disposition: ready to preserve as an auditable empirical checkpoint, with primary/control distinctions, negative results and T2 limitations retained. No additional optional rerun is required for this checkpoint.**
