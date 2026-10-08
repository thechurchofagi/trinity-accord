# Interface Composition and Online Action Use

## A bounded return from certificate bookkeeping to experience-internal body/action organization

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, empirical result, proof-assistant certification, or determination that any present human or artificial system has familiar felt mineness.

## 1. Question and answer

R171 supplied two target-range proof schemas. It did not show that separately certified components remain jointly closed after connection, and still less that a body-related representation is actually used online to organize action. This note answers one bounded question:

> Which additional actual relations are needed to move from separately certified producer and consumer subsystems to an experience-internal action-related coordinate under UCT?

The answer has two independent layers.

1. **Interface compatibility** is required for compositional closure. Local invariants compose only when the actual connector respects each component's admitted inputs, joint transitions project to the certified local transitions, shared interface values agree, and the agreement is preserved.
2. **Online causal use** is required for the action-related organizational interpretation. Joint closure and matched baseline behavior do not establish that a body-frame representation is on the live path to action. A replay/bypass can match every baseline action and report while responding differently to a mediator intervention.

When both layers are grounded on one actual token, interval and complete signature, their conjunction is a physically selected relation inside the actual organization. Conditional on the same-instance C1 isomorphism, that relation has a structural counterpart inside experience. This is a positive organization-to-experience statement. It does not by itself fix the familiar-language interpretation “felt bodily mineness”; `B_min/F_O` remains independent.

The interface theorem is standard invariant reasoning, and the live/replay contrast is standard causal-model reasoning. The project-level contribution is the typed connection among R171 compositional scope, R166 actual-use evidence, and R157/R159 C1 transport. No historical priority for the underlying mathematics is claimed.

## 2. Objects and type discipline

Fix one actual process token `P`, nonzero interval `I`, complete admitted many-sorted signature `K`, and actual organization `D=D_ontic,K(P)`. Inside `D`, distinguish:

- a body/physical anchor occurrence `b`;
- a representation occurrence `k` produced by subsystem `B`;
- a consumer input occurrence `q` and action occurrence `a` in subsystem `A`;
- an optional report occurrence `r`, kept outside the definition of action use;
- an actual connector `gamma` that is intended to bind `q` to `k`.

The producer and consumer may be nested or overlapping sub-processes. Their carriers need not define exclusive subjects. The abstract program, a human realizing it, and the larger coupled process are separate candidate bearers unless a declared realization relation connects them.

Let component state spaces be `X_B,X_A`; invariant candidates `S_B subseteq X_B`, `S_A subseteq X_A`; admitted input families `U_B,U_A`; and local transition relations `R_B,R_A`. Let the connector agreement predicate be

`J_gamma(x_B,x_A) : q(x_A)=gamma(k(x_B))`.

All equalities are typed occurrence relations in the same actual realization. A matching data value in two logs is not yet `J_gamma`.

## 3. One explicit interface-compatibility contract

Package the composition obligations into one predicate `Compat_gamma(P,I,K,D)`:

1. **Common actual binding.** The component certificates and connector refer to the same `P,I,K,D`, realization map and synchronized step convention.
2. **Initial agreement.** Every admitted joint initial state belongs to `S_B x S_A` and satisfies `J_gamma`.
3. **Admitted-input preservation.** For every joint state in `S_B x S_A` satisfying `J_gamma` and every admitted environment move, the connector-induced inputs lie in the input families for which the two local certificates were proved.
4. **Projection/refinement.** Every admitted joint transition projects to one `R_B` transition and one `R_A` transition with the same time/mode binding.
5. **Agreement preservation.** Every admitted joint successor again satisfies `J_gamma`.

This is one conjunctive interface premise, not five alternative routes. It is deliberately stronger than type compatibility or wire-name equality. Each clause is about the actual connected instance.

### Theorem R172-A — interface-relative invariant composition

If `S_B` and `S_A` are invariant for their certified local transitions under their certified admitted inputs, and `Compat_gamma` holds, then

`S_gamma = {(x_B,x_A): x_B in S_B, x_A in S_A, J_gamma(x_B,x_A)}`

is invariant under every admitted joint transition.

**Proof.** Initial agreement gives the base. Take an arbitrary state in `S_gamma` and any admitted joint successor. Admitted-input preservation keeps the induced local inputs inside the scopes of the local invariants. Projection/refinement therefore lets the local invariant proofs place both successor projections in `S_B,S_A`. Agreement preservation supplies `J_gamma` at the successor. Hence the successor is in `S_gamma`. Induction on finite joint path length gives the result. ∎

