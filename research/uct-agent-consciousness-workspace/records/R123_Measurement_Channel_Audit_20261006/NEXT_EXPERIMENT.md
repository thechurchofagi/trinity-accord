# Next bounded experiment — observation-qualified neural increment

Status: PROSPECTIVE, not executed in R123. No additional generic toy theorem is requested. This specification follows already observed R122/R123 results, so it is not a preregistration independent of that history. Its new joint-model scores remain unobserved here.

## Single objective

Determine whether the recorded neural populations improve held-out cumulative-evidence prediction beyond a declared baseline, while separating memory introduced by preprocessing from memory carried by the selected biological process. This is a finite identification step toward T2, not an experience-existence test.

## Inputs and freeze

Reuse the exact twelve Cells.zip sessions and R122 hashes. Reuse original trial identities, exclusions, 5 contiguous outer whole-trial folds and 3 inner whole-trial folds. Freeze all cohort masks using the maximal R122 filter support, then apply the same masks when smoothing is removed. Retain the same training-qualified, matched FOF/ADS unit identities for paired channel comparisons; never select neurons using held-out targets.

Primary channel: original spike counts per 50 ms bin, with no temporal smoothing. Sensitivity channel: the exact seven-tap R122 filter. Explicitly record target time, last available neural time, and raw support. The existing +100 ms alignment remains a retrospective encoding comparison, not an online state at the earlier target time. Do not optimize delay using the final test set.

## Predictors and outputs

For the retrospective diagnostic, fit (a) the R122 choice/time/duration baseline, (b) the neural-only predictor, and (c) baseline plus neural features. All use train-only transformations and nested tuning. Compare paired held-out squared errors for (a) versus (c); do not infer conditional gain from (b) versus (a). Report R² with a common target variance, raw MSE, and session/rat-level contrasts. A recent-evidence baseline is a separately labeled sensitivity analysis because it directly observes part of the target stimulus.

For any subsequent online state comparison, remove eventual choice, future realized duration, future spike windows and other unavailable information. Define a separate causally available input/time baseline and actual observation time. Do not transfer fitted retrospective coefficients or apparent memory into the online certificate without this step.

If population dimension reduction is used, fit it inside training folds, record its dimension and state meaning, and evaluate frozen held-out mappings. No claim of biological state closure follows solely from decoding or dimension reduction.

## Negative controls and failure rules

1. Replay the exact filter on independent raw innovations (R123 already supplies this calibration). A passing control only verifies the channel implementation.
2. Test the model on trial-mismatched neural data with permutation conducted within appropriate session and time strata; this is a diagnostic null, not a replacement for randomized neural interventions.
3. Report all rats and leave-one-rat-out sensitivity; do not promote bins or neurons to independent animals.
4. If neural incremental prediction is weak, unstable, or absent, retain that result and do not rescue the same hypothesis by post-hoc map or cohort changes.
5. A positive result advances finite predictive identification only. C2 still needs frozen mapped transition predictions; C3 needs appropriate matched interventions. Do not claim complete K, complete E, T3, valence, fear, or subjective equality.

## Subsequent mechanism milestone, not a new simultaneous domain

Specify one state map, one input-port map, one observation law, one time map and one output law; compare a recurrent accumulator with recent-input and reset controls using the same externally supplied trial inputs and compatible readout noise. Require held-out transition and intervention errors against frozen tolerances. Obtain appropriate biological intervention outcomes rather than calling the session registry B3. Keep the observation channel external to the selected biological token unless an actual larger token is separately justified.

## Anti-stall execution rule

Do not keep regenerating this plan. Verify artifacts once, make a bounded attempt to access the needed raw data, and then either execute the specified analysis or record the precise missing input. Where current verified artifacts support a different useful computation, execute and label it rather than reporting the unrun primary experiment as completed. Do not call the null calibration a major breakthrough or restart its calculation as the next round's main result.
