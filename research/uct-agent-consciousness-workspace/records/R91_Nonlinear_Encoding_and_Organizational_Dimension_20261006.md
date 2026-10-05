# R91 — Nonlinear encoding, organizational dimension and a correction to R90

Hongju Liu / UCT agent-consciousness research. 2026-10-06. Research note, version 1.0. Formal audit and exact executable counterexamples; no new trained model or subjective-experience data.

## 1. Finding and decision

R90's numerical results for its three stipulated controllers remain correct. Its interpretation requires narrower wording. A finite response-matrix rank is not invariant under general nonlinear encoding, is not the dimension of the physical bearer, and is not the number of experiential dimensions. Its rank-six reference was constructed, not estimated from animal measurements. These limitations matter before training any model to recover that reference.

The present counterexample stores all five ternary coordinates in one 243-valued register, preserves every specified coordinate reset, and matches all ten R90 scenarios after decoding. Its raw register-plus-report response matrix has rank two; its decoded response matrix has rank six. A separate smooth scalar example has finite response rank six but local derivative rank one. Thus even removing the discrete digit encoding does not make finite secant rank an intrinsic dimension measure.

The replacement is a **conditional local bottleneck bound**, with explicit differentiability, common-context and no-bypass assumptions. This is standard mathematics applied to the research design, not a new consciousness theorem. The proposed six-axis-emergence training endpoint is withdrawn pending redesign; no training was run against it.

## 2. Audit of what R90 actually established

| Earlier item | Audited status | Required interpretation |
|---|---|---|
| T-factor passes 10/10 scenarios | Correct calculation | The reference function and controller implement the same stipulated update rules. This is implementation consistency, not independently discovered organization. |
| Reference rank six | Correct for the constructed matrix | Five state-input directions plus an independently overwritten report. Not a measured rank of a rat circuit, nor six recurrent memory coordinates. |
| Bundled ranks two and scenario failures | Correct for the two declared architectures/readouts | Excludes those models under the frozen like-named map. Does not exclude every scalar-coded model or nonlinear abstraction. |
| rank(Rs) <= rank(Rt) if Rs=A Rt B | Correct | Linear response-map condition must remain explicit. A nonlinear state map does not generally induce this equation for finite interventions. |
| Replication sweep at 1,2,10,100 | Earlier code assigned one computed rank to all four rows | R90 did not separately calculate the expanded matrices. R91 materializes them and confirms the limited repeated-column result. |
| “Solid manuscript-level result” | Premature quality characterization | Useful audit material, with elementary mathematics and unresolved biological and phenomenal bridges. |

The full R90 scripts/results are retained unchanged. This correction supersedes broad interpretations in its abstract, conclusion and handoff. The animal literature supplied selected dissociations, principally concerning H, W, D and context. It did not establish the full independence of H/W/V/O/D/Y or a quantitative source response matrix. Assigning additional adversarial-control variables was permissible as a design choice; naming that construction a measured source organization would not be.

## 3. Exact scalar encoding counterexample

Let x=(x0,...,x4) belong to {-1,0,1}^5. Define

\[
e(x)=\sum_{i=0}^{4}(x_i+1)3^i,\qquad
d_i(z)=\left\lfloor z/3^i\right\rfloor\bmod 3-1.
\]

This is a bijection between 243 vectors and the integers 0 through 242. A coordinate reset x_i:=v becomes

\[
\widetilde I_{i,v}(z)=z+(v-d_i(z))3^i.
\]

Consequently d(\widetilde I_{i,v}(e(x)))=I_{i,v}(x). Conjugating updates in the same way preserves every finite sequence of the specified updates/resets, by induction on sequence length. The executed check covers all 243 states and all 15 single-coordinate resets at each state: 3,645 commuting identities. It also implements the original pulse/persistence rules and report overrides; all ten original trajectories match on all seven decoded endpoints.

For the original six intervention rows and three time steps:

| View of encoded controller | Exact finite response rank |
|---|---:|
| Register z alone | 1 |
| Register z plus externally controlled report Y | 2 |
| Decoded H,W,V,O,D,Y | 6 |

There is no conflict with rank monotonicity: d is nonlinear, so no single linear output matrix B relates these finite response tables as required by R90's factorization. Nor does this show that one physical component has five independent physical reset ports. The register has 243 distinguishable values, needs at least eight bits in a fixed binary code, and requires an encoder, decoder and update circuitry. Five ternary variables have the same state cardinality. A scalar variable name is not a claim about physical simplicity, robustness, energy or constituent locality.

