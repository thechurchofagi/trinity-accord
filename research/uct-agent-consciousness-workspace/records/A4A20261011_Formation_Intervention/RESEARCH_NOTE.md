# A4A — Formation intervention after the phenomenal-anchor triage

## 1. Result

A3Z proposed a formation/history contrast as one component of a fallible test for a judgment about the familiar-from-within character of a current action way, `H_way`. Its next-step wording asked whether a formation effect remains after matching motor ease, success, value, expectation, and source/agency feeling. The present result is that this request is not yet a well-defined causal target.

The reason is temporal and organizational. All five proposed matching variables can be produced by the formation intervention. Conditioning on them after formation can (i) select on a common effect and manufacture a residual association, (ii) destroy common support, or (iii) block the retentive/learned route through which formation was supposed to matter. A residual association after such matching is therefore neither automatically a total formation effect nor automatically a direct effect.

This is a substantive correction, not a generic statistics detour. It changes what counts as evidence that formation/history contributes to a body/action familiarity judgment. The strongest currently installable primary target is a randomized **total formation effect**, stratified only by pre-formation variables. Post-formation ease, success, value, expectation, and source/agency judgment should initially be treated as outcomes, fidelity diagnostics, or mediators. A controlled direct effect is a different target and requires physically realizable, route-preserving joint interventions with positivity.

No result here identifies `H_way`. At most, a valid total effect would support formation sensitivity of the installed judgment organization. A null or reversed effect can defeat a preregistered bridge package under all of its premises; a surviving effect still admits A3Z's proxy `W`.

## 2. Typed causal objects

Fix a participant or other actual bearer `p`, an action family `a`, a formation interval `I_F`, a later test episode `e` in interval `I_T`, and a predeclared response `J_H(p,e)` whose content contract is inherited from A3X/A3Z.

- `F`: randomized or otherwise explicitly assigned formation history before the test.
- `C0`: variables fixed or measured before `F` is assigned. Baseline ability and baseline expectations may enter here only with their timestamp recorded.
- `T`: the actual formation-dependent retentive/action route proposed to matter. `T` is an organizational target, not a report or a fitted mediator score.
- `Z=(Z_ease,Z_success,Z_value,Z_expect,Z_source)`: test-episode quantities measured after formation. Their names do not make them pre-treatment covariates.
- `J_H`: the corrected comparative judgment about `H_way`; it is neither `H_way` nor an infallible measure of it.
- `H_way`: the fixed selected phenomenal target. It is not an observed column in the causal table.

The primary total-effect estimand is

`tau_total = E[J_H(F=1) - J_H(F=0)]`.

An observed conditional contrast

`E[J_H | F=1,Z=z] - E[J_H | F=0,Z=z]`

is not, merely by being called residual, a causal direct effect. A controlled direct effect

`tau_CDE(z) = E[J_H(1,z) - J_H(0,z)]`

requires that `do(F=f,Z=z)` denote a coherent physical intervention for both `f`, that the joint intervention preserve the bearer, target episode and declared route question, and that positivity and fidelity hold. It answers a different question from `tau_total`.

## 3. Exact countermodels

### A4A-C1 — a spurious residual after post-treatment matching

Let `F` and an unmeasured cause `U` be independent fair bits, let `M=F OR U`, and let `J=U`. Formation has no total effect: under either `do(F=0)` or `do(F=1)`, `E[J]=1/2`.

Exact matching with common-support trimming retains `M=1`. In that stratum, `E[J|F=0,M=1]=1` and `E[J|F=1,M=1]=1/2`, producing a residual contrast of `-1/2`. Conditioning on the post-formation common effect `M` has created evidence for a formation difference where the total causal effect is zero.

A second XOR model has full overlap in both `M` strata but gives stratum contrasts `+1` and `-1`. A chosen target weighting of `3/4` and `1/4` yields a matched contrast `+1/2` although the total effect remains zero. Thus even with overlap, the matched estimand can depend on a post-treatment target population chosen by the matcher.

### A4A-C2 — matching can remove the organizational path

Let `T=F`, `Z=T`, and `J=Z`. The total formation effect is `1`. Observational exact matching on `Z` is impossible because `Z=F`; common support fails. If an experimenter instead clamps `Z` to either value, then `J` is the clamp and the controlled direct effect of `F` is `0` at both values.

This is not a contradiction. The total effect is fully mediated by the clamped variable. A zero controlled direct effect does not show that formation was organizationally irrelevant; it shows that the intervention removed the route by which formation mattered. If `Z` is ease, expectation, or a source-related state lying on the retentive route, demanding equality of `Z` changes the question.

### A4A-C3 — pre-formation adjustment is a different case

In the exact baseline model, `C0` is measured before randomization, `F` is randomized, and `J=F`. Both `C0` strata retain contrast `1`, as does the marginal population. This elementary positive control does not prove that all baseline adjustment is harmless; it shows why time order and causal role must be declared before matching.

All four finite checks use exact rational arithmetic and pass. They are standard causal-design constructions, not human findings or consciousness measurements.

## 4. Installability contract

