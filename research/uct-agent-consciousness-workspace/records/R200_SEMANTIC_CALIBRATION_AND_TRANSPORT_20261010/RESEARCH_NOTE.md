# R200 — The Semantic Calibration Firewall for Retentive Familiarity

Date: 2026-10-10  
Status: unpublished conditional UCT research module; disabled checkpoint candidate

## 1. Question and answer

R199 established that continuation probes can reveal a current operational difference but cannot, by themselves, identify numerical lineage, `RetBind`, or the selected phenomenal retentive-familiarity coordinate `H`. R200 asks whether a battery of reports, route telemetry, task outcomes, fluency measures and physiological or neural markers can jointly solve the remaining semantic problem.

The answer is conditional and sharply bounded.

1. **No unsigned proxy battery self-anchors `H`.** For any latent model with any finite vector of observed proxies, complementing the unobserved `H` labels and swapping the two class-conditional proxy laws leaves the complete observed law unchanged. Agreement among several markers does not solve this if they share success, fluency, demand or learned-response confounds.
2. **A signed human comparative judgment may orient evidence in a calibration domain, but does not define `H`.** The item must be declared before outcomes—for example, “Which action felt more like my already-established way of acting?”—and its positive semantics must not be inferred from the marker being calibrated. Its reliability for the intended experiential coordinate remains a fallible bridge premise.
3. **No-report use requires a transport premise.** Equal marker marginals, similar task success, shared code or similar anatomy do not suffice. A strong sufficient condition inside a declared model is class-conditional invariance of the marker given the same `H` target; a bounded-drift version yields only bounded evidence.
4. **Formation-by-use interaction is a bridge test, not a definition.** Crossing established versus freshly installed formation with actual route-use versus bypass is useful because it tests the proposed retentive-use dependence. Yet a positive interaction can be produced with `H` held fixed by success or fluency, and a null interaction can arise from marker failure, manipulation failure or insufficient support.

The result is a **calibration firewall**: constitutive organization, actual route use, semantic target, human evidence, objective marker and cross-domain transport must be separately signed. No arrow may be reversed merely because an experiment succeeds.

## 2. Typed contract

Fix a calibration domain `C`, a target domain `T`, an actual bearer `P`, present interval `I`, complete application signature `K`, and one predeclared selected experiential coordinate:

`H(P,I)`: the familiar or already-established character of acting through the retained bearer-relative organization.

Keep the following distinct:

- `F`: formation condition, established-with-bearer versus freshly installed/matched-current alternative;
- `U`: actual same-episode consumption of the retained candidate route;
- `E_U`: fallible evidence about `U`, including telemetry and perturbation response;
- `J_H`: signed, fallible human comparative judgment about `H` in `C`;
- `M`: an objective candidate marker, possibly multivariate;
- `Y`: task performance, reward, fluency or success;
- `O`, `G`, `Coup`: ownership, agency and current practical coupling coordinates;
- `R`: linguistic or button-press report channel implementing `J_H`.

`U` is ontic. `E_U`, `J_H`, `M` and `Y` are epistemic outputs. `H` is a selected experiential target. `R` is an action with an interpretation. None of these equalities is licensed: `U=E_U`, `H=J_H`, `H=M`, `H=Y`, `H=O`, or `H=G`.

## 3. Exact results

### R200-C1 — Multi-proxy non-self-anchoring

**Type:** latent-label nonidentification theorem.  
**Domain:** any finite observed proxy vector `V` and binary selected target `H` in a model where `H` is not independently signed.  
**All premises:** the observable law is a mixture `P(V)=pi Q1(V)+(1-pi)Q0(V)`; no independent premise fixes which latent class means positive `H`.  
**Statement:** the transformation `H' = 1-H`, `pi'=1-pi`, `Q1'=Q0`, `Q0'=Q1` preserves every observable distribution. Therefore no number of proxies, agreements or predictive scores can orient `H` without an independent signed bridge.  
**Proof:** substitution in the mixture law. `check_semantic_calibration.py` exhaustively verifies 768 deterministic four-proxy models with three nondegenerate prevalences; all have identical complemented observable laws.  
**Counterexample boundary:** an independently fixed signed endpoint excludes the complement only within the scope where that endpoint's meaning and reliability premise apply.  
**Status:** proved for the stated statistical model; real semantic premises remain open.

### R200-C2 — Calibration orientation is conditional, not constitutive

