# Coherent prefix transport: a defect bound and arbitrary-secondary subclasses

Date: 2026-10-03. Unpublished all-dimensional research.
The main M_n constant-density problem remains OPEN. This note concerns
specified genuine additive sweeps, including all their coordinate-sign
reflections. Its subclass bounds are not the minimum over all sweeps.

## 1. General coherent secondary orders

Let a,b be real vectors such that the pairs (a dot x,b dot x), x in Q_n,
are distinct. Order vertices lexicographically by these two scores, giving
p. This is a genuine generic additive order: for sufficiently large L,
w=L*a+b induces it. If primary scores differ, their minimum nonzero gap
is positive, and L can dominate every secondary difference. If all
primary scores are equal, the secondary score alone is generic.
Write N=2^n, q for the number of nonempty primary-score buckets.

Use the established Gray reflection graph: h_i is the highest input
coordinate in which successive cyclic vertices differ, e_i is their
Gray comparison sign, D counts consecutive equal edge labels, and
J_hk=sum e_i*e_(i+1) over unordered distinct labels h,k. Let W=sum|J_hk|.
For any input reflection z, with sigma_h=(-1)^(gamma_n(z)_h),

\[
 C_z=(N+D-\sum_{h<k}J_{hk}\sigma_h\sigma_k)/2.
 \tag{1}
\]

A triple is interior if its vertices occur consecutively in the LINEAR
order of one bucket. The closing edge is always a designated bucket
join, even when q=1. This convention prevents a false wraparound claim.
There are q designated cyclic joins and at most 2q noninterior triples.

For m<n-1, an interior triple with distinct labels whose maximum is m
has a common input prefix above m. Toggle its common bit m+1. Call it
an orphan if the translated triple is not consecutive in the new bucket.
Let U_m count these orphans and U=sum_(m=0)^(n-2) U_m.

For a bucket t and a prefix c above m, let S_(t,c,m) be its subsequence
with that prefix, and v_(t,c,m) the number of maximal contiguous visits
to that prefix in the full bucket order. Define the qualified prefix
defect

\[
 G_m=\sum_{t,c:\ |S_{t,c,m}|\ge3}(v_{t,c,m}-1),
 \qquad G=\sum_{m=0}^{n-2}G_m.
 \tag{2}
\]

Empty classes contribute nothing. Classes with at most two vertices are
excluded deliberately: they cannot contain a three-vertex mixed-label
triple, so their fragmentation cannot cause this transport obstruction.

**Theorem 1.** For every such coherent order,

\[
 W\le2q+U\le2q+2G,
 \tag{3}
\]
\[
 \min_z C_z\ge N/2+D/2-q-U/2
              \ge N/2+D/2-q-G,
\]
\[
 \min_z R_z\ge N/2+D/2-q-G-1.
 \tag{4}
\]

The bounds may be vacuous when q or G is large. Taking a=0 includes
every generic additive sweep, but does not make G uniformly small.
The theorem is a quantitative reduction, not a solution of the main
constant-density problem.

## 2. Proof: exact pairing followed by a gap charge

For an interior triple with maximum distinct edge label m<n-1, toggling
bit m+1 adds the same signed a_(m+1) to its three primary scores and the
same signed b_(m+1) to its secondary scores. It therefore preserves
relative order. More strongly, it maps the entire primary-score/prefix
subsequence bijectively to the translated subsequence, preserving its
secondary order. This is where full coherent translation consistency is
used; a Gray-dependent tie rule need not have this property.

The translated vertices are thus consecutive in their restricted prefix
subsequence, even if other prefixes intervene in the full bucket.
When they remain globally consecutive, toggling again recovers the
original actual triple. These protected actual triples form a free
involution. The two edge labels are preserved. Toggling input bit m+1
toggles Gray bits m+1 and m, reversing precisely the comparison with
highest differing input bit m. The product of the two comparison signs
changes sign, so protected off-diagonal contributions cancel exactly.

