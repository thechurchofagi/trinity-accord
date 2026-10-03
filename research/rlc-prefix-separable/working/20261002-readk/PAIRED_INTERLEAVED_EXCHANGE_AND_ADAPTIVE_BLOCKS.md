# Interleaving obstruction and adaptive exchange blocks

Status: analytic all-dimensional results for genuine scan classes. The
uniform-all-weights constant-density M_n problem is OPEN. Published v1.0
is preserved. Standard interval packing/duality and known paired ranks
are inherited, not renamed as new techniques. This continues the exact
noncontiguous translation lemma and the preceding sublayer checkpoint.

## 1. The particular fixed five-face witnesses can collapse

Let n=5+m, T=2^m, and choose secondary coefficients

    b=(T,2T,4T,8T,16T,1,2,...,T/2),

where the tail is empty if m=0. Take primary B>2*sum(b) and actual
positive weights w_j=B+b_j. These are generic: all secondary coefficients
are distinct powers of two, and the primary separates cardinalities.
The scan is increasing cardinality followed by secondary score. The
five low INPUT coordinates have large secondary coefficients; the higher
input coordinates have small ones. This is an actual linear scan, not
an arbitrary shuffle or merely a relaxed projected word.

Retain the EXACT fixed witnesses of the previous checkpoint, one per
outer input prefix f:

    t_f=(32f+3,32f+5,32f+17), q_f=t_f XOR8.

Each is still a valid common-controller translation obligation. Its
original full-turn interval is in cardinality layer |f|+2, its mirror
in layer |f|+3. However, the same-family packing is now only Theta(m).

**Theorem.** For this entire family of T witnesses, the optimum fractional
turn-position packing lies between ceil((m+1)/2) and m+1 for every m>=0.
No equality formula is asserted.

Proof of upper bound. For l=0,...,m set g_l=2^l-1, a canonical outer
prefix of cardinality l. Put dual mass1/2 at each of the positions of

    32g_l+6 and 32g_l+14.

All2(m+1) points are distinct legal middle positions. For any f with
|f|=l, its secondary tail score is between0 and T-1. Hence

    3T+s_f < 6T+s_(g_l) < 17T+s_f,
    11T+s_f < 14T+s_(g_l) < 25T+s_f.

The compared vertices have the SAME total cardinality in each line.
Thus these two points lie in the respective original and translated
full-turn intervals of EVERY witness with |f|=l. Each support has dual
mass at least1. Total dual mass m+1 proves the bound against ALL feasible
fractional packings, not just a greedy algorithm.

For the lower bound, select the witnesses f=g_l for l=0,2,4,... . Their
supports occupy the two layers l+2,l+3; these layer pairs are disjoint.
This gives ceil((m+1)/2) pairwise disjoint witnesses.

There is also an exact unbounded-load certificate. For 1<=l<=m, the
position of vertex32g_(l-1)+13 belongs to ALL original intervals with
|f|=l and ALL translated intervals with |f|=l-1, and to no others. The
same inequalities use3<13<17 and11<13<25. Its load is exactly

    binomial(m,l)+binomial(m,l-1)=binomial(m+1,l).

Consequently bounded overlap of these particular witnesses is false by
an exponential margin. Neither this dual nor these interval loads imply
small actual RLC: witness-family capacity and actual turn complexity are
different quantities. The primary M_n target is not refuted.

## 2. Four coordinates suffice when the atomic order is suitable

Let C={a,a+1,a+2,a+3} be ANY contiguous block of four INPUT coordinates,
not necessarily the lowest or the highest. Write its secondary
coefficients as c0,c1,c2,c3. Assume the core's within-cardinality scores
are generic, and c3 is strictly largest or smallest among c0,c1,c3.
Let S=sum(abs(cj)). Require successive OUTSIDE secondary subset-score
gaps to exceed S, permitting arbitrary signed secondary coefficients
and arbitrary outside priorities. Again take B>2*sum_all(abs(b_j)) and
actual positive weights w_j=B+b_j.

For every assignment u to all outside input coordinates, sort the
single-atom triple

    u OR ((1,2,8)<<a)

by its secondary score and toggle controller coordinate a+2. Since
c3 is extreme, exactly one adjacent pair exchanges atoms0,1, so its
highest changed input bit is a+1. The other pair has highest changed
bit a+3. These differ by2, and the shared bit a+2 is initially0. The
general translated-triple lemma reverses exactly the lower comparison
for EVERY paired orientation, independently of ALL outside rank labels.