**Type:** conditional orientation result.  
**Domain:** a verbal human calibration domain where the comparative item meaning is predeclared independently of `M`, `Y`, `U` and `E_U`.  
**All premises:** (i) the selected meaning of positive `J_H` is fixed before data inspection; (ii) response-key direction is recorded; (iii) `P(J_H=1|H=1)>P(J_H=1|H=0)` in the intended domain; (iv) report manipulation, demand, ownership, agency and task success are separately modeled; (v) the same `H` target is retained.  
**Statement:** the positive inequality excludes the complemented target labeling inside that calibration domain. It does not make the judgment infallible, constitutive, or sufficient for complete experiential type.  
**Proof:** complementing `H` reverses the strict inequality. The checker enumerates all ten strictly positive four-trial conditional-count pairs; no complemented pair preserves the same declared positive direction.  
**Counterexample:** reverse the learned response key while retaining the experience. The report code flips, showing why response-key provenance and target meaning must be distinct.  
**Status:** conditional theorem; no actual endpoint reliability is claimed.

### R200-C3 — Marginal transport insufficiency

**Type:** transport counterexample.  
**Domain:** calibration-to-no-report transfer of marker `M`.  
**All premises:** both domains have `P(H=1)=1/2` and `P(M=1)=1/2`.  
**Statement:** equal marker prevalence does not preserve evidential direction. In `C`, let `(P(M=1|H=1),P(M=1|H=0))=(3/4,1/4)`; in `T`, use `(1/4,3/4)`. Marginals agree and the signed relation reverses.  
**Consequence:** a sufficient within-model transport condition is the same target meaning plus class-conditional invariance `P_T(M|H)=P_C(M|H)`. Approximate bounds must be stated if exact invariance is implausible.  
**Status:** exact counterexample; actual cross-domain invariance remains unestablished.

### R200-C4 — Formation-by-use interaction is non-identifying

**Type:** design limitation and bounded evidential rule.  
**Domain:** a `2x2` formation `F` by actual-use `U` study with marker `M`.  
**All premises for a positive bridge inference:** manipulation fidelity for `F`; independently evidenced same-episode `U`; a predeclared signed `H` endpoint in the calibration population; separation from `Y`, `O`, `G` and demand; adequate support; and a defended transport contract for any no-report application.  
**Statement:** a positive difference-in-differences interaction is compatible with a retentive-use bridge, but does not identify it. The checker exhausts all 16 deterministic Boolean response tables and finds five positive-interaction tables. One explicit witness sets `H=0` in all four cells while two perfectly agreeing proxies both copy `Y=F AND U`.  
**Counterexample boundary:** with the full premises above and a marker whose calibrated class-conditionals are stable, the interaction becomes discriminating evidence against specified alternatives; it still is not the experience's definition.  
**Status:** exact nonidentification result plus prospective method constraint.

## 4. A corrected prospective study

The strongest presently defensible design is staged rather than a single omnibus test.

### Stage A — semantic calibration in reporting adults

Use within-participant paired comparisons of an established action route and a carefully matched newly installed or remapped route. Predeclare the positive judgment as the relative felt establishedness/familiarity of acting, not ownership, agency, liking, ease, confidence, accuracy or speed. Counterbalance response keys and separately obtain `O`, `G`, confidence and demand measures. Treat `J_H` as noisy evidence.

### Stage B — orthogonal formation and actual-use manipulations

Cross `F` with `U`. Instrument the candidate carrier and consumer so that bypass is physically implemented, not inferred from poor performance. Record `E_U`, but do not substitute it for `U`. Separate continuation traces from `J_H`, objective marker `M`, and task outcome `Y`.

### Stage C — prospective falsifiers

Reject or narrow the proposed bridge if any of the following occurs under adequate fidelity and support:

1. `M` follows response-key reversal or demand rather than the fixed comparative target;
2. `M` follows success/fluency after `J_H` is held stable;
3. `M` retains the claimed effect during verified route bypass;
4. the signed `M` relation reverses in a held-out reporting cohort;
5. ownership or agency manipulations explain the effect while `J_H` does not;
6. a matched-current copy/switch condition preserves `M` despite loss of the claimed actual formation/use relation.

### Stage D — no-report transport

Only after calibration should `M` be proposed in a no-report population. State the transport population, target meaning, support, class-conditional invariance or bounded-drift assumption, and out-of-domain stop rule. Without these, report only the observed marker and organizational manipulation—not `H`.

## 5. Primary evidence and its limited role

