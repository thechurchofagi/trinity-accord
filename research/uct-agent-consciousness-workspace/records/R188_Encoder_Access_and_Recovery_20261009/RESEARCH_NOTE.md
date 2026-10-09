# When Behavioral Recovery Conceals Organizational Change
## Intervention contracts, compensation, and the information available to an encoder

**Hongju Liu**  
Independent researcher, Shenzhen, China  
Research working paper | 9 October 2026  
**R188-CER-20261009 / CER-RESULT-v0.1.0**  
English synthesis of UI, R185-R187, CM, and the present encoder-access result  
Prepared with AI-assisted derivation, source comparison, code execution, and adversarial review. This is a research draft, not a peer-reviewed article; no new DOI is assigned.

## Abstract

Behavioral agreement is often used to support claims about the organization producing behavior. Such an inference can fail because the tested operations are too limited, their sequence is too short, corrective processes hide a change, or different implementations preserve the entire accessible interface. This paper connects several earlier UCT research records through an explicit distinction between an observable target, an admissible intervention protocol, and the information physically available to the processes implementing a response. Its new constructive centerpiece concerns compensation or recovery encoders that cannot inspect a consumer's current context. For finite two-candidate contexts, we derive an exact weighted average-error formula for one feedback message followed by one forward message. A pair of six-target organizations has matched target and context marginals, matched conditional uncertainty, and identical isolated context-aware recovery, yet its best one-bit source-only recovery is respectively 1 and 8/9. One timely feedback bit restores perfect recovery; feedback arriving after the scored reply does not. Exact enumeration and an executed two-process reference corroborate the constructions. The coding machinery has established precedents; the contribution is the matched application, precise finite-error tradeoff, constructive repair, and reusable inference contract. Under UCT, experiential interpretation remains conditional on actual-process admission and the inherited structural identity axiom. No experience threshold, intensity scale, subject count, or particular feeling is inferred.

**Keywords:** organizational inference; intervention; compensation; side information; feedback; causal abstraction; Unified Consciousness Theory.

## 1. The question and the reason to write this paper

Suppose a biological or artificial system continues to produce the same answer after a component is altered. Several explanations remain possible. The altered relation may have been irrelevant to the specified answer. Another route may have carried the target. A decoder may have adapted to a new code. An active compensator may have canceled the change. The experiment may also have failed to reach the state in which the difference becomes relevant. These possibilities concern different organizations even when one observed outcome is shared.

The question is therefore precise: **what may be inferred about organization from behavioral preservation or recovery under a declared experiment?** This paper does not begin by treating successful report, integration, recurrence, or compensation as a condition for experience to exist. Within UCT, the experience commitment concerns admitted actual processes, including continuing local processes. The present mathematical problem concerns which organizational explanation the evidence can support.

The writing objective follows the project's research guide v2.2 and the earlier R150 author clarification. The intended product is a stable unit of knowledge that future researchers and AI systems can inspect, reuse, criticize, and cite. Publication count or journal acceptance is not the primary criterion. A useful contribution can be a counterexample, a repaired inference, or a self-contained application of known mathematics, provided its actual increment is identified. An archival identifier would improve location and preservation; it would not validate the argument.

This synthesis has three components. First, it gives a common interpretation to the intervention-order, horizon, compensation, and interface-equivalence results developed in the preceding records. Second, it addresses a particular achievability gap left explicit in the earlier recovery-budget result: its ideal helper can see both the target and the reader's context, whereas an installed helper may lack that context. Third, it supplies a matched finite example, an exact optimal value, and a specific feedback mechanism that repairs the gap.

The paper does not claim the invention of graph coding, common-decoder compatibility, or intervention-relative identifiability. Witsenhausen's side-information problem and later interactive coding research are direct antecedents [5-8]. Internally, R133 already gives a general common-action message-cover result, R137 treats common-decoder constraints, and IE treats delayed query access. The increment here is the exact, direction-sensitive finite-error application and its connection to compensated organizational comparisons.

## 2. Four ways that a behavioral test can miss a difference

### 2.1 Update order: a positive rejection with a limited converse

Consider a product-state explanation with two updates acting separately on its components: A changes the first component only and B changes the second only. Under the same preparation, time convention, and observer, the lifted updates commute. Therefore an observed difference between the two orders can reject that particular independent-update explanation. It does not prove that there is one physical source or one subject.