A claim of a residual formation effect must choose one of two routes before observing the endpoint.

### Route T — total formation effect

All premises are simultaneous:

1. `F` is actually randomized or its exchangeability assumptions are separately justified.
2. `C0` is timestamped before `F`; no descendant of formation is silently moved into `C0`.
3. The same bearer, action grain, target wording, test window, response coding, and endpoint rule are retained.
4. Formation fidelity is checked by evidence independent of `J_H`.
5. Post-formation `Z` variables are reported as outcomes, diagnostics, or mediators, not matched confounders in the primary total-effect analysis.
6. Missingness and selection after `F` are audited as possible post-treatment selection.

Route T is practically installable as a longitudinal randomized training study. It tests whether the assigned history changes the later judgment organization. It does not isolate a route-independent residual and does not identify `H_way`.

### Route C — controlled direct effect

In addition to clauses 1–4 above, every following premise is required:

1. Each component of `Z` has a physically specified intervention, not merely a regression adjustment or score match.
2. The joint settings `do(F=f,Z=z)` are realizable for both formation arms with nonzero support.
3. The `Z` intervention does not create, erase, write, replay, or bypass `T` unless the estimand explicitly intends that change.
4. The intervention does not directly set `J_H`, its response key, its content interpretation, or the report policy.
5. The distinction between total, controlled-direct, and route-specific effects is retained in the claim.
6. One same-event actual installation provides timing, carrier, consumer, and fidelity evidence.

The currently proposed five-way match does not satisfy Route C. Kinematic success and reward can be experimentally manipulated, but subjective ease, expectation, and source/agency feeling are not presently supplied with independent, route-preserving clamps. Merely selecting participants or trials with equal post-formation reports does not repair this.

## 5. One physically credible prospective protocol

Use two kinematically comparable novel visuomotor mappings in a randomized longitudinal design. Assign formation schedule before training: one mapping receives distributed self-generated practice, the other an independently specified short/late formation schedule. Freeze the final task, movement grain, apparatus, reward schedule, response wording, response-key randomization, and test window before data collection.

At test, measure trajectory error, success, effort/ease judgment, expected success, value, source/agency judgment, and `J_H`. The primary analysis estimates the randomized total effect of formation on `J_H` with only pre-assignment `C0` adjustment. The post-formation variables diagnose whether the contrast changed performance or expectations and may enter explicitly labeled mediation analyses. They are not used to manufacture a primary matched residual.

This protocol is installable in the ordinary sense that every assignment and measurement can be physically scheduled. It does **not** yet install the five-way controlled direct-effect intervention. A future Route C protocol must separately demonstrate that its assistance, reward, expectation and source manipulations preserve rather than replace the actual retentive consumer relation.

## 6. Stop rule and inference boundary

Stop the `H_way` interpretation and report only organizational/judgment results if any of the following occurs:

- formation assignment or fidelity is not established;
- the endpoint content contract fails;
- the primary result appears only after conditioning on post-formation variables;
- joint positivity is absent;
- a clamp writes, erases, replays or bypasses the proposed retentive route;
- response selection or missingness depends on formation descendants without a defended model;
- no same-event evidence binds the manipulation, route and endpoint.

Even if Route T or Route C survives, the conclusion is limited to formation sensitivity of `J_H` under that protocol. `J_H=H_way`, the polarity of `H_way`, and the identity of a retentive structural coordinate with familiar mineness remain open. C1 conditionally locates an independently grounded actual relation inside experience; it does not turn a successful causal contrast into a phenomenal gold standard.

## 7. Four thought-experiment families

| Family | Fixed | Varied | Counterexample role |
|---|---|---|---|
| Ancestor/formation | final task and current output | formation route | Equalizing descendants of formation can erase the very historical contribution under test; formation is never made a basal-experience gate. |
| Abacus/calculator | correct answer and reward | practiced bodily routine versus externally scaffolded execution | Matching speed/ease after training can select or block a route rather than reveal a pure familiar-mineness effect. |
| Human-realized agent | implemented abstract policy | which human or artifact history is actually read by the present consumer | Group reports and performance are post-formation evidence, not automatic membership in the implemented process or one exclusive owner. |
| Copy/swap/memory | present state value and report | same-lineage trace versus copied equal-valued state | Matching present consequences does not recover `RetBind`; clamping the trace value can also remove the history route. |

## 8. Direction check

The result returns directly to the original question: when can historical organization contribute to a selected experience-internal familiarity coordinate? It shows that “better matching” is not monotonically better evidence. The causal time and role of the matched variable decide whether the comparison removes nuisance, induces bias, or changes the organization being interpreted. No extra owner, report requirement, self-model, language capacity, integration threshold, accurate-prediction threshold, or continuation-control threshold is added.

## 9. Novelty boundary

Post-treatment bias, collider selection, positivity, total effects, controlled direct effects, and mediation are established causal-inference concepts. The project-level contribution is the scoped diagnosis of A3Z's formation-matching clause and the resulting UCT-specific installability/stop contract. No new causal theorem, human effect, phenomenal calibration, or general proof of C1 is claimed.
