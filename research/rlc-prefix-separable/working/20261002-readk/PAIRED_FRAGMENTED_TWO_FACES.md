# Quarter certificates with an explicit fragmented-face loss

Date: 2026-10-03. Unpublished conditional all-dimensional theorem.
Main M_n constant density is OPEN; published v1.0 is unchanged.
This extends PAIRED_ALL_LEX_QUARTER.md without assuming a lexicographic
ordering of the remaining coordinates. The comparison-graph accounting
and face decomposition are inherited tools; no priority claim is made.

## 1. Precise theorem for arbitrary genuine additive scans

Let n>=2, N=2^n. Choose two coordinate positions j,k such that
|w_j|<|w_k| in a generic signed additive scan. There are N/4 parallel
two-dimensional coordinate faces on these positions. Call a face good
if all four of its vertices are consecutive in the full scan. Let F
be the number of other, fragmented faces.

For EVERY paired-sibling rank, the scan satisfies

    D+K >= N/4-2F,
    R >= 1+max(0,N/4-2F).

In particular, if F=0 then R>=N/4+1, regardless of how the remaining
coordinate faces are ordered. This includes genuine scans with arbitrary
non-lexicographic slow-coordinate subset-sum orders.

## 2. Disjoint certificate and exact losses

Let G=N/4-F. Because each face is ordered by the SAME two additive
coefficients, a good face is read in the signed binary pattern with j
fastest, k second. The quartet proof from the all-lex theorem applies
inside such a face. Its two internal turn positions occur at its start
index t and t+1. Different good faces have disjoint intervals and hence
disjoint internal positions.

If j>k, both positions are forced turns, yielding

    D >= 2G = N/2-2F.

If k=j+1, the two positions give one opposite-product cancellation pair,
yielding

    K >= G = N/4-F.

If k>j+1, pair parallel faces by translating the fixed controller j+1.
Of the N/8 face pairs, at most F have a bad member. Retain only pairs
with BOTH faces good. Every retained pair yields two opposite-product
matches, at exactly the same variable pairs, just as in the all-lex
proof. Thus

    K >= 2*(N/8-F)=N/4-2F.

Negative right-hand sides are harmless. More precisely, if B is the
actual number of paired good faces, then K>=2B; the certificate retains
this stronger bound. All matched raw positions are distinct. At a
variable pair with P positive and Q negative products, t disjoint
matches imply t<=min(P,Q). Other products cannot undo this certificate.
The exact run identity R_min=1+D+K+phi, phi>=0, proves the theorem.

The reasoning directly includes signed coefficients: their sign changes
only the initial free corner of each face and does not affect the three
highest changed positions or the controller pairing. Reflection closure
of the paired rank family supplies an alternative reduction to positive
coefficients.

## 3. Exact face-block scan class

After input reflection, take the free coefficients positive. Their face
span is S=|w_j|+|w_k|. Every parallel face has the same four relative
scores, and its interval is its slow-coordinate score plus [0,S].
Hence ALL faces are good precisely when every consecutive slow score
gap exceeds S. A gap equal to S would contradict full genericity, while
an overlapping pair of intervals prevents their vertex sets from both
being consecutive blocks.

For example, free coefficients 1 and 2, with remaining coefficients
8*u_i for ANY generic integer slow vector u, give disjoint face blocks.
The slow scan need not be lexicographic and may have arbitrary signs.
The new theorem therefore strictly expands the protected scan class.

## 4. All-dimensional obstruction to closing the gap by fragmentation alone

Let the full scan be cardinality-first, with a generic secondary order
inside each layer. ANY two-face has corner cardinalities s,s+1,s+1,s+2.
Every vertex in the entire middle layer s+1 lies between its earliest
and latest corners in the full scan. There are C(n,s+1)>=n such vertices,
and only two belong to the face. For n>=3, at least one external vertex
lies between its corners. Therefore no parallel two-face is good:

    F=N/4 for EVERY coordinate pair.

The fragmented-face lower bound is consequently vacuous in this genuine
all-dimensional scan class. This does not contradict the desired quarter
bound: other raw cancellations or negative cycles may still force it.
It does rigorously exclude proving a global positive constant merely
by assuming some pair has a small fragmented-face count.

## 5. Evidence and next exact restart point

Run verify_paired_fragmented_faces.py. It checks all coordinate pairs at
122 new genuine scans through n=12, including signed non-lexicographic
scores, arbitrary slow orders with separated free faces, and the fully
fragmented cardinality witnesses. It retains actual good-face starts,
disjoint forced indices, opposite raw-product pairs, stronger exact
budgets, and exact ancestor-optimized rank masks/runs. Every construction
with separated free faces has F=0 as asserted; every cardinality witness
has F=N/4 for all pairs.

Audit: 3,253 coordinate pairs, zero violations, 4.171 seconds, digest
dabb251117da6cf13a502085ec67247c2ebb1a0f3c333930bd9276d67a0e0fd5.
The sampled weights test the analytic certificate, not chamber coverage.

Next precise obligation: supply a complementary dimension-uniform budget
on scans with many fragmented faces. A useful exact preflight is the
cardinality-numerical scan w_j=2^n+2^j. Its paired graph has D=2 and
K=N/4 through n=13 (n>=4), despite all faces being fragmented. Do not
promote these finite graph values to a theorem: derive an all-dimensional
raw-product matching or explicit graph recurrence first. Recorded exact
family minima for n=3,...,12 are 4,7,12,25,51,101,203,409,819,1637.
The n=13 graph was counted but not optimized. Full arbitrary secondary
cardinality scans and arbitrary generic weights remain uncovered.