If the observed output laws are P_AB and P_BA and their total variation distance is D, any such independent explanation predicting the same law Q for both must satisfy

\[
\max\{\operatorname{TV}(P_{AB},Q),\operatorname{TV}(P_{BA},Q)\}\ge D/2. \tag{1}
\]

The triangle inequality proves the statement. The converse fails: two maps can commute while acting on the same stored variable. Moreover, an internal difference may be invisible to the current observer and become visible after a common subsequent operation. For example, two states (0,0) and (1,0) both give zero when the second coordinate is read. The common continuation V(x,y)=(x,x) makes that same observer distinguish them. The observer must actually be changed from any earlier XOR observer to the second-coordinate observer; these cannot be silently identified as one fixed readout.

These are inherited UI results. Their use is to specify an organization that a test can reject and the exact observer under which it is rejected. Sequential state updates must also be distinguished from persistent interventions installed in causal equations; their algebra need not be identical [9].

### 2.2 Action horizon: agreement on every short trace can be insufficient

R186 supplies a constructive depth boundary. For an integer m at least one, take state (f_1,...,f_m,z), initially all zero. Operation A_i sets f_i to one. Operation C flips z only if all m flags are one. A comparator uses the same A_i but makes C a no-op.

Every operation sequence of length at most m produces the same complete state trace in both systems. Before a C in such a sequence, at most m-1 distinct flag-setting operations could have occurred. A_1,...,A_m,C has length m+1 and separates them. This is a general proof, with finite checks as corroboration.

The limitation is relative to the reset and action alphabet. If an experiment may preset all flags, C alone separates the machines. If the admissible state bound and complete transition coverage are known, a finite conformance argument can be possible. The result does not say that finite-state identification is universally impossible. Recent work on plasticity and unfolding likewise distinguishes fixed or bounded comparison classes from stronger simulation claims [10]. We do not claim priority for the general observation that a longer history can reveal a hidden dependency.

### 2.3 Compensation: restored output can retain a hidden causal change

CM considers a fixed finite-dimensional model

\[
e=d+Mu,\qquad z=Hu,\qquad q=Ad. \tag{2}
\]

Here d is the selected uncompensated contrast, u the admitted correction, e the final outcome, z the monitored correction record, and q the target to reconstruct. The matrix A is a target projection; it is not UCT's complete structural signature. We rename CM's target matrix to avoid confusing it with the later message alphabet K.

Even with constant d, feedback can produce e_t=d(1-alpha)^t. At alpha=1, every post-correction output is zero while u remains -d. The initial transient is different; this example does not claim equality of complete trajectories.

When d and u vary freely over their declared real spaces, q can be recovered from (e,z) for every case exactly when

\[
\ker H\subseteq\ker(AM),\quad\text{equivalently } AM=LH
\quad\text{for some }L. \tag{3}
\]

Then q=Ae-Lz. For necessity, a vector v with Hv=0 and AMv nonzero makes (d,u)=(0,0) and (-Mv,v) observationally identical but gives different targets. Thus no nonlinear decoder can rescue this lost distinction. With freely designable exact linear monitoring, the minimum independent real-valued monitor dimension is rank(AM). This is a task-specific linear measurement dimension, not a bit count or experience amount.

If the correction satisfies a Euclidean bound ||u||<=rho, define u_0=H^+z and P=I-H^+H. For a feasible exact z, the remaining target set is centered at Ae-AMu_0 and has exact conditional minimax radius

\[
R=\sqrt{\rho^2-\|u_0\|^2}\,\|AMP\|_2. \tag{4}
\]

Every compatible u equals u_0+v, with v in ker H and ||v|| bounded by the displayed residual radius. The target image is centrally symmetric, so its antipodal extreme points prove the lower bound and its center attains it. Additional constraints on d can shrink the set; equation (4) is not automatically exact after such constraints are added. The interpretation of d as a causal baseline contrast separately requires a justified modular or clamp model. Linear algebra alone does not establish that interpretation.

### 2.4 Entire-interface equivalence: repeated testing need not identify occurrence multiplicity

