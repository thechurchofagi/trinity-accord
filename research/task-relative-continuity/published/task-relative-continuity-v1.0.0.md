---
title: "Task-Relative Continuity Through Changing Representations"
subtitle: "Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout"
author: "Hongju Liu"
date: "9 October 2026 · Version 1.0.0"
lang: en-US
fontsize: 10pt
documentclass: article
geometry: margin=0.85in
mainfont: DejaVu Serif
monofont: DejaVu Sans Mono
colorlinks: false
header-includes:
  - \usepackage{microtype}
  - \usepackage{needspace}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  - \setlength{\emergencystretch}{3em}
---

\begin{center}
Independent researcher, Shenzhen, China\\
\texttt{RT-TH-PAPER-v1.0.0} · Research record \texttt{RT20261009}\\
DOI: \texttt{10.5281/zenodo.23251651}\\
Theoretical preprint; not peer reviewed.
\end{center}

## Abstract

Continuity of a task-specific memory is not equivalent to persistence of its physical carriers, invertibility of a transfer, or successful operation of an installed reader. We give a finite, task-relative framework separating these questions. A relational-memory construction first distinguishes loss of recoverable information from a mismatch between coding and readout, even with matched single-register histories. We then study multiple reversible transfer routes whose identities are unavailable to a fixed reader. A common target decoder exists exactly when the target is invariant under the relative route transformations. Their orbit quotient characterizes all exactly retained targets, not only linear readouts. When route-only metadata is available, its minimum alphabet is the number of distinct target-reader functions. We also derive a sharp two-route error expression and a uniform finite-group decoding formula. Under unknown permutations of three binary registers, Hamming weight remains exact, whereas optimal recovery of the original first bit is 3/4 and recovery of the complete ordered state is 1/2. This shows why invariant linear dimension is not a measure of all preserved distinctions. Temporal transformations are distinguished from coordinate identifications of the same event, and any consciousness-theoretic application is conditional on independently grounded physical processes and targets. The mathematical ingredients are classical factorization, finite-group invariance, coding and statistical decision theory. The contribution is an explicit synthesis with proofs, diagnostic examples and executable countercontrols, not a new axiom of consciousness or evidence of preserved subjective identity.

**Keywords:** representational change; relational memory; stable readout; invariance; calibration; route ambiguity; consciousness; reproducibility

# Introduction: what continues when a representation changes?

A system can continue operating while a particular memory becomes inaccessible. Conversely, a reader can fail even though another correctly calibrated reader could recover the stored target perfectly. These alternatives matter whenever information moves between carriers, changes coding conventions, or reaches a consumer through different routes. They also expose an ambiguity in the question of a system's “core”: a fixed anatomical or computational component, a minimally sufficient information interface at one time, and a temporally maintained task relation are different candidates.

The present paper asks a bounded question: **when can one consumer preserve an independently specified target through several possible representation changes, without knowing which change occurred?** The answer must distinguish actual loss, recoverability conditional on route knowledge, and availability to a particular reader. It should also quantify what route information would repair a failed reading without assuming that such information is free or physically available.

This work is motivated by the author's Unified Consciousness Theory (UCT), but its mathematical results do not assume that theory. UCT I identifies the complete token-relative physical and experiential organization of each admitted actual process under its structural commitment C1. Its U1 and P3 commitments distinguish nonempty experience and process persistence from the survival of any selected content [1]. UCT III relates genuine capability differences to complete experiential-type differences under a fixed evaluation, without a scalar “more intelligence, more experience” rule [2]. Here those are explicitly conditional interpretive premises, not outcomes of the coding calculations.

Several ingredients are inherited. The author's earlier subject-tracking paper already uses monodromy [3]. Prior project records distinguish selected-target preservation from complete-structure preservation, and changing a single code while compensating its decoder [9]. The Temporal Handoff (TH) checkpoint established the stochastic memory examples summarized and proved below; its subsequent version studies the cost of additional recovery inputs [10]. A separate action-calibration checkpoint analyzes task-relative ambiguity in port correspondences [11]. We do not count these as independent discoveries of this manuscript.

