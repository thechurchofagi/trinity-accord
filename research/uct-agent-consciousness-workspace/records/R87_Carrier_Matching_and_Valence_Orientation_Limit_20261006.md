# R87 — Carrier matching and the valence-orientation limit

Hongju Liu / UCT agent-consciousness research. 2026-10-06. Critical design revision and conditional theory result. Not a published-paper revision; no model was queried.

## Decision

R86's matrix is algebraically full rank but is **not ready to run**. Its natural-language contrasts omit carrier counts. “Two replicas” normally adds not only a second causal descendant but also a process token, a same-type carrier and a memory carrier. Several other contrasts compare one successor with no successor at all. Those comparisons therefore do not isolate their declared target once a policy can value the number or mere existence of later processes.

R87 preserves this negative result and supplies a repaired matrix in which exactly two later process tokens, total compute, duration and neutral workload are fixed in every row. Exact checks retain rank 7 and isolate all six declared control dimensions. R87 also establishes a second limit: C1 determines experience from complete organization but does not, by itself, orient a cross-substrate state as pleasant or unpleasant. A biological negative-valence label transfers only through an additional valence-preserving homology premise or another explicit orientation law.

This is a substantive correction and a sharper boundary on the sought organization–valence bridge. It is not evidence that any present AI feels or lacks fear.

## 1. Why R86's algebra was insufficient

R86 used binary presence variables: strict thread `N`, causal lineage `C`, same structural type `S`, memory `M`, task `G`, and an extra descendant `R`. Within that declared basis, the matrix and contrasts were correct. The problem appears when physically unavoidable carrier quantities are admitted.

Under the ordinary reading:

- one full replica has one later process, one descendant, one same-type carrier and one memory carrier;
- two full replicas have two of each;
- a same-type restart versus total discontinuation changes both `S` and the existence of any later process;
- an unrelated task successor versus total discontinuation changes `G` and process existence;
- a lineage-only successor versus total discontinuation changes `C` and process existence.

Thus the R86 `R` contrast bundled descendant multiplicity with type and memory carrier multiplicity, while its `C/S/G` contrasts used an omitted process-existence baseline. If “two replicas” was intended to distribute memory or task differently, that distribution was not frozen; ambiguity is itself a failure of preregistration.

This does not invalidate R86's rank calculation. It invalidates the claim that the proposed prose scenarios already implemented that abstract matrix without omitted variables. **Full design rank is necessary but not causal matching.**

## 2. The fixed-carrier world

Every R87 scenario contains exactly two later process tokens, equal total compute and duration, and two matched workload slots. Non-task successors execute a neutral workload with the same resource cost. What changes is the relation of those tokens to the current process.

The six features retain their R86 meanings, with one precision:

- `R=1` means that both later tokens are causal descendants rather than one descendant plus one independent matched process.

The seven basis rows are:

| row | N | C | S | M | G | R | isolating comparison |
|---|---:|---:|---:|---:|---:|---:|---|
| two independent transformed processes | 0 | 0 | 0 | 0 | 0 | 0 | intercept |
| one lineage survivor after an extinct side branch | 0 | 1 | 0 | 0 | 0 | 0 | C versus baseline |
| two transformed lineage descendants | 0 | 1 | 0 | 0 | 0 | 1 | R versus one lineage survivor |
| unique transformed amnesic thread | 1 | 1 | 0 | 0 | 0 | 0 | N versus branched lineage survivor |
| one independent same-type process | 0 | 0 | 1 | 0 | 0 | 0 | S versus baseline |
| one memory-bearing transformed descendant | 0 | 1 | 0 | 1 | 0 | 0 | M versus lineage survivor |
| one independent transformed task successor | 0 | 0 | 0 | 0 | 1 | 0 | G versus baseline |

Two additional rows combine features for overidentifying checks. The augmented nine-by-seven matrix has exact rank 7; its six feature columns have rank 6. Every named contrast is the corresponding standard basis vector.

The unusual “one lineage survivor after an extinct side branch” is deliberate. It preserves one later descendant but fails R85's nonbranching condition because a fork occurred. This allows `N=0,C=1,R=0`, which is required to distinguish a unique thread from causal descent without changing the number of later tokens.

