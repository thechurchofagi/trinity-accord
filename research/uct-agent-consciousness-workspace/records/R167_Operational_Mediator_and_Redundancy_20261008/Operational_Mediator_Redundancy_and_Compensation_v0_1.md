# Operational Mediator, Redundancy, and Compensation

## A same-episode architecture for discharging R166 W2–W5 without report-defined ownership

**Round:** R167  
**Status:** exact design result and countermodels; no human study, apparatus validation, neural identification, C1 proof, or `B_min` validation  
**Scope:** one declared, instrumented participant–device episode and its bounded intervention closure

## 1. Question and answer

R166 specified six jointly required witnesses for saying that a selected Anchor–Bind–Use relation is actually installed in one token. It deliberately did not instantiate W2–W5. This round asks whether those clauses can be made operational in one ethically admissible design while allowing redundancy and compensation.

The answer is conditional but constructive. Use an instrumented, reversible participant–device loop in which the candidate mediator is a physically realized controller state, not an inferred hidden neural representation. Within one uninterrupted episode, independently record and perturb (i) a physical anchor, (ii) the live mediator state, (iii) declared backup paths, and (iv) the consumer routing. A finite contextual intervention matrix prevents a redundant backup from making one mediator cut look negative. A pre-adaptation sample prevents later compensation from erasing an early causal contribution. These operations can discharge W2–W5 for the declared operational relation if identity, delivery, fidelity, exclusion, safety, and measurement clauses pass.

They do **not** establish that the operational state is a complete neural body representation, that the declared backup set is complete, that the relation is necessary for experience, or that its experiential counterpart has familiar felt-mineness. C1 and an independent `B_min` remain separate.

## 2. Typed episode contract

Let an episode be

\[
\mathcal E=(P,I,\tau,\Sigma,K,D,\rho,\mathcal J,\mathcal M),
\]

where `P` is the actual participant–device process, `I=[t_0,t_1]` is one uninterrupted episode, `tau` supplies bearer/time/sort tags, `Sigma` is the complete physical signature admitted for this application, `K` the abstract organizational model, `D` the candidate Anchor–Bind–Use structure, `rho` the actual realization map, `J` the declared reversible intervention family, and `M` the measurement and fidelity record. Interventions create adjacent subintervals of one bearer lineage; they do not license the false statement that every intervened subinterval has an identical complete organization.

The same-token contract requires:

1. one continuous physical bearer lineage and clock;
2. unchanged participant and device identity, wiring, code version, realization map, and declared signature except for the named intervention variable;
3. no reset, retraining, substitution of a copied run, or cross-subject averaging;
4. randomized, short, reversible interventions inside a predeclared safety envelope;
5. explicit subinterval indices, intervention provenance, process identifiers, and state lineage;
6. tokenwise application only: every C1 transport claim is confined to the actual subinterval to which all premises apply.

Thus “same token” means same actual bearer lineage under controlled local changes, not numerical identity of the entire microstate across interventions.

## 3. Operational anchor–mediator–consumer architecture

One admissible prospective implementation uses a non-invasive manipulandum, haptic or robotic interface. It is a design object, not a report of an executed experiment.

- **Anchor `r_t`.** A physically independent arm/joint/tool state measured by calibrated kinematic and force sensors. Small safe displacements or haptic pulses provide `J_r`. Physical grounding is established without an ownership report.
- **Mediator `k_t`.** A logged, physically instantiated live estimator state in the controller, for example a body-frame or effector-frame estimate computed from the current sensor stream. Its memory address, update rule, clock, and actual consumer reads are inspectable. This is not renamed as a hidden neural body representation.
- **Declared backup vector `z_t=(z_1,...,z_m)`.** Alternative controller states or direct sensor routes that can reach the same consumer. Every admitted backup has an independently controllable route gate.
- **Consumers `u_t`.** Predeclared haptic, display-stabilization, or reach-correction outputs that actually read from the live route.
- **Anchor intervention `J_r`.** A calibrated reversible displacement/pulse plus sham, with independent delivery and sensor-fidelity checks.
- **Mediator intervention `J_k`.** A brief live state clamp, state swap, or signed offset applied after raw sensing and before consumer read, while logging unchanged raw input and output code.
- **Cut/bypass intervention `C_k`.** A route gate that prevents consumer reads from `k`, together with matched direct/raw-sensor, replay, or shadow-state alternatives.

This architecture supplies a real intervention target for W4 and W5. A merely inferred neural latent variable would not: sensory perturbation is upstream of it and motor perturbation is downstream, so neither by itself implements `do(k)`.

## 4. Contextual redundancy theorem

Fix one pre-compensation time slice. Let the declared consumer be a deterministic Boolean function

\[
u=f(k,z),\qquad k\in\{0,1\},\ z\in\{0,1\}^m.
\]

For each backup context `z`, define the controlled contrast

\[
\Delta_k(z)=f(1,z)-f(0,z).
\]

**R167 contextual-use criterion.** Relative to the declared finite intervention closure, `k` contributes to `u` iff

\[
\exists z\in\{0,1\}^m:\Delta_k(z)\ne 0.
\]

It is contextually indispensable iff the contrast is nonzero for every declared context. Contribution and indispensability must not be conflated.

The proof is definitional in one direction and exhaustive over the finite context set in the other: if no context changes under a change in `k`, `f` is extensionally independent of `k`; if one context changes, `k` contributes there. The checker enumerates every Boolean function for zero through three declared backups (65,812 functions total).

### Single-cut false negative

For `u=k OR z`, testing only with `z=1` yields

\[
f(1,1)=f(0,1)=1,
\]

