# R124-J — Observation-qualified neural incremental prediction
Executed 2026-10-06. Independent continuation begun from R123 commit 2f358ac0cb29c4dddc53933fa709ca8aec03be1f; the concurrent R124 transition audit remains intact in its separate directory. R124-J is a naming qualifier, not a new cohort.

## Result
All 12 pinned rat recording sessions were actually fitted: 5 rats, 3,319 trials, 32,656 held-out bins. The raw neural increment beyond the retrospective choice/time/duration baseline is small: FOF ΔR² = +0.007603643, ADS +0.002197713. Both descriptive five-rat intervals cross zero. FOF improves in only 1/5 rats, and removing A297 changes its equal-rat gain to −0.004003324. This is weak finite predictive evidence, not an identified biological accumulator.

The stronger recent-input controls reduce the delayed raw increments to FOF +0.002741273 and ADS +0.000076482. The explicitly online raw setting has FOF +0.012144895 and ADS +0.008921495; those descriptive intervals also cross zero. No favorable session or negative score was discarded.

| Channel / controls | Region | Baseline R² | Joint R² | ΔR² | Descriptive 95% rat t interval | Positive rats / sessions |
|---|---|---:|---:|---:|---|---|
| delayed_raw / retrospective | FOF | 0.200573 | 0.208177 | +0.007604 | [-0.025006, +0.040213] | 1/5; 5/12 |
| delayed_raw / retrospective | ADS | 0.200573 | 0.202771 | +0.002198 | [-0.001245, +0.005640] | 4/5; 10/12 |
| delayed_filtered / retrospective | FOF | 0.200573 | 0.210680 | +0.010107 | [-0.038652, +0.058866] | 1/5; 4/12 |
| delayed_filtered / retrospective | ADS | 0.200573 | 0.202231 | +0.001658 | [-0.004295, +0.007611] | 2/5; 7/12 |
| delayed_raw / retrospective_recent | FOF | 0.495881 | 0.498622 | +0.002741 | [-0.009848, +0.015330] | 2/5; 6/12 |
| delayed_raw / retrospective_recent | ADS | 0.495881 | 0.495957 | +0.000076 | [-0.001055, +0.001208] | 3/5; 6/12 |
| online_raw / online_recent | FOF | 0.513119 | 0.525264 | +0.012145 | [-0.014665, +0.038955] | 4/5; 7/12 |
| online_raw / online_recent | ADS | 0.513119 | 0.522041 | +0.008921 | [-0.001689, +0.019532] | 4/5; 10/12 |
| online_filtered / online_recent | FOF | 0.513119 | 0.529852 | +0.016733 | [-0.021617, +0.055083] | 4/5; 8/12 |
| online_filtered / online_recent | ADS | 0.513119 | 0.526432 | +0.013313 | [-0.003294, +0.029920] | 4/5; 10/12 |

## Cohort, measurement, and validation
The source is the complete Cells.zip from Figshare article 30369064 version 1, file 58773835: 1,929,137,550 bytes, official MD5 3b0ab5c964fb492ec36ee0f55a5d53de, SHA-256 e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494. All twelve extracted MAT hashes match the pinned R122 manifest. MacOS AppleDouble files are not recording sessions.

Reuse the original eligible-trial definition, maximum delayed-filter gap support, five contiguous whole-trial outer folds and three whole-trial inner folds. Firing-rate qualification is training-only; FOF/ADS matching uses the original seed 122 and selected identities. Raw and filtered channels use the same rows and neuron identities. The additional online support audit excluded zero rows; all four channels have 32,656 rows. A294 selected identities also match the archived original R122 folds.

Raw bins contain integer spike counts divided by 50 ms. Delayed raw support is [t+50 ms,t+100 ms); delayed seven-tap filtered support is [t−250 ms,t+100 ms). These are retrospective estimates of e_t. Online raw support is [t−50 ms,t); online filtered support is [t−350 ms,t). The online channels contain no spikes after t. An online observation window does not itself identify biological processing latency or a sufficient Markov state.

The retrospective baseline contains intercept, eventual right choice, time, time squared, their choice interactions, and realized duration. It deliberately uses future information and cannot be presented as an online agent. Its held-out equal-rat R² exactly reproduces the R123 diagnostic 0.20057318974711028. The online baseline instead uses intercept, time, time squared, current signed click count, its time interactions, and current total click count. It has no future duration or choice predictor. This baseline omits the full input history, which would already determine the external cumulative target exactly.

## Estimator and controls
The frozen protocol specifies partial ridge with unpenalized baseline terms, training-only residualization and scaling, a mean-MSE ridge grid including an infinite-penalty baseline-only option, and nested tuning. This is a declared estimator change from the R122 Lasso; the new neural-only scores are not an exact replication of its decoder. A model trained with more covariates can still have worse held-out performance.

A held-out mismatch diagnostic swaps whole neural trajectories within an outer test fold, exact bin-count/choice strata, and four chronological blocks. Seeds 1241/1242/1243 are fixed. Donor identities, moved fractions, and scores are retained. It is a pairing diagnostic, not a permutation p-value or an internal neural intervention. Matching by eventual choice in that diagnostic does not put choice into the online fitted predictor.

Session metrics are averaged within rat and then across rats equally. The five-rat t intervals describe these animals; they are not confirmatory population tests. All leave-one-rat-out results are in aggregate.json.

## Recovery and failure history
The first shared signed-URL download attempt failed. Fresh per-range public redirects enabled recovery. Four short ranges caused an initial assembly to fail size and checksum; only those ranges were replaced before accepting the full verified archive. Preserve data_access_failures.json and archive_first_assembly_failure.json.

The X062 2020-03-20 local extracted MAT later failed its source hash and loader before fitting. It had fewer bytes than the verified archive member; the reason for the local truncation is unknown. Re-extraction from the verified archive restored the exact source hash, and only that missing session was fitted. A subsequently zero-byte X087 2021-07-25 prediction file was reconstructed from already saved features and frozen coefficients, without refitting; its metric replay agreed to 1.11×10⁻¹⁶. Preserve the first-pass failure, repair scripts/logs, single-session repair and prediction-repair records. First_Pass_11_Sessions_Aggregate.json is historical; aggregate.json contains the accepted full twelve-session result.

An independent augmented least-squares construction checks the partial-ridge solver (maximum discrepancy about 3.6×10⁻¹⁴). Saved-artifact digests pass; all trial partitions are disjoint; the original OOF R² summary check differs by at most 2.15×10⁻¹⁶. The complete checks are in software_checks.json and independent_result_checks.json. A later independent audit of saved R² and absolute MSE differs by at most 2.84×10⁻¹⁴ and is reproducible through R125 audit_saved_results.py. These are software/data-integrity checks, not biological proofs.

## What this advances
The executed comparison closes the R123 missing-joint-model task on this cohort. It does not infer conditional mutual information from ΔR², identify complete K, measure E, transport an intervention, or close T2. UCT III Appendix B motivates conditional contribution but supplies no license to convert a weak ridge increment into experience evidence. The next executed test freezes the already fitted observable maps and examines state/input/time/output-law correspondence in R125.
