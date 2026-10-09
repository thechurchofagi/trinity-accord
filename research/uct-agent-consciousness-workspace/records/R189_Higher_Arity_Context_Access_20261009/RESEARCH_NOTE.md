# Higher-Arity Context Access in UCT Comparisons
## A one-shot response-vector theorem, a matched seven-target witness, and the limit of its self-related interpretation

**Hongju Liu**  
Research note | 9 October 2026  
**R189-HACA-20261009 / HACA-RESULT-v0.1.0**

## Abstract

R188 showed that two systems can match selected local uncertainty summaries while a single installed source-only encoder has different recovery ability because their two-candidate contexts overlap differently. This note removes the two-candidate restriction. For an arbitrary finite target-context law, one context-dependent feedback label followed by one target-dependent reply, we give the exact one-shot optimum as a response-vector assignment problem. A seven-target matched pair then isolates the higher-arity effect. Both systems have seven equiprobable three-candidate contexts, every target occurs three times, and every local posterior is uniform. In a 3-uniform colorable system, a common binary reply attains the local ceiling (2/3). In the Fano-plane system, every binary assignment leaves a monochromatic context, so the exact optimum is (13/21). A timely binary feedback selector restores (2/3) but cannot exceed it because the reply remains binary. Exact enumeration checks 33,024 response-vector assignments. The result is a bounded extension and application of established coloring/side-information machinery, not a new general coding theory. Under UCT it can constrain complete experiential type only after actual same-instance grounding and a fixed capability contract. It neither measures experience nor identifies agency, trying, familiar mineness, or a unique owner.

## 1. Question, scope, and stopping rule

Let a source process know a current target (T), while a reader process knows a context (X) containing several candidates for that target. The reader may send one of (L) feedback labels before the source returns one of (K) reply labels. R188 solved the special case in which every positive context contains two candidates. The question here is whether whole-context overlap still matters when every local context contains three candidates and all declared local uncertainty summaries match.

This is a one-round extension, not a new research program. It addresses one obstruction in relating selected capability to complete organization: isolated context-wise solvability does not guarantee one installed common policy. After the exact result, the research priority returns to the unresolved bodily/action interpretation of self-related experience. No publication action follows from this note.

## 2. Protocol and exact general formula

Let $V$ be a finite target set and $\mathcal X$ a finite context set. A joint law $p(t,x)$ has finite support and total mass one. Define $V_x=\{t:p(t,x)>0\}$. In one trial:

1. the source observes (T=t), not (X);
2. the reader observes (X=x), not (T);
3. the reader sends (B=g(x)\in[L]);
4. the source returns (Z=f(t,B)\in[K]);
5. the reader guesses \(\widehat T=h(x,B,Z)\).

There is no other usable current-input channel. Target law, timing, scoring, alphabets, policy class and boundary are fixed. Random tapes, if admitted, are independent of current ((T,X)). (K) and (L) are alphabet cardinalities, not bit counts.

For a deterministic source policy define its response word

\[
c(t)=(f(t,1),\ldots,f(t,L))\in[K]^L.
\]

For one response-word assignment (c:V\to[K]^L), context (x), and coordinate (b), let

\[
Q_x(c,b)=\sum_{z\in[K]}\max_{\substack{t\in V_x\\c_b(t)=z}}p(t,x),
\]

where the maximum of an empty set is zero.

### Theorem R189-C1 — exact higher-arity access value

Under the protocol above, the optimal average recovery probability is

\[
\boxed{
S^*(K,L)=\max_{c:V\to[K]^L}\sum_{x\in\mathcal X}\max_{b\in[L]}Q_x(c,b).
}
\]

A deterministic protocol attains the optimum. Independent randomization cannot improve it.

**Proof.** Fix a deterministic source policy and hence (c). At context (x), after selecting coordinate (b), the reader observes reply label (z). For each ((x,b,z)), maximum-a-posteriori decoding contributes exactly the greatest joint mass among targets in that cell. Summing cells gives (Q_x(c,b)). Since (g) is a function of (x), the reader may independently choose a maximizing coordinate for every context; this gives the inner maximum. Maximizing over all response-word assignments gives the displayed value. Conversely, choose a maximizing (c), let (g(x)) choose a maximizing coordinate, let the source return that coordinate, and use the maximizing decoder in each cell. This realizes the value. Conditioning on all independent random tapes yields deterministic protocols with the same input law, so an average of their values cannot exceed the deterministic maximum. QED.