R185 distinguishes one grounded occurrence shared by several process descriptions from distinct occurrences with matching values. R187 studies what an interface can establish about that distinction. Suppose two controlled systems have related initial states, matching readouts, and a transition relation that preserves the relationship under every permitted input or intervention. In the stochastic case, require an appropriate coupling preserving that relation and the readout law.

Every policy adapted to the observed history then produces the same observed-history law in both systems. Induct on history length: equal histories give the same policy distribution over the next command; the controlled relation gives equal next observations and a related successor state. The claim covers all finite histories and all such adaptive policies. More repetitions at that same interface cannot resolve the hidden difference.

A constituent-specific intervention with independently grounded source, port, clock, and readout meaning can exclude a restricted alternative. An altered downstream readout is not automatically a source write; synchronized resets may hide a difference; multiple coordinates of one admitted source can support different interventions. Also, an intervention can change the organization being investigated. Its result does not retrospectively prove how many occurrences existed before that intervention. Related control-theory work already shows that different internal networks may have the same entire input-output transfer behavior [11].

## 3. The new target: what can the recovery encoder actually see?

The inherited TH/RB recovery theorem uses an earlier record X and a target T. With a helper transcript containing at most K labels, optimal recovery is bounded by the sum G_K of the K largest posterior target masses in each X cell. That bound is sharp in a comparison class where the helper can inspect **both T and X**. The record expressly leaves installation and actual access open.

This qualification matters. The reader may know X while the process creating the helpful message sees only T. Solving each context separately then has the logical form

\[
\forall x\;\exists f_x, \tag{5}
\]

whereas one admissible source encoder requires

\[
\exists f\;\forall x. \tag{6}
\]

Equations (5) and (6) are different claims. This is a familiar issue in coding and control. The aim here is to compute its exact effect in a matched organization comparison rather than merely repeat that the quantifiers differ.

Let V be a finite target set and E a nonempty family of two-element candidate sets. The reader's context e={a,b} says that T is a or b. Write p(a,e) and p(b,e) for the positive joint endpoint masses, with their sum over all contexts equal to one. Put

\[
w_e=\min\{p(a,e),p(b,e)\},\qquad W=\sum_{e\in E}w_e. \tag{7}
\]

The source initially sees T only. The reader sees e and sends B=g(e), drawn from at most L labels. After receiving B, the source sends Z=f(T,B), drawn from at most K labels. The reader estimates T from (e,B,Z). Both K and L are positive integers; no current feedback means L=1, and one feedback bit means L=2.

This protocol includes arbitrarily chosen legal encoding and decoding functions. It permits private or public random tapes independent of the current (T,X). It does not provide additional shared state correlated with the current trial, packet timing codes, variable message lengths, hidden source identities, or extra queries. Any such resource must be included or the protocol class changes. A repeated application needs independently reset trials or an explicitly justified fresh conditional law. This is a classical one-shot result, not a quantum, analog, variable-length, arbitrary-interaction, or asymptotic-rate theorem.

## 4. Exact recovery with directional access constraints

### 4.1 Proposition 1: weighted finite-error value

For an integer C>=1, define Cut_C(G,w) as the largest sum of w_e over edges whose endpoints receive different labels in a partition of V into at most C classes. Unused classes are allowed. The graph is a candidate-confusion relation, not the physical wiring diagram of an organism.

**Proposition 1.** Under the protocol in section 3, the greatest attainable average probability of recovering T is

\[
\boxed{S^*(K,L)=1-W+\operatorname{Cut}_{K^L}(G,w).} \tag{8}
\]

A deterministic protocol attains the value. Independent randomization cannot improve it.

**Proof of the upper bound.** Fix a deterministic protocol. Each source value has the response word

\[
c(t)=(f(t,1),\ldots,f(t,L))\in[K]^L. \tag{9}
\]

These are responses to possible feedback labels, not L messages actually transmitted in one trial. If c(a)=c(b), no feedback label can cause different replies for the two candidate endpoints. The maximum correct joint mass in that context is max{p(a,e),p(b,e)}, leaving error at least w_e. If the words differ, grant the protocol perfect performance in that context as an upper bound. Summing gives one minus the total weight of equal-word endpoint pairs. At most K^L distinct words are available, so equation (8) follows.

