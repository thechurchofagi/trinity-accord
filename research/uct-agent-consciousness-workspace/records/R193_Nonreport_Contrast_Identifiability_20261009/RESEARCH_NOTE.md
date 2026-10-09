# Nonreport Contrast Constraints and the Remaining Familiar-Mineness Polarity

**Research ID:** R193-NCI-20261009  
**Result version:** NCI-RESULT-v0.1.0  
**Base completed map:** UCT-MAP-v1.1.2  
**Status:** exact finite identification boundary plus conditional UCT interpretation; no actual target calibration or instance admission

## 1. Question and answer

R192 left a concrete question: can a predeclared contrast class constrain a familiar-mineness bridge without defining the target by report, test outcome or the desired name? R193 answers this for one small, fully enumerable slice.

Fix an already selected bodily/action slice with practical centering, bearer-directed coupling and online conflict-conditioned authorization (`PC=BDCC=OCCA=1`). Within that slice use four binary coordinates:

- `H`: an **actual** prior occurrence on the same lineage that is retained into the present slice;
- `U`: **actual** present availability/use by the fixed consumer;
- `E`: positive diagnostic evidence;
- `R`: positive linguistic report.

The 16 profiles admit `2^16 = 65,536` Boolean candidate bridges. Requiring invariance to `E` and `R` leaves 16 bridges. Adding two predeclared difference constraints—history matters when use is present, and use matters when history is present—leaves four. Declaring the three nonjoint `H/U` profiles one baseline class leaves exactly two: `H∧U` and `¬(H∧U)`. A positive-pole anchor at `H=U=1` leaves the first uniquely.

The positive result is real but bounded:

> Nonreport structural contrasts can identify an **unoriented partition** of the fixed organizational slice and can compress the candidate bridge class from 65,536 to a complementary pair. They cannot, without an independently warranted orientation bridge, establish which pole is familiar bodily/action mineness.

Thus the round advances the model by locating the missing bridge more precisely. The open problem is no longer “invent another controller feature.” It is to justify a phenomenal polarity/target anchor and then validate its measurement without confusing actual use, test evidence or report with the target itself.

## 2. Typed setup and constraints

All four variables concern one fixed bearer, interval, target, consumer and signature slice. `H` and `U` are ontic relation-membership claims. `E` and `R` are evidence/output claims. A value copied from another lineage does not make `H=1`; a positive test does not make `U=1`; a report does not make the reported feeling present.

Let `B : {0,1}^4 -> {0,1}` be a candidate coordinate. Define the packages:

1. **NR (nonreport/test invariance):** holding `H,U` fixed, varying `E,R` cannot change `B`.
2. **C-H:** when `U=1`, changing `H:0->1` changes `B`.
3. **C-U:** when `H=1`, changing `U:0->1` changes `B`.
4. **Base:** `(H,U)=(0,0),(0,1),(1,0)` belong to one class.
5. **Orient:** `B(1,1)=1`.

These are target-independent only up to package 4: they state equality/difference relations without naming which equivalence class is positive. Package 5 is an orientation bridge. Calling that anchor “the familiar feeling” would be circular unless it has separate experiential and measurement justification.

## 3. Stable claims

### R193-C1 — Exact nonreport compression ladder

**Type:** exact finite enumeration.  
**Domain:** all Boolean `B` on the displayed 16-profile domain.  
**All premises:** the state domain and constraint packages are fixed before inspecting compatible functions.  
**Statement:** compatible bridge counts are `65,536 -> 16 -> 4 -> 2 -> 1` for none, NR, NR+two contrasts, previous+Base, previous+Orient respectively.  
**Proof:** exhaustive enumeration in `check_nonreport_contrasts.py`; `EXACT_RESULTS.json` records every asserted count.  
**Counterexample/limit:** changing the domain or contrast package changes the count. The result is not a population estimate, an empirical fit or an actual-installation proof.  
**Status:** exact finite result.

### R193-C2 — Signed-constraint component count