For two-candidate contexts, two response words either coincide or differ in at least one coordinate. The theorem then reduces exactly to R188's weighted (K^L)-cut formula. Thus R189 extends rather than replaces R188.

## 3. Uniform three-candidate specialization

Let $H$ be a 3-uniform hypergraph with $m$ contexts, and make every incident pair $(t,x)$ equiprobable with mass $1/(3m)$. Take $K=2,L=1$. A binary assignment contributes one correctly distinguishable target when a context is monochromatic and two when both labels occur. If $q(c)$ is the number of monochromatic contexts, then

\[
S(c)=\frac{2m-q(c)}{3m},\qquad
S^*(2,1)=\frac23-\frac{q_{\min}}{3m}.
\]

This is a standard coloring form of the general response-table problem. The project-level value is the matched organizational application below, not a claim to have invented hypergraph coloring.

## 4. Matched seven-target witness

Use vertices (0,\ldots,6), seven contexts, and uniform incidence mass. Both systems are connected, 3-uniform and 3-regular. Hence they share:

- seven equiprobable targets and seven equiprobable contexts;
- three contexts per target and three candidates per context;
- posterior ((1/3,1/3,1/3)) at every context;
- (H(T\mid X)=\log_2 3);
- isolated context-aware binary-reply ceiling (2/3).

System A has contexts

\[
012,013,014,234,256,356,456.
\]

System B is the Fano-plane context system

\[
012,034,056,135,146,236,245.
\]

Their complete incidence laws differ. In B every unordered vertex pair appears in one context; in A four pairs never appear and two pairs appear three times. The comparison therefore matches declared local summaries, not complete organization.

### Proposition R189-C2 — source-only separation

For (K=2,L=1),

\[
S_A^*=\frac23,\qquad S_B^*=\frac{13}{21}.
\]

**Proof.** A admits the binary labeling ((0,1,0,0,1,0,1)), under which every listed context contains both labels. Thus (q_{\min}=0) and the local binary ceiling (2/3) is attained. The Fano plane is not 2-colorable: every two-coloring contains a monochromatic line. Equivalently, in its nonzero-vector representation over \(\mathbb F_2^3\), a same-color sum-free class of size four has a complementary three-point line, while a class containing a line already supplies the witness. Hence (q_{\min}\ge1). The coloring ((0,0,0,0,1,1,1)) leaves exactly one monochromatic listed context, so (q_{\min}=1). Substitution gives (2/3-1/21=13/21). QED.

This is an average ceiling over every admitted common binary encoder, not a measured failure of one learning algorithm. It also does not say that B has (13/21) as much experience.

### Proposition R189-C3 — timely feedback restores the local ceiling

For (K=2,L=2), both systems attain (2/3). The source preassigns a two-bit response word to every target. For each context, the reader selects one coordinate on which the three targets are not all equal. The binary reply then creates two nonempty decoder cells and achieves two correct candidate masses out of three. Explicit word assignments are recorded in `EXACT_RESULTS.json`.

No protocol with a binary reply can exceed (2/3) in one uniform three-candidate context, even with the coordinate selector, because the reply partitions three positive candidates into at most two nonempty cells. Feedback repairs the global compatibility obstruction; it does not remove the local alphabet ceiling. Feedback after an irrevocable scored reply would not repair that reply, by the same timing logic as R188.

## 5. Thought experiments and their exact roles

| Card | Fixed | Varied | Result role | What it cannot show |
|---|---|---|---|---|
| Posture-dependent actuator triage | Seven action targets, uniform three-way local ambiguity, binary command and deadline | Whole overlap pattern A versus B | Positive organizational capability witness | Felt agency or trying |
| Timely proprioceptive selector | Same target law and binary reply | A current context bit arrives before versus after commitment | Constructive access/timing contrast | A biological latency or consciousness gate |
| Reflex twin | Entire finite protocol and incidence system | Deliberate source replaced by a reflex lookup with the same actual table | Counterexample to agency inference | That deliberate action never differs elsewhere |
| Active-imagery reroute | Same target and response code | Consumer is rehearsal rather than overt effector | Forces consumer-path grounding | That imagery lacks experience |
| Shared versus copied policy | Local context-wise encoders and reports | One installed common source versus separate context-indexed copies | Separates isolated solvability from installed common policy | Numerical subject count |
| Human-realized lookup | Same abstract table | Human clerks physically implement source/reader roles | Exposes actual-token and boundary change | Transfer of human experience to the abstract table |