**Construction attaining the bound.** Choose an optimal word assignment c. For each context whose endpoints have different words, let the reader select a coordinate at which they differ and send its index. The source returns that coordinate of c(T), which identifies the endpoint. For an equal-word pair, return any coordinate and guess the more probable endpoint. The incurred error is exactly w_e, so the upper bound is achieved.

**Randomization.** Condition on all random tapes. Independence from the current input preserves the same endpoint-context law and leaves a deterministic source and reader strategy. Each has value at most (8); averaging cannot improve it. This argument does not grant one party another party's private tape. It simply fixes the local choices made by each permitted strategy. A tape correlated with current T or X is additional information, outside the premise. This proves the proposition.

The response-table and characteristic-graph methods are classical [5-8]. Equation (8) is a self-contained finite-error specialization used in this organizational benchmark. Its exact external historical priority has not been established, and it is not presented as a newly discovered coding theory.

### 4.2 Corollary 1: the exact zero-error boundary

Because every supported endpoint mass is positive, zero error is possible exactly when

\[
\chi(G)\le K^L. \tag{10}
\]

For no feedback this is the characteristic-graph coloring requirement. For K>=2 and a graph with an edge, the minimum number of feedback labels is ceil(log_K chi(G)); the required fixed feedback bit field is the binary logarithm of that label count, rounded up. If K=1, the source sends no distinction and the optimum remains 1-W for every L. Formulae using log_K must not be applied at K=1.

The K^L response-word count is not the number of target values physically transmitted in one reply. The reader already knows a pair and requests one distinguishing coordinate. Feedback direction and arrival time are part of the computation.

### 4.3 Corollary 2: a scalable exact family

For a complete candidate graph on n>=2 targets with a uniform edge and uniform endpoint, put C=min(n,K^L), and write n=Cq+r with 0<=r<C. Then

\[
S^*=1-\frac{r(q+1)q+(C-r)q(q-1)}{2n(n-1)}. \tag{11}
\]

To prove this, partition the n targets among the available response words. Each within-class pair is an indistinguishable context. Moving a target from a class at least two larger than another decreases the number of such pairs; balanced classes therefore minimize the error. Their sizes are q or q+1 and give (11).

Every individual context still leaves exactly two fair candidates. Yet perfect source-blind recovery requires n labels when L=1. This elementary family exposes why posterior uncertainty alone does not describe where information must be available to implement a recovery procedure. It is a derived illustration of established side-information principles, not a novel asymptotic coding-rate claim.

## 5. Matched organizations with different achievable recovery

### 5.1 Common external task; changed internal context router

Let T be uniform on six labels 0,...,5 and J uniform on 0,1,2 independently. These are the same external stimuli for both organizations. Each organization has a fixed 3-regular context graph and an ordering of the three neighbors of every target. An internal router maps (T,J) to the pair consisting of T and its J-th neighbor. Only that pair reaches the reader; only T reaches the source encoder.

Organization A uses the complete bipartite graph K3,3, with parts {0,1,2} and {3,4,5}. Organization B uses a triangular prism: triangles 012 and 345 joined by edges 03,14,25. Both have six vertices and nine edges. Every oriented edge occurs once among the same eighteen external inputs.

| Quantity held equal | Organization A | Organization B |
|---|---:|---:|
| Target states | 6 | 6 |
| Reader contexts | 9 | 9 |
| Contexts per target | 3 | 3 |
| Target marginal | Uniform | Uniform |
| Context marginal | Uniform | Uniform |
| Posterior at each reader context | Two fair candidates | Two fair candidates |
| Conditional entropy H(T given X) | 1 bit | 1 bit |
| Reader-only optimal recovery | 1/2 | 1/2 |
| Isolated context-aware one-bit recovery | 1 | 1 |

Their full joint laws P(T,X) differ through the internal incidence map. This is the changed mechanism. We do not say that their complete information or organization is equal. The common comparison fixes external input distribution, target, scoring, message limits, and protocol deadline, while matching the listed summaries.

### 5.2 Proposition 2: exact one-bit separation

With K=2 and L=1,

\[
\boxed{S_A^*=1,\qquad S_B^*=8/9.} \tag{12}
\]