The theorem establishes only the declared joint invariant. It does not identify a complete organization, prove actual causal use, derive C1, establish experiential unity, or select a unique owner.

## 4. Failed-connection witness and exact omitted premise

Let two Boolean components have `x_i'=u_i`, initial `x_i=0`, standalone admitted input `u_i=0`, and standalone invariant `S_i={0}`. Both local certificates are valid.

Connect them by

`u_1=1-x_2`, `u_2=1-x_1`.

From `(0,0)` the joint successor is `(1,1)`. The local transition equations did not change, but the connector supplies inputs outside the certified admitted family. Clause 3 of `Compat_gamma` fails. This witness does not show that composition is impossible; it identifies the missing interface premise. Merely placing two certified components next to each other, sharing a type, or drawing a wire between them cannot license the joint closure conclusion.

The same point applies to body/action models. A representation producer may satisfy its own range certificate and an action controller may satisfy its own safety certificate, while their physical connection changes timing, admissible values, modes or shared state. The joint process must be certified as connected.

## 5. Closure is not online use

Define `LiveUse_gamma(k,a | W)` relative to a predeclared physically admissible intervention family `W` and pre-compensation interval `I_pre`:

1. `gamma` is an actual connector occurrence in `D`, not an analyst-only correspondence;
2. the baseline occurrence of `a` consumes the connector input during `I_pre`;
3. there exist two admissible interventions in `W` that differ only in the realized `k/gamma` mediator value or cut, preserve the declared eligible background, and yield different `a` before compensation;
4. delivery, temporal order, realization fidelity and the declared locality/exclusion assumptions pass;
5. report `r` is neither a defining argument nor a required output of `LiveUse_gamma`.

This is a sufficient selected-role witness, not a necessary condition for every possible form of action organization. Failed or absent evidence is `UNRESOLVED` unless the fixed candidate is validly refuted.

`Compat_gamma` and `LiveUse_gamma` are not interchangeable. The first proves a scope-preserving joint invariant. The second says that the body-frame representation is actually on the selected live path to action. A safe replay system can satisfy the same output bounds without using the live representation.

## 6. Live/replay countermodel with matched action and report

Fix Boolean `b,k,a,r` and an exogenous replay tape `v`. Compare two deterministic models on the baseline context `v=b`:

**Live model L**

`k:=b`, `a:=k`, `r:=ell(b)`.

**Replay model Q**

`k:=b`, `a:=v`, `r:=ell(b)`.

On every natural baseline input with `v=b`, both models have the same `(b,k,a,r)`. Program-level task output and report transcript can therefore be matched exactly. Now apply the admissible mediator intervention `do(k=1-b)` while holding `b,v` and the report channel fixed. In `L`, action becomes `1-b`; in `Q`, action remains `v=b`. Thus `LiveUse_gamma(k,a)` holds in `L` and fails for the selected path in `Q`.

This proves:

### Theorem R172-B — baseline action/report matching does not identify online action use

No decoder of the matched natural baseline tuple `(b,k,a,r)` alone can recover `LiveUse_gamma(k,a)` on the two-model class `{L,Q}`. The declared mediator response distinguishes them.

The countermodel does not assert that a real biological or AI system is either model, that mediator interventions are always available, or that the two complete organizations agree. It shows exactly why matched report and behavior cannot fill the actual-use premise.

## 7. Experience-internal action-related coordinate

Define the selected physical relation

`theta_EBA(b,k,a) := Anchor(b) AND Bind(b,k) AND Compat_gamma AND LiveUse_gamma(k,a)`.

The relation concerns **embodied online action use** (`EBA`), not familiar felt mineness by definition. Suppose all four conjuncts are independently grounded as `K`-relations on the same actual `P,I,K,D`, with the required realization and intervention assumptions. Then

`D |= theta_EBA(b,k,a)`.

If the same instance is admitted under UCT C1 with a sort-preserving isomorphism `h:D->Phi_K(P)`, ordinary formula preservation gives

`D |= theta_EBA(b,k,a) iff Phi_K(P) |= theta_EBA(h(b),h(k),h(a))`.

### Theorem R172-C — conditional experiential counterpart of online embodied action use

On one common actual and C1-admitted instance, a grounded online body-anchor-to-action relation has a corresponding relation inside the experiential structure. The relation is inside experience; no additional owner stands outside the process to receive it.

