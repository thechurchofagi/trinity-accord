# Local child-query incompatibility: exact small cases and the density gap

Research checkpoint, 2026-10-03. The original all-dimensional target
\(M_n\ge c2^n\) remains **open**. No result below is a proof of that target.
Published v1.0 is preserved.

## Admissible family and terminology

Use a complete binary coordinate-query tree. At each node, query a coordinate
not previously queried on that input path. Its two children fix that coordinate
to zero and one. An independent orientation chooses which child is ranked
first. Heap node numbers start at one. Require the two child queries to be
**different whenever at least three coordinates remain before the current
query**. With two remaining coordinates, both children must query the last
one; this case is exempt.

These are ordinary conditional lexicographic/coordinate-query trees, not a
new representation. Lexicographic preference trees are discussed, with prior
references, by Fargier et al., *The complexity of unsupervised learning of
lexicographic preferences*, arXiv:2209.11505v1 (23 September 2022), Sections
1 and 4: <https://arxiv.org/pdf/2209.11505>. The pseudo-sweep prefix condition
is existing terminology: Padrol and Philippe, arXiv:2102.06134, Section 6.1,
<https://arxiv.org/pdf/2102.06134>. This is a limited source check, not a
comprehensive originality certificate. The quantitative question tested here
is whether the specified local inequality forces positive run density under
**every genuine signed additive sweep**.

## Prefix separation: analytic integer certificate in every dimension

Let \(z\) be the first excluded vertex of a prefix. Along its input path,
write the distinct queries as \(j_0,\ldots,j_{n-1}\), and let
\(\theta_t\in\{0,1\}\) be the preferred child value at that node. Define
\[
 c_{j_t}=(-1)^{\theta_t}3^{n-1-t},\qquad
 S_z(x)=\sum_j c_j(x_j-z_j).
\]
If \(x\ne z\), the first query on which they differ determines their rank
comparison. Its contribution to \(S_z(x)\) has the same sign as that
comparison, and its magnitude exceeds the sum of every possible later
contribution. Thus earlier vertices satisfy \(S_z(x)\le-1\), and vertices
at or after \(z\) satisfy \(S_z(x)\ge0\). The centered affine threshold
\(-1/2\) strictly separates the prefix. This familiar lexicographic dominance
proof works for **every** valid query geometry and orientation, independently
of the local child-query inequality.

## Exact comparison graph and a conditional route to the main theorem

Fix the geometry, a full vertex sweep \(p\), and the root orientation zero.
Let \(\tau\) be its canonical all-zero-orientation rank and let \(u_i\)
be the query-tree least common ancestor of consecutive sweep vertices. Set
\(s_i=\operatorname{sgn}(\tau(p_{i+1})-\tau(p_i))\). Actual comparison signs
are \(s_i(-1)^{\theta_{u_i}}\). This is the established signed ancestor rule.

In the linear word, let \(D\) count consecutive equal controllers; these
always force a turn. For distinct controllers aggregate
\(J_{uv}=\sum_{\{u_i,u_{i+1}\}=\{u,v\}}s_i s_{i+1}\), set
\(W=\sum|J_{uv}|\), and put \(K=(N-2-D-W)/2\). It is a nonnegative integer:
it counts cancellation pairs. For any orientation,
\[
 R=1+D+K+\phi(\theta),
\]
where \(\phi\) is the weighted number of unsatisfied graph edges:
positive \(J\) wants equal bits, negative \(J\) wants opposite bits.
For cyclic bookkeeping use all \(N\) comparisons and transitions; then
\(K=(N-D-W)/2\) and \(C=D+K+\phi\). These are direct accounting identities,
not a newly named statistical method.

Let \(q\) count active **non-root** controllers in the linear word. Independent
fair orientations give the inherited entropy bound
\[
 \Pr(R\le k)\le 2^{-q}\sum_{j=0}^{k-1}\binom{N-2}{j}.
\]
Indeed the root appears in every full sweep and anchors one known comparison
sign. Its position and the transition word recover the entire sign word,
which determines every active bit. The map is injective.

**Conditional all-dimensional reduction.** Suppose, for every sufficiently
large dimension, some valid deterministic query geometry satisfies
\(D+K+q\ge\delta N\) for **every** genuine signed additive sweep, for a
fixed \(0<\delta\le1\). Then the main goal holds, for example with
\(c=\delta^2/144\).

Proof: if \(D+K\ge\delta N/2\), the run count is already greater than \(cN\).
Otherwise \(q\ge\delta N/2\). For \(k=\lfloor cN\rfloor\), either the event
is empty or \((k-1)/(N-2)\le c\). The binomial entropy estimate and
\(H_2(c)<3\sqrt c=\delta/4\) give probability at most
\(2^{-\delta N/4}\). For completeness,
\(-x\log x\le\sqrt x\),
\(-(1-x)\log(1-x)\le x\le\sqrt x\), and \(\log2>2/3\), so the entropy
inequality is elementary. Union over the baseline bound \(3^{n^2}\) for
additive sweep chambers gives total failure below one eventually. One
orientation then handles **all** sweeps simultaneously, and the separator
proof supplies admissibility. The structural hypothesis is **unproved**;
this conditional reduction does not establish it. Geometry may depend on
\(n\); no compatible infinite family is required by the original goal.