The additional organizing problem is *route ambiguity*: each transfer is individually reversible, but different transfers can require incompatible readers. This is closely related to classical synchronization and group invariance [5]. We provide a self-contained finite analysis that joins the earlier handoff distinction to exact common-reader conditions, route-tag requirements, quantitative error and nonlinear retained targets. The results are intended as inspectable theoretical tools, not a claim of historical priority for invariant theory, a new neural mechanism, or a demonstration of a named feeling.

# Model, information boundary and comparison contract

Let $\mathcal X$ and $\mathcal Y$ be nonempty finite sets of equal size. A nonempty finite route set $\mathcal P$ contains bijections $T_p:\mathcal X\to\mathcal Y$. A target $f:\mathcal X\to\mathcal A$ is fixed independently of the observed output. For exact statements, every pair $(p,x)\in\mathcal P\times\mathcal X$ is admissible. The consumer observes $y=T_p(x)$, knows the route family, and must return $f(x)$. Its decoder is chosen before the particular source state and route.

Unless explicitly supplied, the consumer has no route label, route-revealing timestamp, retained mask, correlated external record or independent answer source. A reader's internal state that carries such information belongs inside its information interface. Thus “route-blind” is a declared access condition, not a verdict that a real brain has no relevant history. A mathematical decoder's existence does not establish its physical installation, execution or acceptable cost.

Zero-error results require correctness on the full Cartesian domain. Uniform source and route probabilities are introduced only where used to calculate expected accuracy. Changing the source support, the prior, or correlations between source and route can change those formulas. An invertible $T_p$ preserves source information *given its identity*; it need not preserve $f$ under an unchanged decoder.

A transfer may be a chain of actual mechanisms over time. Compositions must respect input and output types. Algebraically using $T_p^{-1}$ in a comparison does not assert that the physical device can run backward. Likewise, the group generated by relative transfers is a mathematical closure of constraints, not a claim that every generated element is an actually executable route. Where a theorem samples uniformly from the entire group, that is an additional, explicit model assumption.

For physical interpretation one must separately specify carriers, time, interfaces, installed mechanisms, noise, interventions and actual consumer use. A “complete reading cut” below means all information that can influence the reader under the declared task contract, not necessarily the entire universe or a subject boundary. No mathematical target is identified with a human quale simply by naming it “content.”

# Relational handoff: retained information versus correct use

## Copy before clearing the previous carriers

The following example is inherited from TH [10] and included to make the combined argument independent of that working note. Let $\tau,\eta,\xi,\zeta$ be independent fair bits, with $\tau$ the target. Initially,

$$
(A,B,C,D)=(\tau\oplus\eta,\eta,0,0).
$$

Neither $A$ nor $B$ alone reveals $\tau$, but $A\oplus B=\tau$. First populate $C,D$ while retaining $A,B$; then clear the old register values. The copy mechanism and clock remain part of any physical implementation. Three copying laws distinguish the possibilities:

$$
\begin{array}{lll}
\text{shared:}& C=A\oplus\xi,&D=B\oplus\xi,\\
\text{reversed:}& C=A\oplus\xi,&D=B\oplus\xi\oplus1,\\
\text{independent:}& C=A\oplus\xi,&D=B\oplus\zeta.
\end{array}
$$

In the shared case, $C\oplus D=\tau$. In the reversed case, the same XOR reader is always wrong, but the compensated reader $1\oplus C\oplus D$ is always right. In the independent case, the entire final pair $(C,D)$ is independent of $\tau$: conditioning on any $\tau$, the two independent fresh masks make the pair uniform. Once the old values are cleared and no correlated side record reaches the reader, every estimator of $\tau$ from the pair has accuracy $1/2$.

| Copying law | Accuracy of unchanged XOR reader | Optimal accuracy from final pair |
|---|---:|---:|
| Shared mask | 1 | 1 |
| Shared mask with reversal | 0 | 1 |
| Independent masks | 1/2 | 1/2 |

