# Read-degree concentration and an interleaving obstruction for RLC

## 2026-10-03 update: exact reflection graphs and frustrated merging

GRAY_REFLECTION_GRAPH_AUDIT.md reduces every sign choice of an arbitrary
generic positive magnitude vector to one exact weighted graph:
\[
 \min_z C=(2^n+D-W)/2+\phi,
\]
where D counts equal consecutive highest-differing-bit labels, W is the
absolute off-diagonal coupling weight, and phi is the established weighted
frustration. All couplings to the highest coordinate cancel by additive
complement symmetry. The five-dimensional integer vector (2,20,16,5,12)
is the first possible negative-cycle obstruction: independently satisfying
all edges predicts 18, whereas the true sign-orbit minimum is 20.
Its separated row lifts have an error of \(2^{n-4}\), excluding a
dimension-independent correction to that simplification.

The new independent verifier checks every signed additive sweep through
Q4 and preserves explicit integer certificates. A translated-face test
also covers all positive new weights at fixed parent magnitudes
(1,14,4,12,20), all coordinate assignments and all signs: 34,560 positive
Q6 chambers, minimum cyclic count 20 within that specified family.
Neither result gives a lower bound for every magnitude chamber.
The precise new proof obligation is a uniform positive deficit for
the net coupling energy E*-D. Central symmetry alone is insufficient:
there are centrally symmetric vertex permutations with only two runs
in every dimension, which an exact face contradiction excludes as
additive scans. The main constant-density target remains open.

## 2026-10-03 update: exact Gray scan recursion audit

The new note GRAY_SWEEP_RECURSION_AUDIT.md proves an exact count for every
signed-lex significance permutation and reflection, a same-weight
doubling-recurrence counterexample with unbounded loss, and existence of the
forward-Gray minimum-density limit. If \(p_0=f<n-1\) and
\(\ell=\min\{t\ge1:p_t>f\}\), the signed-lex count is
\(2^n(1-2^{-\ell})\); if \(f=n-1\), it is \(2^n-1\).
Thus every such scan has at least \(2^{n-1}\) runs. Generic subset-sum
scans already improve on that minimum in dimension four, so this theorem
does not give the required lower bound over all weights.
The cyclic minimum \(F_n\) satisfies \(F_n\le2^{n-d}F_d\), and therefore
\(\lim RLC(\gamma_n)/2^n=\inf_d F_d/2^d\). Its positivity remains open.

## 2026-10-03 update: forward-Gray row-lift ceiling

The forward-Gray candidate now has an explicit all-dimensional additive
sweep upper bound.  For every \(n\ge5\), the five high-coordinate weights
\((-1,-14,-4,-12,-20)\), followed by a separated binary row lift using
lower weights \(64\,2^j\), give exactly

\[
 R(\gamma_n\circ\pi)=10\,2^{n-5}=\frac{5}{16}2^n,
 \qquad \gamma_n(x)=x\oplus(x\gg1).
\]

Hence \(\operatorname{RLC}(\gamma_n)\le(5/16)2^n\).  This is a ceiling
for the specific candidate, not a matching lower bound and not a resolution
of the main extremal question.  See `FORWARD_GRAY_ROW_LIFT_CEILING.md` and
`verify_forward_gray_row_lift.py` for the exact proof and integer receipt.

