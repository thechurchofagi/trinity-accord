# R128 — Joint identification is not automatically joint dynamical closure

Hongju Liu / theoretical continuation on the unified A–B–C formal map, 6 October 2026.

## 1. Exact position in the map

This derivation joins three established branches:

- **C:OBS_REFINEMENT**, UCT III §5.3: joint observations intersect fibers and cannot lose set-level identifying information.
- **C:P6**, UCT III §6.4, and **R126:P2**: autonomous summary dynamics require successor-class agreement; in a stochastic model this is agreement of pushed-forward probability laws.
- **R127:P3**: jointly available relations can carry information absent from individual marginals.

The question is whether two individually closed summaries must give a jointly closed summary. The answer depends on the dynamics. C1 is not a premise of the mathematical statements below. It enters only after actual constitutive organization has been separately identified.

## 2. N128:DET_JOIN — Deterministic closure survives a joint summary

Fix the **same** sufficient state domain S and the same physically interpreted total deterministic operation family F_a:S→S. Suppose p_i:S→Z_i, i=1,2, satisfy

\[
p_i\circ F_a=\bar F_{i,a}\circ p_i
\]

for every common operation a. Define p=(p_1,p_2), with domain of summary values Z=p(S), not an assumed full Cartesian product.

Then p has the closed update

\[
\bar F_a(z_1,z_2)=
(\bar F_{1,a}(z_1),\bar F_{2,a}(z_2)),\qquad (z_1,z_2)\in Z.
\]

**Proof.** If p(s)=p(t), each coordinate summary agrees. Their successor summaries therefore agree coordinate by coordinate, so R126:P2 applies. Moreover the displayed pair equals p(F_a(s)) for any representative s of (z1,z2); hence it remains in Z. QED.

The theorem does not combine two different physical systems, two incompatible operation labels, two different resource budgets, or two different time steps. It establishes a description of one supplied dynamics. It does not show that separately executable tasks are simultaneously schedulable.

## 3. N128:MARKOV_JOIN — Marginal stochastic closure is insufficient

Let S={0,1}^3 with current state s=(x,y,z). At every step draw a fresh independent fair bit U and set

\[
X^+=U,\qquad Y^+=U\oplus Z,\qquad Z^+=Z.
\tag{1}
\]

This specifies a finite Markov kernel exactly: each row assigns probability 1/2 to (0,z,z) and 1/2 to (1,1 XOR z,z).

Take p1(s)=x and p2(s)=y. For every current state,

\[
P(X^+=0\mid s)=P(Y^+=0\mid s)=1/2.
\]

Thus each summary separately satisfies the strong-lumpability row-sum criterion, for every initial distribution. Each individual summary has the same fair-bit successor law.

The joint summary p(s)=(x,y) fails that criterion. States

\[
s_0=(0,0,0),\qquad s_1=(0,0,1)
\]

have the same joint summary, but

\[
\begin{array}{c|cc}
 & Z=0 & Z=1\\\hline
P((X^+,Y^+)=(0,0)) & 1/2 & 0\\
P((X^+,Y^+)=(1,1)) & 1/2 & 0\\
P((X^+,Y^+)=(0,1)) & 0 & 1/2\\
P((X^+,Y^+)=(1,0)) & 0 & 1/2
\end{array}
\]

Equivalently,

\[
P(X^+=Y^+\mid s_0)=1,
\qquad P(X^+=Y^+\mid s_1)=0.
\]

No single transition law indexed only by the common present pair (0,0) can represent both preparations. The two point-mass initial distributions violate all-initial-distributions closure in exactly the sense of C:P6. QED.

This does not claim failure for every restricted initialization. After one step, the reachable states satisfy z=x XOR y; restricting the model to that invariant subset changes the domain and makes the hidden value recoverable from the joint pair. That counterlimit is retained deliberately. It is the original eight-state, all-initial-distributions claim that fails.

If one insists on refining the original joint observation on all eight states, every pair-fiber contains one z=0 and one z=1 state whose next-pair laws differ. Each of its four blocks must split. The full eight singleton states therefore form the only stable refinement retaining that exact pair observation. This minimal-refinement claim is specific to this example; general Markov models need not require full-state recovery.

The example does not contradict N128:DET_JOIN. Introducing the random bit as a fixed labeled input u would yield a deterministic family, but then the Y-summary would no longer close under each F_u: Y+=u XOR z depends on the hidden z. Marginalizing the input before checking closure changes the premise.

## 4. N128:JOINT_CRITERION — The exact repair

For a supplied finite operation-indexed Markov kernel K_a on S, let p=(p1,p2). An autonomous joint summary kernel exists exactly when

\[
p(s)=p(t)\ \Longrightarrow\
(p_*K_a)(s,\cdot)=(p_*K_a)(t,\cdot)
\quad\text{for every }a.\tag{2}
\]

Here p_*K_a is the law of the next **pair**, including dependence between its coordinates.

**Proof.** Necessity follows because an autonomous law assigns one successor distribution to one summary value. Sufficiency follows by defining that distribution using any representative state; (2) makes it representative-independent. QED.

A sufficient additional condition is conditional independence of the two next-summary coordinates at each full current state, together with closure of each marginal for the same operation family. The joint law is then the product of the two marginal laws, both determined by the current pair. Conditional independence is not necessary: a fixed shared fair output (U,U) has a perfectly closed, correlated joint law.

Thus it is incorrect to replace (2) with a demand that all jointly modeled constituents be statistically independent. The required property is that their joint response law be determined by the declared current summary.

## 5. What the new map must prohibit

The following implication is invalid without more premises:

\[
\text{each mechanism coordinate closes}
\ \Longrightarrow\
\text{their joint dynamics close}.
\]

It is valid for the common deterministic setup of §2. It is false for the general stochastic setup of §3. Meanwhile C:OBS_REFINEMENT remains valid in both: observing (p1,p2) still refines either observation alone. Increased identifying information and autonomous dynamical sufficiency are different properties.

Consequently, joining B's mechanism coordinates to C's capability profile requires a test of the **joint transition and operation law**, not just separate fits or separate theory translations. A missing coordination variable can determine dependence between outputs while leaving every marginal unchanged.

Within UCT, if such a coordination relation is independently established as constitutive of an actual P, **R127:P5** supplies its structural experiential interpretation under **A:C1**. The Markov counterexample itself identifies no biological mechanism, measures no experience and gives no subject-unification rule.

## 6. Verification and originality boundary

The proof is analytic. `check_joint_closure.py` evaluates its finite transition matrix with exact rational arithmetic, checks both marginal partitions, the failed joint partition, the restricted-domain counterlimit and the stable-refinement claim. This is a finite mathematical counterexample check, not a stochastic simulation or biological/AI experiment.

The criterion in (2) is established strong-lumpability mathematics, already used in Paper C. The targeted search located prior work on lumping and partition refinement, including [Testing lumpability in Markov chains](https://www.sciencedirect.com/science/article/pii/S0167715203001263) and [Symbolic Partition Refinement with Automatic Balancing of Time and Space](https://ira.informatik.uni-freiburg.de/~wimmer/pubs/wimmer-et-al-perfeval-2010.pdf). Only retrieved search summaries were inspected in this round; no full-paper reading or historical originality claim is made. The program-level increment is locating and blocking an unsafe cross-paper inference with a fully specified countermodel.
