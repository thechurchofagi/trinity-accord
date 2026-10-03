# A genuine all-dimensional separation of translation-witness families

Status: exact dual obstruction plus a positive-density packing theorem in a
different restricted scan class, both analytic in arbitrary dimension.
The main all-weight M_n target remains OPEN. Published v1.0 unchanged.
The known numerical-cardinality quarter theorem remains stronger on its
own domain; it is credited, not reclaimed as the new result.

## 1. Two-coordinate corner witnesses cannot give uniform density

Use the genuine positive generic cardinality-then-numeric scan

    w_j=2^n+2^j, j=0,...,n-1.

Its order is increasing Hamming weight, then increasing numeric vertex.
Let h,k satisfy k>=h+2, with controller coordinate c=h+1. Fix every other
coordinate, and let a have bits h,c,k all0. The two-coordinate face has
ordered corners(a,a+e_h,a+e_k,a+e_h+e_k). Take ANY of its four ordered
three-corner subsequences, and translate it by adding e_c. Every such pair
is a valid witness under PAIRED_NONCONTIGUOUS_TRANSLATION_WITNESSES.md.
The case where the controller originally equals1 gives the same union
in reverse and adds no new supports. ALL h,k and bases are allowed here.

**Theorem.** The optimum fractional turn-position packing of this ENTIRE
corner-witness subfamily is at most n-1 for every n>=3. No equality or
integer optimum is claimed. In particular it cannot give c*2^n for c>0.

Proof. Put r=|a|<=n-3. If a triple contains its lowest corner a, its turn
interval contains the FIRST position of cardinality layer r+1. For a
triple ending in layer r+1, its last vertex is not first there because its
middle vertex precedes it in that same layer. If it ends in layer r+2,
the whole intervening layer is between its endpoints. Its translated
interval similarly contains the first position of layer r+2.

If the triple omits a, its first/middle vertices lie in layer r+1 and its
last in layer r+2. The LAST position of layer r+1 is therefore strictly
between its endpoints. The translated interval contains the last position
of layer r+2. All these points are legal turn middle positions because
1<=r+1<r+2<=n-1.

Place dual mass1/2 at the first AND last position of each layer1,...,n-1.
These2(n-1) positions are distinct for n>=3. Every corner-witness union
contains at least two of them, so its total dual mass is at least1.
The sum of masses is n-1. Summing any feasible primal position-load
constraints against this dual proves the bound, with exact half units.

Thus even adding EVERY coordinate pair and all four corner triples does
not repair this local packing shortcut. The main target is not refuted:
the inherited numerical-cardinality result already forces quarter density
through other cancellation certificates on these very scans.

verify_local_corner_interval_obstruction.py enumerates every witness and
checks this scaled integer dual for n3..14. It covers
4*binomial(n-1,2)*2^(n-3) witnesses in dimension n, and directly verifies
rank-product opposition in small dimensions. Complete parameters, legal
dual positions, layer loads and witness digest are retained. Finite checks
audit the explicit all-n proof, rather than substituting for it.

## 2. Within-layer exchange triples escape the dual

Consider the equal-cardinality triple(3,5,17), ordered according to the
scan, and its controller-bit3 translate(11,13,25). These vertices exchange
single atoms1,2,4 while keeping bit0 fixed1. They are not three corners
of a two-coordinate face. If atom4 is the largest or smallest of the
three in secondary score, the two highest changed bits are2 and4.
The shared controller bit3 toggles exactly one rank comparison. The
general translation lemma therefore makes their two intervals a valid
one-turn obligation for EVERY paired orientation.

On cardinality-then-numeric order, the original interval contains exactly
the core middle vertices(5,6,9,10,12), and the translated interval exactly
(13,14,19,21,22). Both lie STRICTLY inside their cardinality layers.
They avoid the first/last layer dual positions used above in higher
dimensions when additional prefixes are present; more generally they
can be packed on disjoint prefix sublayers rather than crossing a layer
boundary. The corner-family dual is not a dual for these exchange witnesses.

