# A linear-size face obstruction for the forward Gray proof route

Date: 2026-10-03. Status: unpublished, all-dimensional route exclusion.
The constant-density RLC target remains OPEN. The permutations in this
note are not additive sweeps and do not give an upper bound for M_n.

This strengthens FACE_LOCAL_COHERENCE_OBSTRUCTION.md at commit
1fee6a7895331a001148463a69d27c6d8af0b84a. It uses precisely that note's
seeded greedy weights and centrally symmetric bucket refinement. The
new step is an entropy bound on the forbidden signed sums; the earlier
polynomial estimate loses too much when the face dimension grows.
The entropy estimate is elementary and standard. Historical priority of
this particular Gray obstruction is not asserted.

## 1. Theorem

Write H_2(a)=-a log_2(a)-(1-a)log_2(1-a). Let a_0 be the unique root
in (0,1/2) of H_2(a)+a=1 (numerically about 0.2270921952).
For every fixed 0<a<a_0, all sufficiently large n admit a positive,
strictly increasing integer vector w and a permutation p of Q_n with:

- On EVERY coordinate face of dimension at most floor(a*n), including
  every translate, the restriction of p is the generic additive order
  induced by the SAME w.
- Every strict comparison of the weak global score w dot x is respected.
- The order has central complement symmetry.
- No generic real additive vector, with any signs, induces p. Two
  opposite strict rows of support floor(a*n)+1 prove this.
- For gamma_n(x)=x XOR (x >> 1),

\[
 R(\gamma_n\circ p)=C(\gamma_n\circ p)
 =O_a\left(n^2 2^{[H_2(a)+a]n}\right)=o(2^n).
 \tag{1}
\]

The number a_0 describes the sufficient range of this construction.
It is not asserted to be an optimal threshold for local consistency.

In particular, all faces of dimension at most floor(n/5) can pass while

\[
 R=C=O\left(n^2 2^{(\log_2 5-7/5)n}\right),\qquad
 \log_2 5-7/5\approx0.9219280949<1.
 \tag{2}
\]

Thus the obstruction reaches a fixed positive fraction of the ambient
dimension, rather than only a fixed face size or o(n/log n).

## 2. Construction and all-dimensional proof

Set k=floor(a*n), with n large enough that k>=2 and n>=k+3. Start with

\[
 (w_0,\ldots,w_k)=(1,2,\ldots,2^{k-1},2^k-1).
\]

There is no nonzero {-1,0,1} relation of support at most k: any equality
using the last seed entry requires all k powers of two. Having chosen
m entries, choose the least integer w_m>w_(m-1) outside the signed sums
of previous entries with support at most k-1. This preserves absence of
zero relations of support at most k. The number of forbidden values is
at most

\[
 B_m=\sum_{r=0}^{k-1}2^r\binom mr.
\]

Consequently w_m<=w_(m-1)+B_m+1. With T=sum w_j and B=B_(n-1), the
monotonicity of B_m in m gives the convenient conservative bound

\[
 T\le n2^k+n^2(B+1).
 \tag{3}
\]

For each integer score t<T/2, order its bucket by increasing gamma_n and
concatenate those buckets by score, giving H. If a middle bucket exists,
list its top-bit-zero entries by increasing gamma, followed by their
reverse complements, giving Z. Set

\[
 p=H,\ Z,\ \overline{\operatorname{reverse}(H)}.
\]

The detailed proof in the preceding note establishes, without any
assumption about the size of k, that this construction respects every
strict primary-score comparison and is consistent with w on every
k-face. It is centrally symmetric, and

\[
 R(\gamma_n\circ p)=C(\gamma_n\circ p)\le4(T+1).
 \tag{4}
\]

For completeness, a bucket below T/2 has one increasing Gray block.
The identity gamma_n(complement x)=gamma_n(x) XOR 2^(n-1) makes each
mirrored bucket have at most three monotone runs; the middle bucket has
at most two. There are at most T+1 buckets. Joining buckets adds at most
two turns per join, which yields C<=4(T+1). The initial vertices 0,1 and
the final reverse complements show R=C directly.

