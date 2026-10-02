# A row-lift ceiling for the forward-Gray rank

Date: 2026-10-03. Status: research note; not a published revision.
Baseline: TA-TR-2026-22 v1.0, DOI 10.5281/zenodo.23103274.

## Statement

Number coordinates from 0 (least significant) to (n-1), and define the
forward-Gray rank

\[
  \gamma_n(x)=x\mathbin\oplus(x\mathbin{\gg}1).
\]

This is the forward rank map, not the inverse map that lists the usual BRGC
vertices.  The distinction is essential.

**Theorem.**  For every (n\ge5), there is an explicit generic integer
additive sweep on (Q_n) having exactly

\[
  \boxed{10\,2^{n-5}=\frac{5}{16}2^n}
\]

monotone runs when read through (gamma_n).  Consequently

\[
  \boxed{\operatorname{RLC}(\gamma_n)\le\frac{5}{16}2^n.}
\]

Thus the forward-Gray candidate cannot have RLC density greater than
(5/16).  This does not show that its density tends to zero, and it does not
disprove the existence of a different prefix-separable family with a positive
dimension-free density.

## Explicit sweep

Put (m=n-5) and write (x=z2^m+y), where (z\in Q_5) and
(0\le y<2^m).  On the five high coordinates, ordered locally from least
to most significant, use

\[
  v=(-1,-14,-4,-12,-20).
\]

On lower coordinate (j), (0\le j<m), use weight (64\,2^j).  Hence the
full weight vector, still from least to most significant, is

\[
 (64,128,\ldots,64\,2^{m-1},-1,-14,-4,-12,-20).
\]

The 32 subset sums of (v) are distinct.  Their increasing order is

\[
\tau=(31,30,27,26,23,22,29,28,19,18,25,24,15,14,11,10,
       21,20,17,16,7,6,13,12,3,2,9,8,5,4,1,0).
\]

Every (v\)-score lies in ([-51,0]).  Therefore the score intervals
([64y-51,64y]) for consecutive values of (y) are disjoint.  The complete
sweep is exactly

\[
  (\tau_1,0),\ldots,(\tau_{32},0),
  (\tau_1,1),\ldots,(\tau_{32},1),\ldots,
  (\tau_1,2^m-1),\ldots,(\tau_{32},2^m-1),
\]

and is generic.

## Exact run count

The top five rank blocks of (gamma_n) are ordered by (gamma_5).  More
precisely, for fixed (z), all ranks of the vertices (z2^m+y) lie in the
interval

\[
  [\gamma_5(z)2^m,(\gamma_5(z)+1)2^m-1].
\]

This follows directly by applying (x\mapsto x\oplus(x\gg1)) to the high
bits.  The low rank bits may depend on the boundary bit of (z), but they do
not affect comparisons between two different top blocks.

Along one row (	au), the top-block ranks are

\[
(16,17,22,23,28,29,19,18,26,27,21,20,8,9,14,15,
 31,30,25,24,4,5,11,10,2,3,13,12,7,6,1,0).
\]

Its comparison word has 10 runs.  Let (a_1,a_{31}) be its first and last
comparison signs, and let

\[
 b=-\operatorname{sgn}(\gamma_5(\tau_{32})-gamma_5(\tau_1))
\]

be the sign of every boundary between consecutive rows.  Direct integer
comparison gives

\[
 \mathbf1\{a_{31}\ne b\}+\mathbf1\{b\ne a_1\}=1.
\]

The exact row-interleaving identity from the preceding research note now
gives, with (L=2^m),

\[
 R=1+L(10-1)+(L-1)\cdot1=10L.
\]

This proves the theorem.  Notice that no assumption about a recursively
dominant new coordinate is used: the construction is one fixed five-bit
subset-sum chamber followed by a rigorously separated row lift.

## What was and was not settled

This result is an all-dimensional upper bound for one important candidate,
not a finite-dimensional extrapolation.  It rules out any conjecture that
the forward-Gray rank itself has RLC density above (5/16), including the
previous (1/2)-density possibility left by the reflection-pairing theorem.

It does **not** prove the desired lower bound
(M_n\ge c2^n), does not prove a matching lower bound for
(gamma_n), and does not show (operatorname{RLC}(gamma_n)/2^n\to0).
The remaining forward-Gray question is whether some non-row-lift sequence of
subset-sum chambers drives the density below (5/16), perhaps to zero, or
whether every generic additive sweep retains a positive fraction of runs.

## Verification

Run `python3 verify_forward_gray_row_lift.py`.  It verifies the distinct
integer subset sums, the stated top order and rank sequence, the endpoint
penalty, the symbolic formula, and the complete explicitly weighted sweep in
every dimension (5\le n\le16).  It also searches seeded continuous weight
samples in dimensions 5 through 8 as a falsification attempt; those samples
are evidence only and are not used in the proof.