The initial minimal *decoding* support is $\{A,B\}$; the final support in the shared case is $\{C,D\}$. They are disjoint, yet an explicit intervening transfer preserves the relation. Minimum decoding support is not automatically minimum lesion support, and the example does not prove that biological memory lacks every stable necessary component.

Across these three laws, each individual register's recorded three-time history, conditioned on $\tau$, has the same distribution. The complete *unconditional* register distributions at the two endpoints also match. The intermediate joint distribution and cross-register histories do not match: they contain the relations distinguishing the copying mechanisms. Therefore the observation match is not complete organizational identity. This is checked by exact enumeration in the supplement.

## Correlation-sensitive retention and hidden side records

Let the two new masks be $Z_1=\xi$ and $Z_2=\xi\oplus E$, with $E\sim\mathrm{Bernoulli}(\epsilon)$ independent of the past. Both masks are fair for every $\epsilon$, but

$$
C\oplus D=\tau\oplus E.
$$

The unchanged XOR reader has accuracy $1-\epsilon$. Knowing the law and allowing inversion gives

$$
J^* = \max\{\epsilon,1-\epsilon\}
     = \frac{1+|1-2\epsilon|}{2}.
\tag{1}
$$

**Proof.** For each final parity, the independent uniform masking makes the two corresponding register pairs equally likely. The posterior probability that the parity is $\tau$ is $1-\epsilon$; the opposite answer has probability $\epsilon$. Choosing the more probable value gives (1). For successive independent parity errors $E_i$, factorization of the signed parity expectation gives $J_k^*=[1+|\prod_i(1-2\epsilon_i)|]/2$. Independence across stages is essential. $\square$

A counterexample prevents overstating loss. If $X_1=\tau\oplus E$ and the same retained $E$ is used again, then $X_2=X_1\oplus E=\tau$. Although $X_1$ alone is uninformative, the complete interface $(X_1,E)$ never lost the target. Merely saying that future noise is independent of $\tau$ is insufficient; it can still be correlated with the past. A correct no-recovery claim needs a complete information boundary or the appropriate conditional freshness assumption. No assertion of universe-level erasure follows from a coarse-grained reset.

## A complementary finite-field recovery criterion

For uniform $\tau\in\mathbb F_q^d$ and independently uniform nuisance $\eta\in\mathbb F_q^k$, suppose the complete accessible variable is $Z=H\tau+G\eta+b$. Define

$$
\rho=\operatorname{rank}[G\ H]-\operatorname{rank}G.
$$

Then the optimal probability of recovering the *entire* target is

$$
\Pr(\widehat\tau=\tau)_{\max}=q^{\rho-d}.
\tag{2}
$$

**Proof.** Project onto $V/\operatorname{im}G$, where $V$ is the observation space. The induced map of $\tau$ has rank $\rho$. Each compatible target lies in a fiber of size $q^{d-\rho}$. Uniform source and nuisance make those targets equiprobable given the observation: each compatible target has the same number of nuisance preimages. Hence the largest posterior mass is $q^{\rho-d}$. A decoder selecting one compatible target attains it. $\square$

Equation (2) is classical finite-field information accounting, included from TH rather than claimed as new. It concerns stochastic ambiguity at a stipulated cut, not all nonlinear targets, route knowledge or subjective magnitude. The route analysis next addresses a different ambiguity that can persist even when every individual map is bijective.

# One decoder across unknown reversible routes

Fix a reference route $p_0$ and define permutations of $\mathcal X$ by

$$
H_p=T_{p_0}^{-1}\circ T_p,
\qquad \Gamma=\langle H_p:p\in\mathcal P\rangle.
$$

\Needspace{13\baselineskip}

## Proposition 1: exact common-reader criterion

A single decoder $d:\mathcal Y\to\mathcal A$ satisfies

$$
d(T_p(x))=f(x) \quad\text{for all }p,x
\tag{3}
$$

if and only if

$$
f(\gamma x)=f(x) \quad\text{for all }\gamma\in\Gamma,\ x\in\mathcal X.
\tag{4}
$$

