# Relational differentiation and joint experiential constraints

Version 0.1 — BR20261008 — 8 October 2026

Author-requested conceptual research extension after R174. This is not R175, a publication, an independently peer-reviewed result, a new basal-experience axiom, or a claim of a major original mathematical breakthrough.

## 1. The problem we are trying to change

The author's question is how a small organizational change could produce an experiential change that matters: from cells to organisms, separated hemispheres to coupled brains, and neurons to distributed mechanical implementations. Repeating a proof that reports do not identify experience does not answer it. Nor does increasing a graph's node count.

This note investigates **relational differentiation**: a local physical asymmetry can give many existing components different roles in one relational organization. It then asks how those roles could constrain experience *jointly*, instead of assigning a separate unconstrained interpretation to every coordinate.

Two distinctions are essential. First, introducing a new actual relation changes a system, whereas learning a new correspondence only changes an investigator's knowledge. Second, a unique structural position is not already an identified human quality. The construction proves selected role differentiation and a joint correspondence constraint; it does not derive redness, pain, temporal phenomenology or an amount of experience.

The proposed research shift is from indefinitely naming separate B_min/B_order/B_fam obligations to testing a jointly constrained candidate experiential relation structure. These obligations remain open; they are neither abolished nor satisfied by notation. Where two targets have no independently justified cross-relation or common token, this proposed unification is not yet available.

## 2. Existing map and direct precedents

The latest observed repository checkpoint is R174 at 49b7bf2e2ce43b6f26ff27f6353efb4d28a76caf. R174 adds the parallel-bypass rival H to the earlier S/C temporal model and leaves B_order open. Its mechanism identification remains useful, but the new author instruction warrants addressing the structural-to-content bottleneck directly rather than adding more bypasses.

Internal precedents already establish much of the background: A:SYM_PREM and A:EQUIV_SELECTOR discuss symmetry and selection; R146:CENTERED_REFERENCE separates a centered family from an unjustified unique owner; R157:COORDINATE_TRANSPORT preserves grounded formulas, while R157:SEMANTIC_RESIDUAL leaves external phenomenal naming open; R149:COMPATIBILITY distinguishes selected descriptions from complete type. TE20261008 already supplied an XOR refinement. None is relabeled as a new discovery here.

Two primary critiques directly bear on this proposal:

