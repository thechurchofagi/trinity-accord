# Noncontiguous translation turn witnesses

Status: an analytic conditional certificate in every dimension, with integer
packing and direct rank audits. Uniform positive-density coverage is OPEN.
Main M_n target and published v1.0 remain unchanged. This extends the earlier
consecutive translated raw-product matching; known cancellation identities,
interval packing and fractional covering are not renamed as inventions.

## 1. Hypotheses

Let p be a Boolean term order on Q_n, in Maclagan's existing sense: common
disjoint additions preserve comparisons and empty set is first. Actual
positive generic additive scans satisfy this. Signed scans may be reflected
to positive ones, with the known paired-family reflection closure. The proof
also works for noncoherent term orders; it uses no invented weight vector.

Let a,b,c appear in that order (not necessarily consecutively). Write h1,h2
for the highest input bits where a,b and b,c differ. Set h=min(h1,h2),
k=max(h1,h2), and assume k>=h+2. Assume all three vertices have the SAME
bit h+1. Toggle this common bit to obtain a',b',c'. Their order is preserved
by common addition when the bit was0, and by common cancellation when1.

The paired rank has bit j equal to x_j XOR x_(j+1) XOR theta_j(x>>(j+2)),
and an optional common root phase. Every theta remains arbitrary.

## 2. Exactly one restricted comparison reverses

For vertices with highest changed input bit j, their highest changed output
rank bit is also j. Its comparison direction is the input bit-j direction
times the phase (-1)^(x_(j+1) XOR theta_j(higher prefix)). All higher input
bits agree between the vertices, so this formula is well-defined.

Toggling bit h+1 reverses the comparison with highest changed bit h. Its
theta_h label uses only bits ABOVE h+1 and is unchanged. The comparison
with highest changed bit k>=h+2 is unchanged: bit h+1 lies strictly below
k, its controller bit k+1 is unchanged, and so is its theta_k label.
The highest changed input bits are unchanged by a common toggle.

Consequently for EVERY paired orientation, including either root phase,

    sign((rho(b)-rho(a))*(rho(c)-rho(b)))
      = -sign((rho(b')-rho(a'))*(rho(c')-rho(b'))).

At least one restricted triple has a peak or valley. This is a pointwise
identity, not an expectation or an optimized mask found by sampling.

## 3. A full-scan turn interval replaces missing adjacency

For any ordered triple a,b,c with a peak/valley, the complete scan between
positions pos(a) and pos(c) cannot be rank-monotone. It therefore contains
at least one turn with middle position in

    I(a,c)={pos(a)+1,...,pos(c)-1}.

This uses only that restricting a monotone word leaves a monotone word.
The translated triple need NOT be consecutive. For the pair above, at
least one complete-scan turn lies in

    S_w=I(a,c) union I(a',c').

Given a collection of such witnesses, any pairwise disjoint supports S_w
prove R>=1+number of witnesses for EVERY paired rank. More generally,
nonnegative rational masses y_w satisfying every middle-position load

    sum_(w:i in S_w) y_w <= 1

give R>=1+ceil(sum_w y_w): sum each valid obligation against its mass,
then interchange the sums. If supports have maximum overlap b, assigning
mass1/b gives the corresponding weaker bound. These are standard capacity
and counting arguments; the new input is the noncontiguous paired-translation
obligation that supplies the valid supports.

## 4. Exact executable audit and its limitations

verify_paired_translation_turn_intervals.py currently uses ORIGINAL
consecutive triples only, permits translated triples to be nonconsecutive,
deduplicates reverse pairs, and greedily packs disjoint support bitsets.
The analytic statement permits arbitrary ordered triples and rational
packings, which are NOT exhaustively implemented in this first audit.

It tests422 genuine scans: all positive Q2-Q4 representative chambers,
the new284-tail family and specified fresh positive Q5-Q12 weights. It
directly checks3396 paired rank instances, including both independently
verified noncoherent Q6 term-order examples. Every witness is tested for
the opposite restricted product and for an actual turn inside its support;
every integer packing is checked for disjointness. Totals12192 witnesses,
7947 disjoint witnesses over the genuine cases; zero violations,
1.9286610039998777seconds, audit SHA256
9cf679daa49622ad39a6b6c2c82016a08eaa52e698b00d44b0eba111f2587b42.
The full lossless certificate, complete chosen triples, position intervals,
weights, rank checks and seed202610031425 are retained with source and log.

The conditional theorem follows from Sections2-3, not these finite tests.
This does NOT prove a uniform number of witnesses, optimality of the greedy
packing, or any new unrestricted M_n coefficient.

Important negative control: the implemented consecutive-only rule has ZERO
witnesses for the natural numeric scan in EVERY dimension. In adjacent
binary increments, one highest changed bit is0 and the other is k>=1.
For k1 the required gap k>=h+2 fails. For k>=2 the carry toggles bit1,
so the three inputs do not share that controller bit. Thus this restricted
generator alone cannot give a universal constant density. The general
arbitrary-triple lemma survives: for example0,1,4 and2,3,6 satisfy it in
numeric scans. The known signed-lexicographic quarter theorem is inherited,
not reclaimed by this negative-control analysis.

The concrete284-tail audit packs2*2^(n-5) witnesses on Q5..Q12. This finite
profile is not promoted to an exact all-n theorem; the independently proved
protected-center class already guarantees the stronger5*2^(n-5)+1 bound.

## 5. Precise continuation

The live proof gap is a GLOBAL capacity bound: build a constant-density
packing from arbitrary ordered translation witnesses, protected centers,
forced turns and genuine signed-cycle obligations, without using any turn
position twice. The cancellation-consistent noncoherent domain remains a
useful stronger negative control. No proof of uniform coverage has been
derived. Original-consecutive witness counts are insufficient by the exact
numeric obstruction above. Do not restart the completed finite audit;
extend the witness generator to nonconsecutive originals, or prove a
structural packing theorem before interpreting finite counts as density.