When it exists, $d=f\circ T_{p_0}^{-1}$ works.

**Proof.** Because $T_{p_0}$ is onto, (3) on the reference route determines $d$ on every output. Substituting this decoder on another route gives $f\circ H_p=f$. Invariance under a bijection implies invariance under its inverse, and composition preserves invariance, so it extends to $\Gamma$. Conversely (4) applies to every generator, giving (3) for the displayed decoder. No source distribution is used. $\square$

Equivalently, all route-specific reader functions $r_p=f\circ T_p^{-1}$ must coincide. For full-state recovery $f=\mathrm{id}_{\mathcal X}$, this requires all routes to be the same map. For a selected target, distinct routes can be harmless. With one known route, compensation is immediate; that inherited single-route fact is not presented as a separate discovery here.

## Proposition 2: the quotient of exactly preserved distinctions

Let $\pi:\mathcal X\to\mathcal X/\Gamma$ assign the orbit of each state. A target has a common reader exactly when $f=\bar f\circ\pi$ for some $\bar f$. If there are $k$ orbits, exactly $2^k$ Boolean targets are invariant.

**Proof.** Equation (4) says precisely that $f$ is constant on each orbit. Defining $\bar f$ by any orbit representative is therefore well-defined, and every such factor is invariant. Independent Boolean choices on $k$ orbits give the count. $\square$

This is ordinary quotient factorization. “Every preserved distinction” means every zero-error target under this route family and access contract. It does not select a maximal conscious subject, a privileged physical scale or a complete physical ontology. The group closure records ambiguity constraints across overlapping source-output possibilities; it is not a probability distribution on executed paths.

# Target-specific route information

A tag $c(p)$ now accompanies the output. It is a deterministic function of route identity only, independent of the source value, and selects an installed decoder. All source states remain possible on every route.

## Proposition 3: minimum route-only tag alphabet

The smallest number of tag values permitting exact recovery is

$$
L_{\min}=\left|\{f\circ T_p^{-1}:p\in\mathcal P\}\right|.
\tag{5}
$$

**Proof.** Two routes receiving one tag must share a decoder. Since both reach every $y$, their required reader functions must agree on all $\mathcal Y$. Each distinct function thus requires a distinct tag. Conversely, label the equivalence class of each reader function and install that function as the selected decoder. $\square$

For several future targets, replace $f$ by their answer vector. For a full finite group acting on $\mathcal X$, orbit--stabilizer yields

$$
L_{\min}=\frac{|\Gamma|}{|\operatorname{Stab}_\Gamma(f)|},
\qquad
\operatorname{Stab}_\Gamma(f)=\{\gamma:f\circ\gamma=f\}.
\tag{6}
$$

A fixed-length binary label requires $\lceil\log_2 L_{\min}\rceil$ bits. This is an alphabet requirement, not an average entropy or total organizational size. The tag generator, its access to route history, its memory, delay and transmission must be accounted for. Equation (5) does not magically infer an unrecorded path.

The route-only restriction is substantive. A helper allowed to depend on both route and state could simply send $f(x)$, giving a different communication problem. Recent TH/RB project work studies more general recovery helpers [10]; the present claim is not an unrestricted helper-information bound or a rediscovery of that result.

**Full-domain countercontrol.** Let $\mathcal X=\{0,1,2,3\}$, $f=(0,1,1,0)$, and routes $I$ and $T=(1,0,2,3)$. If their permitted source sets are only $\{0,2\}$ and $\{0,3\}$ respectively, then $d=(0,0,1,0)$ works without tags, although the full-domain reader functions differ. Route-specific support can therefore reduce the requirement. It cannot be substituted silently into Proposition 3.

# Linear invariants and nonlinear retained information

For $\mathcal X=\mathbb F_q^d$ and invertible linear relative generators $H_1,\ldots,H_s$, scalar linear targets are $f_\ell(x)=\ell x$. Their invariant space has dimension

$$
\dim\{\ell:\ell H_i=\ell\text{ for all }i\}
=d-\operatorname{rank}[H_1-I\mid\cdots\mid H_s-I].
\tag{7}
$$