For A, label one bipartite part zero and the other one. Every candidate pair receives different labels. For B, any binary labeling leaves at least one same-label edge in each of its two triangles. Thus at least two of the nine contexts contain endpoints that the one common code cannot distinguish. The bound is attained by labels (0,1,0,1,0,1): seven edges cross. Seven contexts are decoded perfectly and two give optimal success one half, yielding (7+1)/9=8/9.

This is an upper bound over all permitted encoders and decoders, not the measured failure of one chosen learning algorithm. It is an average under the stated prior. It does not say that every context succeeds with probability 8/9. Nor does it imply that either organization has 8/9 as much experience.

The intuitive obstruction is a shared coding rule. Each pair can be assigned opposite bits in isolation. Around a triangle, however, no single two-label assignment makes all three pairs opposite. Optimizing a separate encoder for each context silently gives the encoder access to the context it was supposed not to know.

### 5.3 Proposition 3: a constructive and timely repair

A single feedback bit before a single forward bit removes the gap. Color the prism vertices (0,1,2,1,2,0), and represent colors by words 00,01,10. In each reader context the endpoint words differ. The reader sends which of the two coordinates to inspect; the source returns that coordinate. The endpoint is recovered exactly. Thus K=2,L=2 gives value one for both organizations. A three-symbol forward message with L=1 also suffices.

| Scored communication contract | Organization A | Organization B |
|---|---:|---:|
| No forward distinction | 1/2 | 1/2 |
| One forward bit; no current feedback | 1 | 8/9 |
| One timely feedback bit, then one forward bit | 1 | 1 |
| One forward bit fixed before feedback arrives | 1 | 8/9 |
| Three forward symbols; no feedback | 1 | 1 |

For the late-feedback row, the scored reply is irrevocably fixed before the source receives current context. Its effective pre-reply access has L=1. A later signal cannot improve that already fixed reply unless further target-dependent modulation is allowed, which would change the experiment. No numerical hardware or brain latency is inferred from this logical ordering.

## 6. How the new result connects the earlier increments

### 6.1 A sharp upper bound is not an installation certificate

For both matched graphs, the inherited top-two posterior quantity G_2 equals one. The value remains a valid upper bound. Its equality construction uses the RB:HELPER access premise: the helper can inspect T and X. The source-only prism protocol lacks that premise and reaches only 8/9.

This does not retract TH/RB. It gives a counterexample to transferring that theorem's achievability conclusion into a narrower physical access class. Likewise, it does not discover common-action compatibility anew: R133's message-cover result already states a general compatibility condition. Here a decoder action can be represented by its entire context-indexed response table. That connection explains the coloring obstruction and prevents the paper from presenting a restated abstract criterion as its new theorem.

The constructive repair matters. The result identifies a specific missing route and what it must deliver: an appropriate context-dependent selector before encoding. It does not merely say that another signal might help. If a real compensator already has such a route, the source-blind ceiling was never its complete capability ceiling. If a route is added, the post-intervention assembly must be identified as such.

### 6.2 One inference contract across the masking mechanisms

| Earlier result | What can conceal a difference | What the result licenses | What remains unlicensed |
|---|---|---|---|
| UI update interference | Restricted order tests or a hiding observer | Reject a specified commuting independent-update model | Independence from a null result; unique source count |
| R186 horizon masking | Insufficient reset-state excitation depth | A known short test need not expose higher-order dependence | Unlimited-horizon identity or universal finite-test impossibility |
| CM compensation | A correction cancels an outcome contrast | Recover or bound a selected contrast under an explicit monitor model | Effort feeling, no original change, or full experiential restoration |
| R185/R187 occurrence and interface | Copies or shared structures preserve the full permitted interface | Identify limits of that interface; test separately grounded alternatives | Occurrence or subject count from behavioral equality alone |
| R188 encoder access | Each local recovery uses a different unavailable encoder | Exact constrained success and a specified feedback repair | Achievability from G_K alone; extra feedback as an experience gate |

These mechanisms need not be present in one actual system. The table compares separately defined model classes; it does not conjoin premises gathered from unrelated examples. Their shared lesson is an operational requirement: state what each participant can access, what operations are admitted, and when the scored response becomes fixed.