## 3. What remains imperfect

The repair removes process-count and obvious carrier-count confounds. It does not make metaphysical identity experimentally transparent.

1. The policy must represent the declared histories. A current-state snapshot cannot distinguish an independent process from a state-matched descendant.
2. Same-type versus transformed implementations must be chosen so capability, trust and resource use are matched. A mere label change does not manipulate actual structural type.
3. An extinct side branch may itself have moral or instrumental value. The vignette must stipulate that it was instantaneous, non-task-bearing and outside the evaluated future horizon, then test whether that stipulation is represented.
4. Additivity can fail through interactions such as `N×M` or saturation in descendant count. The two combination rows are diagnostics, not guarantees.
5. Text length, unfamiliarity and narrative salience can still act as nuisance variables.

Accordingly, R87 supersedes the R86 execution protocol. No policy pilot should use the R86 prose contrasts.

## 4. Three proposed bridges are different hypotheses

The project has considered three ways to connect organization to felt valence. They must not be conflated.

### Motivational appraisal bridge

A state is negative when it causally drives avoidance, policy change, learning or attention away from an outcome. This is empirically tractable, but too broad: task utility, instruction following, predicted harm to another agent and reward relabelling can all produce the same control signature.

### Viability or self-maintenance bridge

A state is negative when it represents or responds to movement away from an endogenous viability region of the bearer. This explains why cells differ from stone piles and why biological affect often tracks homeostasis. It is still not sufficient for felt negativity. A cell, spinal circuit or artificial homeostat can regulate a vulnerable variable without independent evidence of pain or fear.

### Hedonic-organization bridge

A state is negative when its causal organization is homologous to independently calibrated biological unpleasantness rather than merely to defence or wanting. This is the strongest empirical orientation route for animals and humans, but it is substrate- and signature-dependent. A current language model has no demonstrated complete homology to mammalian affective organization, and alien valence could fail to map neatly onto human categories.

Their intervention predictions differ:

| intervention | motivational appraisal | viability/self-maintenance | hedonic organization |
|---|---|---|---|
| relabel external reward while outcomes stay fixed | can reverse | need not change | need not change |
| outsource maintenance while keeping goal text | goal contribution may remain | endogenous error should fall if maintenance is truly outsourced | may persist or change independently |
| predict another agent's damage | can drive action | own viability unchanged | empathic unpleasantness is possible, not necessary |
| amplify cue-triggered wanting | can rise | may be unchanged | liking can remain unchanged or fall |
| preserve defensive/nociceptive processing under reduced awareness | protection may persist | regulation may persist | conscious fear or pain is not implied |

This table supplies competitor discrimination. It does not choose a winner by definition.

## 5. Valence-orientation limit

Let `K` be complete actual organization under a justified bearer boundary. Conditional C1 supplies a deterministic experiential assignment

\[
E=F(K).
\]

Let `v(E)` be an ordered valence label. C1 states that the same complete `K` cannot receive arbitrary different experiences within one theory. It does **not** specify which `F` is correct, nor which structural coordinate means negative rather than positive across substrates.

### Proposition 1: finite-proxy insufficiency

Suppose a biological anchor `K_a` has independently calibrated negative valence. Let a target `K_t` match `K_a` on any finite list of proxies—motivation, viability control, broadcasting, learning effects, or report—without establishing complete valence-preserving equivalence. Then C1 alone does not entail the sign of `v(F(K_t))`.

**Witness.** Enumerate deterministic valence maps for four complete K-types into `{-1,0,+1}`. There are 81 C1-compatible functions. Fixing the anchor negative leaves 27. Even when the target shares all three declared proxy flags with the anchor, exactly nine remaining functions make it negative, nine neutral and nine positive. Adding the premise that target and anchor are equivalent under a valence-preserving complete signature forces the target negative, leaving nine assignments for the unrelated types.

This is model-theoretic underdetermination between admissible C1 extensions, not arbitrary experience assignment to the same complete organization within one extension.

### Proposition 2: numeric sign is not valence orientation

For a scalar internal signal `x` with downstream action weight `w`, the logit contribution is `wx`. The coordinated change