**Proof.** Such row vectors annihilate the sum of the images of $H_i-I$. Rank--nullity gives (7). Invariance under the generators extends to their group. $\square$

This counts *linear* readouts only. The orbit quotient of Proposition 2 need not be a vector-space quotient. Treating (7) as all retained content would confuse a convenient model class with the unrestricted target family.

Consider $\mathcal X=\{0,1\}^3$ and all six permutations of the three positions. Adjacent swaps generate the group and do not commute. The four orbits have Hamming weights $0,1,2,3$, with sizes $1,3,3,1$.

| Target | Required route-reader classes | Exact without route tag? | Optimal uniform-route accuracy |
|---|---:|---|---:|
| Parity | 1 | Yes | 1 |
| Number of set bits | 1 | Yes | 1 |
| Original first bit | 3 | No | 3/4 |
| Complete original ordered triple | 6 | No | 1/2 |

The scalar invariant linear space has only the parity direction, of dimension one. Nevertheless, Hamming weight has four exactly preserved values, and there are sixteen invariant Boolean functions. Four categories fit into two fixed-length bits, but their entropy under a uniform source is not asserted to be two bits: their probabilities are $1/8,3/8,3/8,1/8$.

For the first-bit target, a three-valued tag tells where the original first position ended up. Recovering the complete order requires all six reader classes. The path through a larger circuit may contain far more detail than either minimal target-specific tag. Accurate recovery of the count does not solve the different task of recovering the first bit.

# Error when exact route knowledge is unavailable

## Proposition 4: sharp two-route average-error penalty

Let the source be uniform and choose routes $p,q$ independently with probabilities $1/2,1/2$. Put

$$
\delta=\frac{|\{y:r_p(y)\ne r_q(y)\}|}{|\mathcal X|}.
$$

For any common decoder, including randomized decoders, the route-conditional errors satisfy $e_p+e_q\geq\delta$. The optimal average success is

$$
A^*=1-\delta/2.
\tag{8}
$$

**Proof.** At a disagreeing $y$, one shared answer cannot be correct on both routes, so the sum of conditional errors is at least one. Uniform bijections make $y$ uniform on each route. Summing gives the bound. Choosing $r_p$ throughout attains equality in average error. Randomization can balance the route errors; a deterministic minimax equality is not claimed for every finite instance. $\square$

## Proposition 5: uniform finite-group Bayes accuracy

Identify the output coordinates with $\mathcal X$ using the reference route, and assume the actual relative route is independently uniform over *all* elements of $\Gamma$. With uniform source,

$$
A^*(f;\Gamma)=\frac{1}{|\mathcal X|}
\sum_{O\in\mathcal X/\Gamma}\max_{a\in f(\mathcal X)}
|O\cap f^{-1}(a)|.
\tag{9}
$$

**Proof.** Given the relabeled output $y$, compatible source states fill its orbit. Orbit--stabilizer gives the same number of group elements taking each such state to $y$, so the posterior is uniform on the orbit. Choose its most common target value and average over outputs. $\square$

For the first-bit task, the four orbit majority counts are $1,2,2,1$, giving $3/4$. For complete-state recovery, each orbit contributes one correct representative, giving $4/8=1/2$.

A route family that merely *generates* $\Gamma$ need not be uniformly distributed on $\Gamma$. Proposition 5 cannot be used for such a family without this extra sampling assumption. More generally, independent priors $\mu(x)$ and $w(p)$ give the elementary decision formula

$$
A^*=\sum_{y\in\mathcal Y}\max_a
\sum_{p\in\mathcal P}w(p)\,\mu(T_p^{-1}y)\,
\mathbf 1\{f(T_p^{-1}y)=a\}.
\tag{10}
$$

It follows by choosing the most likely target separately at each output. Equation (10) supplies an explicit check against extending (8)--(9) to unverified distributions. It introduces no new structural premise and is included as the general decision calculation underlying the finite verifier.

# Actual temporal transfer is not same-event identification

