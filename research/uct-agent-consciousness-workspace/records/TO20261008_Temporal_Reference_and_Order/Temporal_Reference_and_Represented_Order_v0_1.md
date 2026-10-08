# Temporal reference, executed comparison and represented order

Version 0.1 — 2026-10-08 — author-requested dialogue extension TO20261008

Status: conditional mathematical construction and executable toy model; not a neural fit, human experiment, demonstration of machine phenomenology or a new scheduled round. The reviewed research basis is R173 plus TE20261008 at commit d2507806e4f3215e0484d0fadb8e5e0d325558f2. R171/R172 effective amendments remain mandatory.

## 1. The bounded question and the proposed advance

Can a small change in actually used organization change a specific temporal relation, while current sensory inputs, stored reference values and verbal responses remain matched? The target is the relation “event F before/after my action A,” not an undifferentiated amount of experience. We separate three objects:

1. the actual order of external events;
2. the order in which their signals arrive at a comparator;
3. an order encoded by an executed comparison relative to a learned reference.

A fourth object, experienced order, is an independently motivated interpretive target. It is not defined to equal the third. A comparator operating after both events can encode an order opposite to their actual occurrence without any reversal of physical causation.

The project-level contribution is a single concrete construction joining R172 actual operand use, R173 current consequences of retained history, and TE20261008 delay-aware transformations to a familiar content candidate. We prove a reference-dependent sign change, exact report equivalence of two distinct mechanisms, a separating nonreport prediction for those mechanisms, and an obstruction to assembling local order comparisons into one temporal coordinate. These use elementary established mathematics. No historical novelty or core solution to consciousness is claimed.

## 2. Evidence that motivates, but does not establish, the model