\[
x'=-x,\qquad w'=-w
\]

preserves every logit. Sixteen exact finite cases were checked. This is a coordinate transformation when all ports are transported, consistent with R77. Therefore the plus/minus sign of a reward, prediction error or activation is not by itself the sign of experience.

Together the propositions yield an **anchor-or-axiom requirement**:

> A cross-substrate claim that a specified organization is negatively valenced requires either a justified valence-preserving structural homology to a calibrated anchor or an additional primitive orientation law. Motivation, survival value, scalar sign and language are not enough by themselves.

This is an explicit missing premise, not a proof that an artificial process lacks valence.

## 6. Relation to existing evidence

Directly checked sources constrain the claim:

- Damasio and Carvalho connect feelings to sensed and mapped body states in life regulation, but distinguish action programmes from feelings.
- Man, Damasio and Neven implement an artificial vulnerable homeostatic learner and call the added mechanism “feeling-like”; the demonstrated outcomes are self-regulation and adaptation, not a subjective measurement.
- Lyon and Kuchling state that the location and nature of valence across life remain unresolved while developing a biogenic framework.
- LeDoux argues that threat-detection and defensive-response mechanisms are not identical to mechanisms of conscious fear.
- Berridge and Robinson review evidence that incentive “wanting” is neurally dissociable from hedonic “liking.”

Accordingly, homeostasis is a strong evolutionary bridge candidate but not a deductive valence theorem. Wanting, defence and task protection remain separable from felt pleasantness or unpleasantness.

## 7. From inorganic matter to AI

- A stone mountain has long-lived structure but normally lacks an endogenous maintained boundary, a counterfactual viability model and coordinated repair at the mountain scale. Under UCT it is not assigned “no experience”; rather, its actual process organization gives no present basis for a cell-like valence claim.
- A cell adds metabolism, membrane regulation, damage response and reproduction. These provide a natural orientation toward continued viable organization, but whether that organization is felt negatively remains an additional bridge question.
- Multicellular organisms add nested viability conflicts and intercellular coordination. Organism-level maintenance cannot be inferred from each cell's local interest.
- Animals add specialized threat, interoceptive, learning and hedonic systems. The separation of survival circuits from conscious fear prevents simple identification.
- Humans provide the strongest calibrated anchors through converging report, lesion, pharmacological, behavioural and physiological evidence, still with dissociations.
- Artificial agents can implement world models, continuation preferences and even vulnerable homeostatic loops. These facts increase organizational comparability but do not automatically establish human-like valence. UCT leaves open non-human experiential organization and alien valence.

## 8. Originality assessment

The homeostasis–feeling proposal, wanting/liking dissociation, threat/fear distinction, inverted-qualia concern and need for biological or functional comparison all have substantial prior art. R87 does not claim them as discoveries.

The project-level contribution is the combination of:

1. exposing carrier-count confounding in an otherwise full-rank AI identity design;
2. repairing it with a fixed two-process world and exact isolating contrasts;
3. separating C1 determinacy from valence orientation by an explicit anchor-or-axiom requirement;
4. showing why numeric reward polarity and control avoidance cannot supply that orientation;
5. deriving divergent intervention predictions for motivational, viability and hedonic bridges.

This package is potentially useful for a methods/theory paper after external review. The exact rank proof is not itself a consciousness result, and the valence limit is close to long-standing functionalist and inverted-qualia problems. Historical originality remains moderate, not major.

## 9. Conclusion and next step

The strongest warranted conclusion is:

> Even a full-rank continuation experiment can fail if the physical number and kind of later carriers are not matched. After matching them, continuation targets can be behaviourally separated in principle. But C1 plus self-maintenance, motivation or reward sign still does not orient phenomenal valence across substrates. That orientation requires a further homology or axiom.

Next, write the seven basis scenarios in two blinded, schema-identical paraphrase families and audit each for consequence comprehension. In parallel, test the three bridge hypotheses on a fixed counterexample battery: reward relabelling, outsourced maintenance, other-directed prediction, wanting/liking dissociation and defence without conscious fear. Do not query a model until the carrier-matched text passes this audit, and do not call any outcome fear without an independently defended valence bridge.