If the maximum label is n-1, use the triple
(complement z,complement y,complement x). Both additive scores reverse
under complementation, so bucket order reverses too. This always maps
an interior actual triple to an interior actual triple. Complementation
of Gray ranks toggles only the top bit. Together with triple reversal,
exactly one of the two comparison signs changes. A fixed triple would
have a self-complementary middle vertex, which is impossible. All these
top-label interior contributions cancel as well.

It remains to count unprotected triples at each m<n-1. In a fixed
prefix class, exactly v-1 adjacent pairs in the restricted subsequence
are separated by other prefixes in the full bucket: one pair bridges
each successive visit. Each missing adjacent pair can occur in at most
two consecutive restricted triples. Every transported orphan contains
such a missing pair. Transport is injective on restricted triples and
preserves the class cardinality; any class receiving a triple has at
least three vertices. Consequently

\[
 U_m\le2\sum_{t,c:\ |S_{t,c,m}|\ge3}(v_{t,c,m}-1)=2G_m.
\]

All remaining off-diagonal graph contributions come from at most 2q
noninterior triples and U orphans. Each has absolute value one; the
triangle inequality yields (3). Equation (1) proves the cyclic part of
(4). For any linear comparison sequence, closing creates at most two
turns while R is one plus its nonclosing turns; hence R>=C-1.
Finally p XOR z is exactly the additive sweep obtained by flipping
coordinate signs of w. This proves every claim of Theorem 1.

## 3. Nearly full-dimensional arbitrary secondary weights

**Theorem 2.** Let n>=4, 1<=r<=n-3 and d=n-r. On the first d-1
coordinates take the positive integer primary vector

\[
 (1,2,\ldots,2^{d-3},2^{d-2}-1).
 \tag{5}
\]

Take primary weight one on the remaining r+1 coordinates. The first d
secondary weights b_0,...,b_(d-1) may be ANY generic additive vector,
with any signs. For the final r coordinates impose only

\[
 |b_j|>\sum_{i<j}|b_i|\quad(j\ge d).
 \tag{6}
\]

Choose L>sum|b_j| and set w_j=L*a_j+b_j. These are positive generic
weights. For ALL independent coordinate-sign choices of w,

\[
 C\ge (1/2-2^{-r-1})2^n-r,
\]
\[
 R\ge (1/2-2^{-r-1})2^n-r-1.
 \tag{7}
\]

For r=1, the secondary weights on n-1 coordinates are arbitrary,
subject to genericity, and only the final secondary coordinate must
dominate their total magnitude. Nevertheless

\[
 R\ge 2^{n-2}-2.
 \tag{8}
\]

These are constrained two-score weight families. Their arbitrary
secondary dimension does not remove the primary-vector and final
hierarchy restrictions.

**Proof.** Put t=2^(d-2)-1. The first d-2 powers of two represent every
integer from zero to t exactly once. Adding the last seed weight t
produces two ranges [0,t] and [t,2t] which overlap only at t. Thus every
subset score on the first d-1 coordinates has multiplicity at most two.
Every restriction to fewer of these coordinates has the same property.
For m<=d-2, each primary-score/prefix class fixes the higher coordinates
and allows only a subset of this seed. Its size is therefore at most
two and G_m=0, regardless of the arbitrary secondary order.

For m>=d-1, condition (6) makes every prefix above m occupy one interval
in the global secondary order. This remains true after restriction to
any primary bucket. Hence v=1 and G_m=0 at all remaining levels. Thus
G=0 and Theorem 1 gives C>=N/2-q and R>=N/2-q-1 uniformly in reflections.

The seed covers every primary score in [0,2t]. Appending r+1 unit weights
covers [0,2t+r+1], so

\[
 q=2t+r+2=2^{d-1}+r.
\]

This yields (7) and (8). Secondary genericity holds inside the arbitrary
first-d block by assumption; a differing higher bit is decided strictly
by (6). Thus b itself is generic. Since primary differences are integers
and L dominates every secondary difference, w induces the prescribed
order. Positivity follows from a_j>=1 and L>|b_j|. This completes the
all-dimensional proof.

## 4. A separate low-level freedom with extensive harmless fragmentation

