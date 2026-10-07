# A Concrete Body/Tool Intervention Protocol and a Strong Falsifier

## From an abstract UCT profile to an executable, still-limited human design

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, clinical protocol, ethics approval, or executed experiment.

## 1. Question and result

R160 defined an abstract body/tool causal profile but left its intervention fidelity, common error model and falsification rule open. This note fixes one candidate human upper-limb protocol and derives a three-valued decision rule.

The main result is deliberately mixed.

1. A non-invasive tendon-vibration contrast and a visual tool-transform contrast can be crossed in a counterbalanced four-session design with body-only and tool-specific angular readouts.
2. Worst-case aggregation over the other manipulation prevents a main-effect average from hiding a sign-changing interaction.
3. Simultaneous intervals yield mutually exclusive **confirm**, **exclude**, and **unresolved** decisions for the R160 body-dominant predicate.
4. A failed fidelity or washout gate produces **invalid protocol**, not evidence for the `neither` profile.
5. The design grounds a protocol-relative proprioceptive-sensitive role. It does not isolate one pure afferent class, identify complete neural organization, establish familiar felt ownership `F_O`, or validate `B_min`.

This is a concrete advance from a logical profile to an executable falsification contract. It is not a human result.

## 2. Fixed actual domain

Fix healthy adult participants screened under an approved human-subject protocol. Exclude people with a contraindication to local vibration, upper-limb injury, relevant neurological disease, inability to complete the task, or a safety concern identified by the responsible clinician or ethics board. The research workspace does not authorize recruitment or intervention.

Each participant completes four sessions corresponding to body condition `q in {0,1}` and tool condition `r in {0,1}`. Sessions are separated by at least seven days, counterbalanced by a Williams design, and admitted only after a preregistered baseline-return gate. Ruttle et al. reported no retention or interference one week after opposed visuomotor rotations in their studied design; the present baseline gate remains necessary because that result is not a universal washout theorem.

Each session is a distinct family of actual trial tokens. Participant continuity does not identify one unchanged complete organization across sessions. Every admitted trial retains its own `P_omega, I_omega, K_omega, D_omega, Phi_omega, h_omega`.

## 3. Candidate interventions

### 3.1 Body-pathway manipulation `J_B`

`q=1` applies 100 Hz vibration in ten-second bursts over a preregistered wrist-flexor tendon; `q=0` applies the same device, nominal frequency, acoustic masking, contact duration and measured acceleration over a nearby bony control site. The exact anatomical site, amplitude envelope, duty cycle, contact force tolerance and stop rules must be fixed by the approved protocol and logged. A published healthy-participant study used 100 Hz wrist tendon vibration for ten seconds and obtained movement illusions; this motivates feasibility but does not prove selective muscle-spindle isolation.

The manipulation is called **proprioceptive-sensitive**, not purely proprioceptive. Tendon vibration also supplies cutaneous and mechanical signals. The bony-site control and independent manipulation check reduce, but do not eliminate, that confound.

### 3.2 Tool-transform manipulation `J_T`

`r=1` applies a clockwise or counter-clockwise 30-degree visual rotation between a hand-held manipulandum and its endpoint cursor; `r=0` uses the identity transform. Rotation sign is randomized and sign-flipped before aggregation. Device telemetry logs the applied matrix, latency, hand path and cursor path. Thirty-degree rotations and angular endpoint measures are directly represented in primary visuomotor-learning protocols.

The manipulandum is the declared tool for this protocol. `J_T` grounds a visual tool mapping, not an anatomical tool member and not ownership.

### 3.3 Reinduction and order

One readout can wash out or contaminate the other. Therefore each session contains two matched induction blocks: one immediately followed by the body readout and one immediately followed by the tool readout. Block order is counterbalanced, and the relevant manipulation is re-established before the second readout. A session-level readout-order term is retained in the model and cannot be discarded after unblinding.

## 4. Readouts that do not use ownership reports

### 4.1 Body-only readout `Y_B`

After the declared induction block, the vibration stops and the hand releases the tool. With the right hand occluded and passively placed at a preregistered location, the participant points with the visible left index finger to the felt right-hand location on a calibrated horizontal surface. The raw endpoint is converted to signed angular localization error. No statement of ownership, agency, confidence or “this is my hand” enters the classifier.

This adapts an established proprioceptive-guided localization method. It remains a finite psychophysical response, not direct access to complete experience.

### 4.2 Tool-specific readout `Y_T`

Immediately after its matched induction block, the participant retains the same manipulandum and performs preregistered no-cursor probe reaches. The raw measure is angular endpoint deviation relative to the target, sign-aligned to the imposed rotation. These probes estimate persistence of the installed tool transformation. They are not a body-ownership report and are not assumed to reveal complete tool representation.

### 4.3 Common normalization

Let `M=30 degrees`, fixed by the programmed transform. For either readout, define a participant/block score

\[
Z_j=\min\{1, |E_j-E_{j,baseline}|/M\},\qquad j\in\{B,T\}.
\]