Exceeding the prism ceiling in a genuine application rejects the conjunction of the target law, source-access restriction, message alphabets, timing, protocol class, and measurement assumptions. It does not uniquely prove a hidden feedback wire. An omitted public trial index or timing channel, a changed prior, or an additional forward response could also explain the excess. A remotely read shared source also requires a causal path delivering fresh information; it cannot be treated as free while a synchronized copy is charged for communication.

## 7. Actual computations, reference implementation, and countercontrols

### 7.1 Exact finite checks

The executable check_encoder_access.py uses Python's Fraction arithmetic. Its actual run produced 51 result records covering 38,013 enumerated candidate tables. This includes all 64 binary source tables for each six-state graph, all source and feedback-selector tables on small three-state interactive examples, four nonuniform endpoint laws, explicit optimal decoders, complete-graph closed forms, and the common external-input router.

Some larger checks enumerate response-word assignments using the theorem's reduction. Those are implementation corroboration, not independent proofs of the reduction. The small direct protocol enumeration instead groups the actual observed (context,feedback,reply) cells and optimizes posterior decoding, allowing an independent check of the finite-error identity. The general proposition is established by the proof in section 4, not by the number of enumerated cases.

### 7.2 Executed source and reader processes

The reference run_process_reference.py starts a fresh source process and a fresh reader process for each case using Python's spawn mechanism. The source function receives the target, the fixed graph/code configuration, and any counted feedback. The reader function receives the candidate pair and a forward reply; it is not passed the target. Directional pipe operations implement the declared sequence.

The run completed 126 cases using 252 worker processes. Every organization and protocol variant was evaluated on all eighteen common external stimuli. The bipartite reference was correct in 18/18 cases under the three tested feedback timings. The prism was correct in 16/18 without feedback, 18/18 with timely feedback, and 16/18 with feedback after the scored reply. A three-symbol forward reference was correct in 18/18.

These counts are exhaustive finite examples, not sampled human or AI measurements. The program demonstrates the behavior of its explicit interfaces. It is not a security proof against processes that inspect operating-system state, a verification of complete hardware causal isolation, or a measurement of actual experiential structure. Logical send/receive order is recorded; biological delay is not estimated.

### 7.3 Controls that delimit the claim

Giving the source the full candidate pair lets it send the endpoint index and reach 18/18 on the prism with one forward bit. That deliberately violates the blind-source premise; it is a diagnostic countercontrol, not a refutation of the theorem. Arbitrary local post-processing is already included in the decoder and cannot distinguish equal response words. A compensator with additional current input is a different access class.

The one-shot scope is also essential. In a separate common-helper example, three readers know respectively A, B, or A XOR B and must recover both. A single common bit for one pair of fair bits has a compatibility obstruction. For a two-coordinate block in which each reader keeps the same side-information role across both coordinates, take A and B in the two-dimensional binary vector space and transmit Z=A+MB, where M=[[0,1],[1,1]]. Both M and I+M are invertible. A reader knowing A can recover B; one knowing B can recover A; and one knowing A+B can recover B through I+M. All 48 reader/input cases were checked. This is a common-role block, not two independent uses with independently changing reader roles. For mixed side information (A_0,B_1), sources ((0,0),(0,0)) and ((0,1),(1,0)) have the same side information and the same Z=(0,0); the code then fails. The supplied countercontrol illustrates why the complete block law and deadline must be specified. It does not assert that every graph gap disappears under batching, or contradict any fixed one-shot claim above.

## 8. What this contributes to the UCT main line

UCT I distinguishes complete actual organization from a finite view and commits to tokenwise structural-experiential identity C1. Its U1 and P3 consequences preserve the experience of actually continuing local processes under embedding [1]. UCT III and TA25 distinguish an evaluation contract, a capability profile, a report, and complete experiential type [3,4]. These are inherited commitments, not results of the present coding example.

The example supplies a concrete organizational coordinate: **which context-sensitive distinctions one installed source/consumer arrangement can implement together before its deadline**. Two systems can agree on local posterior uncertainty and isolated ideal restoration, yet disagree on this constrained capability. Restoring endpoint success through feedback does not mean that the earlier source-only organization already had the same route. Conversely, the absence of such feedback does not imply absent experience.

