# Exact cancellation in coherent integer-score bucket refinements

Date: 2026-10-03. Status: unpublished all-dimensional subclass theorem.
The main constant-density RLC target remains OPEN. This theorem covers a
specified family of genuine additive sweeps and all their sign reflections.
It does not cover every generic additive vector.

## 1. Statement

Let a=(a_0,...,a_(n-1)) be any positive integer vector, n>=2, N=2^n,
and let q be the number of distinct subset sums a dot x, x in Q_n.
Order Q_n first by a dot x and then by the numerical value of x; call
this permutation p. It is a genuine generic additive sweep: exactly

\[
 w_j=N a_j+2^j
 \tag{1}
\]

induces it. An integer primary-score difference dominates every possible
secondary-score difference, which has absolute value at most N-1.
For gamma_n(x)=x XOR (x >> 1), every z in Q_n satisfies

\[
 C(\gamma_n\circ(p\mathbin{\mathrm{XOR}}z))
 \ge N/2+D/2-q\ge N/2-q,
\]
\[
 R(\gamma_n\circ(p\mathbin{\mathrm{XOR}}z))\ge N/2-q-1.
 \tag{2}
\]

Here D is the number of adjacent cyclic edge-label pairs with the same
highest differing input coordinate. It is independent of z. The order
p XOR z is the actual additive order obtained from (1) by changing the
sign of coordinate j exactly when z_j=1.

Since q<=1+T for T=sum a_j, (2) implies the uniform bound

\[
 \min_{\text{all signs of }w}R
 \ge 2^{n-1}-T-2.
 \tag{3}
\]

In particular, if T=o(2^n), every sign choice in this coherent refinement
family has Gray run density at least 1/2-o(1). This is a lower bound for
the family, not an asserted exact asymptotic value.

## 2. Interior off-diagonal cancellation

Index p cyclically. Write h_i for the highest input bit in which p_i
and p_(i+1) differ, and e_i for the comparison sign of their Gray ranks.
Define for h<k

\[
 J_{hk}=\sum_{i:\{h_i,h_{i+1}\}=\{h,k\}} e_i e_{i+1},
 \qquad W=\sum_{h<k}|J_{hk}|.
 \tag{4}
\]

Call a triple (x,y,z)=(p_i,p_(i+1),p_(i+2)) interior when its three
vertices belong to one primary-score bucket. All interior contributions
to every off-diagonal J_hk sum to zero. We prove this by explicit
sign-reversing involutions, separately for each unordered label pair.

Suppose h!=k and m=max(h,k)<n-1. The three vertices have identical bits
above m. Toggle the common bit m+1 in all three vertices. This changes
their scores by the same signed a_(m+1), putting all three in a new
common bucket. It preserves their numerical order. They are still
consecutive in that bucket: any numerical vertex between the translated
endpoints has the same prefix above m, and toggling it back would give
an intervening vertex of the original score, contradicting consecutivity.
Since the original interval lies wholly in one such prefix block, no
vertex from another prefix can intervene either.

The two edge labels remain h,k. Toggling input bit m+1 toggles Gray bits
m+1 and m. It reverses precisely the Gray comparison whose highest
input difference is m; the other comparison has lower highest difference
and is unchanged. Thus the product e_i e_(i+1) changes sign. Toggling
again recovers the original triple, and no vertex is fixed. The paired
contributions cancel exactly.

If m=n-1, use (x,y,z) -> (complement z, complement y, complement x).
Complementation changes the primary score t to T-t and reverses
numerical order, so this again maps consecutive interior triples to
consecutive interior triples. The identity

\[
 \gamma_n(\bar x)=\gamma_n(x)\mathbin{\mathrm{XOR}}2^{n-1}
\]

reverses the highest-coordinate comparison and leaves the lower one
unchanged; reversal of the triple reverses both comparisons. Their
product therefore changes sign. A fixed triple would require its middle
vertex to equal its own complement, which is impossible. This is also
a sign-reversing involution. Interior cancellation is proved for all
label pairs and all n, independently of the number of buckets.

