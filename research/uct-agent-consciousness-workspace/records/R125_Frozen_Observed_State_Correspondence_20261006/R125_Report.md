# R125 — A frozen observed-state candidate fails accumulation-transition and shared-output tests
Executed 2026-10-06. Exploratory real-data continuation of R123/R124-J, with protocol and maps frozen before these scores. This is not a blind preregistration or independent replication.

## Finding and decision
On 12 real recording sessions from 5 rats, 29,337 adjacent held-out within-trial transitions and 3,319 held-out trial endpoints were evaluated. The selected no-future, unsmoothed neural-only ridge coordinates do not behave as unit-gain accumulator states. In both FOF and ADS, the fixed update D(n_t)+u_(t+1) predicts the next observed D(n_(t+1)) worse than persistence in 12/12 sessions and all 5 rat means. All filtered/delayed sensitivities retain that direction.

Retire this point-decoder candidate as a shortcut to a T2 mechanism certificate. The scoped negative finding concerns these frozen observable maps. It does not refute a latent biological accumulator, prove that either region lacks accumulation, falsify UCT C1/U1, or identify biological transition kernels. C2 at the latent mechanism level remains unidentified; C3 is not tested; T2 remains OPEN.

## The executed correspondence candidate
State: D is the R124-J neural-only outer-training partial-ridge map, expressed in the external signed-click coordinate. It uses intercept and neural variables only, with no eventual choice, realized duration or context baseline. Each held-out trial uses its own outer-training map. No new decoder was fitted, no held-out map was rescaled to favor commutation, and all five original outer folds remain whole-trial disjoint.

Input/port: u_(t+1) is the actual signed right-minus-left click increment in the next 50 ms bin. This is an exogenous supplied input; it is not an identified internal reset, projection inhibition or whole-region perturbation.

Time: primary online raw spike support is [t−50 ms,t), available at t. Online filtered sensitivity uses [t−350 ms,t). Delayed sensitivities are physically available at q=t+100 ms while estimating e_t. Relabeling q does not eliminate the in-flight input buffer or identify a Markov state; these sensitivities cannot by themselves certify time/port commutation.

Artificial update: U(a,u)=a+u in signed-count units, with unit gain fixed. This is a simple calibrated algorithmic accumulator, not a frontier-model or R117 decision-noise experiment. External e_(t+1)=e_t+u_(t+1) was checked exactly for all paired rows; that tautological count identity is only an input-coordinate sanity check.

## Observed-state transition result
The held-out target here is the next observed decoded state, not the next external count. All predictions use the same pairs. Persistence, reset/recent-only, a training constant, and a free ARX fitted only to outer-training observed trajectories are retained.

| Online raw region | Unit update MSE | Persistence MSE | Training constant MSE | Free ARX MSE | Unit update worse: rats / sessions |
|---|---:|---:|---:|---:|---|
| FOF | 8.460103 | 4.820242 | 5.698613 | 3.695741 | 5/5; 12/12 |
| ADS | 7.154269 | 3.256836 | 2.839085 | 2.302280 | 5/5; 12/12 |

The unconstrained ARX predicts this observable target better than the unit update, but fitting it neither identifies a biological kernel nor passes C2. Its training states use a map fitted on that outer training set; its scores are diagnostic comparisons, not an independently cross-fitted discovery of mechanism.

The external-next-count comparison is a different target. Primary online raw fixed-update MSE is 100.373869 for FOF and 101.324310 for ADS, versus 104.743455 for recent-only. The small improvement does not cancel the failed observed-state update, and those MSEs must not be subtracted from the observed-state MSEs.

## Compatibility with the concurrent R124 metric
After reading the concurrent R124 report, a separately labeled secondary calculation reused the already saved transition table without refitting. It computes SΔ = 1 − mean[(D_next−D_current−u)²] / mean[u²] for each session, then equal session means within rat and equal rat means. Its denominator is the zero-predicted input-increment loss; it is not the observed-state variance or observed persistence loss.

| Channel | Region | Increment skill SΔ | corr(ΔD,u) | Positive rats / sessions |
|---|---|---:|---:|---|
| online_raw | FOF | -1.180228 | 0.027883 | 0/5; 0/12 |
| online_raw | ADS | -0.824063 | 0.004514 | 0/5; 0/12 |
| online_filtered | FOF | -0.327563 | 0.047774 | 0/5; 0/12 |
| online_filtered | ADS | -0.361821 | 0.013728 | 0/5; 0/12 |
| delayed_raw | FOF | -1.496739 | 0.024958 | 0/5; 0/12 |
| delayed_raw | ADS | -1.002073 | 0.010761 | 0/5; 0/12 |
| delayed_filtered | FOF | -0.433696 | 0.055849 | 0/5; 0/12 |
| delayed_filtered | ADS | -0.376413 | 0.047191 | 0/5; 0/12 |

The concurrent R124 audit used the original R122 filtered Lasso OOF states and reported FOF SΔ = −0.475567 and ADS −0.351133. R125 uses freshly executed R124-J ridge maps plus raw/no-future channels; these are related negative checks on the same animals, not interchangeable estimators or added independent animals. The secondary compatibility script was run after the concurrent report was read, and is not mislabeled as a frozen primary analysis.