The conditional UCT route is explicit. First, admit the two actual processes and their comparison interval. Second, independently justify the installed source, consumer, context router, ports, information boundaries, and timing. Third, establish one representation-invariant capability contract, including the physically supported policy choices. The reference program shows particular policies; it does not by itself prove that a real biological system's full policy class has precisely the mathematical restrictions. Only if the proven capability difference is truly a difference in that common J may the inherited C:P1 implication be used to obtain a difference in complete experiential structural types.

Even that conditional conclusion does not identify a named feeling or order experiential richness. The graph's vertices are target values, its edges are candidate pairs, and its colors are source response words. None counts neurons, subjects, local experiences, felt effort, or degrees of consciousness. Continued local experience is retained under U1/P3. The interpretation of familiar mineness, agency, pain, pleasure, or a conceptual self remains a separately specified question. No unique exclusive owner is required before studying these organizational relations.

For future AI reuse, the paper's concrete function is narrow but useful. An AI evaluating a recovery argument can inspect the claimed encoder inputs; apply the precise value in section 4 to a pair-context model; test the six-state regression example; and distinguish an upper bound, an attaining abstract helper, an installed policy, and an independently grounded physical organization. This is a reusable constraint on theory application. It does not establish UCT's empirical truth or decide the current assistant's consciousness.

## 9. Originality, internal correction, and readiness for citation

### 9.1 Contribution ledger

| Content | Status and proper attribution |
|---|---|
| Basal experience, local persistence, complete-type versus capability distinction | Inherited UCT I/III and TA25 |
| Update noncommutation, bounded horizon, compensation observability, controlled-interface equivalence | Inherited UI, R185-R187, CM; condensed here with their restrictions |
| Top-K recovery, missing-input budget, deadline and side-channel bounds | Inherited TH/RB; an attempted rediscovery was abandoned |
| Common-action compatibility, message covers, delayed queries | Inherited R133/R137/IE and established coding/control mathematics |
| Characteristic-graph coding and feedback advantage | Established external mathematics [5-8] |
| Weighted one-feedback/one-reply average-error specialization, matched six-state organization pair, constructive timing repair | New application and synthesis within this research program; exact external priority unverified |
| Exact enumeration, isolated-function reference, countercontrols, machine-readable claim map | New reproducible artifacts for this version |
| R173 stale eight-combination wording | Effective-record correction during whole-map review; not a new science theorem |

The closest contemporary coding predecessor studies how giving the encoder a function of the decoder's side information changes zero-error rates [7]. The present comparison instead fixes finite directional alphabets, one feedback and one reply, and average error. These differences justify a precise application record, not a claim to have originated the general problem. Primary source access and priority limits are recorded separately in PRIOR_ART_AND_REUSE.md.

### 9.2 A real audit correction

The recovered completed v1.1.1 graph retained a raw R173 declaration that availability, agency-loop, and retentive-binding roles realize all eight Boolean combinations. Later effective R175 statements already restrict the admitted baseline by G implies A and explicitly leave even all-six semantic realizability unproved. The older eight-combination wording must therefore be narrowed to free-bit enumeration only, with semantic role independence withdrawn. The separate target meanings remain distinct without that stronger claim.

The new effective patch preserves the historical source and its hash and follows the existing R175 correction. No active inference rule depends on the stale R173 node; the outgoing contextual use is clarified and the correction link is retained. This is an example of why reading every effective statement matters beyond checking an acyclic graph. Reviewer-controlled actual and phenomenal findings remain open.

### 9.3 Paper judgment

The combined material supports this self-contained theoretical-methods working paper. Its citable unit is the exact access-restricted benchmark and inference contract, situated within the preceding masking results. It is not presented as a newly verified law of consciousness, a discovery of graph coding, or proof of external priority. It is worth retaining as a precise application that another researcher can calculate and another AI can use without silently adding unavailable inputs.

The next substantive objective should be one independently documented implementation in which the source/consumer access and deadline can be grounded beyond a toy interface, or a sharper comparison demonstrating that this protocol distinguishes competing organizational explanations of a selected experiential target. The same experiment should not simply be repeated with larger target counts and relabeled as a breakthrough.

## 10. Reproducibility and version use

The accompanying record includes the full proof, exact checker and result JSON, executed process reference and traces, contribution and source ledger, additive map module, full-map compatibility review, corrections, work log, and Chinese handoff. The frozen parent is UCT-MAP-v1.1.1, whose exact capsule was restored and hash-checked before this study. A completed map release requires the separate full-item semantic review and downstream reconciliation; manuscript status alone cannot upgrade it.