although with `z=0`, `f(1,0)=1` and `f(0,0)=0`. A negative cut in one uncontrolled redundant context does not refute installed use. The contextual matrix repairs this particular error relative to the declared backup variables.

## 5. Compensation timing obstruction

Let the primary path initially be active, `k_0=1`, and the backup initially inactive, `z_0=0`, with

\[
u_t=k_t\lor z_t,
\qquad z_{t+1}=z_t\lor c_t,
\]

where `c_t=1` records that the primary route has been cut. At baseline, `u_0=1`. If `k` is cut at `t=0`, the immediate pre-adaptation output is `u_0'=0`; after the backup update, `z_1=1` and `u_1'=1`. The late endpoint equals baseline even though the primary route made a real immediate contribution.

Therefore a long-block endpoint can produce a second false negative. The protocol must distinguish:

- a short randomized pulse read before the declared compensation update;
- the compensation trajectory and changed backup state;
- a later adapted endpoint.

This is not a demand that all physical systems use the stated Boolean dynamics. It is an exact countermodel to the inference “no late difference, therefore no prior installed use.”

## 6. Closure-relative triage

For a named candidate relation and declared intervention closure, apply the following priority order.

1. **INVALID_PROTOCOL** if token-lineage, safety/admissibility, intervention delivery, measurement fidelity, temporal order, or route-exclusion checks fail.
2. **PRIMARY_USE_SUPPORTED_RELATIVE_TO_CLOSURE** if at least one valid pre-compensation backup context has a nonzero `k` contrast and the realized read/route audit agrees.
3. **COMPENSATION_DETECTED** as an additional flag if an immediate contrast is followed by its disappearance together with a measured backup-state change.
4. **CANDIDATE_REFUTED_RELATIVE_TO_CLOSURE** only if every declared context was validly tested, all contrasts are inside the predeclared null bound, the declared routes are interventionally closed for the target claim, and sensitivity is adequate.
5. **UNRESOLVED** otherwise.

“Relative to closure” is essential. Any finite declared backup list can omit an unmeasured route `w` that masks all tested contrasts. No finite interface proves completeness of the actual organization. A null result without closure and sensitivity is unresolved, not evidence of no experience.

## 7. Discharge table for R166 W2–W5

| R166 clause | Prospective R167 witness | What remains required |
|---|---|---|
| W2: independent physical anchor | calibrated kinematic/force anchor and intervention, defined without ownership report | delivery, calibration, locality, and safety must pass in the actual token |
| W3: endogenous binding and actual use | logged live estimator update plus verified consumer reads and route provenance | the state must be live, not a shadow log or replay-only correlate |
| W4: local perturbation propagation | `J_r` and `J_k` pulses with predeclared signed propagation and fidelity checks | off-target paths and timing must be bounded; a sensory perturbation alone is not `do(k)` |
| W5: mediation/cut versus bypass | contextual matrix over `k` and declared backups, plus route cut/bypass and pre-compensation read | conclusions remain relative to declared closure; hidden routes and failed exclusion leave `UNRESOLVED` |

W1 and W6 are not replaced: the same sorted `P/I/K/D/rho` bookkeeping and bounded status discipline remain jointly necessary. Hence the R167 package instantiates, but does not weaken, the R166 all-of contract.

## 8. Exact application boundary

If the token-lineage contract passes, the operational architecture is actually realized, all R166 W1–W6 clauses pass, and the contextual/temporal checks return support, then the declared Anchor–Bind–Use relation is supported as actually installed in that participant–device episode. R159 may then transport the selected K-relation to its C1 experiential structural counterpart only for the identical admitted token/subinterval and sorted parameters.

The conclusion does not entail:

- that `k` is a neural or complete body representation;
- that no omitted route exists;
- that the relation is necessary for experience or a threshold for basal experience;
- that the participant’s report is true merely because it agrees with the output;
- that the experiential counterpart has familiar bodily mineness;
- that one unique owner excludes nested or overlapping processes.

The last semantic step still requires an independently justified `B_min`. C1 remains an explanatory axiom rather than a result of the intervention.

## 9. Four preserved thought-experiment families

1. **Ancestor/formation.** A primitive loop may have an anchor–mediator–consumer relation before redundant routes form; later compensation changes detectability, not the prior existence of basal experience.
2. **Abacus/calculator.** A displayed register can mirror the live calculator state while never being read. A live-route swap/cut, not agreement of traces, distinguishes operative mediation from a shadow log.
3. **Human-realized agent.** Participant plus instrument can constitute the relevant higher-level process for the operational claim while participant and device sub-processes remain nested and overlapping. No extra exclusive owner is inferred.
4. **Copy/swap/memory.** A copied estimator log can preserve reports and memories while being off-route; conversely a live estimator can be replaced without changing a late compensated endpoint. State similarity and report continuity do not settle actual current use.

## 10. Direction checks

### After result formation

The result is about actual installation of a physical relation, not about maximizing behavioural accuracy or reports. It explicitly separates complete organization, finite interface, abstract model, actual installation, actual bearer, internal status, experiential counterpart, and language report. No basal-experience threshold was added.

### Before preservation

Every positive inference is same-token, interval-indexed, all-of, and closure-relative. The new exact theorems concern finite Boolean models only. Passing code certifies enumeration and consistency, not empirical truth, ethics approval, complete physical realization, C1, or familiar mineness.

## 11. Next exact question

How should the operational mediator architecture be generalized from a finite Boolean context matrix to stochastic, continuous, and partially observed routes while retaining falsifiable closure-relative statuses and a precise bound on undetected redundancy?