For each fixed higher input prefix U=x>>5, use

    original U*32+(3,5,17), translated U*32+(11,13,25).

Within any Hamming layer, numeric ordering keeps the relevant vertices of
this prefix in a contiguous sublayer. Every turn-position interval belongs
to the same prefix and a single layer. Distinct prefixes have DISJOINT
unions. Hence there is an explicit integer packing of2^(n-5) witnesses
and R>=1+2^(n-5) for ALL paired masks and every n>=5.

This weaker bound is not advertised as an improvement over the inherited
quarter theorem. The new structural result is the separation: on the SAME
genuine scan order, all two-face corner witnesses have fractional capacity
O(n), while equal-cardinality exchange witnesses have integer capacity
Omega(2^n). Larger/nonconsecutive originals are essential to this repair.

## 3. An all-dimensional class with arbitrary core secondary scores

The disjoint-sublayer argument extends beyond numeric secondary priority.
Choose arbitrary lowest-five secondary coefficients b0,...,b4 such that
every core cardinality layer has distinct scores, and b4 is EXTREME among
b1,b2,b4. The ordering of b1,b2 may be either direction. Let

    S=sum_(j=0)^4 abs(b_j).

Choose ANY remaining secondary coefficients whose consecutive subset-score
gaps all exceed S. They may have negative signs and arbitrary priorities.
Let B>2*sum_all abs(b_j), and use actual weights w_j=B+b_j.

All w_j are positive. The primary part strictly separates cardinality
layers; the secondary part determines order within one layer. Distinct
outer-prefix secondary intervals are separated there because the core
secondary score range is at most S. Core-layer genericity then gives a
generic complete scan.

In each prefix face, sort(3,5,17) by its core secondary score. Since b4
is extreme, exactly one consecutive pair exchanges atoms1 and2 (highest
changed bit2), and the other exchanges atom4 (highest changed bit4).
Their controller-bit3 translate has the identical order. The two turn
intervals lie in two cardinality sublayers belonging to that one face.
Outer secondary separation makes different faces' intervals DISJOINT.
Thus in ALL dimensions n>=5 and for EVERY paired rank,

    R >= 1+2^(n-5) = 1+2^n/32.

No finite local minimum, root optimizer or LP is required for this proof.
Complete five-faces may occupy SIX separated cardinality-layer blocks;
their ordinary fragment-turn bound can be zero. The witness works inside
sublayers, so it handles a class not covered by whole-face protected centers.
It is still a RESTRICTED scan-class theorem, not RLC over arbitrary weights.

An explicit instance is b_core=(1,2,4,8,16), outer secondary coefficients
32,64,128,..., and B=2^(n+1)-1. Its actual order is the same
cardinality-numeric order as in Section1, although the larger primary
coefficient is a convenient sufficient bound for the general class.

verify_cardinality_sublayer_translation_packing.py checks72 genuine
instances Q5..Q13, with signed and permuted outer SECONDARY coefficients
and arbitrary permitted signed core SECONDARY coefficients. It verifies
576 paired rank orientations directly, every interval owner and disjoint
capacity, every restricted product opposition and actual full runs. The
actual linear weights stay positive. Scope must not be confused with
arbitrary signed CARDINALITY primaries or unrestricted weights.

## 4. Precise remaining proof problem

The local-corner shortcut is now excluded by a true all-dimensional dual.
Within-layer exchange witnesses repair it on separated secondary sublayers.
The remaining step is to control INTERLEAVED sublayers, or derive disjoint
exchange witnesses under arbitrary additive scores without a cardinality
primary. Both current classes retain prefix separability and are quantified
over ALL paired masks, but neither covers ALL generic scan weights.

Use the new interval supports with capped protected-center budgets and
capacity-compatible graph certificates. Preserve the distinction between
an exact valid witness, a packing lower bound, a packing upper bound and a
uniform coverage theorem. The last of these is still unproved.