## Complete small results

The exact chamber enumeration is inherited from the audited cube sweep
scripts. Root orientation can be fixed: flipping all orientations reverses
all ranks and preserves both statistics. All inactive bits are irrelevant.

| Dimension | All local query geometries | All signed additive chambers | Active orientation words for one representative | Universal minimum R | Universal minimum C | Minimum D+K+q |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 6 | 96 | 656 | 3 | 4 | 5 |
| 4 | 96 | 5,376 | 212,864 | 4 | 4 | 9 |

Integer coordinate permutations and reflections prove that the listed
geometries in each dimension form a single cube-isometry orbit. Hence the
complete representative orientation check covers **every** listed geometry.
The budget minima are separately checked on every geometry and every signed
chamber. These finite facts are not extrapolated to arbitrary dimension.
An initial guessed assertion that the Q3 minimum was two was rejected by the
verifier and corrected to three; the error log is retained.

In dimension five there are 34,560 geometries and **16** cube-isometry orbits.
The complete orbit enumeration is a geometric reduction only. It does not
complete all Q5 orientations or sweep chambers.

## Strict genuine Q5 linear counterexample

A proposed stronger conclusion \(R\ge N/4\) for every such geometry and
orientation is false in Q5. The smallest dimension of failure is five within
this family, by the complete smaller cases above. Exact signed weights are
\[
 (8,4,14,-16,-1).
\]
The heap query array, nodes 1 through 31, is
\[
 (0,1,2,2,3,1,3,3,4,2,4,3,4,1,4,4,4,3,3,4,4,2,2,4,4,3,3,4,4,1,1).
\]
Set orientation one at nodes
\(4,5,9,11,15,16,17,20,21,25,28,29\), and zero at all others.
The genuine scan's rank word is
\[
 (6,7,8,10,18,19,23,21,1,3,4,5,9,11,12,13,
 28,30,17,16,29,31,22,20,0,2,14,15,24,25,26,27).
\]
Direct differences give \(R=7\) and \(C=8\). All 32 integer scores are
distinct. A solver-free independent recursive traversal checks the word and
all 31 strict prefix separators, with 992 vertex checks. Its full integer
certificate is retained.

This excludes the **linear** universal quarter bound. It does **not** exclude
\(C\ge N/4\), a linear \(N/4-1\) bound, a smaller positive constant, or
existence of carefully selected good geometries/orientations. In particular,
no asymptotic upper bound on \(M_n\) follows from this witness.

## Pressure evidence and precise continuation

The MILP searches only propose feasible orientations; integer scores, direct
ranks, and separators independently certify each reported counterexample.
Solver lower bounds are not used as mathematical evidence.

* Seed 202610031941, six signed/permuted draws for each coherent Q5 seed,
  stops at the strict linear witness after 156 actual cases and five solves.
* Cyclic pressure seed 202610031947 checks 49,536 actual cases across all
  16 geometry representatives and the 516 inherited coherent sorted weight
  seeds, six signed/permuted draws per seed. No sampled \(C<8\); this is an
  **incomplete** signed weight audit.
* Adding a sixth input coordinate requires repairing the old final two-query
  levels, otherwise equal child queries violate the new local condition.
  All 256 repairs of the displayed geometry, on 38 specified actual new-weight
  intervals, give 9,728 checked cases and 3,072 MILP calls. No feasible
  \(C<16\) was found. The best certified candidate has \(R=17,C=16\).
  This is an incomplete family/weight search, not a theorem over Q6.

The exact next gap is the **cyclic** density question, or the weaker uniform
\(D+K+q\) structural budget sufficient for probabilistic selection. Seek a
true additive counterexample before attempting induction. Do not add local
face run counts without a charging proof: a single global turn can affect
several disjoint rank intervals. Common-addition constraints must enter an
all-dimensional argument. The earlier unrestricted random-tree tail
obstruction remains valid for that earlier distribution; the present local
condition excludes its equal-query prefix event, but no new uniform tail is
claimed.

Reproduction: run `verify_locally_adaptive_query_trees.py`,
`enumerate_locally_adaptive_query_orbits.py`,
`probe_locally_adaptive_query_density.py --seed 202610031941`,
`verify_locally_adaptive_query_counterexample.py`,
`probe_locally_adaptive_query_density.py --cyclic`, and
`probe_locally_adaptive_query_extensions.py` in this directory. The scripts
share `adaptive_query_research.py` and audited existing chamber certificates.
