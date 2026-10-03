# Layer-separated insertion and a metric obstruction inside one chamber

Date: 2026-10-03. Research lemma and exact finite counterexample.
Main M_n constant density remains OPEN. Known tree, Gray graph and
hyperplane arrangements are reused; no historical-priority claim.

## 1. Precise all-dimensional insertion identity

Let b be any k-coordinate secondary vector generic within every
cardinality layer. Let D_int,J_int,E_int be its interior graph,
as defined in CARDINALITY_HALF_DENSITY_COUNTEREXAMPLE.md. Define

    Delta(b)=max_{1<=ell<=k}
             [ max_{|y|=ell-1} b dot y - min_{|x|=ell} b dot x ].

For A>Delta(b), extend the secondary vector by

    b'=(A+b_0,...,A+b_(k-1),0).

After choosing a sufficiently large positive common primary coefficient,
this gives a genuine cardinality-first additive scan. The exact
interior graph satisfies

    D'_int=2D_int,
    J'_int=2J_int (on old labels), with no other coupling,
    E'_int=2E_int.

In particular its normalized interior net energy is unchanged:

    (E'_int-D'_int)/2^(k+1)=(E_int-D_int)/2^k.

This is a sufficient separation condition, not a statement about
arbitrary offsets, arbitrary new-coordinate weights, or full run
count doubling. The complete scan still has cardinality boundary
terms, which are not included in D_int,J_int.

**Proof.** In the extended cardinality layer ell, vertices with the
new highest bit 1 have old cardinality ell-1 and secondary scores
A*(ell-1)+b dot y. Vertices with new bit 0 have old cardinality ell
and scores A*ell+b dot x. The stated inequality places the complete
bit-1 block before the complete bit-0 block, retaining the old
within-layer order in both. Every old layer is copied exactly twice.

Inside the second block the old Gray comparison signs are unchanged.
Inside the first, the old highest Gray bit is toggled; only comparisons
with old highest label k-1 reverse. All old interior mixed couplings
involving that label are zero by core complement-reversal, so lower
couplings double and those couplings remain zero. Diagonals double.

There is at most one cross-block edge per new layer, with label k.
It cannot give a diagonal interior triple because every neighboring
old edge has label below k. All mixed interior terms involving label k
cancel by central complement-reversal in the extended coherent order.
Thus the complete interior graph is precisely the doubled graph.
Taking the maximum spin energy preserves this equality. End of proof.

The same argument holds when A is below every cross-face breakpoint:
the two blocks reverse their order, but the two copies and the
highest-label cancellation remain. Middle overlap has no such
automatic doubling identity.

## 2. Complete real-offset classification

For fixed b, the only changing comparisons in an extended layer are
between its two faces. Their score difference is

    A-(b dot y-b dot x),   |y|=|x|-1.

Thus ALL real generic offsets are covered by the open intervals
between the finitely many exact breakpoints

    { b dot y-b dot x : |y|=|x|-1 }.

At an endpoint the extended cardinality layer has a tie and is not
in the generic class. An exact rational point in each open interval
realizes its entire constant order; scale to integer coefficients
to verify it. This is an exhaustive one-parameter classification
for a fixed parent vector, not a sampled grid.

The exact audit covers these four fixed parents:

| Parent secondary vector | Intervals | Doubled parent net | Maximum child interior net |
| --- | ---: | ---: | ---: |
| (4,6,3,0,8,16,28) | 88 | 32 | 32 |
| (4,6,3,0,8,24,36) | 116 | 32 | 36 |
| (76,74,73,70,78,94,0,138) | 329 | 72 | 76 |
| (108,106,105,102,110,126,32,170,0) | 534 | 152 | 152 |

Both infinite end intervals obey the separated identity. For the
second parent A=38 in the interval (37,39) attains child net 36
and core limit 55/128. For the third A=55/2 in (27,28) attains
child net 76 and limit 109/256. The entire fourth-parent real
parameter family fails to improve its inherited 109/256 limit.
No conclusion about other parents follows.

## 3. A complete parent scan order is insufficient for this extension

The first two seven-bit parents induce exactly the SAME complete
cardinality-first order. Consequently their graphs, every parent
reflection order, every parent run count, and every core interior
graph coincide. Nevertheless the optimum over ALL real insertion
offsets differs: maximum child net 32 versus 36.

This is a strict finite metric-dependence counterexample. It is
stronger than a counterexample based only on two equal scalar run
counts: even preserving the entire parent chamber order does not
determine the best one-parameter extension. Every within-layer
strict comparison is linear in b, so the line segment joining these
two parents stays inside the same open parent chamber. The optimum
changes within that chamber, rather than only across its boundary.

The inherited scalar-doubling failures already motivated richer
state descriptions. This certificate supplies an explicit stronger
obstruction for this particular cardinality extension; it does not
claim that metric dependence or arrangement projection is a new
general mathematical principle.

## 4. What extra geometry is required

As b varies, the insertion breakpoints themselves change order.
That order can change only across equalities

    [(y-x)-(y'-x')] dot b = 0,

where both y-x and y'-x' have cardinality difference -1. These normals
have coefficients in {-2,-1,0,1,2} and coordinate sum zero.
Within a region of this refined arrangement, the order of all
cross-face breakpoints and all old within-layer comparisons is fixed.
Therefore the attainable extended layer orders, and hence the
best interior energy, are combinatorially fixed there.

Degenerate equalities among breakpoints may be identically forced by
the vertex tuples; such duplicate breakpoints are merged. Persistent
ties of this kind do not imply nongenericity of every offset.
A proof using parent chambers alone must either quantify over this
refinement or supply an inequality independent of it.

## 5. Verification, status and restart point

verify_cardinality_offset_intervals.py lists every integer breakpoint,
every interval's exact net energy, and an actual generic signed
weight witness at each improving optimum. It verifies strict
genericity, uniqueness of interval orders, exact optimizer energies,
the separated identities, and full order equality of the first two
parents. The 1,067 generic intervals have zero violations; elapsed
1.067 seconds, digest
b22ae007283494e635699dc8337077e1b269df81a308871f4327fdb13897fc3d.

No constant-density lower bound has been proved. This closes the
attempt to improve the nine-core example by changing only its
single insertion offset, and establishes the exact state information
missing from a parent-order-only induction.

The next precise gap is a geometric condition on the refined
breakpoint arrangement that guarantees a positive density under
arbitrary coherent insertions, or a certified recursive overlapping
family with growing interior deficit. Do not re-search strict
E_*<=D or E_*<=D+O(n), which were already refuted. Do not repeat the
four completed offset classifications in place of refining the
parent metric region.