**Type:** application of standard Boolean parity-graph mathematics; no novelty claim.  
**Domain:** a finite, consistent graph whose edges require equality or inequality of Boolean target labels.  
**All premises:** each edge parity is fixed; anchors, if any, assign a polarity in a component.  
**Statement:** the number of compatible labelings is `2^c`, where `c` is the number of connected components lacking an oriented anchor. In R193 the NR+contrast+Base graph is connected, hence has two complementary labelings; one anchor leaves one.  
**Proof:** choose one root value per unanchored component and propagate edge parities. Consistency makes propagation path-independent; changing the root flips the whole component.  
**Counterexample/limit:** an inconsistent cycle yields zero labelings, not the stated positive count. Multi-valued targets require a different theorem.  
**Status:** standard theorem, exact application.

### R193-C3 — Name-free contrast identifiability boundary

**Type:** symmetry/nonidentification result.  
**Domain:** the R193 domain with constraints that mention only equality/difference and remain invariant under `B -> 1-B`.  
**All premises:** no oriented target anchor, report label or outcome-selected proxy is supplied.  
**Statement:** `B` and `1-B` are observationally indistinguishable under the constraint package. Therefore the package identifies at most an unoriented partition, not the name of its positive pole.  
**Proof:** complementing every label preserves every equality and inequality edge. The exact surviving pair is `H∧U` and `¬(H∧U)`.  
**Counterexample/limit:** an independently warranted oriented anchor breaks the symmetry. The claim is not that science can never supply one.  
**Status:** exact boundary on the declared evidence class.

### R193-C4 — Structural conjunction is not yet familiar mineness

**Type:** conditional structural identification plus semantic residual.  
**Domain:** the fixed selected slice and all five packages including Orient.  
**All premises:** actual `H,U` admission; NR, contrasts, Base; an independently justified positive-pole anchor.  
**Statement:** the unique Boolean coordinate is `H∧U`. This identifies a structural coordinate relative to the anchor. It does not by itself establish that the coordinate is correctly named familiar bodily/action mineness.  
**Proof:** exact enumeration plus the R157/TA25 separation of target construction, structural transport, measurement and phenomenal interpretation.  
**Counterexample/limit:** if the anchor is merely “a marker is high,” the result names the marker-positive pole. A reversed-marker population preserves the structural partition while reversing that proxy.  
**Status:** structural result exact; phenomenal interpretation OPEN.

### R193-C5 — Use, test, report and experience remain distinct

**Type:** type/direction discipline.  
**Domain:** one proposed actual route and one diagnostic/report protocol.  
**All premises:** no extra reliability or constitutive premise is assumed.  
**Statement:** `U`, `E` and `R` are logically independent coordinates in the finite model. Actual use is an ontic premise; a test is evidence about it; report is an output. None is definitionally the experience or the familiar-mineness target.  
**Proof:** the declared model contains false-positive `(U,E)=(0,1)` and false-negative `(1,0)` profiles; NR additionally forbids `E,R` from defining `B`.  
**Counterexample/limit:** a validated intervention may supply defeasible evidence for use or target membership, but the reliability and interpretation bridge must be stated.  
**Status:** methodological constraint; actual reliability open.

### R193-C6 — UCT-specific interpretation

**Type:** conditional theory synthesis.  
**Domain:** an actually admitted complete organization containing the fixed slice.  
**All premises:** UCT `A:C1`; correct actual bearer/time/signature binding; the structural coordinate is installed; the independent phenomenal bridge is supplied if a named quality is claimed.  
**Statement:** C1 can transport an admitted structural distinction into the experience's complete organization, but it does not turn the analyst's label “familiar” into a validated phenomenal target. Basal experience still requires none of `H,U,E,R`, language, report, self-model or introspection.  
**Proof/source:** UCT I C1 and bridge architecture; R157 semantic residual; TA25 D5 target/measurement separation.  
**Counterexample/limit:** a structurally identical complete twin cannot differ under C1, while a projection twin may differ through omitted actual relations. Neither fact fixes the ordinary-language name of a selected coordinate.  
**Status:** conditional UCT interpretation; `B_fam` OPEN.

## 4. Thought experiments