Nonadditivity also holds for variable k. Put u=2^k-1, v=2^k and
z=2^(k+1). The pairs (u,v) and (u OR z,v OR z) are tied in primary score.
Both are below T/2 because at least one further weight exceeds w_(k+1).
Their increasing Gray refinements order u before v and v OR z before
u OR z. Any inducing additive vector b would require simultaneously

\[
 b_k-\sum_{j<k}b_j>0,\qquad
 \sum_{j<k}b_j-b_k>0.
\]

Adding the two rows gives 0>0. This is an exact certificate and also
pinpoints the failure of global disjoint-translation consistency.

It remains to estimate (3). Put m=n-1. Since k-1<=a*m and a<1/2,

\[
 B\le 2^{am}\sum_{r\le am}\binom mr
   \le 2^{m[H_2(a)+a]}.
 \tag{5}
\]

Here is a self-contained justification of the second inequality. For
r<=a*m, the binomial probability factor a^r(1-a)^(m-r) is at least
2^(-m H_2(a)); it decreases as r increases, and that expression is its
value at the real index a*m. Sum the corresponding binomial probability
terms and use their total at most one. Floors only shrink the sum.

Equations (3)--(5), with k<=a*n and H_2(a)>0, prove (1). The derivative
of H_2(a)+a is log_2((1-a)/a)+1>0 on (0,1/2). Its endpoint values are
0 and 3/2, so a_0 exists uniquely. No numerical root calculation is
needed for the explicit a=1/5 case: its exponent is log_2(5)-7/5, and
being below one is exactly the integer inequality 5^5<2^12, or
3125<4096. This completes the all-dimensional proof.

## 3. What this excludes

The algebraic reflection graph identity for a centrally symmetric p is

\[
 \min_{\text{reflections}} C=(2^n+D-E_*)/2.
\]

For this nonadditive p, the identity reflection and (4) give
E_*-D>=2^n-8(T+1)=2^n-o(2^n). Therefore complement symmetry, strict
weak-score comparisons, and agreement with one common vector on all
faces up to any fixed fraction a<a_0 cannot imply a uniform positive
net-energy deficit. Those premises alone would incorrectly include p.

A proof may still use these premises together with a further condition
that excludes p. In particular full global translation consistency
excludes the two-row certificate immediately. The theorem neither
refutes the positive Gray-density conjecture nor proves it. The companion COHERENT_BUCKET_CANCELLATION.md proves a quantitative
turn cost for one genuine refinement: numerical tie breaking gives
R >= 2^(n-1)-T-2 for ALL sign reflections. This covers the same seeded
vectors in the present entropy range. General coherent secondary vectors
and full additive chamber coverage remain open.

## 4. Reproduction and exploratory pressure

Run python3 verify_linear_face_obstruction.py. The verifier checks five
seeded greedy constructions, all 102,777 signed relation tests through
support six in those cases, the opposite-row certificates, and the
improved weight bound. Eight exact arithmetic checks reach n=2000.
For a=1/5 the entropy inequality is tested using integers as
B^5 * 128^(n-1) <= 3125^(n-1), without floating point. Floating point
logarithms in the receipt are explicitly approximate display values.
These checks support the proof and are not its all-dimensional coverage.

A separate exploratory probe perturbed small integer weights by signed
powers of two to resolve every subset-sum tie exactly, with the smallest
magnitude at the highest Gray coordinate. It tested 5,000 draws in each
of dimensions 4 through 10 (27,020 distinct positive orders in total).
No violation of W<=D or E_*<=D appeared. This strengthens pressure on
that subclass conjecture but proves neither inequality; random draws,
even near ties, are not complete chamber coverage. The standalone probe
and its captured receipt are retained separately.
