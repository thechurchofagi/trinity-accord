# A universal obstruction for finite-block tensors of balanced-tree orders

Date: 2026-10-03. Status: research draft; not a published edition.

This note supersedes the preceding \(Q_2\)-specific tensor obstruction. It proves that no ordinary tensor product with an unbounded number of finite-dimensional balanced-tree factors can have positive RLC density, even when every factor and every factor dimension may be chosen differently. The constant-density problem for general prefix-separable ranks remains open.

## 1. Mixed tree tensors

Let \(m\ge1\), let \(d_0,\ldots,d_{m-1}\ge1\), and put
\[
 n=\sum_{t=0}^{m-1}d_t,\qquad
 B_t=2^{d_t},\qquad
 P_t=\prod_{s<t}B_s.
\]
Thus \(P_0=1\) and \(P_t\) is the mixed-radix place value of factor \(t\).

For every \(t\), let
\[
 \sigma_t:Q_{d_t}\longrightarrow\{0,\ldots,B_t-1\}
\]
be an arbitrary traversal rank of a balanced coordinate tree. Different factors may use unrelated dimensions and unrelated node orientations. On the block product \(Q_n=\prod_tQ_{d_t}\), define
\[
 \rho(x)=\sum_{t=0}^{m-1}P_t\,\sigma_t(x^{(t)}). \tag{13}
\]
This is a bijective rank. It is itself a balanced-tree traversal: traverse the most significant factor first in the order \(\sigma_{m-1}\), then the next factor, and so on. Consequently every proper nonempty rank prefix is strictly affine-separable by the established tree-prefix separator.

The construction includes homogeneous powers of one seed, inhomogeneous seed choices at every block level, and unequal block dimensions. It does not include a seed that changes separately at different nodes according to the previously visited block prefix.

## 2. The root-bit sweep

In factor \(t\), call the first coordinate split by its tree the root bit. Reflect that bit if necessary, and denote the reflected bit by \(A_t\), so that
\[
 A_t=0\Longrightarrow 0\le\sigma_t<B_t/2,\qquad
 A_t=1\Longrightarrow B_t/2\le\sigma_t<B_t. \tag{14}
\]
The remaining \(d_t-1\) coordinates of that factor are called outer bits.

Consider the signed lexicographic additive sweep with:
1. all \(n-m\) outer bits first, in any fixed order;
2. the root bits \(A_{m-1},A_{m-2},\ldots,A_0\) last, from the most significant factor to the least.

It has an explicit strict integer realization. Give the displayed coordinates successive magnitudes
\[
 2^{n-1},2^{n-2},\ldots,1,
\]
and give an original root coordinate a negative weight exactly when its definition as \(A_t\) uses a reflection. Every score is distinct, because each magnitude is greater than the sum of all later magnitudes.

The sweep consists of
\[
 H=2^{n-m}
\]
consecutive outer blocks, one per assignment of the outer bits. Inside each outer block, \((A_{m-1},\ldots,A_0)\) counts from 0 to \(2^m-1\).

## 3. Exact run formula

Fix the outer bits. Suppose the inner binary counter carries at factor \(q\): \(A_q\) changes from 0 to 1 and \(A_t\) changes from 1 to 0 for every \(t<q\). By (14), the rank digit at \(q\) rises by at least one. Every lower mixed-radix digit can fall by at most \(B_t-1\). Therefore
\[
 \Delta\rho
 \ge P_q-\sum_{t<q}P_t(B_t-1)
 =P_q-(P_q-1)=1. \tag{15}
\]
The telescoping equality is the usual mixed-radix identity. Thus the rank sequence is strictly increasing inside every outer block, independently of every non-root orientation in every factor.

At a boundary between outer blocks, the preceding point has \(A_t=1\) in every factor and the next point has \(A_t=0\) in every factor. By (14), every preceding mixed-radix digit lies in its upper half and every next digit lies in its lower half. Hence the rank strictly decreases at every outer-block boundary.