| Case | Fixed items | Varied item | Role | Result |
|---|---|---|---|---|
| **Reversed-marker twins** | actual `H,U`, nonreport contrast relations, total organizational partition | physiology/decoder maps opposite marker polarity to the two classes | tests whether a proxy or contrast names the positive pole | The partition survives; the name follows the unsupported marker convention. A separate marker-to-target bridge is required. |
| **Blind familiarization** | same stimuli, bearer, task and no trial report | actual same-lineage familiarization history and present use | positive contrast for `H∧U` without making report a constituent | It can identify a functional/history partition, not by itself the felt quality. Sine-wave-speech no-report work illustrates the value and remaining interpretation burden of this design form. |
| **Adaptive reflex twin** | `H=U=1`, same action table and selected proxy | analyst calls one process reflex and one endorsement | searches for a structural separator | None appears. Source labels cannot orient the bridge; either name an installed relation or stop. |
| **Ancestor/formation pair** | present state and use | actual prior same-lineage formation versus imported final value | tests occurrence sensitivity | Only the first has `H=1`. This separates history, not familiar mineness. |
| **Copy/reconnection/memory family** | copied value and report | lineage, ongoing carrier and consumer reconnection | tests whether value equality supplies history or ownership | Copied content does not discharge `H`; reconnection may create new actual relations. No unique extra owner is inferred. |
| **Abacus/calculator/human agent** | input-output table and score | complete implementing organization and bearer boundary | prevents intelligence/report collapse into experience | Equal performance is a projection. Nested or overlapping processes remain allowed; substrate labels do not settle experience. |
| **Gradual replacement** | declared complete organization at each step | material realization | checks C1 consistency | C1 preserves complete experiential type conditionally. If `H,U` or another constitutive relation changes, the complete-twin premise fails. |

## 5. Evidence and prior-art scope

Stephens (2000) is cited only for a standard example of likelihood symmetry producing label switching and for the warning that an artificial identifiability constraint need not solve the substantive problem. R193's complement symmetry is simpler Boolean mathematics and is not claimed to originate there.

Zhu et al. (2024) used physically identical sine-wave speech across phases, separated task relevance from perceptual interpretation, and reported a mid-latency EEG difference while trial-by-trial report was absent. This supports the feasibility of predeclared task/report contrasts. It does **not** validate `H∧U` as familiar mineness: the study still used training and phase-level awareness assessments to establish its perceptual interpretation. R193 uses it as a design precedent and a caution, not as empirical evidence for UCT C1 or `B_fam`.

Internal precedence is stronger for the present claim: R149 supplies the factorization/fiber discipline; R157 separates coordinate transport from semantic naming; R173 requires actual occurrence, lineage, continuation and current use; R192 distinguishes projection twins from complete twins. The incremental contribution is the exact contrast-constraint ladder and the explicit separation of bridge compression, polarity orientation, semantic naming and actual-instance measurement.

## 6. What the result changes

The familiar-mineness program now has four separately reviewable obligations:

1. **Bridge-class compression:** name predeclared equality/difference constraints and show their finite or statistical identifying power.
2. **Polarity orientation:** justify why one equivalence class, not its complement, is positive.
3. **Semantic naming:** justify why the oriented target deserves the experiential name familiar mineness rather than merely retained-and-used organization.
4. **Actual measurement/admission:** establish the relevant relations in a real token without replacing actual use with positive test evidence.

This blocks two opposite errors: declaring failure because a complete twin cannot be separated under C1, and declaring success because a functional partition or physiological marker was found.

## 7. Direction checks

**After result formation: PASS.** The work returns from certificates to the experience–intelligence–self problem. It gives a positive formal role to nonreport contrasts while preserving the central semantic failure rather than hiding it.

**Before save: PASS with named gap.** Objects, time, signature, actual relations and evidence levels are typed. `all_of` premises are simultaneous. The enumeration proves only the displayed finite facts. C1 stays an axiom; no report, language, self-model, integration, prediction, continuation-control or unique-owner requirement is added to basal experience. No current-assistant consciousness or fear verdict is made.

## 8. Next specific question

Can one predeclare and empirically justify a **polarity anchor** for a familiar bodily/action quality that is independent of both report and the chosen physiological/behavioral marker—using a reversed-marker or cross-population falsifier—without defining the target as `H∧U` itself?