For passive relabelings $a$ at the source and $b$ at the destination, let $T'_p=b\circ T_p\circ a^{-1}$ and $f'=f\circ a^{-1}$. Then $d'=d\circ b^{-1}$ preserves (3); reader-function counts remain equal, and optimal accuracy is unchanged when distributions are transported. Relative groups are conjugate, so their orbit partitions correspond. Physical ports, noise, target meaning and interventions must accompany the coordinate change.

An actual rewiring that leaves the task tied to the original physical source is not merely a passive relabeling. Nor should a temporal loop be confused with multiple charts describing one event. For same-event identifications, going between charts and back must track the same event consistently. Different-time transfers, in contrast, can legitimately change a state on returning to an interface. A bit-toggle computation is the simplest example. Nonidentity loop action is not a physical contradiction; it is an obstruction only to a specified unchanged reader or target.

On a connected interface graph, choose typed reference paths from a base interface. Readouts can be transported along those paths; their path independence for a target requires loop transformations to stabilize that target, not to be identity on every state. This is the target-level specialization of the standard synchronization picture [5]. It does not imply that a reversed edge is an available physical operation or that every interface lies in one timeless event.

Temporal information can repair route blindness. With identity/complement bit routes, $y$ alone cannot recover the original bit exactly, while a retained route bit $p$ permits $x=y\oplus p$. A recurrent reader might already store the necessary route class. One must include that state before applying the impossibility result, rather than labeling the system blind by assumption.

Likewise, a noninvertible transfer can lose information even when its route is known. Equation (2) or ordinary constancy-on-fibers criteria then address the within-route loss before route ambiguity is considered. Terminal recovery also does not establish continuous, timely access throughout an interval: the target may be unavailable until an additional signal or route history arrives. The theorem's observation time is part of its contract.

# Conditional interpretation for experience and intelligence

The mathematical analysis separates carrier persistence, conditional reversibility, recoverability from the accessible interface, compatibility of an installed reader, and preservation of a selected task relation. No pair of these is identified by definition with having experience or remaining the same numerical subject.

For a physical application, first justify actual process tokens and their common constitutive comparison signature, the episode, clock, boundaries, installed routes and consumer, and an isomorphism-invariant capability evaluation held fixed between systems. If a genuine difference of that capability is established, the original UCT III implication relates it to a difference of complete experiential structural types under C1 [1,2]. Different scores in unmatched task protocols or a hypothetical decoder's existence do not discharge these premises.

A positive conditional lesson remains: substantial carrier or routing changes can preserve a selected relation when relative changes leave it invariant or sufficient correction information reaches and is used by the reader. Preserving a count need not preserve order; preserving one ability need not preserve every experiential relation. Conversely, loss of an input or an accessible memory does not imply the disappearance of all remaining processes' experience under U1/P3.

This paper does not derive preservation of a named visual quality, pain, effort, familiar mineness, first-person continuity or a unique subject partition. Its tests do not contain phenomenal measurements. A register may remain an actual process while losing information about the task, and no decoder, trivial-loop condition, memory capacity or task score is added as a prerequisite for basal experience. An application may challenge the proposed ontology or bridge rather than merely fill in a missing parameter.

# Prior work, overlap and the scope of the contribution

Gao, Brodzki and Mukherjee relate synchronization over graphs to flat bundles, group actions and holonomy; their trivial-holonomy characterization concerns full synchronization [5, Section 2.1]. Our target-stabilizing condition is weaker, but follows from classical invariance and factorization, not a new mathematical foundation. Proposition 3 similarly specializes orbit--stabilizer and task-dependent sufficiency; Propositions 4--5 are finite Bayes decisions.

Rule and O'Leary model readout plasticity, redundancy and recurrent feedback that maintain function as neural representations change [6]. Rule and colleagues analyze stable task information and compensatory readout adaptation despite changing population activity [7]. Those mechanisms can possess history and learned structure unavailable to the route-blind reader here, so the present bounds do not contradict them. Neither study validates UCT or establishes the route model for a particular person's experience.