- Johannes Kleiner, *Towards a structural turn in consciousness science*, **Consciousness and Cognition 119 (2024), 103653**, [DOI](https://doi.org/10.1016/j.concog.2024.103653), [author/institutional PDF](https://epub.ub.uni-muenchen.de/120081/1/1-s2.0-S1053810024000205-main.pdf). Sections 3–5 distinguish structural methods from structural individuation, analyze automorphisms, and challenge the explanatory use of a bare isomorphism when phenomenal structure lacks independent specification. This is a direct precedent and a substantive objection, not support for claiming that symmetry analysis was invented here. C1 adds an explicitly consciousness-specific interpretation, so the paper does not by itself prove C1 false. It does block treating an arbitrarily renamed copy of a physical graph as independent confirmation of a phenomenal explanation.
- Davide Aldé, *Two geometrical arguments against similarity structuralism*, **Synthese 207 (2026), 204**, published **4 May 2026**, [DOI/full text](https://doi.org/10.1007/s11229-026-05562-5). Sections 3–4 argue that similarity geometry alone does not adequately recover specific color-composition distinctions. We do not settle that philosophical argument. Its relevant warning is that a geometrically unique location need not explain why a particular phenomenal distinction is salient. Our ring is not a color-space model.

Reading scope: selected substantive sections of the full primary texts above, not an exhaustive literature census. Group actions, stabilizers, matrix-power bounds and isomorphism cosets are classical. The contribution claimed here is a constructive application and a change in the project's explanatory strategy.

## 3. Fixed vocabulary, roles and actual relations

Let X be a finite structure in a fixed relational vocabulary Sigma, with any claimed sorts, pointing, weights and ports included. Let Gamma=Aut_Sigma(X). Two elements have the same **symmetry role** when an automorphism sends one to the other. This is a declared mathematical notion, not a psychophysical definition or an experience measure.

For this finite setting, automorphism orbits coincide with classes indistinguishable by parameter-free first-order formulas: invariance proves one direction; a finite full relational description with a distinguished variable proves the other. This finite claim is not asserted for arbitrary infinite structures. Numerical weights below can be encoded as finitely many edge-weight predicates with fixed meanings; they are not freely relabelled colors.

**P1: adding a specified relation can refine roles.** Expand X by a relation R on its existing carrier, without removing any old relation. Then

\[
\operatorname{Aut}(X,R)=\{g\in\Gamma:gR=R\}\leq\Gamma.
\]

Hence every new orbit is contained in an old orbit. Strict role differentiation occurs exactly when some old orbit splits into at least two new orbits. A proper subgroup alone is insufficient: an undirected n-cycle has dihedral symmetries; adding a consistent direction to the entire cycle leaves only rotations, but all vertices still lie in one orbit.

Proof: an automorphism of the expanded structure must preserve both the old relations and R; conversely their simultaneous preservation suffices. Inclusion of groups gives inclusion of orbits. The directed-cycle example proves the failed converse.

This concerns actual organizational change only if R is independently a realized relation. Adding an analyst's colored sticker to a diagram is not a physical intervention. Conversely, observationally discovering an old R does not mean the system just acquired a new role. A selected vocabulary can omit many distinctions in the complete physical organization. Therefore splitting selected orbits does not establish how many *previously absent complete experiential distinctions* have appeared.

## 4. Thought experiment BR-1: one coupling, eight differentiated roles

Fix n>=3 otherwise identical units on a ring with symmetric nearest-neighbor couplings. The model fixes a common clock and a uniform initial state, so a selected initial pulse does not covertly distinguish one vertex. There are no individual names or unique vertex tags in the modeled structure. Integers 0,...,n-1 are notation for calculating; admissible automorphisms need not fix them.

Change only one directed coupling strength: the route from unit 0 to unit 1 gains epsilon>0, while its reverse and all other routes keep their old strengths. This is a weighted expansion of the same undirected ring, not the addition of another unit.

**P2a: the new weighted ring is rigid.** The original ring has 2n automorphisms, all rotations and reflections. The uniquely strengthened directed edge identifies its source and target in the selected structure. An automorphism must fix both adjacent vertices individually. Following the cycle fixes every other vertex. Thus only the identity remains, and the n vertices occupy n different selected symmetry roles.

The result holds for every n>=3 and every nonzero positive epsilon in the declared range. It is not inferred from the eight-unit enumeration. The ring's role partition changes from one class to n classes while its member count is constant.

What this contributes: a new relation can reorganize the roles of old members throughout a whole, not merely append one more local state. This is a candidate explanation of organizational differentiation relevant to multicellular specialization and artificial organization. It is not a biological evolutionary law, and neither a nervous system nor language is assumed. A pre-existing physical asymmetry omitted by the model could already distinguish the roles; actual applications must check this rather than infer full-organizational novelty from the drawing.

### 4.1 The tiny-asymmetry trap

Use the following actual update equations of the *abstract model*, with destination index first:

\[
x_{t+1}=M_\epsilon x_t,\quad
M_0=\frac{I+A(C_n)}{10},\quad
M_\epsilon=M_0+\frac{\epsilon}{10}e_1e_0^T,
\quad 0\leq\epsilon\leq\tfrac12.
\]

The time index is a discrete physical-step placeholder. x is a signal amplitude vector; this is a dissipative linear network, not a probability-transition matrix or a neural fit. All initial components equal 1 in the executable witness. No report channel is required. Each unit's next value is actually computed from the displayed neighbors in the simulation; a hardware realization has not been established.

**P2b: dynamical effects approach zero continuously although exact role counts jump.** In the infinity operator norm, both matrices have norm at most rho=7/20 and their difference has norm epsilon/10. The noncommutative telescoping identity gives, for every integer t>=1,

\[
M_\epsilon^t-M_0^t
=\sum_{j=0}^{t-1}M_\epsilon^{t-1-j}(M_\epsilon-M_0)M_0^j,
\]

and therefore

\[
\|x_t^\epsilon-x_t^0\|_\infty
\leq t\frac{\epsilon}{10}\rho^{t-1}\|x_0\|_\infty.
\]

At every fixed t this tends to zero with epsilon. Nevertheless the exact selected symmetry-role count is n for every epsilon>0 and 1 at epsilon=0. Thus role count is discontinuous in this ordinary matrix norm. It is not justified as a continuous experiential-richness scale. If one additionally demands continuity of a proposed richness metric in this geometry, this example rules out *that metric equalling exact orbit count*. It does not prove every legitimate experience measure must use this geometry, or contradict C1's own explicitly chosen type geometry.

In the eight-unit calculation, epsilon=1/2, 1/10 and 1/1000 all yield eight selected roles, but step-four maximum signal differences are respectively 0.00275, 0.000526 and 0.0000052006. These are modeled signal differences, not experiential magnitudes.

### 4.2 The distant-network trap

**P2c: role differentiation is not instant propagation.** With the common positive initial state, the first state difference at vertex i occurs at

\[
t_i=1+\operatorname{dist}_{C_n}(1,i).
\]

A changed contribution must first traverse 0->1, then reach i through nearest-neighbor steps. Before that many updates every path contributing to i avoids the changed edge. At the first permitted time there is a positive path contribution, and nonnegative weights prevent cancellation. For n=8 the first-change times at vertices 0,...,7 are (2,1,2,3,4,5,4,3).

The global graph's exact symmetry changes as soon as its coupling is changed, but distant local states do not change immediately. This separates a description of an installed global relation from its propagation in an actual episode. It is directly relevant to fiber-separated hemispheres and cosmic mechanical networks. A chosen actual token and interval must contain the relations being claimed; neither a static role index nor a future available route is an actual past communication event. No superluminal influence, instantaneous global feeling or unique subject follows.

## 5. Thought experiment BR-2: a common experiential correspondence

Consider two fixed finite Sigma-structures X and Y. Their carriers and independently interpreted relations are given. X may be a proposed physical relational description; Y may be a candidate experiential relational description **only under the independent admission conditions in §6**. At the mathematical stage they are simply two structures. Let

\[
H=\operatorname{Iso}_\Sigma(X,Y),\qquad
H_A=\{f\in H:f(a_i)=b_i\ \text{for every }i\}.
\]

A is a list of proposed correspondence pairs. It is evidence or a semantic hypothesis about an already fixed system, not a new physical coupling. Empty H_A means that this *joint description/anchor package* has no solution; it does not alone falsify C1.

**P3: one-map compatibility and the exact residual ambiguity.** Suppose H_A is nonempty and choose f_0 in H_A. Write

\[
\Gamma_A=\{g\in\operatorname{Aut}(X):g(a_i)=a_i\text{ for all }i\}.
\]

Then

\[
H_A=\{f_0\circ g:g\in\Gamma_A\},\qquad
\{f(x):f\in H_A\}=f_0(\Gamma_A x).
\]

Proof: if f and f_0 agree at each a_i, then f_0^{-1}f is an automorphism fixing every a_i. Conversely composing f_0 with such an automorphism preserves every anchor. The image formula follows immediately. Thus a selected element's counterpart is determined exactly when its stabilizer orbit is a singleton. A target function of the correspondence is determined exactly when it is constant over H_A. This latter criterion also handles relational targets for which pointwise uniqueness is unnecessary.

Any further anchors intersect H_A with additional constraints. They can remove ambiguity, be redundant, or make the whole package inconsistent. In particular,

\[
(\forall i\ \exists f_i\in H\ f_i(a_i)=b_i)
\quad\not\Rightarrow\quad
(\exists f\in H\ \forall i\ f(a_i)=b_i).
\]

This is the quantifier error a collection of separately plausible phenomenal interpretations must avoid. A route for each separate interpretation is not yet one joint interpretation of the same token.

### 5.1 An exact eight-element witness

Let X and Y each be an unweighted eight-cycle, with separate carrier labels x_i and y_i. The elements are anonymous structural elements; this is **not** a model of eight real colors or eight successive experiences.

| Correspondences admitted | Number of compatible maps | Consequence |
|---|---:|---|
| None | 16 | Rotation and reflection remain |
| x_0 -> y_2 | 2 | Reflection remains |
| x_0 -> y_2, x_4 -> y_6 | 2 | Antipodal second anchor is redundant for reflection |
| x_0 -> y_2, x_1 -> y_3 | 1 | Every remaining element is fixed by the common map |
| x_0 -> y_0, x_1 -> y_4 | 0 | Each anchor separately is possible, but jointly they violate adjacency |

With the two adjacent compatible anchors, x_2 must correspond to y_4 and x_7 to y_1; these are held-out structural predictions. One does not need to postulate six further free element-by-element matches. But this conclusion presupposes the given structures, relation meanings and anchors. It does not manufacture independent phenomenal evidence for them.

The same mathematics appears in BR-1 and BR-2 for different reasons. BR-1 changes the selected organization; BR-2 leaves it unchanged and narrows possible descriptions. Confusing them would turn improved scientific knowledge into a spurious increase in experience.

## 6. Exact UCT attachment: what is positive and what remains missing

### 6.1 Positive role transport

Fix an actual token P over a specified interval and its complete K-organization, as required by A/I v1.2. Independently ground the selected ring relations, weights, executed events and current pointing within K. Do not claim that the finite ring exhausts the full organization. If the unique directed relation is only a diagram annotation, the following application is unavailable.

In the weighted finite ring each role is definable without individual names: the special relation identifies source and target, and ring relations distinguish the remaining positions. Let theta_i be the corresponding K-interpretable role formula. Under C1 and R157, every theta_i and its uniqueness transport to the experiential structure with all physical parameters mapped by h_P.

This gives a positive conditional claim: **a grounded actual organization containing those differentiated relational roles has their differentiated experiential structural counterparts**. They need not be accessed by introspection, expressed in language, owned by a unique extra observer, or used by a report module. No new experience-existence threshold is introduced. This does not establish that these roles exhaust experience, that a real symmetric predecessor lacked every such distinction, or that n role formulas imply n subjects or n units of richness.

### 6.2 One token, one jointly constrained map

For the correspondence result to constrain particular experience, more is needed. X and Y must be independently admitted interpretations of the **same selected vocabulary on the same token**, with a justified restriction of the complete C1 map carrying X onto Y. Every proposed anchor must refer to that common restriction. Individual successful matches cannot silently switch bearer, interval, physical subset, phenomenal relation meaning or h_P.

Under that package, the actual restriction belongs to H_A, so H_A must be nonempty; every claim invariant across H_A is a conditional prediction. H_A may include more maps than actually extend to a complete K-isomorphism. Thus its ambiguity is ambiguity under the selected information, not proof of genuine metaphysical freedom in the complete theory. A singleton H_A is sufficient for selected correspondence uniqueness; several elements in H_A do not imply several genuinely realizable experiential assignments.

C1 is tokenwise. It does **not** by itself provide one shared h across different trials, people, species or substrates. A across-trial quality space requires an additional justified family correspondence. Eight hypothetical brain states cannot simply be inserted as eight constitutive events of one actual token. These restrictions are especially important for interpreting familiar hue spaces and the gradual replacement experiments.

### 6.3 What cannot be obtained from the algebra

Even a rigid graph, or a single possible isomorphism between two known graphs, does not establish that Y is a phenomenal structure or that a particular vertex is redness, pain or experienced order. Choosing Y to be a renamed copy of X and calling its points feelings makes the matching easy but does not independently test the explanatory claim. C1's substantive experiential commitment remains an axiom; this note neither derives nor refutes it.

Existing R157 semantic residual therefore remains. The proposed advance is narrower and useful: **once a candidate set of relations and some correspondences have independent support, their consequences are joint, and other correspondences can become predictions rather than additional free stipulations.** Whether human phenomenal evidence supplies a suitable structure and anchors remains OPEN. Reports may contribute fallible evidence on a restricted domain without becoming a universal experience gate.

## 7. How this changes the retained thought experiments

**Formation and biological organization.** Search for a new actual directed, compositional or body-relative relation that differentiates old roles while preserving identified old relations. Do not assume every added component or every asymmetry increases richness. A developmental example must independently establish the relation and its experiential relevance; the ring supplies neither biological history nor a biological threshold.

**Separated hemispheres and cosmic mechanical networks.** Ask which role relations are preserved and over what actual interval they are executed. A global drawing may be asymmetric while a distant process has not received any changed signal. Distance or slow mechanics alone settles neither complete experiential identity nor a subject's spatial center.

**Silicon replacement and copied memory.** Matching isolated local functions or labels does not guarantee one jointly compatible global correspondence. A claimed role-preserving replacement must preserve the relevant relation structure and actual timing; material identity is not built into the abstract matching theorem. Complete physical sameness, numerical personal identity and a unique successor remain separate claims.

**Human array, abacus/calculator and artificial network.** External naming of parts does not create intrinsic roles, and an observer's lookup table does not make all its represented relations actual. Participants, implemented computation and coupled processes can overlap. The proposed analysis does not require selecting a single owner above them.

## 8. A bounded next problem and an explicit stopping condition

The next positive problem is to choose **one** proposed phenomenal relation richer than generic similarity—for example a separately motivated composition, incompatibility or temporal relation—and ask whether a physically grounded relation plus independently supported anchors forces an uncalibrated experiential relation. Freeze the relation meanings and mapping domain before the held-out prediction. A concrete success consists of at least one forced, independently assessable target relation that rules out a rival mapping without redefining the target after observing it.

Failure has two distinct forms: no common map exists, so the proposed descriptions/anchors are inconsistent; or several common maps disagree on the selected target, so that target remains unidentified. Even a unique map is inadequate if the alleged experiential structure was manufactured from the physical one. Keep these failures, and stop rather than expanding another generic certificate or statistics chain.

This proposal remains open to rejection. It cannot guarantee a major breakthrough, a universal measure for silicon and biology, or an explanation of intrinsic phenomenal character. It does deliver a concrete relation-change mechanism, an exact warning against a tempting richness metric, a finite-propagation distinction, and a unified way to make candidate content interpretations constrain each other.

## 9. Validation and review scope

MODEL.py independently enumerates the C8 automorphisms, checks anchor compatibility, computes exact rational trajectories, checks small-effect bounds and verifies first-arrival times. General claims are supported by P1–P3's proofs, not by enumeration. No human experiment or biological manipulation was performed. No neural circuit, full physical signature, experiential geometry, semantic anchor or independent review closure is claimed.

All earlier graph objects and mandatory R171/R172 overlays are preserved. QC-06/07 remain reviewer-controlled. A minor wording inconsistency in R174-G5 is recorded separately for correction: its first counterexample says *same* F_order inside one Theta_STC fiber, whereas a sufficiency counterexample needs *different* F_order in the same fiber, as R174 §8 already states. This editorial finding is not the conceptual result of the present note and does not invalidate R174's correctly scoped model.
