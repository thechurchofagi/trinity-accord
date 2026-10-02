# A square-root obstruction for tensoring optimal \(Q_2\) tree orders

Date: 2026-10-03. Status: research draft; not a published edition.

This note tests a natural response to the macro-subtree obstruction in the preceding read-degree note: choose a finite prefix-separable seed with the best possible RLC in its dimension, and repeat that seed in every coordinate block. The result below rules out the entire family obtained by tensoring the optimal two-dimensional balanced-tree seeds. It does not rule out larger seeds, prefix-dependent substitutions, non-tree prefix-separable ranks, or the main constant-density conjecture.

## 1. The four optimal two-dimensional seeds

Use bit order \(x=(a,b)\), where \(a=x_1\) is the higher tree coordinate and \(b=x_0\). A balanced depth-two tree has three orientation signs, hence eight traversal ranks. Exact enumeration of all eight generic additive orders of \(Q_2\) gives:
\[
 \max_{\rho\ {\rm balanced\ tree}}RLC(\rho)=2.
\]
Exactly four tree ranks attain 2. Take the representative
\[
 \phi(a,b)=2a+(1\oplus a\oplus b),
 \qquad [\phi(0),\phi(1),\phi(2),\phi(3)]=[1,0,2,3].
\]
The other three optimal ranks, and no others, have the form
\[
 \phi_{e,c}(a,b)=
 \begin{cases}
  \phi(a,b\oplus e),&c=0,\\
  3-\phi(a,b\oplus e),&c=1,
 \end{cases}
 \qquad(e,c)\in\{0,1\}^2. \tag{8}
\]
Here \(e\) is a reflection of the low input coordinate and \(c\) reverses the four rank values. Direct enumeration establishing both assertions is included in the verifier. The terminology and traversal representation are inherited; the finite classification is used only as the premise of the all-dimensional statement below.

## 2. Block tensor construction

For arbitrary choices \((e_t,c_t)\in\{0,1\}^2\), \(0\le t<m\), define a rank on \(Q_{2m}\) by putting one optimal \(Q_2\) digit in each base-four place:
\[
 \rho(x)=\sum_{t=0}^{m-1}4^t\,
 \phi_{e_t,c_t}(a_t,b_t),
 \quad a_t=x_{2t+1},\quad b_t=x_{2t}. \tag{9}
\]
This includes homogeneous powers of any one optimal seed and inhomogeneous choices of a different optimal seed at every coordinate-pair level. It is a balanced-tree traversal rank: at each successive pair of tree levels use the three signs of the selected seed. Therefore every proper nonempty rank prefix is strictly affine-separable by the established tree separator. No claim about arbitrary prefix-dependent seed choices is made.

## 3. The explicit bad sweep

Define reflected variables
\[
 B_t=b_t\oplus e_t,\qquad A_t=a_t\oplus c_t.
\]
Use the signed lexicographic additive sweep whose variables, from most to least significant, are
\[
 B_0,B_1,\ldots,B_{m-1}, A_{m-1},A_{m-2},\ldots,A_0. \tag{10}
\]
This is realized by integer weights of magnitudes
\(2^{2m-1},2^{2m-2},\ldots,1\), in the displayed order, giving the original coordinate a negative weight exactly when its reflected variable uses xor 1. Every score is distinct because each magnitude is larger than the sum of all following magnitudes.

The sweep has \(2^m\) consecutive outer blocks, one for each \(B=(B_0,\ldots,B_{m-1})\). Inside a block, \(A=(A_{m-1},\ldots,A_0)\) counts from 0 to \(2^m-1\).

For fixed \(B_t\), changing \(A_t\) from 0 to 1 increases the \(t\)-th base-four digit of (9) by either \(4^t\) or \(3\cdot4^t\). This statement includes \(c_t=1\), because the definition \(A_t=a_t\oplus c_t\) reverses the input at the same time as the output rank values. When binary counting in \(A\) carries at position \(q\), the rank change is at least
\[
 4^q-3\sum_{t=0}^{q-1}4^t=1>0. \tag{11}
\]
Thus the complete rank sequence inside every outer block is strictly increasing.