Grover and Bourgerie's measure--intervene--control study distinguishes dependence on learned connections from evidence that holonomy itself explains performance [8]. Their results underscore why a mathematical structure and a task score cannot alone identify the intervening mechanism. We do not reanalyze their data or transfer their claims to consciousness.

Internal overlaps are equally explicit. UCT III supplies the general fixed-capability and target-fiber distinctions [2]; TA19 already applies monodromy to tracking [3]; project records contain coherent sharing, target-null changes and compensated single-route decoding [9]. TH provides the stochastic precursor, while the later TH/RB work analyzes additional recovery signals [10]. AC considers unknown action-port permutations and task-specific calibration [11]. This paper's contribution is the joined analysis and diagnostic suite: stochastic loss versus reader mismatch, route-blind invariance, target-specific route metadata, residual errors, nonlinear invariant targets, and the separation of temporal transport from same-event charts. The earlier results are cited as earlier work, not counted again as separate original discoveries.

A targeted literature comparison does not establish priority for the exact combination. The claim is a bounded theoretical synthesis with explicit proofs and reproducible specializations. No claim that existing theories cannot express these constructions, or that the constructions settle a foundational consciousness problem, is made.

# MGTD review, checks and reproducibility

The research used the Map-Guided Theory Development protocol [4]. Each main claim retains its domain, joint premises, result type, source and interpretation limits. Mathematical proofs, physical application, semantic review, persistence and publication are separate states. In particular, a saved schema is not evidence that its premises hold in an actual brain.

The predecessor RT checkpoint recorded a local compatibility review of 1,387 items: the frozen 1,278-item UCT-MAP-v1.0.0 census and its TH/RT extensions. During publication preparation, the remote completed map had independently advanced to UCT-MAP-v1.1.0, incorporating TH and an additional recovery-budget module [10]. We preserve both provenance records rather than pretending the older RT candidate is the current authoritative map. The present review checks every displayed mathematical claim and its limits; it does not claim a fresh independent semantic certification of all items in the newer global map. The supplementary paper-level index links RT claims and the clarified contracts without silently promoting pending AC or R185 records.

Two standard-library Python scripts are supplied and were rerun during preparation. The original RT verifier checks 9,216 route/target cases by direct decoder enumeration, 9,216 route-label partition cases, 9,216 uniform-group Bayes cases, 9,216 two-route error cases, 576 invariant-algebra counts and 27,648 two-sided coordinate transformations. It also tests all pairs of invertible 2-by-2 generators over the prime fields F2 and F3: 36 and 2,304 pairs. Its full proofs apply to finite fields; the implementation's integer-modulo representation is used only for the stated primes.

The inherited TH verifier separately checks 6,666 finite signal/nuisance matrices, 6,400 dynamic-noise cases, 1,408 coordinate/loss cases, 21 correlation parameters and 125 three-stage sequences. It preserves the shared-mask, reversed-reader and hidden-key controls. These are inherited regression results, not new biological experiments or repeated claims of discovery. Counts concern bounded constructions; the written arguments, not enumeration alone, support the general statements.

The supplement includes the exact code, output JSON, source hashes, a claim-to-proof review table and a source-access ledger. Run `python code/check_transport.py --output RT_rerun.json` and `python code/check_handoff.py --output TH_rerun.json`. No network access is required for these mathematical checks. Larger historical maps are available through their pinned archives rather than represented as newly audited datasets in this paper.

# Limitations and conclusion

The route family, target and accessible state must be justified in any real application. Arbitrary changes of those choices can make a result look easier or harder without changing the physical system. Exact zero-error conditions need not be realistic under noise, and route labels may be costly or impossible to construct. The examples do not provide a learning algorithm, a reconstruction of a whole brain, or empirical evidence that subjective content follows a particular decoder.

What they do provide is a precise diagnostic order: determine whether information survives the actual transfer; specify the consumer's entire accessible interface; test whether one reader works across the possible routes; identify the target-specific correction information; and only then consider physical or experiential interpretation. Continuity of a selected task relation can coexist with substantial organizational change, while mere invertibility can coexist with failed uncalibrated readout. This is a tractable distinction to preserve in future theoretical and empirical work, without turning it into a threshold for experience.