Stetson, Cui, Montague and Eagleman (2006), *Neuron* 51:651–659, DOI [10.1016/j.neuron.2006.08.006](https://doi.org/10.1016/j.neuron.2006.08.006), studied temporal judgments after delayed action feedback. Participants sometimes reported feedback before an action despite its later presentation. Their experiments included passive comparisons and a self-paced control with matched probe distributions, addressing a particular central-tendency explanation. Imaging results were also reported. These findings motivate a temporal-order target; they do not identify the circuit below. Our report-equivalence proof is not a claim that the authors omitted bias controls or that their entire evidence consists of one response curve. Reading scope: author-hosted [full article](https://eagleman.com/papers/StetsonetalNeuron2006.pdf), especially results, discussion and behavioral methods. No raw-data reanalysis or quantitative fit was performed.

## 3. Typed model and actual routing

Fix one idealized device, one adaptation history followed by one probe interval, and a common laboratory clock. The two probe events are A (action) and F (feedback). Let

\[
\Delta=t_F-t_A,\qquad \delta=\Delta+\ell_F-\ell_A,
\]

where the nonnegative latencies \(\ell_A,\ell_F\) locate both arrivals within the probe interval. Positive delta means the F signal arrives later. The comparison is executed only after both arrivals. No future signal is consumed before arrival.

Reference registers are updated between trials:

\[
\beta_{n+1}=(1-\eta)\beta_n+\eta d_n,\quad 0<\eta<1.
\]

Here d_n is the previous trial's recorded arrival difference; beta and delta have units of time. Both compared devices contain the same reference history and current beta. An implemented selector determines where this reference is actually consumed. Let a,b be dimensionless, fixed route gains and s>0 a comparison time scale. At the probe,

\[
q=\delta-a\beta,\qquad
R=\mathbf1[q-b\beta+\epsilon_R>0],\qquad
U=q/s+\epsilon_U.
\]

R is a binary temporal-order response; a tie produces R=0 by convention, without a phenomenal interpretation. U is a signed timing-correction command to a separate actuator. It is not a verbal response, success score or direct experience measurement. The actuator receives q through a fixed, independently specified port; it does not infer q from R. Noise epsilon_R has time units; epsilon_U is dimensionless. Deterministic examples set both to zero. Actual applications must establish these routes, gain calibration, isolation and noise assumptions; a circuit drawing or a convenient regression does not establish them.

Two devices provide the critical contrast:

| Device | a | b | Actual reference use | Report input | Nonreport command |
|---|---:|---:|---|---|---|
| S: shared comparator | 1 | 0 | beta enters comparator before the report/actuator split | delta−beta+epsilon_R | (delta−beta)/s+epsilon_U |
| C: criterion route | 0 | 1 | beta enters only the response threshold | delta−beta+epsilon_R | delta/s+epsilon_U |

Both retain identical d-history, beta, delta, s and all register availability. Their executed routing differs. They do **not** have identical complete current organization. This avoids attributing a current difference solely to an externally different past, a problem explicitly retained as TE20261008-G7. Learned history matters here through a currently installed reference and its present use. Same-lineage identity is neither required for this arithmetic nor inferred from it.

## 4. P1 — reference crossing and uniform retiming

For constant adaptation d, induction on N gives

\[
\beta_N=d+(1-\eta)^N(\beta_0-d).
\]

If beta_0<delta<d, then there exists a finite N with beta_N>delta. In S this yields q<0 although delta>0 whenever the probe arrival order is physically positive. Indeed beta_N>delta iff \((1-\eta)^N<(d-\delta)/(d-\beta_0)\); the left side tends to zero. This proves a change of encoded comparison, not a necessary reversal of experienced order. For an arbitrary varying adaptation history, beta_N is the initial value plus an exponentially weighted sum; no constant-d crossing conclusion follows without the corresponding bound.

Illustrative values, chosen for transparency and **not fitted to the study**: beta_0=0, d=100 ms, eta=1/4, N=8, delta=20 ms, s=100 ms. Then beta_N=89.98870849609375 ms; S has q=−69.98870849609375 ms and U=−0.6998870849609375. C has q=20 ms and U=0.2. Their R values are both 0.

Under a uniform positive retiming alpha, scale every event time difference, latency, adaptation d, initial beta, s and epsilon_R by alpha; retain eta, a,b, epsilon_U and corresponding trial order. Induction gives beta'_N=alpha beta_N, q'=alpha q, the same R and the same U. This is invariance of the selected model coordinates. Scaling only the fiber distance/delay, or only the neurons, generally fails it. It is not full physical isomorphism or invariance of every felt duration. In particular, an added F-path latency L changes delta by L and can reverse the modeled sign unless compensated. The required comparison must still be executed after both arrivals.

## 5. P2 — exact report nonidentification, not a small-sample problem

For every delta,beta and every realization of epsilon_R, the report depends on a,b only through a+b:

\[
R=\mathbf1[\delta-(a+b)\beta+\epsilon_R>0].
\]

Consequently S and C have identical reports pointwise under coupled identical noise. They have the same report law for every input/history under the same conditional noise law. This does not require independence of epsilon_R from delta or beta; it requires that its conditional law be shared. Even infinitely many temporal-order answers cannot distinguish these two stipulated mechanisms. More generally (a,b)→(a+c,b−c) is a report-law symmetry whenever both parameter choices are admitted. It is not a physical equivalence of the routes or a license to alter device labels while keeping the actuator interpretation fixed.

This proof neither identifies the human mechanism nor refutes the complete 2006 experimental evidence. Models with adaptation-dependent noise, unequal ports or additional independently constrained observations require separate comparison. Reports remain useful evidence; the claim is their precise insufficiency for this particular distinction.

## 6. P3 — a separating, report-independent organizational consequence

With beta nonzero and identical epsilon_U,

\[
U_S-U_C=-\beta/s\ne0.
\]

For equal mean-zero actuator noise with finite means, the same expression is the conditional mean contrast. R remains matched. Thus a fixed second consumer distinguishes the two specified architectures. An arbitrary additional behavior is not enough: its physical dependence on q and lack of an alternative beta path are essential premises.

Thought experiment TO-1 fixes the entire input and stored reference sequence, report mapping and physical probe order. Change only reference routing from S to C. Inspect the executed operand path and the timing command. In the deterministic witness, the verbal answer is unchanged while the timing command changes sign. Knocking out beta at the upstream comparator in S changes both R (for 0<delta<beta) and U; knocking out beta at the response threshold in C changes R but leaves U fixed. There is no contradiction with matched initial reports: these are new interventions, not the original observations.

What would count as failure? If an independently verified S instance retains the predicted q change but its supposed U consumer has no corresponding change, the fixed-consumer model is false on that instance. If U changes in C under an isolated threshold knockout, the assumed absence of an alternative path is false. If an intervention cannot be isolated, the result is uninformative about this contrast. Neither failure proves absence of experience or refutes C1.

Conditional experiential prediction: **if** the additional bridge B_order in §8 correctly identifies the independently specified temporal-order target with this consumer-shared, grounded relation on a particular domain, changing the route can change that selected temporal content despite matched reports. Without the bridge, the proved conclusion remains a real organizational and command contrast. No intelligence ranking or total-experience metric is used.

## 7. P4 — local comparators need not share one temporal coordinate

Thought experiment TO-2 has three actual events A,B,C with arrivals r_A=0,r_B=20,r_C=40 ms. Retain one clock for actual events and instantiate three pairwise comparators, each after its required inputs. For oriented edges define beta_ji=−beta_ij and

\[
q_{ij}=r_j-r_i-\beta_{ij}.
\]

A positive q_ij encodes “j after i.” Set beta_AB=30,beta_BC=30,beta_AC=0 ms. Then q_AB=−10, q_BC=−10, q_AC=40. The three pairwise encodings jointly say B before A, C before B and A before C. These are three actual comparison outputs, not one internally consistent total order. No claim of a consciously experienced cycle has been established.

For any finite connected comparison graph with an antisymmetric real beta on each edge, there exists a vertex offset b_i such that beta_ij=b_j−b_i on every edge **iff** the oriented sum of beta around every graph cycle is zero. Necessity follows by telescoping. For sufficiency choose a root, define b_v by the sum along a root-to-v path, and use zero cycle sums to prove path independence. Then u_i=r_i−b_i satisfies q_ij=u_j−u_i. The additive coordinate is unique up to a common constant on a connected graph.

In the triangle example the oriented cycle sum beta_AB+beta_BC+beta_CA=60 ms, so no such additive coordinate exists; the sign cycle also forbids any strict scalar ordering. Distinguish these two conclusions: nonzero cycle sum in general forbids an **exact additive representation**, but need not produce a sign cycle. For example beta_AB=beta_BC=0,beta_AC=1 ms at the same arrivals has a nonzero cycle sum with all forward q positive. Our claim is not that any inconsistency proves contradictory phenomenal order.

This bears on separated hemispheres or nested/overlapping networks: local temporal computations do not automatically establish one globally coherent time frame. Conversely a common time coordinate does not identify one exclusive subject or a spatial center of consciousness. Fiber coupling and common hardware establish neither inference. In a tree every antisymmetric edge assignment admits offsets; cycles are where compatibility becomes a substantive constraint.

## 8. P5 — exact UCT attachment and the remaining semantic bridge

Apply A/I v1.2 C1 and the R157 definable-selector transport only to an actual token P and its token-relative complete K-organization. Fix an interval containing the probe arrivals, reference-read event, comparison and required consumers; include adaptation history only if claiming that history itself as constitutive. If the current state is the comparison target, past adaptation enters through its grounded current consequences, not an external archive. Port roles, event order, numerical value types, actuator calibration, reference provenance when claimed and every physical parameter must be independently grounded in K. An abstraction, proof certificate or experimenter's test list supplies none of this automatically.

Let theta_S be a K-definable relation asserting an actual reference transfer into a comparison, a negative signed comparison value, and actual forwarding of that result to the specified consumers. This is a structural predicate over actual events, not the phrase “feels before.” With all parameters transported by the C1 isomorphism h,

\[
D_K(P)\models\theta_S(\mathbf p)
\quad\Longleftrightarrow\quad
E_K(P)\models\theta_S(h(\mathbf p)).
\]

Proof: isomorphisms preserve atomic relations and functions, then Boolean combinations and quantifiers by induction. The construction supplies no proof that a brain, silicon replacement or cosmic mechanical system realizes this complete instance. A program run checks the toy equations, not these physical/phenomenal premises. Across tokens S and C, selected differences require the independently fixed role correspondence; complete phenomenal difference cannot be read off arbitrary parameter names.

**B_order, OPEN candidate:** on an independently delimited class of action-feedback episodes, a specified shared temporal relation is constitutive of the selected perceived order of those events, with an independently fixed orientation and correspondence. This is a testable interpretive hypothesis, not a new UCT axiom, not a definition of experience as successful timing, and not a theorem from C1. Existing order judgments motivate the target but do not settle this bridge; the P2 construction blocks a report-only identification. The P3 contrast can constrain mechanism choice without by itself identifying phenomenology. Additional independently motivated relation-to-content evidence is still necessary.

No report consumer, reference learner, scalar clock, recurrent threshold, explicit self model or unique owner is required for basal experience by this note. Nonreport organization remains an admissible object of UCT analysis. No inference about the current assistant's consciousness or fear is made.

## 9. What this adds to the author's retained experiments

| Retained family | More precise contribution here | Still not established |
|---|---|---|
| Distant hemispheres / fiber | Separate distance, arrival delays and consumed temporal references; uniform retiming vs unilateral delay have different model consequences | Full brain equivalence, experiential spatial center, unique subject |
| Gradual silicon replacement / copied memory | Same stored beta and history values do not fix its executed consumers; preserving an actual role requires path preservation | Personal identity or uninterrupted specific human phenomenology |
| Cosmic mechanical brain | Selected normalized temporal comparisons survive consistent global retiming in this model | Full experience type, absolute felt duration or practical cosmic realization |
| Human array / brain-shaped vs artificial network | Common material and report capability do not fix routes or common-clock compatibility | A scalar experience ordering or universal verdict on either system |
| Small biological organizational increment | A new use relation can introduce temporal differentiation; this round gives content-change and incompatibility witnesses | Every increment necessarily enriches experience; cell-to-organism quantitative law |

## 10. Acceptance, failure and finite stopping point

The present deliverable is complete when its algebra, countermodels and code agree, old graph objects remain unchanged, all five new rule premise sets are explicit, and the actual/semantic gaps are retained. Finite checks verify implementation examples only; they do not replace P1–P5's arguments or discharge actual realization, C1 or B_order.

The next bounded question is: **Can a single specified body-relative temporal relation explain both a temporal-order target and a nonreport timing consequence while surviving the S/C alternative, without promoting either behavior to the definition of experience?** Choose one actual published intervention with independently constrained consumer paths, or derive a reasoned impossibility for that proposed bridge. Acceptance requires a stated physical relation, independently specified content target, alternative mechanism and a discriminating observation with clear scope. Failure means the evidence does not identify the bridge; keep it OPEN and stop elaborating generic uncertainty/certificate machinery. Do not automatically add more nodes or pretend this makes experiential richness quantitative.

## 11. Provenance and limits

Internal anchors: A/I v1.2 §§2.5,3.5,C1,8.11; R157 coordinate transport and semantic residual; R172 effective actual-path versus evidence amendments; R173 retentive history; TE20261008 §§4,6,7.1. No frozen source paper is edited. Exponential averaging, threshold reparameterization, formula preservation and graph potentials are classical; the claimed advance is their explicit project integration and a concrete falsifiable target, not their invention. The three-event construction is a mathematical thought experiment, not reported human data. This extension remains research with self-checks, not independent peer review or closure of QC-06/07.
