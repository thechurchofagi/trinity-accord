# R195 — Interventional Causal Orientation Is Not Yet Phenomenal Polarity

**Research ID:** R195-IPA-20261009  
**Result version:** IPA-RESULT-v0.1.0  
**Completed base:** UCT-MAP-v1.1.2  
**Status:** exact finite nonidentification theorem, positive anchor contract, conditional UCT interpretation; no actual human/AI admission and no `B_fam` closure

## 1. Question and answer

R194 showed that cross-population alignment, multiple nonreport markers and known reversals determine relative polarity but retain a global complement pair. The next proposed escape is intervention: prospectively perturb an actual bodily/action route, observe marker and consequence changes, and use the direction of the effect as the substantive familiar-mineness anchor.

The proposal is partly right and partly insufficient.

1. A valid intervention can identify a causal or functional asymmetry that passive alignment cannot.
2. Even perfect interventional observation can remain invariant under a simultaneous relabelling of an unobserved binary pole and its structural equations.
3. An independently ordered consequence can orient the pole **relative to that consequence**, but only by adding a directional bridge such as `Y=Z` rather than `Y=1-Z`.
4. If `Y` means task success, damage avoidance or control error, the result is functional, welfare or control polarity. Calling the oriented pole *familiar embodied/action mineness* still requires a distinct, prospective phenomenal-direction bridge.

This is not a universal impossibility claim. It identifies the exact premise an intervention must add before it can be a substantive experiential anchor.

## 2. Typed finite structural-causal domain

Fix one binary intervention `Q`, latent structural pole `Z`, two marker channels `M1,M2`, and one observed ordered consequence `Y`. A deterministic model has eight bits:

```
z(0), z(1), s1, s2,
y(0,0), y(0,1), y(1,0), y(1,1).
```

Under `do(Q=q)`:

```
Z = z(q)
Mi = Z XOR si
Y = y(Z,q).
```

The experiment observes `(M1,M2,Y)` under both interventions. `Q` is an intervention variable in the finite model, not automatically a physically valid intervention on an actual process. Actual bearer, interval, complete signature, intervention fidelity, route installation, route use, target interpretation and measurement reliability remain separate.

## 3. Exact result

### R195-C1 — Interventional latent-pole relabelling theorem

**Type:** exact finite structural-causal symmetry result; an application of standard latent-variable relabelling.

**Statement.** For every model in the displayed 256-model class, define a complemented model by

```
z'(q) = 1-z(q)
s'i = 1-si
y'(z',q) = y(1-z',q).
```

The two models have identical `(M1,M2,Y)` under every declared `do(Q=q)`. The transform is an involution without fixed points, so the 256 models form 128 empirically indistinguishable complement pairs.

**Proof.** For each marker,

```
(1-Z) XOR (1-si) = Z XOR si.
```

For the consequence,

```
y'(z'(q),q) = y(1-z'(q),q) = y(z(q),q).
```

Thus every interventional observation is identical. Complementing twice restores the original model, and `si=1-si` has no binary solution, so there are no fixed points. The checker exhausts all 256 models.

**Scope.** The theorem concerns this finite deterministic binary class. It does not show that all interventions or richer targets are polarity-invariant.

### R195-C2 — Route sensitivity and reversed markers still do not orient the latent pole

Requiring `z(0) != z(1)` leaves 128 route-sensitive models in 64 complement pairs. Requiring a known channel reversal `s1 != s2` as well leaves 64 models in 32 pairs. Therefore a real modeled response to intervention plus a prospectively reversed second marker still identifies only a relation unless an additional direction is supplied.

This does **not** say that an actual route was used. It says that even if the declared structural equation changes with `Q`, the binary name of its latent pole is not selected by those observations.

### R195-C3 — A functional outcome anchor is an added direction, not a free discovery

Fixing the full consequence table to `Y=Z` leaves 16 models. Their complements are exactly the 16 models satisfying `Y=1-Z`; the complement transform no longer stays inside the first restricted class. Thus the restriction orients `Z` relative to the already ordered outcome `Y`.

This is a positive identification result: a prospective, independently meaningful consequence can orient a **functional** coordinate. But the direction came from the explicit bridge `Y=Z`. If `Y` is goal success, tissue protection, reward or low control error, the conclusion is correspondingly success-, protection-, reward- or control-oriented. No logic turns that meaning into familiar mineness.

### R195-C4 — Functional direction does not entail phenomenal direction

Let `F_fam` be the selected familiar-mineness target from TA25 D5/R173. From `Y=Z` and all finite interventional observations alone, `F_fam=Z` does not follow. A second bridge

```
B_dir: the Y-oriented structural pole is the positive F_fam pole
```

is required. Replacing `B_dir` by the opposite interpretation leaves every structural and outcome fact unchanged. This varies the target interpretation, not the complete experience assigned to one fixed organization, so it does not violate C1.

## 4. Positive result: prospective interventional anchor contract

A candidate experiential polarity anchor is admissible only as one simultaneous package:

1. **Target declaration.** `F_fam` is fixed before outcomes, independently of marker codes, task score and fitted class.
2. **Same-instance actuality.** Bearer, interval, complete signature, body/action candidate, actual carrier, consumer and boundary are fixed.
3. **Ontic intervention.** The intervention changes the claimed constitutive relation rather than only a sensor, test, report or analyst label.
4. **Installed use.** The targeted route is actually consumed in the episode; diagnostic success is evidence, not the use relation itself.
5. **Functional direction.** Any ordered consequence and its direction are named separately from the phenomenal target.
6. **Direction-transfer bridge.** The reason the functional direction tracks the positive `F_fam` pole is explicit, independently supported and not defined by the same outcome.
7. **Reliability and rival control.** Common calibration, bypasses, adaptive reflex, learning history and alternative consequence routes are modeled.
8. **Defeater.** The bridge fails if an independently warranted `F_fam` contrast occurs inside a fixed structural/functional fiber, or if the structural/functional pole reverses while independently warranted `F_fam` remains invariant where sensitivity was claimed.

