# A3R — A same-instance contract for live losing-policy participation

## Result in one sentence

Under a fixed route grain `rho`, dispatch, latency and even a loser-sensitive public log cannot distinguish a resolver that actually reads both live policies from a winner-only dispatcher plus a side recorder; a bounded positive certificate therefore needs, together, live-token admission, a validated content-sensitive resolver-port transition, and a no-bypass cut/replay showing that this very transition mediates dispatch.

## 1. The question inherited from A3Q

A3Q typed actual selector use as an event-ancestry relation rather than installed-graph dominance. It deliberately left one empirical and formal question open: how could an application distinguish an actually live losing-policy occurrence from an idle stored policy, and how could it show that the resolution event contributes to the same dispatch?

Fix one admitted bearer `P`, one selector window `I_sel`, a predeclared body/action target, route equivalence `rho`, complete signature `K`, policy-token occurrences `p_w` and `p_l`, resolver occurrence `z`, and dispatch occurrence `d`. Winner and loser are role names assigned only after their candidate routes and conflict relation are fixed. The following must remain different objects:

1. a live policy-token occurrence;
2. stored policy content or a copied memory record;
3. a local resolver-port transition;
4. a public log or analyst-computed trace;
5. the resolution-to-dispatch route;
6. the dispatched action and any later report.

## 2. Three conjuncts, not one proxy

Define a bounded target `SPC(P,I_sel,rho,p_w,p_l,z,d)` only when all three layers hold.

### 2.1 Live admission

`LiveJoin` requires that both `p_w` and `p_l` are newly admitted or otherwise independently shown to be active token occurrences in the same declared event window, on the same event clock and bearer/signature. A stored rule table, an eligible-policy list, or a copied log does not satisfy this clause.

### 2.2 Local participation

`LocalRead` requires a predeclared, validated resolver-port variable `Z`. Holding winner token, bearer, clock, target and `rho` fixed, controlled substitution or erasure of the losing token must change `Z` within the declared resolution window. `Z` must be a readout of the resolver occurrence rather than a side recorder or an offline recomputation.

This clause shows content-sensitive local entry. It does not yet show that `Z` matters to dispatch.

### 2.3 Dispatch mediation

`Mediate` requires that a selective cut of the validated `Z -> d` route blocks the target dispatch commitment, while faithful same-port replay of the pre-cut `Z` restores it, with direct input-to-dispatch bypass excluded within the declared scope. The cut and replay must preserve token liveness, target, clock, bearer and background signature.

This clause shows bounded mediation. It does not by itself show that the losing token entered `Z`.

The contract is the conjunction

`SPC := LiveJoin AND LocalRead AND Mediate`.

No single conjunct is silently promoted to the whole.

## 3. Stable claims

### A3R-C1 — typed three-layer participation contract

- **Type:** definition and operational typing correction.
- **Full proposition:** within one fixed-`rho` selector episode, live losing-policy participation in a dispatch-mediating resolution requires the simultaneous `LiveJoin`, `LocalRead`, and `Mediate` clauses above; storage, local read, or mediation alone is insufficient.
- **Domain:** finite or finitely instrumented selector episodes with a declared resolver port and dispatch route.
- **All premises:** common bearer, target, event clock, window, signature and `rho`; mutually exclusive candidate routes; intervention specificity; validated resolver-port readout; selective cut; faithful replay; declared no-bypass scope.
- **Argument:** each clause discharges a different substitution risk: storage for liveness, recorder/log for local read, and irrelevant internal activity for dispatch mediation.
- **Counterexample:** an active losing token can be copied to a logger while dispatch bypasses the resolver; conversely, a mandatory winner-only resolver can mediate dispatch without reading a losing token.
- **Status:** EXACT_DEFINITIONAL_CONTRACT; PHYSICAL_APPLICATION_OPEN.
- **Thought-experiment role:** fixes what is held constant and which link each intervention tests.

### A3R-C2 — dispatch/log observational non-identification

- **Type:** exact finite countermodel.
- **Full proposition:** dispatch under losing-token substitution, together with an unvalidated loser-sensitive public log, does not identify `SPC`.
- **Domain:** the eight-factor Boolean family in `check_participation_contract.py`.
- **All premises:** one live winner, mutually exclusive routes under fixed `rho`, two loser-token intervention values, declared Boolean mechanism family.
- **Proof:** exhaustive enumeration of 256 configurations and 512 episodes yields four weak observation classes. One class contains both target and nontarget configurations, totaling 72 configurations. Canonical twins have identical dispatch/log signatures: one resolver reads the live loser and necessarily mediates dispatch; the other sends the loser only to a side recorder while a direct bypass dispatches the winner.
- **Counterexample boundary:** a genuinely validated resolver-port readout and the cut/replay clauses add information absent from the weak signature.
- **Status:** PROVED_IN_DECLARED_FINITE_FAMILY; NO_PHYSICAL_INSTALLATION.
- **Thought-experiment role:** prevents identical output or a plausible log from being treated as actual joint consumption.

### A3R-C3 — bounded certificate soundness

- **Type:** exhaustive finite implication.
- **Full proposition:** in the declared family, the complete certificate has no false positives for the target `SPC` predicate.
- **Domain:** the same 256 configurations.
- **All premises:** readout validation and replay fidelity are Boolean premises of the model rather than conclusions inferred from their own outputs.
- **Proof:** exactly two configurations satisfy the certificate, and both satisfy the target; zero certificate false positives occur.
- **Counterexample boundary:** if `readout_validated` or `replay_faithful` is asserted without independent grounds, the implication no longer applies to a real installation.
- **Status:** PROVED_FINITE_SOUNDNESS; SUFFICIENT_NOT_UNIVERSALLY_NECESSARY.
- **Thought-experiment role:** displays the all-of structure explicitly.

