---
title: "Task-Relative Continuity Through Changing Representations"
subtitle: "Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout"
author: "Hongju Liu"
date: "9 October 2026 · Version 1.0.0"
lang: en-US
fontsize: 10pt
documentclass: article
geometry: margin=0.88in
mainfont: DejaVu Serif
monofont: DejaVu Sans Mono
colorlinks: false
header-includes:
  - '\usepackage{amsmath,amssymb}'
  - '\usepackage{microtype}'
  - '\usepackage{fancyhdr}'
  - '\pagestyle{fancy}'
  - '\fancyhf{}'
  - '\fancyhead[L]{\small Task-Relative Continuity}'
  - '\fancyhead[R]{\small Liu · v1.0.0}'
  - '\fancyfoot[C]{\thepage}'
  - '\setlength{\headheight}{14pt}'
  - '\emergencystretch=2em'
---

\begin{center}
Independent researcher, Shenzhen, China\\
\texttt{RT-TH-PAPER-v1.0.0} / Research record \texttt{RT20261009}\\
Theoretical preprint; not peer reviewed.
\end{center}

**DOI:** [10.5281/zenodo.23251651](https://doi.org/10.5281/zenodo.23251651)\

## Abstract {-}

A persisting component need not preserve a particular memory, and a recoverable memory need not be correctly used by its installed reader. We analyze these distinctions in finite models of representation transfer. A relational-memory example separates loss, invertible misencoding, and successful handoff between different storage carriers. For multiple bijective routes on a full source domain, one route-blind target decoder exists exactly when the target is invariant under every relative route transformation. The orbit quotient characterizes all exactly retained targets. Route metadata need distinguish only the distinct target-reader functions; we give its exact minimum alphabet. We also derive a sharp two-route error expression, a uniform-group Bayes law, and a finite-field signal-versus-nuisance recovery criterion. A three-position example preserves Hamming weight under unknown permutations while limiting recovery of the original first bit to three quarters and of the full ordered state to one half. Explicit counterexamples show why source support, route probabilities, decoder access, and hidden correlated variables must remain part of each claim. Conditional implications for a structural theory of experience are separated from the mathematics. The contribution is a task-sensitive theoretical synthesis with reproducible diagnostics, not a new foundation for invariant theory, a measured neural mechanism, or a criterion for consciousness.

**Keywords:** representational change; task-relative continuity; readout; invariance; calibration; relational memory; structural theories of experience

# 1. Introduction: what is supposed to continue?

A changing system can retain its material constituents while losing a memory. It can retain enough information for recovery while a particular downstream mechanism misreads the code. It can also preserve a selected task relation without preserving the whole source state. These possibilities make the statement that an organization “continues” underspecified: the relevant carrier, target, access interface, and time interval must be stated.

This paper asks a bounded question: **when representations pass through several possible transformations, what can one reader recover without knowing which transformation occurred, and what additional correspondence information makes exact recovery possible?** We connect that problem to the complementary distinction between genuine information loss and decoder mismatch. Here continuity means preservation or recoverability of a specified task relation across declared stages. It does not mean topological continuity, uninterrupted availability at every intermediate time, numerical personal identity, or unchanged subjective quality.

The motivation includes a structural account of experience. Unified Consciousness Theory (UCT) postulates a token-relative correspondence between the complete organization of an admitted actual process and its experiential organization [1]. Its universality and persistence commitments do not make a report channel, successful decoder, or stable memory a condition for basic experience. A continuing local process is not declared nonexperiential because a larger reader loses access to its former information. Those commitments are inherited assumptions, not conclusions of this paper. The mathematical results below do not depend on them.

Earlier work in the same research program already distinguishes task-relative sufficiency from complete structural identity [2], employs monodromy in subject tracking [3], and records compensated single-route readout, shared-event compatibility, and target-relative calibration [4,5]. The temporal-handoff checkpoint [6] separates loss and misbinding in moving memory supports. The present manuscript consolidates that example and develops the multiple-route, target-sensitive comparison. It does not present those earlier principles as new discoveries.

The exposition proceeds from a self-contained handoff example to exact decoder conditions, metadata requirements, error formulas, and limitations. Formal statements are analytic. Finite enumeration checks their implementations on declared domains; it is neither empirical validation of a consciousness theory nor an estimate of real neural performance.

# 2. Relational memory: persistence, recovery, and use

## 2.1 A memory moves between storage positions

Let the binary target $\tau$ and mask $\eta$ be independent and uniform. Initially two registers store

$$
A=\tau\oplus\eta,\qquad B=\eta.
$$

Each register alone is independent of $\tau$, whereas $A\oplus B=\tau$. The target is encoded in a joint relation. Consider a declared transfer to registers $C,D$, after which the original stored values are no longer available to the reader.

In the **shared-refresh** regime, an independent uniform mask $\xi$ gives

$$
C=A\oplus\xi,\qquad D=B\oplus\xi,
\qquad C\oplus D=\tau.
$$

The same XOR reader recovers the target exactly. In the **reversed-refresh** regime,

$$
C=A\oplus\xi,\qquad D=B\oplus\xi\oplus1,
\qquad C\oplus D=\tau\oplus1.
$$

The old reader is always wrong, but the compensated reader $1\oplus C\oplus D$ is always correct. In the **independent-refresh** regime, an additional independent uniform mask $\zeta$ gives

$$
C=A\oplus\xi,\qquad D=B\oplus\zeta.
$$

The pair $(C,D)$ is then independent of $\tau$. Every reader limited to this pair has optimal accuracy $1/2$.

| Transfer regime | Accuracy of the old XOR reader | Optimal accuracy from the final pair |
|---|---:|---:|
| Shared refresh | $1$ | $1$ |
| Reversed refresh | $0$ | $1$ |
| Independent refresh | $1/2$ | $1/2$ |

These are different claims about information and its use. They are not three degrees of consciousness. The declared reading interface excludes retained masks, old values, or other target-correlated side information. If such information remains available, it must be included.

The sufficient storage pair can change from $\{A,B\}$ to $\{C,D\}$ with no common register. This establishes a possibility for migrating *storage support*, not the absence of any fixed clock, transfer mechanism, or other necessary physical component. It also does not establish continuity of access at every instant between the specified stages.

## 2.2 Correlation can matter when marginal noise does not change

Choose two marginally uniform masks with $\Pr(\xi\ne\zeta)=\epsilon$, independently of the original target and mask. The final parity is $\tau\oplus E$, where $E=\xi\oplus\zeta$. Consequently,

$$
J_{\rm old}=1-\epsilon,
\qquad
J_{\rm opt}=\max(\epsilon,1-\epsilon).
\tag{1}
$$

At $\epsilon=0$ the old reader is correct. At $\epsilon=1$ a deterministic inversion repairs it. At $\epsilon=1/2$ the stipulated interface contains no target information. The marginal flip rates are unchanged across the family. Therefore neither synchrony nor the accuracy of one installed reader is, by itself, a measure of retained task information.

## 2.3 A general signal-versus-nuisance criterion

The following result is included to make the inherited handoff analysis self-contained. Let $\tau$ be uniform on $\mathbb F_q^d$, let $\eta$ be independently uniform on $\mathbb F_q^k$, and let the reader receive

$$
Z=H\tau+G\eta+b,
\qquad
\rho=\operatorname{rank}[G\ H]-\operatorname{rank}G,
$$

where the matrices and offset are fixed and known, and $\mathbb F_q$ is a finite field. No additional source information is available.

**Proposition H1 (finite-field recovery).** For arbitrary, including nonlinear or randomized, estimators,

$$
\sup_{\widehat\tau(Z)}\Pr(\widehat\tau=\tau)=q^{\rho-d}.
\tag{2}
$$

Perfect recovery is possible exactly when $\rho=d$, equivalently when there is a linear $D$ satisfying $DH=I_d$ and $DG=0$, with the known offset removed.

**Proof.** Quotient the observation space by $\operatorname{im}G$. The induced map from $\tau$ has rank $\rho$ and kernel dimension $d-\rho$. Every feasible observation therefore leaves a coset of $q^{d-\rho}$ source values. Their likelihoods are equal because the independent nuisance is uniform; their prior probabilities are equal as well. No estimator can exceed the reciprocal posterior class size, and any representative attains it. When the quotient map is injective, its inverse on its image extends linearly to the quotient space and gives $D$. Conversely, such a $D$ implies injectivity. $\square$

Equation (2) concerns exact recovery of the entire target vector. It is not a bound for arbitrary nonlinear encoders, a nonuniform source, or the average accuracy of a different question battery. A restricted observation port can lose further information, and an installed reader can perform worse than the optimum. None of these quantities measures phenomenology.

A crucial failure control is $Z_1=\tau\oplus E$, followed by $Z_2=Z_1\oplus E=\tau$. The mask $E$ is marginally independent of $\tau$ but correlated with the intermediate representation. If it remains available later, $Z_1$ was not a complete information boundary. Claims that later processing cannot restore an apparently lost target require a complete interface and an appropriate conditional-independence assumption, not merely marginal independence of a later variable.

# 3. Reversible routes and the blind-reader contract

Let $X,Y$ be nonempty finite sets of equal size. A nonempty finite route family $\mathcal P$ specifies bijections $T_p:X\to Y$. A target $f:X\to\mathcal A$ is fixed independently of the route. Every source state is permitted on every route: the allowed domain is $\mathcal P\times X$. The reader observes $y=T_p(x)$ and knows the family, but not the realized route. It has no route-revealing clock, retained key, history register, or other correlated side channel.

The zero-error question is whether there is one decoder $d:Y\to\mathcal A$ such that

$$
d(T_p(x))=f(x)\qquad\text{for every }p\in\mathcal P,\ x\in X.
\tag{3}
$$

No probability distribution is needed for this question. A “full domain” here is a property of the comparison model; it is not a claim that every mathematically expressible state can be independently prepared in a real organism. Replacing the Cartesian product by route-specific source supports changes the problem.

An individual route being invertible means that the entire source can be recovered *conditional on that route*. It does not guarantee recovery when the route is unknown. Conversely, failure to reconstruct the full source need not prevent recovery of a coarser target. Changing the target from the original first bit to a count is a change of task, not a repair of the original first-bit answer.

For an actual implementation, register identity, intermediate computation, transfer order, physical ports, noise and receiver state require independent specification. Abstract invertibility alone does not establish an admissible complete physical comparison.

# 4. Exact route-blind recovery

Choose a reference route $p_0$ and write

$$
H_p=T_{p_0}^{-1}\circ T_p,
\qquad
\Gamma=\langle H_p:p\in\mathcal P\rangle\leq\operatorname{Sym}(X).
$$

**Theorem R1 (common target decoder).** Equation (3) holds for some $d$ if and only if

$$
f\circ\gamma=f\qquad\text{for every }\gamma\in\Gamma.
\tag{4}
$$

When it exists, $d=f\circ T_{p_0}^{-1}$ is the unique decoder on $Y$.

**Proof.** Surjectivity of the reference route makes (3) on that route determine $d$ on all of $Y$. Substitution on any other route gives $f\circ H_p=f$. Invariance under a bijection implies invariance under its inverse; it is also preserved under composition. Thus the generators fix $f$ exactly when every element of $\Gamma$ fixes $f$. Conversely, (4) makes the displayed decoder satisfy (3). $\square$

The equivalent condition is equality of all route-specific reader functions

$$
r_p=f\circ T_p^{-1}.
$$

For complete-state recovery, $f=\operatorname{id}_X$, a common decoder requires every $T_p$ to be the same bijection. A selected target can tolerate nonidentical routes. Single known-route compensation is the familiar special case already recorded in the project's preceding work [4].

**Corollary R2 (all exactly preserved targets).** Let $\pi:X\to X/\Gamma$ map a source state to its orbit. A target has a common decoder if and only if

$$
f=\overline f\circ\pi
\tag{5}
$$

for some function $\overline f$. If there are $k$ orbits, there are exactly $2^k$ invariant Boolean targets.

**Proof.** Invariance is precisely constancy on each orbit. This makes $\overline f$ well defined, and conversely every such factor is invariant. Each orbit can independently receive one of two Boolean values. $\square$

The quotient is maximal only relative to the stipulated route family and reading interface. It is not a privileged physical scale or a maximal conscious subject. This is ordinary orbit factorization rather than a new general result in invariant theory [2,7].

## 4.1 Temporal loops are not conflicting descriptions of one event

In a connected interface graph with invertible edge maps and algebraically available reverses, relative paths generate loop transformations. A compatible target readout requires those transformations to preserve the target. It need not require every loop transformation to be the identity.

This differs from identifying several descriptions of *one actual event*. Coordinate transition maps for the same event must compose consistently. A physical process at a later time, however, may legitimately return to an interface with a changed state. A bit-toggle loop is not an inconsistency merely because it changes the bit. It obstructs a particular invariant-readout demand, not the possibility of the physical computation itself. This distinction prevents misapplication of the earlier shared-event compatibility results [4].

Algebraic closure is also not a claim that every generated transformation occurs with equal probability, or even occurs as an actual route. The generated group is a valid tool for the universal invariance statement. A statistical formula requires the actual sampling law, introduced separately below.

# 5. How much route information is sufficient?

Suppose a tag $c(p)$ is delivered with $y$, where the tag is a deterministic function of the route only, not of the source state. For each tag, the receiver has a fixed decoder. The full-domain condition remains in force.

**Theorem R3 (minimum route-tag alphabet).** The smallest tag alphabet permitting exact recovery is

$$
L_{\min}=\left|\{f\circ T_p^{-1}:p\in\mathcal P\}\right|.
\tag{6}
$$

**Proof.** Routes with the same tag must share one decoder. Each bijection reaches every $y$, so their reader functions must agree everywhere, not merely on an observed sample. Distinct reader functions therefore need distinct tags. Conversely, label their equality classes and use the corresponding reader. $\square$

For several possible future questions, replace $f$ by the joint vector of their required answers. If the route family is a finite group acting on $X$, orbit--stabilizer gives

$$
L_{\min}=\frac{|\Gamma|}{|\operatorname{Stab}_{\Gamma}(f)|},
\qquad
\operatorname{Stab}_{\Gamma}(f)=\{\gamma:f\circ\gamma=f\}.
\tag{7}
$$

A fixed-length binary tag then needs $\lceil\log_2L_{\min}\rceil$ bits. This is an alphabet-size bound, not a Shannon-entropy identity, a communication-rate theorem, or a count of all physical resources. Variable-length, interactive, source-dependent, or probabilistically tolerated-error protocols are different problems.

Creating the tag is not free. An actual system must acquire, retain, deliver and use sufficient route information within the required time. Equation (6) does not provide an observer able to discover an unrecorded route. Its relation to prior task-fiber and action-calibration results is explicit [2,4,5].

**Restricted-domain counterexample.** Let $X=Y=\{0,1,2,3\}$, with target table $f=(0,1,1,0)$ and routes $I$ and $T=(1,0,2,3)$. Permit only source states $\{0,2\}$ on $I$ and $\{0,3\}$ on $T$. The decoder $d=(0,0,1,0)$ succeeds with no tag, although the full-domain reader functions differ. Removing unreachable source-route pairs can therefore reduce the required tag alphabet. One must not use (6) after silently changing its domain.

# 6. Exact quantitative consequences

## 6.1 Linear invariants are only one class of targets

For $X=\mathbb F_q^d$ and invertible linear relative transfers $H_1,\ldots,H_s$, a scalar linear target is $f_\ell(x)=\ell x$. It is invariant precisely when $\ell(H_i-I)=0$ for every generator. Thus

$$
\dim\{\text{invariant scalar linear targets}\}
=d-\operatorname{rank}[H_1-I\mid\cdots\mid H_s-I].
\tag{8}
$$

The condition describes the annihilator of the sum of the images of $H_i-I$; rank--nullity proves the formula. The orbit quotient need not be a vector-space quotient. Accordingly, (8) cannot count all nonlinear invariant targets or all retained information.

## 6.2 Two equally likely routes

Let the source be uniform on $X$. Independently choose routes $p,q$ with probability $1/2$. Define the disagreement fraction

$$
\delta=\frac{|\{y:r_p(y)\ne r_q(y)\}|}{|X|}.
$$

**Theorem R4 (sharp average-error penalty).** For any common decoder, including randomized decoders, its route-conditional error probabilities obey $e_p+e_q\geq\delta$. The optimal mean success is

$$
A^*=1-\frac{\delta}{2}.
\tag{9}
$$

**Proof.** Both routes make $y$ uniform. Wherever their required answers disagree, the probabilities of correctly answering both sum to at most one. The summed conditional error is therefore at least one on that output. Average over all outputs. Always using $r_p$ attains the bound in mean error. Randomizing equally between the two readers balances their errors at $\delta/2$ if randomized minimax balance is sought; deterministic minimax equality is not asserted for every finite case. $\square$

## 6.3 Uniform sampling of a full finite group

Now impose a different, explicit probabilistic contract: the source is uniform on $X$ and the realized route is independently uniform over *all* elements of a finite group $\Gamma$ acting on $X$.

**Theorem R5 (orbit Bayes law).** The best route-blind target accuracy is

$$
A^*(f;\Gamma)
=\frac{1}{|X|}\sum_{O\in X/\Gamma}
\max_{a\in\mathcal A}|O\cap f^{-1}(a)|.
\tag{10}
$$

**Proof.** Given an output $y$, every possible source state in its orbit has the same posterior probability: the number of group elements carrying that source to $y$ is its stabilizer size. For each orbit, the optimal answer is a most frequent target value. Summing over the equally likely outputs gives (10). $\square$

Unlike the zero-error results, (9)--(10) depend on the stated distributions. For example, a uniform source on three states and two equally likely routes, identity and one three-cycle, give complete-state recovery probability $1/2$. Replacing those two routes by their uniformly sampled generated group gives $1/3$. The zero-error invariant targets agree, but the Bayes laws differ. Generating a group algebraically cannot justify changing the experimental sampling law.

# 7. A three-position diagnostic example

Let $X=\{0,1\}^3$ and allow all six permutations of its three positions. Adjacent swaps generate the group and do not commute. Its four orbits consist of states with Hamming weights $0,1,2,3$, with sizes $1,3,3,1$.

A common reader can always recover the number of set bits, but not the original first bit or ordered triple. Under the uniform source and uniform route assumptions of Theorem R5:

| Target | Minimum route-tag values for zero error | Best untagged accuracy |
|---|---:|---:|
| Parity | 1 | $1$ |
| Hamming weight | 1 | $1$ |
| Original first bit | 3 | $3/4$ |
| Full original ordered state | 6 | $1/2$ |

For the first bit, the weight-one and weight-two orbits each have target-value counts $1$ versus $2$. Equation (10) gives $(1+2+2+1)/8=3/4$. Complete-state recovery allows one representative per orbit, giving $4/8=1/2$. A three-valued tag identifies which final position contains the original first bit; six reader classes are required for the full ordered state.

The invariant scalar linear space contains only the parity direction and has dimension one. Nevertheless Hamming weight has four distinguishable values, and there are sixteen invariant Boolean targets. This is a concrete reason not to interpret a convenient linear dimension as all retained content. Four categories can be encoded using two fixed-length bits, but their entropy under this source distribution is not asserted to be exactly two bits.

Known permutations do not erase individual bits. The reduced performance is a limitation of the route-blind interface. A receiver supplied with the actual permutation can invert it; a receiver requiring only Hamming weight does not need the permutation at all. The target determines which correspondence information matters.

# 8. Interpretation controls and conditional relevance to experience

## 8.1 Recoding a description is not rewiring a system

For bijective source and output relabelings $a,b$, transform

$$
T'_p=b\circ T_p\circ a^{-1},\qquad f'=f\circ a^{-1}.
$$

Common-decoder existence, the number of target-reader classes, and Bayes accuracy with transported probability laws remain unchanged. Relative groups are conjugate. This is a change of representation. In a physical claim, ports, timing, noise, interventions and target interpretation must also be transported. Changing the device while leaving those relations fixed is not merely relabeling it.

A clock or route bit can remove an apparent obstruction: with routes identity and complement, an output $y$ and the actual route bit $p$ determine $x=y\oplus p$. If the receiver's ongoing state already contains that history, it belongs in the modeled reading interface. The route-blind impossibility does not apply to the enlarged interface.

## 8.2 Terminal recovery is not uninterrupted experiential continuity

The results distinguish persistence of a carrier, conditional invertibility, availability to a specified reader, correctness of the installed reader, and retention of a task relation. Recovery at the endpoint says nothing by itself about access at each intermediate moment. An endpoint code may be restored from a separate key after an interval during which the designated consumer could not use it.

Likewise, a freely chosen mathematical target is not automatically redness, pain, effort, familiarity, or any named subjective quality. The bare existence of an inverse is not an installed mechanism. An actual application must justify the source, transfer law, episode, allowed interventions, reader and independently interpreted target. These are substantive obligations, not metadata that become true when entered in a graph.

## 8.3 A conditional UCT application, not a new axiom

UCT I distinguishes the actual process, its complete organization and its experiential counterpart; UCT III fixes the evaluation context before relating genuine capability differences to complete experiential-type differences [1,2]. Only after the actual comparison, common constitutive signature and true fixed capability functional are justified can that inherited implication be applied. A different observed sample score or a change in the information allowed to the reader is not automatically such a comparison.

The positive interpretive point is target-relative: some relations can persist through changing carriers and routes, while others require correction information. Preserving a count does not establish preservation of ordering, and preserving one capability does not establish complete experiential identity. Conversely, if a local process independently continues, loss of a larger consumer's access does not cancel that local process's basic experience under U1/P3. No stable decoder, trivial loop action, task score, or unique-subject selector is added as an experience-existence threshold.

This manuscript therefore offers a way to articulate what a claimed continuity requires. It does not locate a human consciousness core or prove numerical identity of an experiencing subject across replacements.

# 9. Prior work and the contribution boundary

The mathematics of synchronization, invariance and factorization is established. Gao, Brodzki and Mukherjee connect synchronization over graphs to flat bundles and holonomy; their treatment distinguishes synchronization in a group from synchronization in an associated representation [7]. Target-invariant readout can allow nonidentity transformations, but it would be misleading to portray that possibility as absent from prior group-action theory. Our finite reader criterion is a specialization organized around task access and missing route information.

Rule and O'Leary model stable readout of changing neural codes using plasticity, redundancy and recurrent constraints [8]. Their adaptive readers are not contradicted by a theorem whose receiver has no compensating history. Rule and colleagues analyze representational drift and the plasticity required for reliable readout [9]. These studies motivate careful separation of changing code and stable task information; neither directly tests the present finite route family or validates UCT.

Grover and Bourgerie's preprint distinguishes learned geometric changes and sensitivity to connection interventions from stronger claims that holonomy itself mediates a task [10]. It supplies a relevant caution about mechanism attribution, not evidence of subjective experience. No raw data or learned model from these studies was reanalyzed here.

The author's earlier published paper already uses monodromy for subject tracking [3], and earlier records contain target-relative sufficiency, single-route compensation, consistent shared-event identification and action calibration [2,4,5]. The TH checkpoint supplies the stochastic handoff material included in Section 2 [6]. The present contribution is the integrated diagnostic structure: **loss versus mismatch; task-preserving versus state-preserving transport; exact route-reader metadata; and quantitative performance under separately declared route laws**. Individual formulas are proved for clarity and reproducibility, not presented as a new general foundation of mathematics.

The targeted prior-work comparison has not established historical priority for the exact synthesis. The latest repository also contains a distinct extension of TH on omitted-input recovery budgets, included in map release v1.1.0 [6]. That extension is acknowledged but is not republished here as a fresh result. This article remains a modest theoretical analysis rather than a claim of a foundational consciousness breakthrough.

# 10. Review, provenance, and reproducibility

The work follows the separation of claims, guards, source versions, counterexamples and preservation states proposed in Map-Guided Theory Development [11]. The research package inherited a compatibility review of a frozen 1,278-item map and a local TH/RT extension with 1,387 item-level records. Those counts describe the saved inventory, not an independent count of proved propositions or an error-detection benchmark.

At final review, the live repository had advanced to UCT-MAP-v1.1.0, sequence 2, at commit \texttt{e1ceadd3}. Its completed TH integration must not be replaced by the older local v1.0.1 candidate. The supplement therefore preserves the earlier snapshot as provenance and supplies a separate paper-claim crosswalk and reconciliation note. This article does not claim to merge its RT module into that live release, or to have repeated every historical semantic review. Existing actual-instance and named-experience obligations remain open.

All central proofs were reviewed again. The review tightened the distinction between a generated group and the actual sampled route family, made the full-domain and route-only-tag conditions explicit, distinguished alphabet size from entropy and total resources, and supplied the handoff derivation within the article. No empirical conclusion or published UCT axiom was changed.

The standard-library program \texttt{check\_transport.py} independently enumerates decoder tables and route partitions. Its actual rerun reproduced the following saved results:

| Verification category | Executed finite cases |
|---|---:|
| Common-decoder criterion | 9,216 |
| Minimum route-tag partitions | 9,216 |
| Uniform-group Bayes law | 9,216 |
| Two-route average-error formula | 9,216 |
| Invariant Boolean-target counts | 576 |
| Transported-coordinate comparisons | 27,648 |
| Linear invariant space over $\mathbb F_2$ | 36 generator pairs |
| Linear invariant space over $\mathbb F_3$ | 2,304 generator pairs |

Additional review fixtures cover nonbinary targets, route families without an explicitly included identity, nonuniform-source counterconditions, hidden route bits, and the generated-group sampling mistake. The inherited TH verifier is rerun separately and is not counted as a new discovery. Results and source hashes are preserved in the supplement. Finite enumeration checks implementations on these domains; the general mathematical conclusions rest on their proofs.

To reproduce, run the scripts in the supplementary \texttt{code/} directory using Python 3.11 or later. Exact claims use integer or rational arithmetic; there are no network requests or human, animal, or deployed-language-model interventions in the tests. The supplement separates historical outcomes from the current rerun.

# 11. Limitations and conclusion

The main route model is finite, bijective, full-domain and explicit about receiver access. Noninvertible transformations can lose information within a known route; the general fiber criterion and Proposition H1, where applicable, address that earlier issue. Arbitrary nonuniform priors, route-dependent supports, interactive protocols, history-dependent readers, and continuous noisy dynamics require their own analysis. A larger physically faithful model may reveal information omitted by a smaller one.

The current formalization also idealizes away the difficulty of identifying complete organization in a real brain or artificial agent. It does not establish a uniquely correct spatial grain, a universal organizational metric, a named phenomenal interpretation or an experience count. Failure of an experimental decoder is not proof that the entire actual process lacks the target. Successful mathematical decoding is not proof of actual downstream use.

Within its scope, the synthesis gives a precise alternative to demanding an unchanging material core: identify the target, the admissible transfers and the receiver's actual information; then ask whether relative changes preserve the target or whether adequate correspondence information reaches the reader. A changing organization can preserve one relation and lose another. Even reversible transfers can defeat a path-blind reader. These distinctions make claims of continuity more testable without turning successful memory or coordinated readout into a prerequisite for basic experience.

# Declarations {-}

**Authorship and AI assistance.** Hongju Liu provided the research program, conceptual constraints and originating thought experiments, and is the human author responsible for public claims. Substantial AI assistance was used for literature comparison, formal derivation, programming, checking, review and writing. Author-side review is not independent peer review, and no independent reviewer endorsement is claimed.

**Data and code.** The accompanying package contains the manuscript, executable finite-model checks, rerun outputs, claim and source records, explicit revision history, and the frozen predecessor research archive. It reports no new human-subject or animal experiment and no measurement of subjective experience. Third-party publications are cited rather than republished in full.

**Version and publication identity.** This manuscript is version 1.0.0 of the standalone RT/TH theoretical preprint. Its manuscript identifier is separate from research-result and map-release identifiers. This published preprint has Zenodo DOI 10.5281/zenodo.23251651; OTS and Arweave completion must be separately verified from their later receipts. Completed scientific versions are not silently overwritten.

**Rights.** CC BY 4.0 applies to original material to the extent the author holds the rights. Cited third-party works retain their own rights. DOI registration and timestamping establish artifact identity or dated existence, not truth, originality or peer review.

# References {-}

[1] Liu, H. (2026). *Unified Consciousness Theory I: Structural--Experiential Identity and the Continuity from Physical Process to Conceptual Self*. Version 1.2. Theoretical preprint. DOI: [10.5281/zenodo.23131575](https://doi.org/10.5281/zenodo.23131575).

[2] Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience---From Inorganic Processes to Artificial Agents*. Version 1.0. Theoretical preprint. DOI: [10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088).

[3] Liu, H. (2026). *Selecting and Tracking Conscious Subjects: Symmetry, Monodromy, and an IIT 4.0 Case Study*. Version 1.0. Theoretical preprint. DOI: [10.5281/zenodo.23002980](https://doi.org/10.5281/zenodo.23002980).

[4] Liu, H. (2026). *UCT-MAP-v1.0.0: Frozen Semantic Audit and Research Recovery Artifacts*. Research archive; author-side review. [Release at commit f6445052](https://github.com/thechurchofagi/trinity-accord/blob/f6445052acb1644fcdd7b2adcdda2307f7b98bc7/research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.0.0/RELEASE.json). Includes R149, R157, R177 and shared-event source references. Not independent empirical evidence.

[5] Liu, H. (2026). *Action Calibration and Task-Relative Self-Models*. AC20261009, result v1.0.0; research checkpoint. [Fixed handoff at commit 11c1af83](https://github.com/thechurchofagi/trinity-accord/blob/11c1af83fa7e9eabca8351b67dfe162f59da7dd1/research/uct-agent-consciousness-workspace/records/AC20261009_Action_Calibration/CURRENT_HANDOFF_ZH.md). Cited as antecedent, not as a promoted premise.

[6] Liu, H. (2026). *Temporal Handoff of Relational Memory*. TH20261009 v0.1.0, preserved predecessor package. Subsequent extension: *Temporal Handoff and Omitted-Input Recovery Budget*, result v0.2.0, UCT-MAP-v1.1.0. [Fixed repository record at commit e1ceadd3](https://github.com/thechurchofagi/trinity-accord/blob/e1ceadd3097bec5ac6abb4510ae613ff7e41bbc3/research/uct-agent-consciousness-workspace/records/TH20261009_Temporal_Handoff/README.md). Section 2 draws on the preserved v0.1.0 equations, not on unpublished claims of the later budget extension.

[7] Gao, T., Brodzki, J., and Mukherjee, S. (2019). *The Geometry of Synchronization Problems and Learning Group Actions*. [arXiv:1610.09051v3](https://arxiv.org/abs/1610.09051v3), 14 May 2019; journal DOI [10.1007/s00454-019-00100-2](https://doi.org/10.1007/s00454-019-00100-2). Sections 1.1 and 2.1 are direct mathematical antecedents.

[8] Rule, M. E., and O'Leary, T. (2022). Self-healing codes: How stable neural populations can track continually reconfiguring neural representations. *Proceedings of the National Academy of Sciences*, 119(7), e2106692119. DOI: [10.1073/pnas.2106692119](https://doi.org/10.1073/pnas.2106692119).

[9] Rule, M. E., Loback, A. R., Raman, D. V., Driscoll, L. N., Harvey, C. D., and O'Leary, T. (2020). Stable task information from an unstable neural population. *eLife*, 9, e51121. DOI: [10.7554/eLife.51121](https://doi.org/10.7554/eLife.51121).

[10] Grover, A., and Bourgerie, R. (2026). *Do Sheaf Neural Networks Use Holonomy? A Measure--Intervene--Control Study*. [arXiv:2607.19514v2](https://arxiv.org/abs/2607.19514v2). Preprint; used as a bounded mechanism-attribution comparison, not as replicated evidence.

[11] Liu, H. (2026). *Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human--AI Research*. Version 1.0.1. Methods preprint. DOI: [10.5281/zenodo.23241982](https://doi.org/10.5281/zenodo.23241982).