The entire comparison-sign word is consequently
\[
 \underbrace{+\cdots+}_{2^m-1},-,
 \underbrace{+\cdots+}_{2^m-1},-,\ldots,-,
 \underbrace{+\cdots+}_{2^m-1}.
\]
There are \(H-1\) isolated negative boundary signs and two turns per boundary.

### Theorem 5: universal finite-block tensor obstruction

Every rank (13) satisfies
\[
 \boxed{RLC(\rho)\le 2^{\,n-m+1}-1.} \tag{16}
\]
Indeed the displayed generic additive sweep has exactly that many monotone runs.

Consequently,
\[
 \boxed{\frac{RLC(\rho)}{2^n}\le 2^{1-m}-2^{-n}.} \tag{17}
\]
For every sequence of such tensor constructions with the number of factors \(m\to\infty\), the RLC density tends to zero.

If all factor dimensions are bounded by a fixed \(D\), then \(m\ge n/D\), and
\[
 RLC(\rho)\le 2^{\,n-n/D+1}-1=o(2^n). \tag{18}
\]
Thus no recursion obtained by tensoring bounded-dimensional balanced-tree seeds can prove \(M_n\ge c2^n\). Local optimality of the seeds, varying the seed with the block level, and increasing the finite menu of seeds do not repair the obstruction.

This theorem is an upper bound for this specified recursive family. It is not an upper bound for arbitrary balanced-tree orientations, because in a general tree the orientations inside a later coordinate block may depend on all earlier prefix bits. It is also not an upper bound for arbitrary prefix-separable ranks.

## 4. Consequences for the research program

The ordinary finite-seed tensor route is now closed, not merely the optimal-\(Q_2\) case. Exhaustive \(Q_3\) classification, performed while finding the general proof, gives
\[
 \max_{\rho\ {\rm balanced\ tree\ on}\ Q_3}RLC(\rho)=4,
\]
with eight maximizers among 128 tree orientations. But tensoring those maximizers is already covered by (16); a separate \(Q_3\) transfer-matrix analysis would add no generality for ordinary block tensors.

The next meaningful recursive route must break at least one hypothesis of (13):
- allow the seed used below a block to depend on the full higher-block prefix;
- leave the fixed balanced-tree family while preserving every-prefix affine separation;
- or avoid coordinate-block tensor structure altogether.

The first option is the closest continuation. It produces a finite-state tree substitution rather than a simple tensor. A valid positive result would need a lower bound for every additive sweep of every power. A valid negative result may come from extending the root-bit sweep to a synchronizing state cycle. Sampling weights cannot decide either statement.

## 5. Verification

Run:
~~~bash
python3 verify_finite_block_tensor_obstruction.py
~~~
The verifier uses Python integer arithmetic only. It independently constructs each factor rank by recursive tree traversal, constructs the strict integer score vector, and compares the actual run count with (16).

Coverage:
- a complete Q3 additive-order classification using the two chambers (c>a+b) and (c<a+b), all coordinate permutations and all coordinate reflections: 96 orders, all 128 tree orientations, maximum RLC 4 attained by eight codes;
- every orientation of \(m=1,2,3,4\) two-dimensional factors;
- every orientation for dimension patterns \((3,2)\), \((2,3)\), and \((3,3)\);
- 23,112 exhaustive mixed tensors in total;
- 383 seeded random mixed tensors with one to five factors, individual dimensions at most six, and total dimension at most fifteen;
- zero violations.

The verifier is a pressure test, not the all-dimensional proof. The proof is the root-half property (14), the exact telescoping inequality (15), and the boundary comparison.

## 6. Prior-art scope

Boolean term orders, lexicographic products, tree representations of separable permutations, and alternating runs are established notions and must not be relabeled as new. A targeted search did not locate the quantitative mixed-tree-tensor bound (16), but the search was not an exhaustive forward-citation review. The defensible research increment is the explicit obstruction theorem and its proof, subject to later priority audit.