At a boundary between outer blocks, the preceding point has every \(A_t=1\), and the next point has every \(A_t=0\). In each base-four digit, regardless of \(B_t\), the preceding digit is 2 or 3 and the next digit is 0 or 1. Hence every boundary rank comparison is strictly decreasing.

The comparison-sign word therefore consists of \(2^m\) nonempty positive strings separated by \(2^m-1\) isolated negative signs. It has exactly \(2(2^m-1)\) turns.

### Theorem 4: square-root tensor obstruction

Every rank (9), for every sequence of optimal \(Q_2\) seeds, satisfies
\[
 \boxed{RLC(\rho)\le 2^{m+1}-1=2\sqrt{2^{2m}}-1.} \tag{12}
\]
Consequently
\[
 \frac{RLC(\rho)}{2^{2m}}\le2^{1-m}-2^{-2m}\longrightarrow0.
\]

This is an exact all-dimensional upper bound, not a sampled extrapolation. It proves that repeatedly tensoring even dimension-wise optimal \(Q_2\) balanced-tree ranks cannot establish a positive-density lower bound. The candidate fails much more strongly: an explicit signed lexicographic scan leaves only \(O(\sqrt N)\) runs.

## 4. Why this matters and what it does not prove

The preceding read-degree work showed that merely demanding nontrivial high-level orientations does not create a sufficiently strong uniform random tail. The present result addresses a different repair: install locally optimal protected blocks at every scale. At block size two, all possible optimal choices are now excluded, including inhomogeneous choices by level.

This does not show that finite-block substitution always fails. A \(Q_d\) seed for \(d\ge3\) can have a genuinely nonlinear rank digit and may not admit the monotone-inner-block mechanism used in (11). Nor does it cover a seed selected separately at each tree node according to its prefix. Therefore the precise remaining finite-seed question is:

> Does there exist a fixed \(d\ge3\), a prefix-separable seed (or a finite prefix-dependent substitution rule), and a constant \(c>0\) whose recursive ranks have RLC at least \(c2^n\) in every power?

A productive next step is to formalize the obstruction as a finite-state min-plus problem for \(Q_3\) and \(Q_4\) seeds. One must certify all generic additive scans of every power, or derive an analytic recurrence; random-weight sampling cannot prove success. Conversely, finding one explicit scan family with sublinear recurrence would rigorously eliminate a proposed seed, as (10) does here.

## 5. Exact verification

Run:
~~~bash
python3 verify_q2_tensor_obstruction.py
~~~
It uses only Python integer arithmetic.

The verifier:
- enumerates all eight generic additive orders and all eight balanced-tree ranks of \(Q_2\);
- confirms that precisely codes 2, 3, 4 and 5 have RLC 2;
- checks the four representations (8);
- exhausts all \(4^m\) inhomogeneous optimal-seed sequences for \(1\le m\le5\), a total of 1,364 tensor ranks through dimension 10;
- constructs the strict integer-weight sweep (10) and confirms exactly \(2^{m+1}-1\) runs;
- records zero violations and a deterministic digest.

These finite tests pressure-test the implementation. The all-dimensional result is the proof in Sections 2–3.

## 6. Prior-art scope

A targeted check included Maclagan's Boolean term-order framework and literature on direct/skew sums and alternating runs. It confirms that Boolean term orders, coherence, recursive permutation blocks, and alternating-run statistics are established subjects. The check did not locate the quantitative bound (12) for these four tensor seeds, but it was not an exhaustive forward-citation audit. The defensible contribution claim is therefore the explicit RLC obstruction proved here, subject to a later dedicated priority review—not the underlying notions of lexicographic product or alternating runs.
