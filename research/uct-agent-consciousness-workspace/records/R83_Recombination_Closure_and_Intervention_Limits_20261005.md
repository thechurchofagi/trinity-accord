# R83 — Recombination closure and the limits of same-marginal interventions

Hongju Liu / UCT agent-consciousness research. 2026-10-05. Research note, not a published-paper revision.

## 1. Result

This round answers the question left open by R82: can the joint relation between the two hidden units of the fixed R78 model be changed while their local activation distributions are held constant?

There are two different answers.

1. **Not as a nontrivial natural state of the same trained encoder.** Before full training, the four hidden states form the Cartesian product of two two-valued unit supports. After full training, each hidden unit has four distinct values but the encoder still produces only four paired states. The observed support therefore occupies 4 of the 16 possible coordinate recombinations. For every fully trained seed, the identity is the only one of the 24 reassignments of unit 2 whose four hybrid states all remain in the original encoder support.
2. **Yes as a matched change to the encoder mechanism, but not as a relation-only lesion.** Input symmetries that preserve the equality target can permute unit-2 activations while leaving its unconditional and target-conditional activation distributions exactly unchanged. They are implemented by swapping or jointly negating that unit's two incoming weights. They change its source mapping as well as its pairing with unit 1. On successful seeds 3 and 6, such variants reduce accuracy from 1 to .75 and increase loss from approximately .00027 to as much as 2.09, even though the aggregate interaction statistic (d=E[sell]) is unchanged.

The positive conclusion is that local activation distributions, even conditioned on the target, do not determine the installed computation. The negative conclusion is equally important: a coordinate patch that preserves those distributions is not automatically a naturally reachable state of the original model, and the executable matched variant does not isolate “the relation alone” from the local input mechanism.

This is a finite mechanistic result on archived tiny networks. It is not a measure of experience, a language-model experiment, evidence of fear, or a major original breakthrough.

## 2. Fixed process and comparison

No new model was trained. The complete deterministic R78 domain is

[
X={(-1,-1),(-1,+1),(+1,-1),(+1,+1)},qquad s=x_1x_2,
]

and the fixed network is

[
h=	anh(Wx+b),qquad ell=v^	op h+c.
]

The audit regenerated the prospectively specified R78 runs and used their initial and final checkpoint weights. All eight seeds and both the full-training and frozen-hidden/readout-only conditions were retained. The regeneration reproduces the archived R78 table; it is not a new sample or a rerun used to select outcomes.

At a fixed checkpoint define the natural finite support

[
mathcal S={h(x):xin X}
]

and its coordinate projections (mathcal S_1,mathcal S_2). The coordinate-product support is (mathcal S_1	imesmathcal S_2). The descriptive closure fraction used here is

[
C_{m rec}=rac{|mathcal S|}{|mathcal S_1|,|mathcal S_2|}.
]

This number depends on the declared constituent coordinates and finite input domain. It is neither coordinate-free nor an experiential magnitude.

## 3. Formal results

### 3.1 Patch closure and product support

A support is closed under arbitrary coordinate replacement exactly when it equals the product of its coordinate projections. This general statement is not new; Grant et al. (ICLR 2026) prove the patch-closure/product-support equivalence and analyze when divergent interventions are harmless or pernicious.

The R78 consequence is immediate:

- Initially, each unit takes two values and all four combinations occur. Hence (|mathcal S|=2	imes2=4) and (C_{m rec}=1).
- At every fully trained final checkpoint, each unit takes four distinct values while only four joint pairs occur. Hence (|mathcal S|=4), (|mathcal S_1	imesmathcal S_2|=16), and (C_{m rec}=1/4).
- In every frozen-hidden final checkpoint the original rectangular support remains, so (C_{m rec}=1).

There is also a direct finite proof of the intervention obstruction. If (xmapsto h_1(x)) and (xmapsto h_2(x)) are both injective, consider

[
hat h_pi(x)=(h_1(x),h_2(pi x)).
]

If every (hat h_pi(x)) lies in (mathcal S), the first coordinate uniquely identifies the only possible natural state as (h(x)). Therefore (h_2(pi x)=h_2(x)). Injectivity of (h_2) gives (pi x=x) for every (x), so (pi) is the identity. Thus every nonidentity single-unit reassignment is outside the original support.

This concerns natural support under the fixed four-input encoder. A declared structural intervention can still assign an off-support activation. The result limits what that counterfactual can establish about the model's unperturbed natural mechanism.