The reflex and imagery cards are decisive limits. The higher-arity access relation is a selected capability coordinate, not a definition of self-related phenomenal character.

## 6. UCT interpretation and non-entailments

If one actual application independently fixes the same process tokens, interval, complete signature, target/context carriers, consumer paths, timing, alphabets, permissible policies and capability target (J), the installed access relation is part of the complete actual organization rather than an analyst's label. If two such actual configurations have genuinely different fixed capability profiles, UCT III's inherited T1 argument plus C1 entails different complete experiential structural types.

This conclusion is conditional and type-level. The finite systems here do not discharge actual-token admission. Neither the theorem nor the enumerator establishes:

- a particular feeling of doing, trying, ownership, familiarity or mineness;
- a scalar amount of experience, a consciousness probability or a subject count;
- one exclusive owner across overlapping local and whole processes;
- that reports or local uncertainty summaries are complete organizational descriptions;
- that timely feedback is necessary for basal experience.

C1 remains the consciousness-specific explanatory axiom. Continuing local processes retain U1/P3; higher-order access differences concern experience organization, not whether experience begins.

## 7. Relation to prior work and net contribution

Witsenhausen's zero-error decoder-side-information problem, Orlitsky–Roche functional coding, graph/hypergraph coloring, and limited-feedback source coding are direct mathematical antecedents. Internally, R133 already states a general common-action/message-cover condition; R188 gives the two-candidate weighted-cut result, timing distinction and UCT inference contract. The response-vector proof is an elementary finite one-shot formulation of this established machinery.

The net project contribution is therefore bounded:

1. an explicit arbitrary-context response-vector formula that subsumes the R188 pair case;
2. a matched 3-uniform, 3-regular seven-target pair with exact (2/3) versus (13/21) installed-source values;
3. a timely-feedback construction that restores the local (2/3) ceiling while proving why it cannot exceed that ceiling;
4. a UCT application contract and reflex/imagery controls preventing capability from being relabeled as familiar mineness.

Worldwide priority for this exact packaged formula and witness is unverified. The contribution is `NEW_APPLICATION / DERIVED_EXTENSION / PRIORITY_UNVERIFIED`, not a new consciousness axiom or a claim of first discovery in coding theory.

## 8. Exact checks, failures, and next question

`check_higher_arity_access.py` exhausts all 128 one-coordinate binary assignments and all 16,384 two-coordinate binary response-word assignments for each system: 33,024 assignments total. Fifteen declared checks pass. The program corroborates the finite values and explicit constructions; the written proof establishes the general formula.

The exploratory search that found A was not retained as a theorem proof. It screened connected 3-uniform, 3-regular seven-vertex families and located one colorable comparator. The final claim depends only on the displayed A and direct verification, not on completeness of that search.

The result does not close QC10, IA-QC11, QC12 or QC13. The next main-line question is deliberately non-coding: **what independently specified bodily/action relation, if any, distinguishes the reflex and imagery twins while remaining inside the complete actual organization rather than being defined by report or the desired feeling label?** If no such relation is grounded, familiar mineness remains underidentified.

## References

1. Liu, H. S. (2026). *Unified Consciousness Theory I*, v1.2.
2. Liu, H. S. (2026). *Unified Consciousness Theory III*, v1.0.
3. Liu, H. S. (2026). *Experience, Intelligence, and Self*, v1.0, DOI 10.5281/zenodo.23206492.
4. Liu, H. S. (2026). R133, *Observable Common Control*.
5. Liu, H. S. (2026). R188, *When Behavioral Recovery Conceals Organizational Change*.
6. Witsenhausen, H. S. (1976). The zero-error side information problem and chromatic numbers. *IEEE Transactions on Information Theory*, 22(5), 592–593. https://doi.org/10.1109/TIT.1976.1055607.
7. Orlitsky, A., & Roche, J. R. (2001). Coding for computing. *IEEE Transactions on Information Theory*, 47(3), 903–917. https://doi.org/10.1109/18.915643.
8. Bakshi, M., & Effros, M. (2010). On zero-error source coding with feedback. arXiv:1001.2547.