Thus both readouts lie in `[0,1]` under a declared physical angular reference. Clipping, the baseline estimator, number of trials, target set, artifact rule and missing-data policy are fixed before target unblinding. A sensitivity analysis reports unclipped degrees but cannot replace the primary score after inspection.

Common numerical scale does not imply common phenomenology. It only makes the R160 inequalities defined.

## 5. Interaction-robust effect profile

Let

\[
\mu_{jqr}=\mathbb E[Z_j\mid Y_j,q,r]
\]

for admitted protocol instances. Define the eight conditional simple effects

\[
\begin{aligned}
d^{B}_{j}(r)&=|\mu_{j1r}-\mu_{j0r}|,\\
d^{T}_{j}(q)&=|\mu_{jq1}-\mu_{jq0}|.
\end{aligned}
\]

Instantiate the R160 profile conservatively as

\[
\begin{aligned}
a&=\min_r d^B_B(r), & x&=\max_q d^T_B(q),\\
b&=\max_r d^B_T(r), & y&=\min_q d^T_T(q).
\end{aligned}
\]

The diagonal effects use a minimum: the intended effect must survive both levels of the other manipulation. The cross-effects use a maximum: the strongest cross-modulation counts against a dominance claim. This does not require independence and permits overlap. It prevents a positive and negative cell effect from averaging to an apparently small main effect.

Let simultaneous confidence intervals for each simple-effect magnitude be `[L_s,U_s]`, with familywise coverage at least `1-alpha`. Valid aggregate bounds are

\[
\begin{aligned}
L(a)&=\min_r L[d^B_B(r)], & U(a)&=\min_r U[d^B_B(r)],\\
L(x)&=\max_q L[d^T_B(q)], & U(x)&=\max_q U[d^T_B(q)],
\end{aligned}
\]

and analogously for `b,y`. These are bounds for the specified min/max estimands; they are not post-hoc selected cells.

## 6. Fidelity gate

Classification is admissible only if all six preregistered gates pass:

1. `F_B-delivery`: accelerometer/contact logs meet the active and control vibration tolerances;
2. `F_T-delivery`: telemetry confirms the programmed transform and latency tolerance;
3. `F_cross`: tool software does not change with `q`, and vibration delivery does not change with `r`, within equivalence bounds;
4. `F_washout`: pre-session body and tool baselines return within the fixed equivalence region;
5. `F_B-sensitive`: an independent calibration block shows the expected tendon-versus-bony-site kinesthetic displacement above its manipulation-check margin;
6. `F_T-sensitive`: an independent early-exposure block shows rotation-linked cursor error above its manipulation-check margin.

Calibration outcomes do not enter `Y_B` or `Y_T`, and ownership reports never define a gate. If any gate fails, the output is `INVALID_PROTOCOL`. It is logically wrong to turn failed delivery, failed washout or nonresponsive manipulation into a `neither` profile.

The gate does not prove afferent purity. Residual cutaneous stimulation, strategic compensation, attention and task-order effects remain explicit alternatives.

## 7. Confirmation, strong exclusion and unresolved middle

Fix `epsilon>0` before target unblinding. The R160 confirmation rule remains

\[
C_B:\quad L(a)>\epsilon\ \land\ L(a)-U(x)>\epsilon.
\]

Add a **strong exclusion** rule

\[
E_B:\quad U(a)\le\epsilon\ \lor\ U(a)-L(x)\le\epsilon.
\]

If the fidelity gate passes:

- report `BODY_DOMINANT_CONFIRMED` when `C_B` holds;
- report `BODY_DOMINANT_EXCLUDED` when `E_B` holds;
- otherwise report `BODY_DOMINANT_UNRESOLVED`.

`C_B` and `E_B` cannot both hold because every valid interval has `L<=U`. If intervals are replaced by nested narrower intervals, an already confirmed or already excluded decision cannot revert to unresolved or to its opposite. The exact verifier checks 225 rational interval pairs and 4,900 nested-interval cases at `epsilon=1/4`; all checks pass.

This is a real falsifier for the fixed **protocol candidate**: under valid fidelity and coverage, `E_B` excludes the preregistered R160 body-dominant inequality. It does not falsify basal experience, C1, every possible body organization, or familiar ownership.

The tool-dominant predicate receives the symmetric rule with `y,b`.

## 8. Error and sample-size contract

The primary practical analysis should use participant-clustered simultaneous intervals for all eight conditional simple effects, with its resampling method, number of resamples, seed policy, multiplicity control, exclusions and estimand fixed in advance. Because no pilot variance or raw dataset exists in this round, no convenient sample size is invented.

For audit only, participant-level paired contrasts in `[-1,1]` admit a worst-case Hoeffding/union bound. With `m=8` contrasts and familywise `alpha`, radius

\[
r_n=\sqrt{2\log(2m/\alpha)/n}
\]

covers every signed simple effect simultaneously. Requiring `2r_n<=gamma` to resolve a dominance slack `gamma` gives

