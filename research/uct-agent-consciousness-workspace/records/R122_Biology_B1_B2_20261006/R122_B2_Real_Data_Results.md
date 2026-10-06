# R122 B2 — real rat-session decoding result

**Status:** all 12 public MATLAB sessions independently processed; 5 rats; no failed session; no convergence warning. This is the frozen conservative B2 reanalysis, not an exact numerical reproduction of the original Figure 2C.

## Main result

The raw data support modest, heterogeneous out-of-trial stimulus decodability under this protocol. Averaging sessions within each rat and then giving each of the five rats equal weight:

| Population | Mean session Pearson r, averaged by rat | Mean held-out R², averaged by rat | Same-time / within-choice centered r |
|---|---:|---:|---:|
| FOF | 0.184790 | 0.054277 | 0.049238 |
| ADS | 0.136561 | 0.036449 | 0.042104 |

These are averages of session-level scores, not a pooled cross-rat fitted model. The centered correlation is a descriptive residual diagnostic; it is not a causally identified state variable or a nuisance-adjusted predictive model R². Weak and negative results are preserved.

The paired rat-level FOF−ADS correlation contrast is 0.048229. A descriptive five-rat percentile-bootstrap interval is [−0.031930, 0.128388]. This does not establish regional equivalence or a reliable regional advantage. No external experience labels were produced.

## Session values

| Rat | Source session ID | B2 trials | Held-out bins | FOF r | FOF R² | ADS r | ADS R² |
|---|---|---:|---:|---:|---:|---:|---:|
| A294 | 821234 | 155 | 1517 | -0.0258 | -0.0481 | -0.1739 | -0.0184 |
| A297 | 825669 | 173 | 1526 | 0.4704 | 0.2194 | 0.3288 | 0.1020 |
| X046 | 733984 | 321 | 2751 | 0.1415 | 0.0152 | 0.2576 | 0.0619 |
| X046 | 734639 | 281 | 2361 | 0.0396 | -0.0000 | 0.1019 | 0.0102 |
| X046 | 735578 | 193 | 1615 | 0.1139 | 0.0095 | 0.0552 | -0.0012 |
| X046 | 736200 | 250 | 2242 | 0.0924 | 0.0072 | 0.1111 | 0.0079 |
| X062 | 779404 | 224 | 1995 | -0.0304 | -0.0666 | 0.1705 | -0.0091 |
| X062 | 779405 | 353 | 3159 | 0.3893 | 0.1459 | 0.3430 | 0.1166 |
| X062 | 779406 | 323 | 2913 | -0.0424 | -0.0328 | 0.0327 | -0.0095 |
| X087 | 826310 | 204 | 2986 | 0.2795 | 0.0769 | 0.2204 | 0.0478 |
| X087 | 826993 | 355 | 5287 | 0.3043 | 0.0922 | 0.2530 | 0.0631 |
| X087 | 827623 | 487 | 4304 | 0.2473 | 0.0609 | 0.1696 | 0.0280 |

The full CSV also retains conditional metrics, descriptive controls, trial coverage, sampled population counts and temporal limits. In particular, A294 and several X062 values were not removed or tuned to improve the aggregate.

## Coverage and availability

- Raw MATLAB trial rows: **5,230**.
- Shared loader's eligible non-violation accumulation trials: **3,344**.
- B2 trials after the declared availability and temporal rules: **3,319**.
- Out-of-fold trial-time bins: **32,656**, with one prediction from each population per retained bin.
- Five A294 trials were excluded because a causal-filter/readout or firing-rate support window intersected a conservative finite-neighbor bracket around raw NaN spike runs. This inference is recorded as uncertainty about availability, not a measured artifact diagnosis.
- Twenty additional trials lacked a complete 50 ms neural bin satisfying the stimulus/exit cutoff after the 100 ms lag. All original IDs and exclusion reasons remain in the session audit.
- Explicit `recorded` flags are available for seven sessions and absent from five. Source laser-on flags were zero in all sessions. Forty A297 eligible rows lack a center-poke exit timestamp; the stimulus cutoff was still applied and the missing restriction is disclosed.
- Outer-fold matched population sizes range from **5 to 52 units per region**. Both regions use the same held-out trials and the same count within each split; neurons differ across sessions and are not treated as independent biological replicates.
- Target endpoints begin at 0.05 s. For ten sessions the largest retained endpoint is 0.85 s with neural observation ending at 0.95 s. Two X087 sessions have longer actual source stimuli, reaching a target endpoint of 1.15 s and neural endpoint of 1.25 s. The code uses the actual source duration and does not force all sessions into a nominal one-second task.

