# Selected proof spine — existing results, consolidated in R138

7 October 2026. This is a selected readable ledger, not a replacement for the full R137 proof ledger. No new deductive claims or edges are introduced. Each result retains its stable source IDs. All full-organization interpretations require actual tokens and a common complete signature. Finite model proofs alone do not establish those premises.

## T1. Exact target identification

**Stable anchors:** C:P2_COORD, C:P2_FULL; finite refinements R131:TARGET_SPAN/R131:COMPLETE_LAW. **Status:** published factorization result; established mathematics.

Let S be a fixed set of admitted types/models, F:S->O an exact observation map, and Q:S->V a specified target. A target decoder exists on the attainable observations,

\[
g:F(S)\to V,\qquad Q=g\circ F,
\]

if and only if

\[
F(s)=F(t)\ \Longrightarrow\ Q(s)=Q(t),\qquad s,t\in S.
\]

**Proof.** If Q=gF, equal F-values have equal Q-values. Conversely, when Q is constant on each fiber, define g(y) as the common Q-value for all s with F(s)=y. Every y in F(S) has a preimage and the value is unique, so g is well defined and Q=gF. QED.

For Q equal to the complete type itself, this condition is injectivity of F. No claim of continuity, computability, stable estimation or statistical confidence follows. Restricting the domain can change injectivity. A finite number of real-valued observations is not, by itself, proof of noninjectivity.

For the finite full-simplex model p in Delta_n with exact probe expectations F(p)=Ap, include normalization by defining B to have first row all ones and remaining rows A. The payoff c^T p is identified throughout Delta_n iff c lies in row(B); the full p is identified iff rank(B)=n. **Proof:** row membership constructs the payoff from known expectations and normalization. If c is not in the row space, a vector v in ker(B) has c^T v !=0; a sufficiently small signed perturbation of the uniform interior p gives two simplex points with equal observations and unequal payoff. Full-law identification similarly is ker(B)={0}. This is R131's standard linear-algebra certificate, with normalization explicit, not a result for every restricted model family.

**Counterlimit:** distinct complete types can have F(s)=F(t). Then any target that separates them is not determined by F. Which types are physically realized remains a separate question.

## T2. Exact executable feedback abstraction in the declared class

**Stable anchors:** R137:CONTROL_MODEL, R137:LOCAL_LP, R137:EXACT_INTERFACE, R137:CLOSED_LOOP; antecedent R132:PARTIAL_CLOSURE. **Status:** existing project theorem with established control-theoretic antecedents.

Let S,Z,A,O be finite nonempty sets and alpha:S->Z onto. The current z=alpha(s) is actually observed. Concrete s is Markov-sufficient, including any persistent hidden mechanism, memory, resources and clock needed for the kernel. Let A(s) be the legal concrete actions and K(s,a;s',o) the joint successor/output kernel. The abstract model supplies nonempty legal requests U(z) and joint rows bar K(z,u;z',o), on the same declared time/output contract, with paired initial state z_0=alpha(s_0).

For every z,u consider a fixed memoryless action distribution w_{z,u} in Delta(A). It must use only z,u, put zero weight on every action illegal at any compatible concrete state, and have that conditional distribution at every invocation. Randomness is fresh conditional on history and independent of controller/plant randomness. Abstract controllers may use projected histories and private randomness, but not hidden s or decoder coins/actions. Their legal policies are defined on all histories.

Define

\[
p_{s,a}(z',o)=\sum_{s':\alpha(s')=z'}K(s,a;s',o).
\]

An exact decoder exists iff, for every z,u, a **single common** simplex vector satisfies

\[
w_a=0\quad(a\notin A(s)),\qquad
\sum_a w_a p_{s,a}(z',o)=\bar K(z,u;z',o)
\]

for all s in alpha^{-1}(z) and all z',o. These are finite linear feasibility constraints.

For a fixed decoder in this class, those conditions are equivalent to legal execution and preservation of every finite-horizon projected state/request/output law for every paired start and every legal abstract feedback controller.

**Proof of feasibility.** An observable decoder uses one w throughout the fiber. Its support must be legal and its joint row is the indicated mixture, so the constraints are necessary. Conversely, sampling a feasible w with the stipulated conditional randomness supplies the decoder. Choices for each z,u are independent within this declared interface class. QED.

**Proof of path-law preservation.** Given any compatible hidden state and the requested u, the next projected joint row is the same bar K. It remains that row after averaging over any conditional distribution of hidden states. Condition on a common controller seed; identical projected histories produce identical requested actions. Induction gives equality of the complete finite-horizon projected history distributions, and the support constraints give legality at each step. For necessity, use a one-step controller requesting any u at any concrete start s; law equality forces its row equation, and legal execution forces support zeros. QED.

Every bounded payoff of that projected history is consequently preserved. Costs, concrete action labels and hidden states not included in the projected target are not thereby preserved. This is one-way abstract-to-concrete controller transport; it is not equality of every concrete capability or complete structural isomorphism. Failure is only failure in this restricted decoder class, not every possible sensor, memory or multi-step implementation.

**Existing separating examples:** R137:OBSERVATION_GAP gives two hidden states requiring opposite successful actions; each has a perfect state-aware action, but one common visible decoder has worst error at least 1/2. R137:SEED_GAP gives equal one-time fair marginals but temporal path-TV 1-2^(1-H) when one coin is reused instead of fresh draws. Thus the common-information and conditional-randomness premises cannot be dropped. These are already recorded model examples, not newly discovered cases.

## T3. Capability differences and conditional experiential-type differences

**Stable anchors:** A:C1, A:C1_OI, C:P1, C:P2_FULL, C:P3. **Status:** published conditional conclusions, not independent evidence for C1.

Let S be complete organizational types of justified actual process tokens in a common complete signature. Fix the evaluation environment, tasks, resources, laws and comparison conditions sufficiently for J:S->V to be well defined and isomorphism invariant. Under C1 let E:S->E(S) be the resulting bijection of complete organizational and experiential types.

Then

\[
J(s)\ne J(t)\Rightarrow s\ne t\Rightarrow E(s)\ne E(t).
\]

**Proof.** Equal arguments have equal values under the function J, so different values require different complete types. C1's tokenwise isomorphisms, composed in either direction, identify exactly the same complete-type equivalence classes. Hence E is injective and different s,t have different E-values. QED.

J identifies E throughout S iff J is injective. **Proof.** Apply T1 with Q=E: injectivity of E turns fiber constancy into singleton fibers of J. Conversely singleton fibers define the recovery map on J(S). QED.

Nothing here supplies a scalar magnitude, valence or richness order. For a separately supplied experiential coordinate Q, recovery from J requires T1's factorization condition; monotone recovery additionally requires order compatibility. C:P3 already supplies a countermodel to an unconditional capability-to-richness monotonic conclusion. Do not reinterpret the absence of a derived scalar ordering as an absence of any relation between intelligence and experience.

Equal finite-view kernels do not satisfy this theorem's complete-type premise merely because T2 holds. Likewise different noisy estimates need not mean different true J-values. U1 remains universal on admitted actual tokens; none of these theorems introduces an experience-existence gate.

## Review and intended use

The three proofs were manually rechecked by the same assistant against the pinned definitions and source results. Algebraic statements remain conditional; no independent peer review or proof-assistant verification is claimed. Exact R137 example checks remain in its original record and were not rerun solely for consolidation.

T1 and T3 are foundations already in C/A. T2 is the candidate technical center, whose overlap with established feedback-refinement and stochastic abstraction literature must be compared precisely. A unifying presentation and application can be useful, but must not be advertised as a new general theorem without that comparison.