## Shared output law
For each outer fold, fit one unpenalized logistic law P(right|a)=sigmoid(b0+b1*a) to actual outer-training endpoint external evidence and choices. Transport exactly the same intercept and slope to the neural state on held-out trial endpoints. No separate biological recalibration is fitted. The endpoint is the last eligible 50 ms target within the trial, not a guarantee that every late click has been included.

| Online raw state passed to shared law | Equal-rat log loss, nat/trial |
|---|---:|
| External count algorithmic state | 0.595439 |
| FOF decoded state | 0.674542 |
| ADS decoded state | 0.686178 |
| Outer-training choice-frequency prior | 0.698839 |

The transported state under this shared law is worse than the external count state in 5/5 rat means for each region. Its average improvement over the prior is predictive information under this chosen law, not law equivalence, a mechanism certificate, or evidence of experience. Filtered/delayed law scores are retained in aggregate.json; none equals the external-count reference.

Optimization gradients were checked against the execution tolerance; per-fold success flags, iteration counts and gradients are retained rather than silently treating every optimizer status as identical. The frozen OOF maps replay the saved predictions with maximum absolute discrepancy 1.243e-14. Feature/model/source identity checks gate every session before analysis.

## What is and is not rejected
The rejected operational candidate is the selected noisy point estimate D(n) with unit-gain input and supplied 50 ms clock. Differencing spike-derived estimates amplifies observation noise; ridge shrinkage, omitted neurons/regions, biological processing latency, time aggregation and an unmodeled in-flight input buffer can break pointwise commutation even when some latent dynamics accumulate evidence. A complete causal state cannot be asserted from predictive decoding alone.

The result therefore narrows an attempted mapping. It supports stopping repeated favorable decoder/offset searches on these held-out records. It does not warrant the universal conclusion that no biological–algorithmic mapping exists. A latent stochastic observation/transition model would need independent causal grounding and validation before its kernel could be transported.

## T2 certificate scope
| Clause | Current status | Supported scope |
|---|---|---|
| C0 | LIMITED_PASS | Shared externally defined signed-click input coordinate only. |
| C1 | PARTIAL / UNIDENTIFIED | Weak finite predictive readout; complete constitutive state not identified. This certificate clause is distinct from UCT axiom C1. |
| C2 | FAIL_SCOPED for selected D; latent kernel UNIDENTIFIED | Unit-update observable candidate fails all rat means; no complete biological kernel. |
| C3 | NOT_TESTED | No matched internal intervention outcomes in the twelve recording sessions. |
| C4 | PARTIAL | Observation supports and availability declared; biological delay/buffer and clock correspondence unresolved. |
| C5 | PARTIAL / FAILED selected shared-law equivalence | Held-out law transport scored; selected neural coordinate does not reproduce the count reference. |
| C6 | PROCEDURAL_ONLY | Source, fold, coefficient and result replay; no global intervention-preserving isomorphism. |

E remains latent. T1 functional analogies, T2 mechanism correspondence and T3 constitutive homology remain distinct. No G4 selected-content closure, qualia label, valence/fear measurement, subject-boundary solution or external C1/U1 validation is claimed. Published A/B/C bytes remain unchanged.

## Next work justified by these results
Stop treating another positive decoding score or a new toy theorem as closure. The current evidence excludes certifying these point maps; it leaves a causal identification problem. A next empirical study must first specify an independently supported observation model, biological latency/in-flight input representation and candidate sufficient state; freeze the fitted laws; then test held-out innovations and transition/output predictions under the same support. A stochastic latent model that merely optimizes these same scores would not solve identification.

C3 requires relevant biological perturbation data and a physically justified map from that perturbation to the algorithmic operation. Natural clicks, artificial click insertion, whole-region inhibition, projection inhibition and accumulator reset remain separate operations. The concurrent R124 ledger notes a clinical visual-stimulation dataset as a possible separate domain; its first-party article/data were not reread or analyzed in R125 and it does not replace the unidentified fourth UCT medical manuscript. Do not splice a visual-content intervention into the rat signed-evidence certificate.

## Execution, preservation, and concurrency
The full source recovery, raw/filtered joint fits and failures are documented in the R124-J report. This R125 study executes on the saved real feature matrices and frozen maps, so future replay does not require another Cells.zip download. The exact protocol, code hashes, run log, paired per-transition tables, endpoint output tables, ARX/shared-law parameters and summaries are retained. Secondary increment compatibility is separately recorded. The independent audit_saved_results.py replay recalculates transition MSE and endpoint log loss from all saved tables with maximum discrepancy 3.56×10⁻¹⁵, confirms no duplicate test pairs/endpoints, and does no refitting; see saved_result_audit.json.

Concurrent branch commits through f2f34ca5f5a9738659780729c8a7e8aefe01dbf3 and the R124_Transition_Commutation_Audit_20261006 directory were read and are preserved. The source/concurrency ledger distinguishes direct reading, inherited reading and external material not verified here. New files use distinct directories. HANDOFF.md and MASTER_INDEX.md point to R125 while their R123 versions are preserved byte-for-byte at the same directory level.