Original vertices have core cardinality1, translated vertices2. Each
full-turn interval stays inside its own core sublayer: score intervals
of different outside assignments are disjoint within any cardinality
layer by the gap hypothesis. A full interval may contain other core
vertices, which is harmless. Its middle positions all belong to the
SAME outside assignment. The two intervals in a witness lie in different
layers; different outside assignments give disjoint unions. Therefore
in every dimension n>=4 and for EVERY paired rank,

    R >= 1+2^(n-4) = 1+2^n/16.

This is an analytic scan-CLASS theorem, not a minimum over arbitrary
additive weights. On natural cardinality-numeric scans the inherited
quarter-density theorem remains stronger. The improvement here is the
smaller certificate and arbitrary INPUT block position, including fixed
coordinates both above and below its leading comparison bits.

## 3. The obstruction scans themselves admit the adaptive repair

For the SAME weights of Section1, whenever m>=4 (n>=9), choose the input
block C={5,6,7,8}. Its secondary coefficients are(1,2,4,8), with S=15.
All outside secondary coefficients are powers of two starting at16, so
their successive subset-score gaps are16>S. Section2 applies exactly,
giving a disjoint integer witness packing2^(n-4).

Thus on one and the SAME genuine scan, the fixed lower-five-face witness
family has fractional capacity O(n), while an adaptive block family has
integer capacity Omega(2^n). No change of scan order, target rank, or
relaxation is used for this separation. The particular fixed witnesses
cannot be relied on uniformly; changing the active coordinates matters.

## 4. An arbitrary five-coordinate core needs no extreme assumption

For a contiguous five-coordinate input block a,...,a+4, assume only
generic within-cardinality secondary scores. In particular the four
numbers c0,c1,c2,c4 are distinct. At least two of c0,c1,c2 lie on the
SAME side of c4. Choose such a pair with indices i<j<=2. Then c4 is
extreme among ci,cj,c4, and j+2<=4.

Sort the three single atoms(e_i,e_j,e_4) by score, leaving the unused
core coordinates fixed0, and toggle controller e_(j+1). The leading
comparison bits are a+j and a+4; their gap is at least2. The controller
is none of the three atom coordinates. The lower comparison flips and
the other is unchanged for EVERY paired rank.

Under outside secondary gap>S=sum_core(abs(cj)), the full intervals
remain in that SAME five-face's cardinality sublayers, even if other
vertices of the face lie between endpoints. Taking one witness per
outside assignment gives, in ALL dimensions n>=5,

    R >= 1+2^(n-5).

There is NO longer a condition that a particular fixed pair of low atoms
make c4 extreme. This removes the fixed-atom restriction in the previous
five-core theorem while retaining its outside separation hypothesis.
The choice follows a three-number pigeonhole argument; no finite core
minimum or ancestor optimizer is involved.

## 5. Exact audit and remaining gap

verify_interleaved_exchange_and_adaptive_blocks.py audits the complete
fixed witness family and scaled integer dual for m0..11 (Q5..Q16), all
alternating-layer disjoint witnesses and exact binomial point loads.
It checks the repair on the SAME adverse scans Q9..Q16, and arbitrary
four- and five-coordinate blocks with signed/permuted secondary scores.
All chosen intervals are verified against actual positive generic scans;
rank products and full turns are independently read directly for320
paired orientations. Full parameters, weights, chosen atoms, dual points,
loads and support digests are retained with the certificate and run log.
The all-n proofs above, rather than these finite tests, justify the stated
theorems. No new general M_n coefficient is obtained.

The next precise gap is outside-score separation. For a fixed atomic
triple with secondary range[l,u] and controller coefficient c, its two
intervals lie in windows(s_f+l,s_f+u) in layer|f|+1 and
(s_f+c+l,s_f+c+u) in layer|f|+2. Only equal outside cardinalities or
cardinalities differing by1 can conflict. Exploit this layer-aware window
description to weaken whole-face separation, or produce a strict capacity
counterexample before asserting any global uniform density. Ultimately
arbitrary additive scans without a dominant cardinality primary remain
uncovered; paired constant density and the main existence target are OPEN.