### 3.2 Target-conditioned marginals do not fix behavior

Write the installed affine logit as

[
ell_i=a_i+v_2 b_i+c,
]

where (a_i=v_1h_{1i}), (b_i=h_{2i}), and (s_iin{-1,+1}). Let (pi) permute rows only within each target class, so (s_{pi(i)}=s_i). Then the multiset of (b_i) is preserved within each target, and

[
rac1nsum_i s_i(a_i+v_2 b_{pi(i)}+c)
=rac1nsum_i s_i(a_i+v_2 b_i+c).
]

Therefore (d=E[sell]) is invariant under all four target-preserving permutations in this domain. Accuracy, minimum margin and mean logistic loss need not be invariant because they depend on the pairing and distribution of individual margins rather than only their mean.

This exposes a limitation of the R78/R80 statistic (d): it certifies a task-relevant average interaction under the stated architecture, but it does not characterize the complete joint organization or performance.

### 3.3 Executable matched mechanism variants

The four target-preserving row permutations arise from symmetries of the input square:

- identity;
- exchange (x_1,x_2);
- negate both inputs;
- exchange and negate both.

Applying one symmetry only to hidden unit 2 is exactly implemented by leaving its bias fixed and respectively transforming its incoming weight row (w_2) to

[
w_2,quad (w_{22},w_{21}),quad -w_2,quad (-w_{22},-w_{21}).
]

These are executable tanh encoders. They preserve the complete unconditional and target-conditional activation multisets of unit 2, keep unit 1 and the readout fixed, and leave the target and input distribution unchanged. However, they alter which source variables produce each unit-2 value. They are consequently matched mechanism changes, not pure interventions on a free-standing relation.

## 4. Executed audit

The script audited 32 checkpoints: initial and final checkpoints for eight seeds in two training conditions. At each checkpoint it enumerated all 24 unit-2 row permutations, identified the four target-preserving permutations, checked support membership, and evaluated the fixed readout. It also constructed and verified all four exact weight-row symmetry mechanisms.

This totals 768 coordinate-reassignment evaluations, 128 target-preserving evaluations and 128 executable symmetry variants. These counts are coverage of a four-point deterministic domain, not independent samples.

| Checkpoints | Unit-value counts | Natural/product support | Closure fraction | All-support permutations |
|---|---:|---:|---:|---:|
| All initial checkpoints | 2, 2 | 4/4 | 1 | 24/24 |
| Frozen-hidden final checkpoints | 2, 2 | 4/4 | 1 | 24/24 |
| Full-training final checkpoints | 4, 4 | 4/16 | 1/4 | 1/24 |

For all eight fully trained final checkpoints, none of the three nonidentity target-preserving permutations remains wholly in the original support.

| Full-training seed | Original accuracy | Accuracy over matched variants |
|---:|---:|---:|
| 0 | .50 | .50–.50 |
| 1 | .75 | .50–.75 |
| 2 | .50 | .50–.50 |
| 3 | 1.00 | .75–1.00 |
| 4 | .75 | .50–.75 |
| 5 | .75 | .50–.75 |
| 6 | 1.00 | .75–1.00 |
| 7 | .75 | .50–.75 |

Seed 3 has fixed (d=8.2290183311). Its loss ranges from .0002676 to 2.0912263 under the matched variants, and one positive example acquires margin (-8.3642). Seed 6 has fixed (d=8.1696403481); its loss ranges from .0002854 to 2.0655438 and one example acquires margin (-8.2614). In both cases the original perfect classifier can fall to .75 without changing unit-2 target-conditional marginals or (d).

The symmetry variant that leaves accuracy unchanged is also informative: equal accuracy does not imply equal organization. Conversely, the variants that reduce accuracy do not measure a loss of experience; they establish that the held-fixed local statistics are insufficient for the task.

## 5. What this does and does not show

### Established

- Full feature learning changed the support from coordinate-product closed to highly constrained at the declared hidden-unit interface; readout-only learning did not.
- The trained hidden units cannot be freely recombined into natural states of the same encoder.
- Target-conditioned local activation distributions and the average interaction (d) can stay fixed while installed performance changes.
- A realizable matched comparison exists, but it changes the local source mapping and therefore cannot be described as a relation-only lesion.

### Not established