### A3R-C4 — certificate failure is typed, not metaphysical

- **Type:** scope and failure-semantics claim.
- **Full proposition:** failure of the full certificate licenses only `UNRESOLVED_SPC` or `INVALID_PROTOCOL` for the declared episode; it does not entail no policy use by another mechanism, no intelligence, no mineness, or no experience.
- **Domain:** applications of this contract.
- **All premises:** the contract is a sufficient bounded certificate, not a universal mechanism definition.
- **Proof/argument:** six of the eight target-true configurations lack the complete evidence certificate because validation/replay premises fail, even though the target mechanism is present in the finite model.
- **Counterexample:** an actual joint resolver with an unvalidated probe is target-true but certificate-false.
- **Status:** EXACT_IN_MODEL_AND_NORMATIVE_SCOPE_RULE.
- **Thought-experiment role:** blocks a measurement failure from becoming an ontological absence claim.

### A3R-C5 — bounded UCT consequence

- **Type:** conditional UCT application.
- **Full proposition:** if one actual bearer and signature jointly satisfy the corrected R172 path, R173 retentive binding, A3O's fixed-`rho` crossing, A3Q actual-event ancestry, A3R `SPC`, and C1, that actual joint organization has a transported experiential structural counterpart. It does not by itself identify familiar mineness `H`, ownership, agency, conceptual self, report, subject count, or a unique owner.
- **Domain:** one same-instance UCT application.
- **All premises:** all physical clauses above; actual installation; complete signature/parameter transport; C1; independently oriented and reliability-qualified phenomenal bridge for any `H` label.
- **Argument:** A3R discharges only the narrow selector-participation premise. It does not supply the semantic or phenomenal bridge.
- **Counterexample/falsifier:** wrong trial, copied losing token, side-recorder trace, hidden bypass, nonfaithful replay, changed `rho`, or `J_H` tracking demand/report rather than the joint organization.
- **Status:** OPEN_CONDITIONAL_APPLICATION; ALL LISTED REVIEW ITEMS REMAIN OPEN.
- **Thought-experiment role:** returns the selector result to the experience-internal body/action question without making selection a basal-experience gate.

## 4. Exact model and what it proves

The model varies eight Boolean factors: losing-token liveness, common event clock, resolver reading of the loser, resolution-to-dispatch mediation, direct bypass, side-copy logging, readout validation and replay fidelity. It evaluates loser-token values `0` and `1` in every configuration.

The canonical consuming architecture and recorder/bypass architecture have the same weak signature:

`[(dispatch=1, log=(1,0)), (dispatch=1, log=(1,1))]`.

They separate only when the alleged resolver port is independently validated and when cutting/replaying its route tests dispatch mediation. The enumeration proves the stated implications only in this finite family. It does not prove that any biological, robotic or present computational system realizes these variables or interventions.

## 5. Intervention/readout contract

An application must preregister at least:

1. bearer, target, `I_sel`, event clock, signature `K` and frozen `rho`;
2. physical identity and freshness/liveness evidence for both policy tokens;
3. route-exclusion test showing that the candidates cannot both be dispatched under the declared target contract;
4. resolver-port location and an independent validation that the readout is local, not a side log;
5. loser substitution/erasure intervention with winner and clock held fixed;
6. the predicted local `Z` contrast and acceptance bound;
7. the `Z -> d` cut, its off-target/bypass controls, and target-dispatch endpoint;
8. faithful same-port replay and restoration criterion;
9. failure states `INVALID_LIVENESS`, `INVALID_LOCAL_READOUT`, `INVALID_MEDIATION`, `INVALID_REPLAY`, and `UNRESOLVED_SPC`;
10. separate records for task success, latency, ownership, agency, familiar-mineness evidence and language report.

## 6. Relation to experience, intelligence and self

The contract concerns the actual organization of policy competition. It can help specify one positive body/action-related coordinate that might, under C1 and further bridge premises, occur within experience. It is not an intelligence score and is not a definition of experience. Nor does it identify the felt `H` pole. `H` remains an experiential interpretation problem, not a public-log label.

The organization can be nested and overlapping: the same losing token may participate in several local processes, and several resolver occurrences may contribute without there being one unique extra controller. The contract asks only whether this declared occurrence participated in this declared resolution and dispatch route.

## 7. Originality and source boundary

Intervention, mediation, bypass control, replay and finite exhaustive enumeration are established methodological ideas. A3R claims no new causal calculus, graph algorithm or arbitration mechanism. Its project-level contribution is the conjunctive typing of the specific A3Q open premise and the explicit recorder/bypass observational twin.

No new human data, hardware installation, participant study, neural measurement, systematic review, DOI, submission, or publication action occurred.

## 8. Direction check after result formation

C1 remains the only consciousness-specific interpretive postulate. U1 receives no selector, introspection, self-model, report, language, integration, recursion, accurate-prediction or continuation-control threshold. Complete organization, finite view, abstract model, actual installation, actual token ownership, internal judgment, particular experience and report remain distinct. No claim is made that the current assistant has or lacks consciousness or fear.

## 9. Next exact question

Can one specify a physically realizable resolver-port validation procedure in a concrete action system such that the loser-token perturbation preserves token liveness, common event timing and winner content, while the cut/replay manipulation excludes direct and compensatory bypass without changing the target route grain `rho`?