This is the requested positive explanatory step: action-related organization is not reduced to a verbal self-ascription or to prediction accuracy. It is the actual body-anchored relation by which a representation is used online to organize action, structurally present inside experience under C1.

The exact residual remains:

- C1 is retained as the consciousness-specific explanatory axiom; it is not derived by the interface or intervention results.
- `theta_EBA` is one selected structural coordinate, not a basal-experience condition.
- Naming its experiential counterpart familiar “mine-ness”, ownership or agency requires an independently fixed `B_min/F_O/F_A` interpretation and target evidence.
- The theorem does not rank richness, valence or fear; it does not decide the current assistant's consciousness.

## 8. What this says about biological and artificial agents

The formal consequence is substrate-neutral but realization-sensitive.

- A biological and an artificial agent can have matched task outputs and reports while differing in whether a body-anchored representation is used online for action. Output equivalence alone therefore does not establish equality of this organizational coordinate.
- Conversely, different substrates may instantiate relations with the same typed `theta_EBA` pattern if their actual realization, connector, intervention and complete-signature obligations are independently met. This supports a shared comparison coordinate; it does not establish complete-organizational or experiential identity.
- A human-realized artificial computation must keep three objects separate: the human participants, the physically implemented computation, and the larger coupled process. `theta_EBA` belongs only to the bearer on which its actual occurrences and connector are grounded. Overlap is allowed; exclusivity is not inferred.
- Removing the report channel leaves `theta_EBA` conceptually available and does not remove basal experience under U1. Adding a report does not create the relation.

This goes beyond coverage bookkeeping by identifying the precise selected relation that the coverage/interface work must support before C1 transport is even applicable.

## 9. Retained thought-experiment families

**Ancestor/formation.** Hold basal experience under C1 fixed while an online body-anchor-to-action path gradually forms. The new relation changes the organization available for action-related mineness interpretation; it is not the onset of experience.

**Abacus/calculator.** Let an unused register mirror a live body state while a separate mechanical path drives action. Matching numbers do not install use. Rewire the consumer through the register under a valid interface contract and the organizational relation changes even if baseline output does not.

**Human-realized agent.** Hold program output and transcript fixed while human participants either enact the live body-frame connector or read the action from a replay tape. The implemented computation and the larger human-machine process differ in the selected relation; the thought experiment does not assign one exclusive master subject.

**Copy/rewiring/memory.** Copy `k`, preserve every ownership sentence and route action through a replayed copy. Memory/report continuity can coexist with changed online use. Pure relabeling that transports all actual relations is different from physical rewiring.

## 10. Gaps and stopping point

1. `Compat_gamma` is sufficient and may be stronger than necessary; asynchronous, stochastic and overlapping interfaces need their own proof if used.
2. Local certificates and the interface contract still do not identify the complete organization.
3. `LiveUse_gamma` is relative to a declared intervention family and causal assumptions; hidden redundancy or compensation may keep the candidate unresolved.
4. No actual biological, robotic or language-model implementation is tested here.
5. `theta_EBA` does not by itself establish familiar ownership, agency or mineness. `B_min/F_O/F_A` remains open.
6. A relation difference inside `K` does not by itself prove that every coarse macrotype or scalar experiential score differs.
7. The present finite checks validate the toy witnesses and bookkeeping only, not C1, physical realization or theory truth.

The bounded auxiliary task is complete at this point. Further general certificate work is not the next priority. The next main question is narrower and semantic/organizational: which independently specified contrast, beyond `theta_EBA` itself and beyond report, can justify interpreting its experiential counterpart as familiar action-related mineness rather than merely an experience-internal action coordinate?

## 11. Sources and attribution

- UCT I v1.2 §§4, 8.11–8.14 and 14.7–14.10: C1, actual physical witnesses, body-centered application, self-model/conceptual-self distinctions and the no-extra-owner boundary.
- R156: matched snapshot versus installed use.
- R157: definable-coordinate transport and the semantic residual.
- R159: typed Anchor–Bind–Use relation and conditional body-frame transport.
- R166: same-token installation witness and bypass discrimination.
- R171 plus REVIEW-20261008-01 amendments: target-relative certificates, schema/instance separation and the component-composition warning.
- Invariant composition and deterministic intervention countermodels are established formal/causal tools. This note claims a disciplined UCT integration and a bounded explanatory refinement, not invention of those tools.