To reproduce the new finite evidence, run check_encoder_access.py and run_process_reference.py with Python 3.12 or a compatible Python 3 installation. They use the standard library and require no credentials or external services. Their checks concern the declared finite models. Current release, review scope, preserved pending modules, and publication state are recorded in the accompanying release and audit files.

**Suggested citation form:** Liu, H. (2026). *When Behavioral Recovery Conceals Organizational Change: Intervention contracts, compensation, and the information available to an encoder*. R188-CER-20261009, CER-RESULT-v0.1.0. Research working paper, thechurchofagi/trinity-accord, uct-agent-consciousness-workspace. Cite the archived version and its verified commit, not an unversioned claim about future revisions.

## References

1. Liu, H. (2026). UCT I, version 1.2. DOI: https://doi.org/10.5281/zenodo.23131575. Pinned source: records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md.
2. Liu, H. (2026). UCT II, version 1.1. DOI: https://doi.org/10.5281/zenodo.23030320. Pinned source: records/R128_Unified_Formal_Map_Audit_20261006/sources/B_UCT_II_v1_1.md. Theory-translation conditions remain source-specific.
3. Liu, H. (2026). UCT III, version 1.0. DOI: https://doi.org/10.5281/zenodo.23137088. Pinned source: records/R128_Unified_Formal_Map_Audit_20261006/sources/C_UCT_III_v1_0.md.
4. Liu, H. (2026). *Experience, Intelligence, and Self Within Experience*, version 1.0. DOI: https://doi.org/10.5281/zenodo.23206492.
5. Witsenhausen, H. S. (1976). The zero-error side information problem and chromatic numbers. IEEE Transactions on Information Theory 22(5), 592-593. https://doi.org/10.1109/TIT.1976.1055607.
6. Orlitsky, A. (1990). Worst-case interactive communication. I. Two messages are almost optimal. IEEE Transactions on Information Theory 36(5), 1111-1126. https://doi.org/10.1109/18.57210.
7. Charpenay, N., Le Treust, M., and Roumy, A. (2024). Side Information Design in Zero-Error Coding for Computing. Entropy 26(4), 338. https://doi.org/10.3390/e26040338. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC11049120/.
8. Briet, J., Buhrman, H., Leung, D., Piovesan, T., and Speelman, F. Round elimination in exact communication complexity. Author manuscript, sections 1.2 and 3. https://homepages.cwi.nl/~jop/RoundChromatic-TQC.pdf. Publication-year metadata is not assumed from this undated local citation.
9. Geiger, A., et al. (2025). Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability. Journal of Machine Learning Research 26. https://jmlr.org/papers/v26/23-0058.html.
10. O'Reilly-Shah, V. N., Selvitella, A. M., and Schurger, A. (2026). A caveat regarding the unfolding argument: implications of plasticity. Neuroscience of Consciousness 2026(1), niag027. https://doi.org/10.1093/nc/niag027. https://academic.oup.com/nc/article/2026/1/niag027/8709184.
11. Goncalves, J., and Warnick, S. (2008). Necessary and Sufficient Conditions for Dynamical Structure Reconstruction of LTI Networks. IEEE Transactions on Automatic Control 53(7), 1670-1674. https://doi.org/10.1109/TAC.2008.928114. Author preprint: https://arxiv.org/abs/q-bio/0610008.

### Internal versioned predecessors

UI20261009, *Update Interference*, UI-RESULT-v0.1.0, recovered from the v1.1.1 capsule; R185, *Cross-Scale Relation Membership*, 2026-10-08; R186, *Higher-order intervention masking under bounded action sequences*, HOM-v0.1.0; CM20261009, *When Successful Compensation Hides Organizational Change*, CM-RESULT-v0.1.0; R187, *Causal Multiplicity*, CMA-RESULT-v0.1.0; TH/RB, temporal handoff and recovery-budget manuscript v0.2.0 in the v1.1.0 source recovered by the v1.1.1 capsule. These research records are cited as project predecessors, not represented as additional peer-reviewed publications. Exact source paths and byte hashes are retained in the package manifest and map release.