For n>=3 another useful family has a_j=1 for EVERY coordinate. Let
b_0,b_1,b_2 be any three pairwise distinct real numbers. For j>=3 require
|b_j|>sum_(i<j)|b_i|, and choose L>sum|b_j| as before. Then

\[
 \min_{\text{all signs}}R\ge2^{n-1}-n-2.
 \tag{9}
\]

Indeed q=n+1. For m=0 or 1, a fixed Hamming score and higher prefix leave
at most respectively one or two choices, so G_m=0. For m>=2 the remaining
higher prefixes are contiguous by secondary dominance. Hence G=0.
The first three coordinates are generic on fixed Hamming layers because
singletons have distinct b values and pairs have the distinct complementary
sums b_0+b_1+b_2-b_j. Higher differences are decided by dominance.

For example b=(1,4,2,8,16,...) puts singleton vertices in order 1,4,2.
The highest bit of this three-coordinate block takes values 0,1,0; this
is not the numerical or a fixed signed numerical prefix order. Every
higher-coordinate assignment contributes one split in each of two
primary buckets, so the UNQUALIFIED prefix defect is N/4. Those classes
have only two vertices. The qualified defect G, and the orphan count U,
are exactly zero. Thus simply demanding all prefix fragmentation to be
o(N) would miss a genuine half-density family. Capacity qualification
is a substantive part of the general transport bound.

## 5. Audit and precise remaining gap

Run python3 verify_prefix_transport_defect.py. The exact verifier checks
protected-triple cancellation, sign reversal, the orphan gap charge,
qualification by class capacity, graph equality, and reflection minima.
It includes all 5,376 signed Q4 chambers from the inherited certified
generator, and additional coherent primary/secondary orders with zero,
positive and negative primary weights. It separately audits both positive
families above. The receipt states finite counts and a deterministic
checksum; the written proofs supply all-dimensional coverage.

The Q4 generator's completeness is established in the preceding audit
using Maclagan's characteristic polynomial and chamber count. These
counts and the general Boolean term-order/coherence framework are prior
work, not new claims. No historical priority claim is made for this
transport defect or its subclass application.

The main gap is now explicit: for arbitrary actual sweeps, orphan
contributions can remain after translation, and G can be of order N or
larger. A useful next step must charge those residual contributions to
forced turns or prove their energy cannot align. Alternatively one may
choose a coherent primary partition with small q and qualified defect,
but coverage of EVERY actual generic chamber would need proof.
The special representation in Theorem 2 has not been shown to cover
arbitrary weights and must not be called an RLC lower bound for gamma_n.
No new DOI, release or archive publication was requested in this round.

## 6. A necessary boundary loss, even with perfect interior cancellation

The stricter proposed cardinality-secondary statement E_*<=D is FALSE.
An exact six-coordinate counterexample has primary a_j=1, secondary
b=(75,74,7,14,20,60), and L=251. Its positive generic magnitudes are
(326,325,258,265,271,311). The graph is

    D=2, J_(1,3)=-2, J_(2,3)=2, J_(3,4)=2, W=E_*=6.

The reflection z=2 is realized by the actual signed vector
(326,-325,258,265,271,311), giving R=C=30<32. All 64 actual signs
were independently sorted and their minimum is exactly 30.

There are q=7 primary buckets; joint integer scores are distinct.
Every interior off-diagonal coupling cancels, and U=0. The entire
positive net energy E_*-D=4 arises from the designated bucket joins.
Thus dropping the boundary loss from Theorem 1 would be false even
when there are no transport orphans. This supplements the preceding
nonzero-interior-flux family, where forced D pays for the large coupling.

Run verify_cardinality_net_boundary_counterexample.py for the complete
finite certificate. Discovery seed 202610030835, trial 1023 of a domain
of at most 5000 draws of six distinct integers from 1 through 100.
The receipt makes no minimality or chamber-coverage claim.

This supersedes the strict cardinality net-energy conjecture left as
the next action in the concurrent master version 14. The more useful
E_*<=D+O(n) statement over unrestricted cardinality secondary vectors
remains OPEN; so does the all-chamber main problem. The present general
transport theorem retains its boundary term and is unaffected.