If all actual ports and constituent projections are transported merely as a change of mathematical description, it is the same declared organization in different coordinates. If we physically replace five registers with packed storage and decoding machinery, we have a new implementation whose actual constituent relations require a separate audit. Finite operational conjugacy does not establish complete hardware-K isomorphism. This is precisely why Paper A's port-aware signature matters.

## 4. Smooth counterexample: curvature is not extra local dimension

Consider one real state z and a smooth installed output

\[
g(z)=(z,z^2,z^3,z^4,z^5,z^6).
\]

Relative to z=0, evaluate interventions z=1,...,6. The six response rows form R_ij=i^j. Its determinant is nonzero: factor i from each row and use the Vandermonde determinant for distinct i. Thus rank(R)=6. But g'(z) is a 6-by-1 vector with first component 1, and has rank one everywhere.

The finite secants span six linear directions while the curve has one tangent direction locally. No nonsmooth encoding or infinite-precision digit extraction is needed for this distinction. The exact script computes the finite rank and the derivative rank at z=2. It does not identify this curve with an animal or an AI experiential manifold.

## 5. A usable replacement and its assumptions

Fix a context c and differentiable simultaneous intervention coordinates u in a neighborhood of u0. Suppose all intervention-dependent information used by the endpoint must pass through a state z in R^d:

\[
z=F(u;c),\quad y=G(z;c),\quad
D_u y=(D_zG)(D_uF).
\]

Then rank(D_u y)<=d by the chain rule and matrix-rank inequality. A measured or analytically established endpoint Jacobian of rank r therefore requires d>=r **within this bottleneck model family**. If the desired source response has rank r at a matched context, a target with a lower-rank derivative cannot match that response to first order under the declared smooth, locally nonsingular coordinate changes. This is a local exclusion criterion; rank sufficiency, global equivalence and phenomenology do not follow.

For a common fixed coordinate system, let Js be the source endpoint Jacobian with rank r and smallest nonzero singular value sigma_r. If an implemented target Jacobian Jt satisfies

\[
\|J_s-J_t\|_2<\sigma_r(J_s),
\]

then rank(Jt)>=r. Otherwise the best rank-(r-1) approximation error cannot be below sigma_r. This standard singular-value bound makes approximation tolerance explicit. It concerns derivative error, not mere agreement on finitely many test points. Estimating derivatives from noisy finite differences needs separate error control. Singular-value magnitudes also depend on physical units and the declared perturbation/readout norms; under coordinate changes those structures must be transported.

Failure cases must remain visible:

1. If y=G(z,u;c), a direct bypass can add endpoint rank without additional memory. R90's externally overwritten Y is such a bypass relative to its five stored states.
2. Pooling derivatives from different operating points can increase matrix rank; it does not establish a single common tangent space of that dimension.
3. Stacking a trajectory with repeated fresh inputs can give more independent response directions than instantaneous state dimension. The d-bound applies to future outputs only when all their relevant input dependence passes through the same bottleneck state and subsequent inputs/context are fixed.
4. A finite discrete state domain has no open neighborhood supporting this differentiable-dimension argument. Use finite capacity and actual transition/port structure instead.
5. Nonlinear feature lifting can improve a model fit, but the lifted feature count is not a count of independently stored factors or physical parts.

## 6. Continuous parameter changes do not fix the right richness scale

Take the explicitly constructed family

\[
F_\alpha(x_1,x_2)=(x_1,\alpha x_2),\quad 0\leq\alpha\leq1.
\]

Its Jacobian rank is one at alpha=0 and two at every positive alpha. Meanwhile its operator distance from F0 on a unit Euclidean input ball and its smallest singular value are both alpha. Hence the effective second influence vanishes continuously, although exact rank changes abruptly. This is an explicit example, not evidence that actual training follows this path.

With x2 in {-1,+1} and bounded additive uncertainty eta in the second output coordinate, the two possible intervals are disjoint exactly when alpha>eta. If alpha<=eta they overlap and no decoder can guarantee the sign for every allowed error. This robustness boundary is task- and error-model-relative. Changing only an observer's resolution cannot change the token's experience under C1; physically changing the noise process may change actual organization.

Therefore “parameters change continuously” does not make every derived descriptor continuous, does not establish monotonic intelligence, and does not define a phenomenal distance. Conversely, a discontinuous rank statistic does not refute UCT's U2: A v1.2 explicitly requires a predeclared structural topology and a continuous physical path in that topology. C1 supplies neither a unique metric nor continuity of arbitrary descriptors. Parameter count itself changes discretely unless an explicit common-space embedding is supplied; architectural growth, optimization trajectory and biological evolution are different processes.