## 3. Boundaries and all sign reflections

There are q cyclic edges joining different buckets, including the
closing edge. Every noninterior triple contains such an edge. Each edge
belongs to two triples, so at most 2q triples are noninterior. Interior
off-diagonal contributions have just canceled. Each remaining contribution
has absolute value one. The triangle inequality in (4) gives

\[
 W\le2q.
 \tag{5}
\]

If two successive edge labels are equal, their Gray comparisons are
opposite: the middle vertex differs at that highest bit from both outer
vertices, while their higher bits coincide. Their contribution is -1
for every reflection. These are the D forced diagonal turns.
For an input reflection z, put sigma_h=(-1)^(gamma_n(z)_h). Each edge
comparison is multiplied by sigma_(h_i). Counting cyclic sign changes
therefore gives the exact identity

\[
 C_z=\frac{N+D-\sum_{h<k}J_{hk}\sigma_h\sigma_k}{2}.
 \tag{6}
\]

Use (5) to bound the sum in (6) by 2q. This proves the cyclic statement
in (2). Closing a linear comparison sequence introduces at most two
turns, while R is one plus the nonclosing turn count. Thus C<=R+1 and
R>=C-1, proving the linear statement without an endpoint assumption.
Reflection realizes the signed weights because
w dot (x XOR z) differs from sum_j (-1)^z_j w_j x_j by a constant.
Finally positivity and integrality give scores in {0,...,T}, so q<=T+1.
This completes the proof of (3).

## 4. Relation to the local-face countermodel

The earlier local-face obstruction deliberately resolves primary-score
ties by increasing Gray rank below T/2. That refinement violates global
translation consistency and can have R=o(N). Replacing it with the
coherent numerical refinement (1) changes the conclusion completely.

For every fixed a<a_0 from LINEAR_FACE_COHERENCE_OBSTRUCTION.md, the same
seeded integer vector has T=O(n^2 2^([H_2(a)+a]n))=o(N). Consequently
ALL sign reflections of its genuine coherent refinement satisfy

\[
 R\ge N/2-O(n^2 2^{[H_2(a)+a]n}).
\]

This is an analytic all-dimensional comparison, not an inference from
finite densities. The preserved numeric prefix intervals make the
pairing work. A general coherent secondary vector need not preserve
these intervals, so this proof must not be extrapolated to arbitrary
additive sweeps.

The remaining useful question is whether a corresponding cancellation
or turn charge survives general coherent secondary orders or genuine
subset-sum chambers with q comparable to N. Equation (3) becomes weak
when q is large; treating all generic scores as singleton buckets does
not solve the main problem.

## 5. Verification

Run python3 verify_coherent_bucket_cancellation.py. It exhausts primary
integer vectors with entries 1 through 4 in dimensions 2 through 4,
including nongeneric primary scores, and checks additional specified
vectors through dimension 12. It verifies the interior pairing directly
in the exhaustive small cases, exact cancellation in every case,
boundary equality of the graph coefficients, W<=2q, and the resulting
minimum over sign reflections. Its receipt states finite coverage;
the proof above supplies general-dimensional coverage.

The prescribed secondary refinement was also evaluated on the k=2 and
k=3 polynomial-range seed families through n=18, optimizing over ALL
sign reflections rather than only the positive vector. For n=18,
the two minimum run counts are 131,076 and 131,094 out of 262,144.
These fourteen finite vectors are exploratory receipts, not new exact
all-n formulas. The theorem proves a positive asymptotic lower bound
for those families and the wider q=o(N) class regardless of the receipts.

The reflection identity and the Gray comparator were established in the
preceding working notes; they are repeated here to make the proof
self-contained. The standard entropy estimate and coherent/translation
framework are not claimed as new. No historical priority claim is made
for this particular cancellation application.