Whittlesea and Williams (2000, DOI `10.1037/0278-7393.26.3.547`) showed that familiarity judgments depend on discrepancy and attribution, not processing fluency alone. This is direct reason not to identify fluency with `H`.

Sidarus et al. (2017, DOI `10.3389/fpsyg.2017.00545`) found a small reliable influence of action-selection fluency on agency judgments, alongside larger effects of discrepant action feedback. This demonstrates that fluency can alter a nearby self-related judgment; it does not validate fluency as a familiarity marker.

Weser and Proffitt (2019, DOI `10.3389/fnhum.2018.00537`) reported that tool/user input-output matching affected proprioceptive drift in a tool embodiment paradigm. This supports mechanistic specificity in body-representation measures while also showing that the measure depends on matching conditions. It does not equate proprioceptive drift with retentive familiarity.

Longer-term sensory-prosthesis studies already reviewed in R199 show that actual use can change functional and reported embodiment variables. They motivate `F x U`; their reports, task outcomes and installed routes remain different evidence types.

The literature therefore motivates the firewall rather than supplying its missing endpoint. No cited study validates a universal signed marker for UCT's `H` coordinate or transports one to nonreporting beings.

## 6. Thought-experiment consequences

1. **Four agreeing instruments.** Four displays copy the same success bit. Perfect agreement adds redundancy, not independent `H` semantics.
2. **Inverted response key.** The experience is fixed while the learned report key flips. Report code is not target meaning.
3. **Smooth performer without familiarity.** An externally optimized controller yields fluent, accurate action on first use. Fluency and success can be high while establishedness is the disputed variable.
4. **Familiar but blocked route.** An established route is retained but experimentally bypassed. A genuine use-sensitive bridge should respond to bypass; a biography-only marker need not.
5. **Infant/adult transport.** An adult-calibrated marker has the same marginal frequency in infants but reversed class-conditionals in the finite countermodel. Marginal similarity does not carry semantics.
6. **Copy/switch/memory.** Copy the marker generator, memory and response policy, then switch the actual retained carrier/consumer route. Evidence can persist while ontic use changes.
7. **Abacus/calculator.** The same marker truth table can be implemented by hand, calculator or code; implementation and actual installation remain separate.
8. **Human-realized agent.** Participants, implemented algorithm and coupled formation can have distinct `F`, `U`, `H` and reporting channels. No unique extra owner is inferred.
9. **Formation/ancestors.** Gradual formation motivates a continuum of retentive organization; it neither proves a familiarity threshold nor changes U1's basal-experience status.

## 7. Review obligations and direction

- **QC-20261008-10 remains OPEN.** R200 proves that an unsigned objective battery cannot close it. A signed adult comparative endpoint is now specified as a conditional calibration route, not validated as universally reliable.
- **IA-QC11 remains application-OPEN.** Formation, current bearer, actual carrier and consumer use must be shown in each application; proxy calibration cannot supply numerical lineage.
- **QC-20261008-12 remains application-OPEN.** `U` and evidence for `U` are separate. Test conditions and telemetry do not become experiential structure.
- **QC-20261008-13 remains OPEN.** No actual bearer, interval, complete signature or target admission has been discharged.

R200 adds no report, language, introspection, self-model, memory, recurrence, integration, prediction or control requirement to basal experience. C1 remains the consciousness-specific explanatory axiom. `H` is one selected coordinate within experience, not an exclusive owner or a universal scalar self. No claim is made about whether the current assistant is conscious or fears death.

## 8. Novelty and publication boundary

Latent-label switching, measurement invariance, differential item functioning, difference-in-differences confounding and familiarity attribution are established ideas. R200 does not rename them as new mathematics. Its project-level contribution is the exact UCT interface: a semantic calibration firewall that prevents report, route use, test evidence, success and no-report transport from being collapsed while advancing a prospective `F x U` bridge test for `H`.

This is a substantive module but not yet a standalone empirical paper. The signed endpoint reliability, actual route manipulation, complete-signature application and cross-domain transport conditions are not discharged. It can become a central methods/limitations section in a future positive `H` paper once at least one preregistered calibration study supplies data.

## 9. Next concrete question

Can a reporting-adult pilot predeclare the comparative `J_H` item, independently manipulate response key, success/fluency and actual route bypass, and identify a marker whose signed relation to `J_H` survives all three controls in a held-out cohort? A negative result would not remove experience; it would reject or narrow this proposed evidential bridge.