## Predeclared descriptive controls

A control based on the eventual choice, time, their interactions and stimulus duration has an equal-rat mean held-out R² of **0.200573**. Adding the actual most recent 50 ms click difference raises that descriptive value to **0.495881**. These controls include the eventual choice and therefore are **not online deployable predictors**. They demonstrate why correspondence with a cumulative click statistic is not enough to identify an accumulator mechanism: broad stimulus statistics and an eventual choice can already explain substantial variance. Neither the controls nor the neural decoder establish the causal role of a selected neural state.

The actual neural same-time/within-choice centered correlations are small on average and vary by session. A clean, strong biological internal-state map has not been established by this reanalysis.

## Why this differs from the published figure

The published methods specify Gaussian smoothing, nested validation, an encoding lag and matched populations. The pinned executable path uses shuffled flattened time-bin folds and full-session normalization; its declared lag is not visibly applied to the onset alignment. R122 uses contiguous **whole-trial** nested folds, training-only unit qualification/scaling, outcome-blind count matching, an explicit 100 ms lag, causal smoothing and a within-stimulus observation domain.

These choices jointly change the evaluated quantity. Lower scores under R122 cannot be assigned to one source-code feature, and do not independently refute the published result. No outcome-driven retuning or author-compatible rerun was performed in this round. The settings were locally fixed before inspecting neural decoding outcomes; this is not an external preregistration claim.

## Independent validation completed

A separate review reconstructed **all 32,656 target values directly from raw MATLAB data**, verified whole-trial disjointness in every nested fold, checked one outer fold per trial, matched region counts, all reported metrics and output hashes. It also manually checked 378 causal firing-rate values in A294/A297 (maximum numerical difference 2.14×10⁻¹⁴ Hz), first-fold training means/scales (within 10⁻¹³), and stored linear readouts (within 2×10⁻¹⁴).

All twelve summaries have the same script and loader SHA-256 pair, equal to the files present at completion. The shared loader was held fixed during execution. No failed fit or warning was hidden.

## T2 consequence and next requirement

B2 is operationally complete for the declared conservative analysis, and the data-access blocker has been removed. It establishes an auditable biological measurement boundary, with a meaningful weak/heterogeneous result.

B1/B2 alone still do not establish a biological transition law or intervention transport. The R119 certificate therefore remains incomplete, especially C2 and C3. The next mechanistic step must identify corresponding ports and obtain independently assessable intervention behavior; a first-half neural pathway inhibition cannot be silently equated with the artificial accumulator's reset or a +1 evidence pulse. The optogenetic session registry is not a trial-level replication.

## Machine-readable artifacts

- `B2_aggregate.json`: equal-session-within-rat / equal-rat summary, contrasts and fixed configuration.
- `B2_session_metrics.csv`: session values and coverage.
- `*_B2_summary.json`: full source audit, exclusions, source SHA-256, code SHA-256, temporal and conditional metrics.
- `*_B2_folds.json`: original trial identities, inner/outer splits, selected units, alpha losses, trained scalers and coefficients.
- `*_B2_predictions.csv.gz`: complete out-of-fold prediction table.
- `B2_run.log`: actual run progress, retained with its executed command.
- `independent_analysis_checks.json`: separately executed verification results.

Executed command:

```sh
python b2_decode.py --data /workspace/scratch/42800b14a096/data/rat_sessions/Cells_upload --output /workspace/scratch/42800b14a096/staging_r122/b2_results
```

Scientific sources and exact source-read scope are recorded in `R122_Methods_Source_Ledger.json` and `R122_Primary_Methods_and_T2_Audit.md`. No T3, phenomenal-label, fear, valence or subject-unity conclusion is made.