Date: 2026-10-02. Status: research draft; not a new published version.
Baseline: TA-TR-2026-22 v1.0, DOI [10.5281/zenodo.23103274](https://doi.org/10.5281/zenodo.23103274).
This note strengthens its general lower-bound constant and rules out a particular concentration route. The constant-density problem remains open.

## 1. Definitions and inherited construction

Put \(Q_n=\{0,1\}^n\), \(N=2^n\), with coordinate 0 least significant.
A rank \(\rho:Q_n\to\{0,\ldots,N-1\}\) is prefix-separable if each nonempty proper initial rank segment is strictly separable from its complement by an affine functional, with different functionals allowed for different segments.
For a permutation \(p\) of distinct ranks, let
\[
 R(p)=1+\sum_{i=1}^{N-2}\mathbf1\{(p_{i+1}-p_i)(p_{i+2}-p_{i+1})<0\}.
\]
Thus adjacent monotone runs share their turning vertex, and edges belong to exactly one run.
A generic additive sweep \(\pi_w\) lists vertices by increasing \(w\cdot x\), with no ties and no restriction on the signs of \(w\).
Define
\[
 RLC(\rho)=\min_{w\ {\rm generic}}R(\rho\circ\pi_w),
 \qquad M_n=\max_{\rho\ {\rm prefix\text{-}separable}}RLC(\rho).
\]

Use exactly the balanced coordinate tree of v1.0: depth \(n\), split the highest remaining coordinate first, fixed leaf order \(0,\ldots,N-1\). At every internal node \(u\), an independent fair sign \(\xi_u\in\{-1,1\}\) says whether to traverse the 0-child first (\(+1\)) or the 1-child first (\(-1\)). The traversal rank is \(\rho_\xi\).

Every realization is prefix-separable. For completeness, for the first excluded leaf \(z\), and the node \(u_j(z)\) that splits coordinate \(j\) on its path, set
\[
 L_z(x)=\sum_{j=0}^{n-1}3^j\xi_{u_j(z)}(x_j-z_j).
\]
At the highest differing coordinate \(j\), the term of magnitude \(3^j\) dominates the total smaller-coordinate magnitude \((3^j-1)/2\). A leaf earlier than \(z\) has negative value, at most \(-1\); a later leaf has positive value, at least \(1\); \(z\) itself has value 0. Threshold \(-1/2\) strictly separates the prefix.

Tree representations, the LCA comparison rule, alternating runs, and the arrangement bound below are inherited tools, not new inventions of this note. There is no Gray-code assumption anywhere in the arguments.

## 2. New application of a known read-k theorem

Fix any leaf permutation \(\pi=(x_1,\ldots,x_N)\), even one not realizable by an additive sweep. Let \(u_i\) be the lowest common ancestor of \(x_i,x_{i+1}\). Let \(\eta_i=+1\) if this edge goes from its 0-child to its 1-child, and \(-1\) otherwise. Then
\[
 s_i=\operatorname{sgn}(\rho_\xi(x_{i+1})-\rho_\xi(x_i))
     =\eta_i\xi_{u_i}.
\]
Write \(m_u=\#\{i:u_i=u\}\), \(J=\#\{i:u_i=u_{i+1}\}\).
If two consecutive labels equal \(u\), the middle vertex lies in one child and both other vertices in the other child. Hence the two \(\eta\)'s are opposite and a turn is forced.
If the labels differ, the turn indicator depends on two independent fair spins and has mean \(1/2\).

We use the established read-k concentration theorem of Gavinsky, Lovett, Saks and Srinivasan (GLSS), Theorem 1.1 of [arXiv:1205.1478](https://arxiv.org/pdf/1205.1478), submitted 25 April 2012; [ECCC TR12-051](https://eccc.weizmann.ac.il/report/2012/051/). If Boolean functions \(Y_1,\ldots,Y_\ell\) of independent inputs read every input at most \(d\) times, their average marginal is \(p\), and \(q<p\), then
\[
 \Pr\{\textstyle\sum_iY_i\le q\ell\}
 \le \exp[-(\ell/d)D(q\Vert p)],
 \quad
 D(q\Vert p)=q\log(q/p)+(1-q)\log((1-q)/(1-p)).
\]
This theorem is prior work. The new step here is its quantitative application to the sweep-dependent turn functions and the extremal lower bound.

### Proposition 1: the sweep-specific read-degree bound

Delete the \(J\) forced turn indicators. Let \(\ell=N-2-J\), and let
\[
 d_\pi=\max_u\#\{i:u_i\ne u_{i+1},\
                         u\in\{u_i,u_{i+1}\}\}.
\]
The remaining \(\ell\) indicators are a read-\(d_\pi\) family, all of marginal \(1/2\). Also \(d_\pi\le2\max_um_u\).

If \(K-1<J\), then \(\Pr(R\le K)=0\). If \(\ell>0\) and
\(0\le t=K-1-J<\ell/2\), then
\[
 \boxed{\Pr(R(\rho_\xi\circ\pi)\le K)
 \le \exp[-(\ell/d_\pi)D(t/\ell\Vert1/2)].} \tag{1}
\]
If \(\ell=0\), the run count is deterministically \(N-1\).
If \(t\ge\ell/2\), the useful lower-tail assertion is replaced by the trivial probability bound 1.

Proof: each nonforced indicator uses exactly its two displayed node signs. A fixed occurrence of \(u\) in the comparison-label word is adjacent to at most two turn positions, proving the read-degree inequality. The identity \(R=1+J+\sum Y_i\) and the GLSS theorem give (1). End of proof.

### Proposition 2: a uniform bound suitable for the union argument

For \(n\ge2\) and any integer \(1\le K<N/2\),
\[
 \boxed{\Pr(R(\rho_\xi\circ\pi)\le K)
 \le
 \exp\left[-\frac{N-2}{2K}
       D\left(\frac{K-1}{N-2}\Big\Vert\frac12\right)\right].} \tag{2}
\]

Proof: first retain the deterministic multiplicity dichotomy from v1.0. In a monotone rank run, the two child subtrees of any node occupy ordered disjoint rank intervals, so their split can be crossed by a comparison edge at most once. Therefore \(R\ge m_u\) for all \(u\). If some \(m_u>K\), the probability is zero. Otherwise each spin is read by at most \(2m_u\le2K\) of all \(N-2\) turn indicators. Forced indicators are constants, require no inputs, and have marginal 1; other indicators have marginal \(1/2\). Thus their average marginal \(p\ge1/2\). Put \(q=(K-1)/(N-2)<1/2\). For \(p<1\),
\(\partial D(q\Vert p)/\partial p=(p-q)/(p(1-p))\ge0\).
The GLSS bound with read degree \(2K\) is consequently no larger than the right side of (2). If \(p=1\), the event is impossible. End of proof.

Crucially, \(m_u\) and the read bound depend only on the fixed permutation, not on the random event \(R\le K\). No conditioning on a low-run event has been used.

### Theorem 3: strengthened general constant

All logarithms are natural. One has
\[
 \boxed{\liminf_{n\to\infty}\frac{n^2 M_n}{2^n}
          \ge \frac{\log2}{2\log3}
          =0.3154648767857287\ldots.} \tag{3}
\]
This improves the v1.0 coefficient \(1/(8\log3)\) by the factor \(4\log2=2.772588722\ldots\).

Proof: score equalities have the \((3^n-1)/2=:H_n\) distinct central hyperplane normals in \(\{-1,0,1\}^n\), modulo overall sign. The number of different generic sweeps is at most
\[
 S_n=2\sum_{j=0}^{n-1}\binom{H_n-1}{j},
 \qquad\log S_n\le(\log3)n^2+O(n).
\]
Fix \(0<c<\log2/(2\log3)\), set \(K=\lfloor cN/n^2\rfloor\). For all sufficiently large \(n\), \(1\le K<N/2\). The argument of \(D\) in (2) tends to zero; with \(D(0\Vert1/2)=\log2\), its exponent is
\[
 \frac{N-2}{2K}D\left(\frac{K-1}{N-2}\Vert\frac12\right)
 =\left(\frac{\log2}{2c}+o(1)\right)n^2.
\]
Union bounding (2) over all sweeps gives failure probability at most
\[
 \exp\left[\left(\log3-\frac{\log2}{2c}+o(1)\right)n^2\right]\longrightarrow0.
\]
Some tree orientation therefore has every sweep's run count greater than \(K\); all its prefixes are separable. Let \(c\) increase to the displayed coefficient. End of proof.

This is an improvement of the leading coefficient, not of the asymptotic order. It establishes neither \(M_n\ge c_0N\) nor the exact optimal coefficient.

## 3. Exact rational certificates for the concentration application

For the family of \(\ell\) fair nonforced turn indicators of read degree \(d\), and integer \(0\le t<\ell/2\), equation (1) is equivalent to
\[
 P^d\le ((1+a)/2)^\ell a^{-t},
 \qquad a=\frac{t}{\ell-t}\quad(t>0).
\]
At \(t=0\), interpret this as \(P^d\le2^{-\ell}\).
This follows by substituting the minimizing Chernoff parameter; no separate unproved moment inequality is needed for the checks. For the uniform bound (2), take \(\ell=N-2\), \(t=K-1\), \(d=2K\).
An arbitrary rational \(0<a<1\) gives a weaker valid bound because the displayed expression is minimized at \(t/(\ell-t)\).

The verifier constructs traversal ranks independently from the LCA formula, enumerates the actual probability \(P\) as a rational number, and tests these power inequalities with exact rational arithmetic.

Writing \(a=A/B\), a finite sufficient certificate for existence of a prefix-separable rank with \(RLC>K\) is the integer inequality
\[
 S_n^{2K}(A+B)^{N-2}B^{K-1}
 <
 (2B)^{N-2}A^{K-1}. \tag{4}
\]
Indeed it says the union bound, raised to its positive integer power \(2K\), is less than 1.
The attached receipt certifies (4) for:
- \(n=12,\ K=11,\ a=5/2042\), implying \(M_{12}\ge12\);
- \(n=16,\ K=98,\ a=97/65437\), implying \(M_{16}\ge99\).

These finite claims are conservative existence certificates, not exact values or explicit witness ranks. They are not the proof of (3).

## 4. An all-dimensional interleaving identity

Fix integers \(1\le d\le n\); put \(k=2^d\), \(L=2^{n-d}\).
Write a leaf as \(x=(z,y)\), with \(z\) its top \(d\) coordinates and \(y\) its lower \(n-d\) coordinates, both in integer binary order. The top \(d\) levels of the tree define a rank \(\sigma\) of the \(k\) subtrees. The full ranks in subtree \(z\) are precisely
\[
 \{\sigma(z)L,\ldots,(\sigma(z)+1)L-1\}.
\]

For any permutation \(\tau=(z_1,\ldots,z_k)\), consider the row sweep
\[
 (z_1,0),\ldots,(z_k,0),\
 (z_1,1),\ldots,(z_k,1),\ \ldots,\
 (z_1,L-1),\ldots,(z_k,L-1).
\]
If \(\tau\) is a generic additive sweep on \(Q_d\), this is a generic additive sweep on \(Q_n\). Namely, for top weights \(v\), choose \(A>\sum_h|v_h|\), and lower weights \(A2^j\). The score is \(Ay+v\cdot z\), its row intervals are disjoint, and every within-row score is distinct. There is no positivity assumption on \(v\).

Let \(a_1,\ldots,a_{k-1}\) be the sign word of \(\sigma\circ\tau\),
\(r=R(\sigma\circ\tau)\), and
\(b=-\operatorname{sgn}(\sigma(z_k)-\sigma(z_1))\).
Every row has the identical comparison sign word \(a\), and every row boundary has sign \(b\), because it goes between two different rank intervals. The full word is
\(a,b,a,b,\ldots,b,a\).
It follows, exactly and independently of every lower subtree orientation, that
\[
 \boxed{R_{\rm row}=
 1+L(r-1)+(L-1)
       \big(\mathbf1\{a_{k-1}\ne b\}+\mathbf1\{b\ne a_1\}\big).} \tag{5}
\]
In particular
\[
 R_{\rm row}\le L(r+1)-1,\qquad
 \boxed{RLC(\rho_\xi)\le2^{n-d}(RLC(\sigma)+1)-1.} \tag{6}
\]
The rank \(\sigma\) belongs to the same balanced-tree family in dimension \(d\).

Equation (6) is an upper bound for this particular family; it is not an upper bound for all prefix-separable ranks, and does not disprove the constant-density target.

## 5. A tail obstruction: why one proposed route cannot work

For the fixed row sweep with \(\tau=(0,1,\ldots,k-1)\), choose integer weights
\[
 w_j=k2^j\quad(0\le j<n-d),\qquad
 w_{n-d+h}=2^h\quad(0\le h<d).
\]
The score is \(ky+z\), so the sweep is generic for every \(n\ge d\).

On the event that all \(k-1\) signs in the top \(d\) levels are \(+1\), \(\sigma(z)=z\). All within-row comparisons are positive, all row boundaries negative, and (5) yields \(R=2L-1\). When all those signs are \(-1\), the top traversal is reversed: \(\sigma(z)=k-1-z\). The same run count holds with all signs reversed. These disjoint events have total probability \(2^{-(k-2)}\); all remaining tree signs are unrestricted. Thus
\[
 \boxed{\Pr(R(\rho_\xi\circ\pi_{\rm row})\le2N/k-1)
          \ge2^{-(k-2)}.} \tag{7}
\]

For any fixed \(c_0>0\), choose a fixed power of two \(k\ge2/c_0\). For all \(n\ge\log_2k\), the threshold in (7) is strictly below \(c_0N\), yet its probability is bounded below by a positive constant independent of \(n\). Therefore the unconditioned fair balanced-tree model cannot satisfy a uniform estimate
\[
 \Pr(R(\rho_\xi\circ\pi)\le c_0N)\le\exp(-aN)
\]
for all additive sweeps and all sufficiently large \(n\), for any \(a>0\). It cannot even make \(RLC\ge c_0N\) hold with probability tending to 1. This leaves open a positive probability of success and leaves open existence of exceptional good orientations.

More generally, at \(K=2N/k-1\), the lower tail in (7) has
\[
 -\log\Pr(R\le K)\le (k-2)\log2,\qquad
 N/K=\frac{k}{2-k/N}\in[k/2,k].
\]
Thus this family of fixed sweeps exhibits the \(N/K\) scale. Improving the old fixed-sweep tail uniformly to a dimension-free \(\exp(-\Theta(N))\) estimate at \(K=c_0N\) is not a viable way to remove \(n^2\). This does not prove that every refined proof based on the tree family must lose \(n^2\): it only excludes the stated uniform-tail strategy.

Small illustration, not a replacement for the proof: \(d=3,n=4\), weights \((8,1,2,4)\), and all seven top signs equal give \(R=3\). The unrestricted eight lower signs generate 512 bad orientations in total, probability \(1/64\). The verifier checks the entire event.

## 6. Verification, provenance, and limitations

Run:
~~~bash
python3 verify_readk_and_interleaving.py
~~~
Dependencies: Python 3 and NumPy. There is no floating-point solver.

Actual coverage in verification.json:
- \(n=1,2,3\): all leaf permutations and all tree signs, respectively 4, 192 and 5,160,960 rank sequences. Exact probability checks test both (1) and (2) wherever applicable, and verify all deterministic empty-event cases.
- \(n=4\): 27 selected permutations, all 32,768 tree signs, 884,736 rank sequences. This is not an exhaustive sweep search in dimension 4.
- Interleaving: 12,876 identity cases. All top orientations at \(d\le3\); all top permutations at \(d\le2\); only 32 selected permutations at \(d=3\). Lower signs are sampled. In addition, 39 exact generic integer score realizations cover \(n\le10\).
- Obstruction: the entire asserted bad event at \(n\le4\), selected unrestricted lower signs at \(n=5,\ldots,10\).
- Two integer existence certificates (4).
- Zero violations. The traversal/turn enumeration digest is 379ed2b5a39991152411c95401d94385c8fdbd7319eb4a68ad05dac7ed584f37.

The code and receipt are pressure tests and reusable audit artifacts. The all-dimensional claims rest on the proofs above and the cited read-k theorem, not on enumeration.

A bookkeeping TypeError in JSON hashing of a NumPy integer was corrected by converting J to int; it did not produce or reveal a mathematical counterexample. An initially overbroad coverage comment was corrected to distinguish sampled \(d=3\) permutations from exhaustive \(d\le2\) coverage.

The new results are relative to the repository's published v1.0 and the three 2026-10-02 handoffs. The known read-k theorem was checked in its primary source. Targeted searches on prefix separability and Boolean-cube run bounds did not establish prior-art coverage of every synonymous formulation. Literature priority remains unconfirmed; in particular, the elementary sign-word identity should not be advertised as a new general permutation statistic.

## 7. Precise remaining gap and next productive route

The primary target still has neither a proof nor a counterexample:
\[
 \exists c_0>0\ \forall n\ge n_0:\ M_n\ge c_0 2^n.
\]
Theorem 3 supplies only a stronger coefficient in the same order. Deterministic explicit witness families attaining that lower bound also remain open.

A useful next step is to separate high-level macro-subtree bottlenecks from truly distributed turning constraints. Equation (6) is a necessary check on any proposed hierarchical constant-density family: every top projection must avoid low RLC at the corresponding density. A conditioned or deliberately chosen top tree might remove the events used in (7), but conditioning changes independence and does not by itself give a proof.

The missing useful statement would be either:
1. a structural decomposition of all additive sweeps showing that a deliberately protected orientation has at least \(c_0N\) turns, or
2. for a genuinely specified conditioned/randomized prefix-separable family, a simultaneously usable bad-sweep bound strong enough to beat \(\log S_n=O(n^2)\) at threshold \(c_0N\), with all conditioning dependencies accounted for.

Merely repeating McDiarmid, replacing it by another uniform fixed-sweep concentration inequality, sampling more weights, or extending the eight five-dimensional Gray cones is not enough. The failed uniform-tail route is now excluded by the all-dimensional certificate (7). Formal v1.0, its DOI, and its archived bytes remain unchanged.
