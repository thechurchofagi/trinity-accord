# R122 B1 — Independent rat temporal-evidence reanalysis

Date: 2026-10-06. Biological source: Gupta et al., *Neuron* 114(3), 521–535.e5, DOI [10.1016/j.neuron.2025.12.029](https://doi.org/10.1016/j.neuron.2025.12.029). Raw data: [Figshare 30369064 version 1](https://doi.org/10.6084/m9.figshare.30369064.v1). This report concerns only B1 on the 12 genuine recording sessions. It does not reproduce the separate large optogenetic behavioral experiment (B3).

## Main finding

**The prespecified flexible ten-bin kernel versus final-bin contrast is inconclusive across the five rats.** It underperformed the final-bin model in two rats, and its descriptive across-rat interval spans zero. The prespecified total-evidence control gives the more favorable result: total accumulated click evidence predicted held-out choice better than the final normalized bin in all 12 recording sessions and all five rats. The flexible model also underperformed this one-parameter total-evidence control in 11 of 12 sessions.

This is actual raw biological analysis. Its strongest result is a reproducible observational distinction between total history and the final-bin control. It does not establish that each rat integrates every click on every trial, identify a biological state-transition map, or verify the transport of a biological neural perturbation to the AI midpoint reset.

## Input and source audit

All 12 MATLAB files loaded successfully with selective `scipy.io.loadmat(..., simplify_cells=True, variable_names=...)`. They contain 5,230 source trial rows from five rats. The author's accumulation/nonviolation conditions retain 3,344 rows. The independent schema checks introduce no additional losses in this dataset. Forty-five zero-total-evidence ties are retained in choice fitting; both correct and error trials are included. No source trial is relabeled using UCT.

The loader preserves source filename, file SHA-256, source MATLAB row (one based), plain session ID, rat and all trial exclusions. `Trials.rat` and `Trials.sess_date` are opaque MATLAB objects in these files; plain top-level metadata and `rec` provide matching identity records. `Trials.sessid` is a repeated vector and is independently checked to be constant and to match the top-level session ID.

Click alignment follows the pinned author source exactly: remove the common first stereo click and subtract its timestamp separately on each side. Both first timestamps must agree. The reconstructed number of right-minus-left clicks matches the stored `click_diff` in every eligible trial. The result is onset-relative click timing, while `stateTimes.clicks_on` is a session-clock timestamp. No additional `cpoke_in` offset is added. The distinction matters because a comment in the author loader describes a poke-relative frame, whereas the actual data and analysis use the session clock.

Primary source anchors:

- [Author trial loading and click conversion, lines 25–74](https://github.com/Brody-Lab/fof_ads_interactions/blob/39d056fb12f688034b543d9ac8b7406a58ad0f77/helpers/physdata_preprocessing.py#L25-L74).
- [Author accumulation/nonviolation exclusions, lines 199–202](https://github.com/Brody-Lab/fof_ads_interactions/blob/39d056fb12f688034b543d9ac8b7406a58ad0f77/helpers/physdata_preprocessing.py#L199-L202).
- [Raster session-clock alignment, lines 61–72 and 101–119](https://github.com/Brody-Lab/fof_ads_interactions/blob/39d056fb12f688034b543d9ac8b7406a58ad0f77/helpers/rasters_and_psths.py#L61-L119).
- [Author cumulative-evidence target, lines 27–39](https://github.com/Brody-Lab/fof_ads_interactions/blob/39d056fb12f688034b543d9ac8b7406a58ad0f77/figure2/fig2_helpers/evidencedecoding.py#L27-L39).

The full final paper and supplementary PDF was obtained from the author's website, SHA-256 `8daabdb02884a87b51c0c618f64c7f14a53e92b20eda7eaf70132ff640f24789`. The pinned repository and full text were checked for an author behavioral temporal-kernel estimator; none was located. **B1 is therefore an independent requested analysis, not a reproduction of an author-reported kernel.** The source PDF itself is not redistributed in this output package; its URL, hash and reading scope are retained in the source ledger.

## Method fixed before choice-effect fitting

`R122_B1_Frozen_Protocol.md` was written after a first-file structural schema inspection and before B1 choice-effect fitting. This was a local analysis freeze, not an external preregistration. Its exact SHA-256 and the executed script/loader hashes are recorded in `B1_results.json`.

The primary predictors are right-minus-left click counts in ten equal fractions of each trial's actual stimulus duration. This normalization is an independent operational definition. Biological actual durations vary; these fractions cannot be treated as the same physical clock as R117's fixed ten-bin artificial task.

Each session is fit separately. All four logistic models include an intercept, actual stimulus duration, prior rewarded signed choice, prior error signed choice, and a prior-history missing flag. Prior means the immediately preceding source row, never the preceding retained row. First-trial history is unknown; no default rewarded-right event is fabricated. Predictors are standardized using training data only. Models use the fixed L2 setting `C=1.0`, LBFGS, tolerance `1e-8`, and 2,000 maximum iterations.

| Model | Evidence predictors | Role |
|---|---|---|
| full10 | Ten freely varying temporal-bin counts | Requested temporal kernel |
| lastbin | Final normalized-bin count | Limited-history comparator |
| total | One total right-minus-left count | Constant temporal-weight comparator |
| nuisance | No evidence count | History/duration baseline |

Five contiguous source-order blocks are held out in each session. Each held-out unit is an entire trial. The immediately adjacent retained trial on each side of a test block is purged from training. Held-out choice may be available as a previous observed choice when predicting the next trial inside the test block; this is an explicitly history-conditioned behavioral prediction, not unconditioned future rollout. No held-out current choice is a predictor, and no held-out row enters fitting or scaling.

There were zero fitting/convergence failures. Every full-fit design, including intercept, had full column rank. The fixed regularization setting was not changed after seeing the biological results.

An independent reviewer rederived all 3,344 trial rows and 33,440 temporal count features directly from the raw MATLAB files, verified the source-history identities and all 12 sets of fold/purge assignments, and recomputed every reported metric, paired difference, equal-rat aggregation and descriptive t interval. An independent refit of all four models for the first A294 test fold reproduced saved probabilities to maximum absolute discrepancy 1.12e-16. No held-out choice appeared in a training-row history predictor. The reviewer scripts and machine-readable audit are retained separately as `independent_b1_checks.py` and `independent_b1_checks.json`.

## Results

The table first averages sessions within each rat and then weights the five rats equally. Accuracy predicts the observed choice; it is not an estimate of conscious experience, intelligence, or correctness on arbitrary tasks.

| Model | Held-out log loss ↓ | Held-out accuracy |
|---|---:|---:|
| full10 | 0.587307 | 0.710356 |
| lastbin | 0.606539 | 0.678490 |
| total | **0.562148** | **0.725328** |
| nuisance | 0.691398 | 0.561456 |

Positive loss gain means the named model predicts better than the comparator.

| Rat | Sessions | Eligible trials | full10 over lastbin | total over lastbin |
|---|---:|---:|---:|---:|
| A294 | 1 | 160 | −0.015834 | +0.014757 |
| A297 | 1 | 176 | −0.008405 | +0.054744 |
| X046 | 4 | 1,051 | +0.087959 | +0.093266 |
| X062 | 3 | 906 | +0.019506 | +0.032266 |
| X087 | 3 | 1,051 | +0.012933 | +0.026924 |
| **Equal-rat mean** | **12** | **3,344** | **+0.019232** | **+0.044391** |

The primary flexible-kernel versus last-bin contrast has a descriptive across-rat t interval of **[−0.031799, +0.070263]**. It is not a uniform positive result. The total-evidence control versus last-bin contrast has a descriptive interval of **[+0.005989, +0.082794]** and is positive in every session. The flexible ten-bin model's mean loss gain over total evidence is **−0.025160**, interval **[−0.053915, +0.003596]**. Thus these data do not justify preferring the flexible temporal model over the simpler total-evidence predictor.

These intervals describe variation over only five independent rats. They do not propagate every source of within-rat fitting uncertainty, and no p-value or strong population-level confidence claim is assigned to them. Session rows and time bins are not treated as independent animals.

### Kernel shape

Equal-rat mean coefficients in raw log-odds per right-minus-left click are:

`[0.014573, 0.073632, 0.077106, 0.000559, 0.067125, 0.098400, 0.128133, 0.143231, 0.070043, 0.126452]`.

Individual-rat profiles vary substantially; several early-bin coefficients have wide descriptive intervals that span zero. These are regularized descriptive slopes. They do not certify that early evidence is absent from a rat, nor support an exact flat-kernel match to the R117 artificial accumulator. Raw and standardized coefficients for every session are preserved.

### Absolute-time sensitivity

The prespecified long-duration analysis includes 902 trials across all five rats. It uses four absolute 200 ms bins from 0 to 0.8 s, includes remaining post-0.8-s evidence as a nuisance predictor, and retains the common duration/history terms. All 12 session fits complete. Mean raw coefficients are approximately `[0.026136, 0.040876, 0.035386, 0.136783]`, with large between-rat uncertainty. This secondary descriptive result preserves the distinction between actual time and normalized fractions; no duration threshold or bin count was searched after the main fit.

## B2-relevant raw-schema discoveries

The common loader also independently inspected the neural fields in all 12 files. There are 3,014 source units before population filters. `recorded` masks exist in the four X046 and three X062 sessions; they are absent in A294, A297 and all three X087 sessions. Absence is explicitly represented, not converted into a fabricated all-recorded mask.

A294 contains 3,956 nonfinite spike timestamps in 54 of 67 units. The loader retains counts and conservative time brackets around each nonfinite run, while returning finite timestamps for counting. Those brackets are inferred exclusion intervals between neighboring finite spike times, not independently observed recording masks. B2 must handle overlapping trials explicitly. No other session contains nonfinite raw spike timestamps in this inspection. These facts are input-quality findings, not neural decoding outcomes.

## Meaning for the UCT comparison

B1 supplies new independent biological evidence for the selected task-level grounding: actual click history contains predictive information beyond the final normalized bin. The simple total-evidence model is the most effective tested predictor under the fixed protocol. The heterogeneous ten-bin fits and the failed uniform primary contrast are retained as constraints on the comparison.

The result initially belongs to **T1 / observational components of a prospective T2 certificate**. It does not identify causal state use from decoding alone, transport a biological neural intervention to an AI reset, establish transition commutation, or meet T3/G4. R117 artificial performance, model scale, source noise and intervention operators differ, so absolute accuracy/coefficient numbers are not a calibrated cross-substrate similarity score. AI E remains latent. No valence, fear or experiential content label is constructed.

## Reproduction and artifacts

Keep `b1_kernel.py`, `rat_cells.py` and `R122_B1_Frozen_Protocol.md` together. With the same dependency versions from `B1_results.json`:

```bash
python b1_kernel.py --data /path/to/Cells_upload --out /path/to/b1_results
```

The program writes every source trial with exclusion/identity information, session-level held-out predictions and fold memberships, raw and standardized coefficients, full result JSON, input/code/protocol hashes, and the static figure. `b1_run.log` preserves the actual execution. `R122_B1_Source_Schema_Ledger.json` preserves source scope, the unavailable author-linked `npx-utils` repository, the `whosmat` failure, the initial strict-NaN loader failure and their resolutions. `schema_scan/` contains the independent all-session neural schema inspection.
