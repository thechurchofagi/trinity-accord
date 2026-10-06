# R125 — Frozen observed-state correspondence attempt
Frozen after the R124 joint-decoding study, before computing these transition/output-law scores. Exploratory continuation, not an independent preregistration.

## Exact selected maps
State map: the existing R124 outer-training neural-only ridge map D(n_t), expressed in externally grounded signed-click units. Use zero-delay raw bins as primary and zero-delay seven-tap filtered bins as sensitivity. No choice, future duration, future spikes, or context baseline enters D. Each held-out trial uses a frozen map from its own outer training fold. A decoded state estimate is not complete biological constitutive state.

Input map: u_(t+1) is the actual signed click increment in the next 50 ms bin. Time map: common supplied 50 ms sequence with explicitly recorded zero-delay observation availability. Candidate artificial update: U(a,u)=a+u. No outcome-specific map or numerical scaling is retuned.

## Transition comparison on real neural trajectories
On adjacent within-trial held-out rows, compare prediction of D(n_(t+1)) by:
1. fixed unit-gain accumulator: D(n_t)+u_(t+1);
2. persistence: D(n_t);
3. reset/recent-only: u_(t+1);
4. training constant;
5. an unconstrained ARX, fitted only to outer-training trajectories.

Also report held-out error against the external next-evidence coordinate for the fixed update versus recent-only. The external identity e_(t+1)=e_t+u_(t+1) is a coordinate sanity check and supplies no biological mechanism evidence. Save all coefficients and paired errors. Normalize errors only with a stated common target variance. Report equal-session-within-rat and equal-rat aggregates, all rats, and no-bin-as-animal inference.

A lower raw/filtered transition score cannot establish absence of latent accumulation: observation noise, ridge shrinkage and omitted neural dimensions may matter. Conversely, smoother trajectories or a fitted ARX do not pass C2. This attempt can qualify or disqualify this observable candidate for further work, but does not identify biological transition kernels or prove an intervention-preserving mechanism correspondence.

## Output-law correspondence
Use the last eligible zero-delay observation within each trial. Fit one logistic output law on outer-training signed external evidence and actual right choices. Transport exactly the same intercept/slope to held-out D(n_last). Compare held-out log loss for an external-count algorithmic accumulator, the transported neural estimate, and a training-choice-frequency prior. This is a restricted, calibrated algorithmic comparison, not the R117 Gaussian/sigmoid noise setup and not a new experiment on a frontier AI model. Do not refit a separate biological output law to make correspondence look stronger.

A single end-of-trial summary does not guarantee sufficiency; withheld late inputs, noise, endogenous readout, and the chosen cohort remain explicit limits. Report optimizer failures.

## Certificate boundary
C0 input grounding remains narrow. Observational transition and output-law errors are not a C2 PASS. C3 is NOT TESTED: no matched biological counterfactual internal intervention is supplied by these recording sessions. Natural clicks, click insertion, whole-region inhibition, projection inhibition and internal reset remain distinct operations. Do not add a pulse-only toy as a substitute for biological intervention data. E stays latent; no T3, qualia, valence, fear, subject-boundary or C1/U1 empirical claim.
## Declared additional latency sensitivity before execution
Also replay the already fitted delayed raw/filtered neural-only maps. Their physical availability is q=t+100 ms; the compared coordinate is e_t. These are retrospective history estimates, not states available at t. A uniform clock relabeling does not remove the in-flight input buffer or make D alone Markov. Scores are retained separately and cannot certify temporal/port commutation. No new decoder is fitted.