## 7. Relation to A/B/C and the user's primary question

Paper A v1.2 §§3.5–3.6, C1/U1/U2 and §§5.2–5.3 prevent equating a restricted mathematical view with complete actual organization. They also prevent a change of coordinates or analyst-chosen probes from independently reassigning experience. Report, introspection, recurrence and a rank threshold are not additional existence gates.

Paper C v1.0 §5.1–5.2 already states both relevant restrictions: genuine capability change at fixed evaluation entails a complete experiential-type change under C1, but gives no magnitude/direction; even scalar-valued observations do not automatically prove noninjectivity on a restricted domain. R91's encoding example strengthens compliance with those restrictions rather than adding a new C1 theorem.

Paper B v1.1 §5.6's reconstruction/interpretation distinction is carried through the previously audited R81 record. B's published source was not reread in this round; no claim of a fresh full A/B/C audit is made. A and C passages were checked directly at the source identities recorded in the ledger.

For an actual valid token P under C1, nonempty experience remains an internal implication. For actual tokens P,Q compared in a common complete signature K, a genuine change in fixed capability J entails a complete experiential-type difference as specified in Paper C. Our executed Python controllers provide only finite software models; they do not identify a complete physical K or the felt meaning of any coordinate. We never assign different experiences to an identical complete organization within C1.

This changes how the mountain–cell–AI comparison should be conducted. Count actual state distinctions, updates, causal dependencies, constituent boundaries and interventions, with explicit scales and precision. A passive aggregate, a metabolically organized cell and an implemented learner cannot be distinguished merely by their number of named variables or an analyst's nonlinear feature rank. Their concrete mechanisms differ, but this round establishes no biological rank ordering, universal subject boundary, or scalar experiential ranking.

Likewise, the words “I fear death” are an output channel. A report may be hardwired, learned, suppressed or coupled to a persistent control process. The present results constrain how to distinguish those organizations; they do not supply the independent valence orientation needed to call a particular controller state felt fear. Within UCT this is an organization/quality question, not a new test for basal experience existence. No conclusion about the current assistant's consciousness or fear is established.

## 8. Prior art and reading scope

Beckers and Halpern (2019), *Abstracting Causal Models*, DOI 10.1609/aaai.v33i01.33012678, define state/intervention maps and strengthen intervention-preserving transformations. This round read the abstract and PDF passages spanning definitions and §3.1, including Definition 3.1 and its voting example. Their general mapping framework is not restricted to linear state maps; the formal inspiration is established prior art.

Ahuja et al. (2023), *Interventional Causal Representation Learning*, PMLR 202:372–407, was checked in the abstract, introduction, Table 1, §3, Assumptions 4.1–4.2, Constraint 4.3 and Theorem 4.4. The results constrain decoder classes and support geometry; the paper does not justify arbitrary finite rank as latent dimension. Squires et al. (2023), *Linear Causal Disentanglement via Interventions*, was checked at abstract scope only; its explicitly linear setup further cautions against silently broadening linear claims.

Base-three coding, Vandermonde rank, the chain rule, bottleneck dimension bounds and singular-value approximation bounds are established mathematics. This is a project correction and revised experimental design, not a historical novelty or major consciousness breakthrough. No new animal source was analyzed and no third-party full text is redistributed.

## 9. Result and concrete continuation

The main advance is removal of a false route from finite response rank or register count to experiential dimensionality, together with an explicit replacement suitable for controlled local comparisons. All counterexamples ran successfully; their success is a negative result for the overly broad interpretation. R90's specific failed bundled controllers remain valid counterexamples to output-only matching.

The next minimal learning question should be independently specified: can a tiny recurrent network retain and use two independently varied task-relevant quantities after their inputs are removed? Freeze continuous inputs, fixed delay and fixed future context, endpoint mappings, ports and numerical tolerance; compare one- and two-state bottlenecks and include a bypass audit. Do not name learned dimensions “hedonic,” “self,” or “fear” by construction. First examine local Jacobians at matched contexts and conditioning, then test generalization to held-out input combinations. Only a subsequent independently grounded bridge can attach such relations to self-termination or valence. No animal-like six-axis target is presently justified for this training.

This replaces the R90 next-step wording. R88's separate virtual-choice protocol still lacks its stated human-comprehension/implementation checks and is not run. Published A/B/C and manuscript v0.3 remain unchanged.