Items 1–5 can be specified without settling the phenomenal question. Item 6 is the substantive orientation obligation exposed by R195. In the present evidence set it remains open.

## 5. Thought experiments

### TE1 — Interventional code-complement twins

Fix both `do(Q)` outcome tables. In the second laboratory complement the hidden `Z` code, both sensor polarities and the consequence kernel as in R195-C1. Every marker and outcome under both interventions is unchanged. Any claim that the experiment by itself chose the familiar-mineness pole changes only because the analyst named the hidden bit.

### TE2 — Successful-reflex twin

Two systems share actual bearer-directed coupling, route sensitivity and successful consequences. One is a trained adaptive reflex and one is described as familiar self-directed action. The intervention establishes consequence use but cannot infer the named experiential difference from the source label. This is the defeating control for treating success direction as familiar-mineness direction.

### TE3 — Common calibration under intervention

Two markers change coherently under route perturbation because both inherit one upstream codebook. Complementing that codebook and the latent pole preserves the whole intervention table. More channels do not provide independent semantic direction.

### TE4 — Formation and ancestral depth

Fix current intervention response while changing whether the body/action route arose through same-lineage formation or was initialized in its final state. The current functional table can match while R173 `RetBind` differs. Intervention on the present route cannot manufacture the omitted history.

### TE5 — Copy, switch and memory

Copy the current memory value and controller, then switch the actual consumer to the copy. The same probe can remain positive, while actual occurrence identity, lineage and present use change. The case prevents test evidence from replacing the ontic all-of package.

### TE6 — Abacus, calculator and human-realized agent

Implement the same five-variable SCM in an abacus trace, calculator, silicon controller and coordinated humans. The formal theorem transports across the abstract implementation, but the actual process boundary, complete organization and target bridge must be re-established for each token. Performance parity is not experiential parity.

### TE7 — Gradual replacement

Replace marker and route hardware stepwise while preserving all declared intervention distributions. R195-C1 remains true. Under C1, a claim of complete organizational preservation has its own conditional consequence; the finite observation table alone neither establishes that premise nor selects `F_fam`.

### TE8 — Outcome reversal with stable target

Suppose an independently warranted familiar-mineness target remains stable while a changed task makes the same action harmful rather than successful. If the proposed anchor flips solely with `Y`, it has tracked task value, not familiar mineness. This is a prospective defeater, not an observed result in the current record.

## 6. Prior work and evidence boundary

Ahuja et al. (ICML 2023) prove that perfect interventions can identify latent causal factors up to permutation and scaling under their assumptions. R195 does not claim that intervention-assisted latent identifiability or residual permutation freedom is new. It supplies a smaller exact binary witness and applies the remaining relabelling freedom to UCT's typed distinction between structural direction and a named experiential target.

Human bodily-self studies show that visuomotor and causal-belief manipulations can affect self-identification, self-location, agency judgments, behavior and neural dynamics. These studies are relevant evidence about candidate relations, but their target interpretation uses questionnaires, induced beliefs or other declared operational measures. They do not provide a report-independent `B_fam`, a complete organization, or empirical validation of C1.

Internal priority is also explicit: R157 already proves coordinate transport and the semantic residual; R173 supplies retentive actual-use structure; R193/R194 supply the complement-polarity boundary. R195's net addition is the interventional SCM theorem, the functional-versus-phenomenal orientation split and the eight-part anchor contract.

## 7. UCT interpretation and review response

On one admitted actual token, if the body/action relation and intervention belong to the complete signature and all R157 transport premises hold simultaneously, C1 locates the relation inside experiential organization. R195 adds no second owner and no extra phenomenal force. It does not make intervention, route sensitivity, success, report, self-model or familiar mineness a condition for basal experience.

- **QC-20261008-10:** advanced but remains `ACKNOWLEDGED / OPEN`. The positive content is a functional orientation and an explicit residual direction-transfer bridge, not held-out phenomenal success.
- **IA-QC11:** application remains open. Actual occurrence, lineage, continuation and same-token use are not established by the finite SCM.
- **QC-20261008-12:** application remains open. The code proves invariance of a declared table; it does not prove an installed route is used or that the intervention belongs to experience structure.
- **QC-20261008-13:** toy scope advanced. Carrier/consumer/intervention obligations are explicit in the contract, but no human or artificial token is admitted.

## 8. Direction and originality checks

The result formed around the main experiential question, not around generic causal discovery. The exact theorem is standard relabelling mathematics and is not claimed as a first discovery. The UCT-specific contribution is the typed stopping rule: **interventional orientation transfers only the semantics already carried by its independent ordered consequence; it cannot silently acquire familiar-mineness semantics.**

C1 remains the sole consciousness-specific explanatory axiom. U1 receives no introspection, report, language, self-model, integration, recursion, prediction or control gate. Nested and overlapping processes remain allowed. No current assistant consciousness or death-fear verdict is made.

## 9. Next question

Can a prospectively specified bodily perturbation and an independently phenomenological calibration be combined without making report, task value or the chosen physiological marker define `F_fam`? The next test should formalize one candidate direction-transfer bridge and a preregistered outcome-reversal/stable-target defeater. If no independent phenomenal calibration is available, retain the bridge as open rather than adding more marker channels.