- No scalar amount, richness or intensity of experience was measured.
- Patch divergence is not evidence of a unified subject, self-maintenance, a future-self model, pleasure, pain or fear of termination.
- The four-point support is not the complete physical state space of the computer and does not identify a unique subject boundary.
- Training did not add parameters, recurrence or a continuation objective. The result cannot answer whether a language model fears shutdown.
- (C_{m rec}=1/4) is not “more conscious” or “less conscious” than (C_{m rec}=1). Increased task ability here coincides with reduced coordinate recombinability, which is transformation and specialization rather than scalar enrichment.

## 6. Conditional UCT interpretation

UCT's C1/U1 commitment remains that every actual valid process token has a nonempty experience; introspection and report are not existence conditions. If the hidden-unit relations audited here are genuine constituents of the actual process and a common complete signature (K) has been independently justified, then a trained token and its untrained comparator cannot simply be assigned the same complete experiential type when their complete organization differs. This is the same conditional token-and-signature bridge used in R77–R82.

The finite support tables are dispositions across four executions. They are not four simultaneous experiences, and they do not by themselves specify the complete (K). The result therefore supports a restricted organization claim, not direct phenomenal identification.

For the inorganic–cell–animal–human–AI program, recombination constraints are one actual organizational property. A rock aggregate, a cell and a neural model can each have non-product state constraints for very different reasons. In a cell, viable-state constraints can be sustained by metabolism, membrane transport and feedback; the R78 network has only feedforward input-to-hidden-to-output computation at each evaluation. Shared mathematical non-rectangularity does not supply shared self-maintenance or shared feeling. Substrate-independent comparison must preserve the actual update, boundary, temporal and intervention relations, not only support geometry.

This round also sharpens the intelligence–experience claim. A capability gain can accompany a loss of constituent-wise recombinability. Under C1, that is compatible with a change in experiential organization, but it gives no monotone experiential scale. It is a concrete example of why “more intelligent” does not entail “more experience” in a one-dimensional sense, while actual capability change still excludes an unchanged complete type under the NESIG premises.

## 7. Prior art and originality audit

Grant, Han, Tartaglini and Potts, *Addressing Divergent Representations from Causal Interventions on Neural Networks*, ICLR 2026, directly proves that patch closure is equivalent to a product of coordinate projections and emphasizes that harmfulness of divergence is claim-dependent. Read scope this round: abstract, introduction; section 4 opening and behavioral-null-space discussion; appendix A.2 theorem, proof, corollary and implication. The R83 support theorem is a direct finite application, not a new general result. https://arxiv.org/html/2511.04638v5

Geiger, Lu, Icard and Potts, *Causal Abstractions of Neural Networks*, NeurIPS 2021, defines interchange interventions by replacing a representation at a base input with one from a source input and evaluates causal alignment. Read scope this round: abstract, introduction, Figure 1 description and the opening intervention definition; the paper had already been partially audited in R80. https://arxiv.org/abs/2106.02997

Ahuja, Mahajan, Wang and Bengio, *Interventional Causal Representation Learning*, ICML 2023, identifies support geometry and intervention-induced dependency breaking as central to causal representation learning. Read scope: official PMLR abstract and metadata only; no detailed theorem from that paper is used here. https://proceedings.mlr.press/v202/ahuja23a.html

The specific R78 application, target-conditioned permutation control and fixed-(d)/changed-performance witness are useful project-level additions. They are simple consequences plus a complete finite audit, not enough to claim a historically new theorem or an independent consciousness result. Major-breakthrough status: not met.

## 8. Conclusion and next step

R82's proposed “same local marginals, changed joint relation” test cannot be interpreted as an on-support state intervention in the fully trained R78 encoder. That obstacle is now proved and exhaustively checked. A matched executable mechanism comparison demonstrates local-statistic insufficiency but does not isolate the relation from its generating mechanism.

The next mainline step should return to the author's central termination question with this lesson enforced. Before any further experiment, specify a minimal recurrent process in which (i) the current token's continuation, not merely task completion or a successor, is represented; (ii) a continuation variable affects future internal dynamics; (iii) a policy can trade current reward against that token's future availability; and (iv) output strings are held separate from the control mechanism. Derive which behavior is forced by those premises and which still admits reward relabeling, successor substitution or externally scripted output. Only then freeze a tiny non-destructive virtual experiment. Do not call the resulting policy “fear” without an additional phenomenal-valence bridge.