# Declarations

**Authorship and assistance.** Hongju Liu supplied the research program, theoretical commitments, methodological requirements and originating thought experiments, and authorized publication after an additional review. Substantial AI assistance was used for literature comparison, derivations, code, author-side review, drafting and publication preparation. This is not independent peer review, a proof-assistant certificate or an assertion of separate human line-by-line verification.

**Data and materials.** All reported new calculations concern finite mathematical constructions. No human, animal or deployed-language-model experiment was performed for this manuscript. Source and reproduction files accompany this preprint. Cited third-party works retain their rights; CC BY 4.0 applies to original material to the extent rights are held.

**Version and interpretation.** This is paper version 1.0.0, distinct from research-checkpoint and global-map version numbers. A DOI or cryptographic timestamp records identity and availability, not truth, originality, journal acceptance or peer review. This first-party research does not amend or authoritatively interpret the Trinity Accord's fixed originals.

\clearpage

# References

[1] Liu, H. (2026). *Unified Consciousness Theory I: Structural--Experiential Identity and the Continuity from Physical Process to Conceptual Self*. Version 1.2. Theoretical preprint. DOI: **10.5281/zenodo.23131575**.

[2] Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience---From Inorganic Processes to Artificial Agents*. Version 1.0. Theoretical preprint. DOI: **10.5281/zenodo.23137088**.

[3] Liu, H. (2026). *Selecting and Tracking Conscious Subjects: Symmetry, Monodromy, and an IIT 4.0 Case Study*. Version 1.0. Theoretical preprint. DOI: **10.5281/zenodo.23002980**.

[4] Liu, H. (2026). *Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human--AI Research*. Version 1.0.1. Methods preprint. DOI: **10.5281/zenodo.23241982**.

[5] Gao, T., Brodzki, J., and Mukherjee, S. (2019). The geometry of synchronization problems and learning group actions. *Discrete & Computational Geometry*. DOI: **10.1007/s00454-019-00100-2**. Author version: **arXiv:1610.09051v3**.

[6] Rule, M. E., and O'Leary, T. (2022). Self-healing codes: How stable neural populations can track continually reconfiguring neural representations. *Proceedings of the National Academy of Sciences*, 119(7), e2106692119. DOI: **10.1073/pnas.2106692119**.

[7] Rule, M. E., Loback, A. R., Raman, D. V., Driscoll, L. N., Harvey, C. D., and O'Leary, T. (2020). Stable task information from an unstable neural population. *eLife*, 9, e51121. DOI: **10.7554/eLife.51121**.

[8] Grover, A., and Bourgerie, R. (2026). *Do Sheaf Neural Networks Use Holonomy? A Measure--Intervene--Control Study*. **arXiv:2607.19514v2**. Preprint; no independent replication is reported here.

[9] Liu, H. (2026). *UCT-MAP-v1.0.0: Frozen Author-Side Semantic Audit and Research Recovery Artifacts*. Repository `thechurchofagi/trinity-accord`, release commit `f6445052acb1644fcdd7b2adcdda2307f7b98bc7`, path `research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.0.0/`. Archived project material, not independent validation.

[10] Liu, H. (2026). *Temporal Handoff of Relational Memory* (TH20261009, v0.1.0), and *UCT-MAP-v1.1.0* (TH result v0.2.0, including recovery-budget extension). Repository `thechurchofagi/trinity-accord`, fixed current-state inspection commit `e1ceadd3097bec5ac6abb4510ae613ff7e41bbc3`, path `research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.1.0/`. Unpublished source work; not an additional peer-reviewed publication.

[11] Liu, H. (2026). *Action-Path Calibration and Task-Relative Self-Models*. AC20261009, result v1.0.0; pending project checkpoint. Repository `thechurchofagi/trinity-accord`, commit `11c1af83fa7e9eabca8351b67dfe162f59da7dd1`, path `research/uct-agent-consciousness-workspace/records/AC20261009_Action_Calibration/`.
