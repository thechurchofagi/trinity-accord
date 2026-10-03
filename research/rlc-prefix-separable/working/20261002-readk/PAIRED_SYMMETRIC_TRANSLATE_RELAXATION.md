# Symmetric equal translations are still an insufficient scan relaxation

Research draft, 2026-10-03. Published v1.0 is unchanged. The main
constant-density lower bound remains open.

## 1. Precise failed route

The selected normalized five-dimensional paired rank
\(\sigma(x)=\rho_{5,2}(x)\) has cyclic complexity at least 12 on every
generic signed additive scan, as independently certified in checkpoint 59.
One prospective extension route was to use only the following consequences
of a genuine six-dimensional scan:

* its upper projection consists of two copies of the same genuine
  five-dimensional additive order;
* the copies are sorted using scores \(s_i\) and \(s_i+a\), with the same
  positive translation \(a\) for every vertex;
* \(s_i+s_{31-i}\) is constant and the complete vertex order is antipodal;
* the complete order extends coordinatewise inclusion.

These conditions do **not** imply a conditional cyclic mean of 24 for this
parent. We give an exact witness with conditional mean 18, independent of
every fresh bottom label. The full order is not additive on the cube. This
rejects the stated relaxation, not the actual additive extension conjecture
and not the original existential lower-bound target.

## 2. An exact dynamic programming relaxation

Let \(M\) be even. List a centrally symmetric upper vertex order as
\(x_0,\ldots,x_{M-1}\), where \(x_{M-1-i}=\bar x_i\), and write
\(r_i=\sigma(x_i)\). A merge of the first and second copies is encoded by
a word of zeros and ones. The indices consumed in each chain increase.
Because \(a>0\), the first chain always has consumed at least as many
vertices as the second. Antipodality determines the second half as the
reverse complement of the first half. Not every such shuffle is an equal
translation of some scores; allowing all these shuffles is a relaxation.

A bottom-fresh comparison occurs only when consecutive projected indices
coincide. Two such comparisons cannot be adjacent, since that would repeat
a full vertex. Its two adjacent cyclic turns have total expectation one.
All other comparisons have the fixed sign of their upper-rank comparison.
Consequently the exact conditional cyclic mean is
\[
 \mu=L+F,
\]
where \(L\) counts fresh comparisons and \(F\) counts sign changes between
two adjacent fixed comparisons. This identity is inherited from checkpoint
57; it is not a new permutation statistic.

The DP state after consuming a first-half prefix is
\((i,j,\ell,s,t)\): the two consumed chain counts, last chain, last forward
comparison sign, and sign of its reflected reversed comparison. The special
sign 2 denotes a fresh comparison. The initial comparison is the closing
edge \(\bar x_0\to x_0\), with the same reflected sign. Extending the prefix
adds both fixed-turn indicators, one on each half, and adds two when the
new edge is fresh. At length \(M\), add the two turns adjacent to the central
edge \(x\to\bar x\). The reflected second half has already been charged.
Thus the recurrence charges every term of \(L+F\) exactly once. Minimizing
over states is valid because all future costs depend only on the stated
state. There are \(O(M^2)\) states and a constant number of transitions per
state; a stored attaining path supplies a direct independent check.

For numeric upper vertex order and parent \(\rho_{5,2}\), this recurrence
gives minimum 18. This is a finite exact DP result, not an all-dimensional
statement. Section 3 attains it with symmetric integer scores, so the
minimum is also exactly 18 within the smaller equal-translation class
having this fixed upper order. Small DP instances are checked independently
by enumerating every admissible half-word; see section 5.

## 3. Integer equal-translation witness

Set \(a=32\). The first 16 upper scores are
\[
(-123,-121,-95,-93,-87,-67,-65,-59,
 -45,-43,-41,-39,-37,-15,-3,-1).
\]
Set \(s_{31-i}=-s_i\). These scores increase strictly. Assign the full
vertex \(2i+b\) the score \(s_i+32b\). All 64 scores are distinct integers.
They produce exactly the DP attaining path and satisfy
\(S(x)+S(\bar x)=32\). The full order is coordinatewise increasing because
numeric upper indices and the bottom bit are increasing in each coordinate.
Its upper order is genuinely additive: the binary weights
\((1,2,4,8,16)\) produce that order. The scores \(s_i\) themselves are not
claimed to be additive on the upper cube.

No consecutive full vertices, including the cyclic closing pair, differ
only in their lowest bit. Therefore \(L=0\), every comparison is decided by
the retained upper parent, and every one of the \(2^{16}=65536\) bottom
assignments has \(C=18\). The parent on the numeric upper order has \(C=16\),
while its minimum over all signed additive upper orders is 12. The failed
proposed bound is therefore \(18<2\cdot12\); it is not merely a comparison
with an arbitrarily high pointwise parent value.

## 4. Two integer inequalities exclude actual cube additivity

The full order contains \(4\prec1\) at positions 2 and 4, and
\(35\prec38\) at positions 36 and 37 (zero-based). In binary coordinates,
\(34\) is disjoint from both 4 and 1, and
\(4\lor34=38\), \(1\lor34=35\). A genuine additive score would require
simultaneously
\[
 w_0-w_2>0,\qquad w_2-w_0>0.
\]
Adding these inequalities gives \(0>0\). This is an exact integer
infeasibility certificate, independent of LP tolerances or the signs of
the weights. It is the known common-addition requirement for Boolean term
orders. The new contribution here is the explicit selected-parent
equal-translation relaxation obstruction, not that requirement itself.

The same witness explains the geometric omission: a repeated cube
difference must have the same gap. The relaxation assigned different gaps
to two copies of that difference. Antipodal symmetry and equal translation
between the two full layers do not restore upper-cube difference equality.

## 5. Audit and remaining gap

`verify_symmetric_translate_relaxation.py` uses integer comparisons only.
It checks the DP against direct exhaustive central half-word enumeration
on 786 signed upper-order/paired-parent contexts through dimension three,
covering 53860 direct paths. It then verifies the displayed scores,
inclusion monotonicity, antipodality, every fresh assignment, and the two
canceling required difference vectors. Its certificate retains every score,
vertex, DP layer, parameter, digest and actual scope. Exploratory LP was used
to discover integer scores, but no final claim depends on its output.

The precise next gap is the selected-parent conditional mean on **genuine**
cube scans. For parent mask2, mean at least 24 in dimension six remains
unproved beyond the earlier pressure tests. A useful next computation must
enforce repeated-difference consistency and actual linear feasibility,
rather than treating every symmetric equal-translation merge as genuine.
Even proving the finite statement would not by itself yield a positive
all-dimensional density: the selected-parent losses and seed must satisfy
the existing controlled-loss reduction.
