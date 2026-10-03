# A complementary cardinality/numeric quarter theorem

Status: proved for all dimensions in the stated restricted scan class.
The unrestricted constant-density problem remains open. Published v1.0 is
unchanged. This note continues PAIRED_SIBLING_RANKS.md and
PAIRED_FRAGMENTED_TWO_FACES.md; its matching concerns raw turns, not contiguous
two-dimensional face blocks. In particular it covers a genuine regime in
which all those face blocks are fragmented.

## Statement and scan scope

Let n>=3 and N=2^n. Let rho be any paired-sibling rank as defined in
PAIRED_SIBLING_RANKS.md. Order cube vertices by (|x|, x), where x denotes the
usual binary numerical value with coordinate 0 least significant. Then

    R(rho along this order) >= N/4 + 2.

The order is a generic additive scan: use integer coefficients w_j=N+2^j.
Two distinct vertices have score difference N times their cardinality
difference plus their numerical-value difference, whose absolute value is
less than N. Thus there are no ties and cardinality has priority. The same
theorem holds if the secondary coefficients are positive and naturally
superincreasing, and the common primary coefficient exceeds their sum:
these coefficients induce exactly the same vertex order. Coordinate
reflections also preserve the conclusion because the paired-sibling family
is closed under reflection. This does not cover arbitrary secondary weights
or arbitrary generic additive orders.

## Raw turns and their accounting

For consecutive scan vertices x,y let h be the highest coordinate in which
they differ. Their rank-comparison sign equals their forward-Gray comparison
sign multiplied by the orientation spin indexed by (h,x>>(h+2)); h=n-1
uses the common top spin. Denote these labels by v_i and Gray signs by s_i.
A turn with v_i=v_(i+1) has opposite Gray signs and forces a run boundary;
let D count these turns. For each distinct unordered variable pair e, let
P_e and Q_e count its raw products +1 and -1. Set

    K = sum_e min(P_e,Q_e).

Regardless of the chosen spins, each opposite raw-product pair forces at
least one run boundary. These boundaries are disjoint if the underlying raw
turn positions are disjoint. Consequently R>=1+D+K. The exact family
minimum is 1+D+K+phi, with phi the nonnegative signed-graph frustration.
We do not need phi in this proof.

## Explicit disjoint cancellation matching

For every t=1,...,n-2 and P=0,...,2^(n-t-2)-1 put U=P*2^(t+2). Consider the
two triples

    A = (U+2^(t-1), U+2^t, U+2^(t+1)),
    B = (U+2^(t+1)-1,
         U+2^(t+1)+2^t-1,
         U+2^(t+1)+2^t+2^(t-1)-1).

Each triple is consecutive within a cardinality layer, hence also in the
full scan. For A, all three lower patterns have one bit. The first two are
consecutive powers of two and no intervening numerical value has one bit.
For B, the first lower pattern consists of the lowest t+1 bits. Its next
same-cardinality pattern has bit t+1 together with the lowest t bits; the
next has bits t+1,t together with the lowest t-1 bits. These are consecutive
combination successors. Throughout each triple the bits at and above t+2
stay P; a numerical value between its entries cannot change those bits.

The edge labels in A are (theta_(t,P), theta_(t+1,P>>1)), whereas those in B
are reversed. If t+1=n-1, the second label is instead the common top spin.
For A the lower edge has Gray sign +1, since bit t+1 is 0; for B it has
Gray sign -1, since bit t+1 is 1. The higher edge has the same sign in both
triples, namely (-1)^(P mod 2), with the absent top controller interpreted
as zero. Both input comparisons increase the highest differing bit.
Thus the two raw turn products have opposite signs at the identical
unordered variable pair and can be matched.

No raw turn is used twice. The two highest-difference coordinates recover
t from a matched triple. The lower comparison's higher prefix recovers P.
For fixed t,P, A and B are distinct (their cardinalities differ by t).
It follows that this construction certifies

    K >= sum_(t=1)^(n-2) 2^(n-t-2) = N/4 - 1.

Overlap of vertices or comparisons in different triples causes no problem:
the accounting uses distinct raw turn positions, not vertex-disjoint paths.

## Two additional forced turns

The following triples are consecutive at cardinality-layer boundaries:

    (N/4, N/2, 3),
    (N-4, N/2-1, 3*N/4-1).

The first consists of the final two singletons and the first two-bit vertex.
The second consists of the final (n-2)-bit vertex and the first two
(n-1)-bit vertices. Each has highest-difference coordinate n-1 on both
edges, with opposite Gray signs, so each contributes one forced turn.
Their raw turn positions are distinct for every n>=3. They cannot coincide
with the matched mixed-label turns. Hence D>=2, and

    R >= 1+D+K >= N/4+2.

For n=3 the two boundary triples share vertices but have distinct middle
positions; this does not affect the argument. The n>=3 hypothesis is
necessary for the displayed bound (n=2 permits R=2).

## Exact audit and remaining gap

verify_paired_cardinality_numeric.py checks every listed triple and the
disjointness and load inequalities, directly from generic integer scores,
for n=3,...,18. It independently recomputes all raw-product loads and D,K.
For n<=12 it obtains an exact family optimum with the certified ancestor DP
and checks the attaining rank by direct run counting; for n<=8 it also
checks an independent standard-library recursion, and for n<=4 all masks.
Higher-dimensional results are reproducible formula certificates with a
digest, not claims that finite computation establishes the theorem.

The observed stronger equality K=N/4 for n>=4 is not proved here. Arbitrary
within-layer additive perturbations need not keep A and B consecutive.
The exact next gap is to replace numerical-priority matching by a
certificate that survives those interleavings, or to quantify its loss and
pay for that loss with independently certified negative cycles. The two
previous quarter theorems (all signed lex scans and intact/partly fragmented
face blocks) and this complementary theorem still do not cover every
generic additive scan, so they do not remove the n^2 denominator in M_n.