\[
n\ge \left\lceil\frac{8\log(2m/\alpha)}{\gamma^2}\right\rceil.
\]

At `alpha=.05`, this worst-case bound requires 4,615, 2,051, 1,154 and 739 complete participants for `gamma=.10,.15,.20,.25`, respectively. These deliberately large values expose that distribution-free logical validity is not practical power. A feasible confirmatory study needs an independent variance pilot or a justified parametric/hierarchical model, frozen before target analysis. Failure to fund the conservative sample is not a theoretical refutation.

## 9. C1 and the selected-mineness boundary

For each admitted trial token, a physically grounded relation in the complete `K_omega` remains conditionally transported by that token's C1 isomorphism. The factorial estimands compare distributions across tokens and sessions. They are not one formula evaluated in one unchanged `D(P)` and `Phi(P)`.

Therefore neither `C_B` nor `E_B` directly establishes a phenomenal ownership contrast. A claim about familiar `F_O` still requires:

- a fixed selected target `Psi_v` or `F_O`;
- a separately defended sufficiency/reflection bridge;
- valid measurement assumptions;
- no post-hoc token, view or bridge rescue.

The protocol may be run without linguistic ownership reports. That strengthens separation between physical roles and report, but it does not magically measure experience. C1 retains its consciousness-specific explanatory status and is not derived from the experiment.

## 10. Counterexamples and retained thought experiments

### Ancestor and formation

An organism may acquire tendon-sensitive body localization before learning any rotated visual tool mapping. The protocol can then yield body dominance without making that capacity a gate for the organism's basal experience. Role: formation-order test.

### Abacus and calculator

Two people can return the same answer while one has a robust tool-transform aftereffect and the other uses an external lookup with no installed mapping. Equal output therefore does not fix `y` or `T_Pi`. Role: behavior-equivalence counterexample.

### Human-realized agent

A group can implement the cursor transform while each human's proprioceptive manipulation remains local to a member. Naming the group endpoint “its hand” does not satisfy `F_B-delivery` or establish a single complete bearer. Role: grounding and bearer test.

### Copy, swap and memory

Copy the controller and swap the rotation table while preserving its report history. `Y_T` can change while every stored ownership sentence remains fixed. Conversely, swap sentences without changing the transform. Role: report/profile dissociation; no phenomenal-transfer conclusion.

## 11. What failed or remains open

1. Tendon vibration is not a pure pathway intervention; the present controls do not prove selective spindle causation.
2. The body localization action remains a finite psychophysical response and can contain attention, response-mapping and contralateral-hand error.
3. Tool probes and body probes require separate reinduction; order and decay cannot be assumed absent.
4. The fixed 30-degree normalization is interpretable but conventional; another preregistered scale defines another protocol.
5. The exact worst-case sample bound is too large for a routine study. No pilot variance or practical power calculation is available.
6. The four sessions do not share one complete organization or one `h`.
7. No complete neural realization, `B_min`, `F_O`, proof-assistant certification or human dataset is supplied.
8. The searched sources support components, not the complete crossed protocol; priority/exhaustiveness is unverified.

## 12. Contribution and next question

The substantive contribution is the combination of a concrete crossed manipulation, interaction-robust min/max estimands, a fidelity-invalid state and a strong exclusion rule. It repairs a common loophole: an unsuccessful manipulation may no longer be counted as evidence that neither body nor tool organization is present.

The next exact question is not another classifier. It is whether a practical, independently justified variance/measurement model can shrink the uncertainty enough to distinguish `CONFIRM`, `EXCLUDE` and `UNRESOLVED` without using ownership reports, while retaining the six fidelity gates. This requires either an existing suitable dataset or a prospective pilot; no such data were analyzed here.

## 13. Sources and attribution

- UCT I v1.2 §§8.11–8.14, 10.1–10.3, 11 and 14.7–14.10 supply the physical-witness, bridge, no-post-hoc-rescue and subject/quality boundaries.
- Ruttle et al. (2016), DOI `10.1371/journal.pone.0163695`, provide a full primary example of 30-degree rotated-cursor training, no-cursor reach aftereffects, proprioceptive hand localization and angular normalization.
- Mostafa et al. (2019), DOI `10.1371/journal.pone.0221861`, show that passive visuoproprioceptive discrepancy can shift hand localization and reach aftereffects, warning that tool manipulation can cross-modulate a body readout.
- *Influence of virtual reality visual feedback on the illusion of movement induced by tendon vibration of wrist in healthy participants* (2020), PMCID `PMC7678999`, provides a primary 100 Hz, ten-second wrist-tendon-vibration implementation and demonstrates visual-context dependence.
- R160's Cardinali, Martel, Maravita, Holmes and Weser sources remain relevant to post-tool body effects, distal readouts, attention confounds and ownership/tool dissociation.

Tendon-vibration methods, visuomotor adaptation, simultaneous confidence bounds, Hoeffding's inequality and factorial contrasts are established methods. The project contribution is their typed integration into this UCT application and the explicit invalid/exclude distinction. No historical-method priority is claimed.
